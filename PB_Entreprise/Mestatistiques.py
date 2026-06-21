"""Vue « Mes statistiques » — agrégations userauths + PB_Entreprise."""
import json
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.utils import timezone as dj_timezone
from django.views.generic import TemplateView

from userauths.mixins import CustomPermissionRequiredMixin
from userauths.models import (
    CustomUser,
    EmailVerificationToken,
    LoginHistory,
    Notification,
    PasswordHistory,
    PasswordResetOTP,
)

from .forms import DateFormMJR
from .models import (
    Assurance,
    Autrarret,
    Billetage,
    CategoVehi,
    ChargeAdminis,
    ChargeFixe,
    ChargeVariable,
    Decaissement,
    DocumentVehicule,
    Encaissement,
    Entretien,
    Patente,
    Piece,
    PiecEchange,
    Prevision,
    Recette,
    Reparation,
    SoldeJour,
    Stationnement,
    UserProfile,
    Vehicule,
    Vignette,
    VisiteTechnique,
)
from .views import (
    _dashboard_aggregate_montant,
    _dashboard_chart_axis_hint,
    _dashboard_get_period_bounds,
)


def _fmt_amount(value):
    return '{:,}'.format(value or 0).replace(',', ' ')


def _period_datetimes(date_debut, date_fin):
    start = datetime.combine(date_debut, time.min)
    end = datetime.combine(date_fin, time.max)
    if dj_timezone.is_naive(start):
        start = dj_timezone.make_aware(start)
        end = dj_timezone.make_aware(end)
    return start, end


def _vehicules_for_user(user):
    if user.user_type == '4':
        try:
            categories = user.profile.gerant_voiture.all()
            if categories.exists():
                return Vehicule.objects.filter(category__in=categories)
        except UserProfile.DoesNotExist:
            pass
        return Vehicule.objects.none()
    return Vehicule.objects.all()


def _apply_vehicle_filters(qs, form, categorie_filter=None):
    if not form.is_valid():
        return qs
    immatriculation = form.cleaned_data.get('immatriculation')
    if categorie_filter is None and form.cleaned_data.get('categorie'):
        categorie_filter = form.cleaned_data.get('categorie')
    if categorie_filter:
        qs = qs.filter(category=categorie_filter)
    if immatriculation:
        qs = qs.filter(immatriculation__icontains=immatriculation)
    return qs


def _filter_by_vehicle_path(qs, vehicule_path, vehicule_ids):
    if vehicule_ids is None:
        return qs
    return qs.filter(**{f'{vehicule_path}__in': vehicule_ids})


AUDIT_SOURCES = [
    ('Recette', Recette, 'montant', 'vehicule'),
    ('Charge fixe', ChargeFixe, 'montant', 'vehicule'),
    ('Charge variable', ChargeVariable, 'montant', 'vehicule'),
    ('Charge admin.', ChargeAdminis, 'montant', None),
    ('Réparation', Reparation, 'montant', 'vehicule'),
    ('Entretien', Entretien, 'montant', 'vehicule'),
    ('Arrêt', Autrarret, 'montant', 'vehicule'),
    ('Véhicule', Vehicule, None, None),
    ('Encaissement', Encaissement, 'montant', None),
    ('Décaissement', Decaissement, 'montant', None),
]

HISTORY_TYPE_LABELS = {'+': 'Création', '~': 'Modification', '-': 'Suppression'}


def _build_audit_trail(start, end, vehicule_ids=None, limit=40):
    start_dt, end_dt = _period_datetimes(start, end)
    entries = []
    for label, model, amount_field, vehicule_path in AUDIT_SOURCES:
        qs = model.history.filter(history_date__range=[start_dt, end_dt])
        if vehicule_ids is not None and vehicule_path:
            qs = qs.filter(**{f'{vehicule_path}__in': vehicule_ids})
        for record in qs.order_by('-history_date')[:15]:
            detail = str(record)
            if vehicule_path:
                related = getattr(record, vehicule_path, None)
                if related:
                    detail = str(related)
            entries.append({
                'model': label,
                'action': HISTORY_TYPE_LABELS.get(record.history_type, record.history_type),
                'action_code': record.history_type,
                'date': record.history_date,
                'user': record.history_user,
                'detail': detail,
                'montant': getattr(record, amount_field, None) if amount_field else None,
            })
    entries.sort(key=lambda item: item['date'], reverse=True)
    return entries[:limit]


def _login_chart_data(start, end):
    chart_dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    success_map = {d: 0 for d in chart_dates}
    failure_map = {d: 0 for d in chart_dates}
    for entry in LoginHistory.objects.filter(created_at__date__range=[start, end]):
        day = entry.created_at.date()
        if day not in success_map:
            continue
        if entry.login_successful:
            success_map[day] += 1
        else:
            failure_map[day] += 1
    labels = [str(d.day) for d in chart_dates]
    return labels, list(success_map.values()), list(failure_map.values())


def _audit_action_counts(start, end, vehicule_ids=None):
    start_dt, end_dt = _period_datetimes(start, end)
    counts = {'Création': 0, 'Modification': 0, 'Suppression': 0}
    for _label, model, _amount, vehicule_path in AUDIT_SOURCES:
        qs = model.history.filter(history_date__range=[start_dt, end_dt])
        if vehicule_ids is not None and vehicule_path:
            qs = qs.filter(**{f'{vehicule_path}__in': vehicule_ids})
        for code, label in HISTORY_TYPE_LABELS.items():
            counts[label] += qs.filter(history_type=code).count()
    return counts


class MesStatistiquesView(CustomPermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    login_url = 'login'
    permission_url = 'mes_stats'
    template_name = 'perfect/mes_statistics.html'
    form_class = DateFormMJR
    timeout_minutes = 600

    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, 'Vous avez été déconnecté')
                return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        form = self.form_class(self.request.GET)
        date_debut, date_fin, selected_period, chart_granularity = _dashboard_get_period_bounds(
            self.request, form
        )
        start_dt, end_dt = _period_datetimes(date_debut, date_fin)
        categorie_filter = form.cleaned_data.get('categorie') if form.is_valid() else None
        if selected_period != 'custom':
            categorie_filter = None

        vehicules_qs = _apply_vehicle_filters(_vehicules_for_user(user), form, categorie_filter)
        vehicule_ids = None if user.user_type != '4' else list(vehicules_qs.values_list('pk', flat=True))

        # --- Utilisateurs & connexions ---
        users_qs = CustomUser.objects.all()
        login_qs = LoginHistory.objects.filter(created_at__range=[start_dt, end_dt])
        context['users_total'] = users_qs.count()
        context['users_active'] = users_qs.filter(is_active=True).count()
        context['users_inactive'] = users_qs.filter(is_active=False).count()
        context['users_blocked'] = users_qs.filter(failed_login_attempts__gte=3).count()
        context['users_by_type'] = list(
            users_qs.values('user_type').annotate(count=Count('id')).order_by('user_type')
        )
        context['login_success'] = login_qs.filter(login_successful=True).count()
        context['login_failed'] = login_qs.filter(login_successful=False).count()
        context['login_recent'] = login_qs.select_related('user').order_by('-created_at')[:20]
        context['users_failed_attempts'] = (
            users_qs.filter(failed_login_attempts__gt=0)
            .order_by('-failed_login_attempts')[:10]
        )
        context['password_resets'] = PasswordResetOTP.objects.filter(
            created_at__range=[start_dt, end_dt]
        ).count()
        context['email_verifications'] = EmailVerificationToken.objects.filter(
            created_at__range=[start_dt, end_dt]
        ).count()
        context['password_changes'] = PasswordHistory.objects.filter(
            created_at__range=[start_dt, end_dt]
        ).count()

        login_labels, login_success_data, login_failure_data = _login_chart_data(date_debut, date_fin)
        context['login_labels_json'] = json.dumps(login_labels)
        context['login_success_json'] = json.dumps(login_success_data)
        context['login_failure_json'] = json.dumps(login_failure_data)

        # --- Véhicules ---
        in_parc = vehicules_qs.filter(car_statut=True).count()
        out_parc = vehicules_qs.filter(car_statut=False).count()
        context['vehicules_in_parc'] = in_parc
        context['vehicules_out_parc'] = out_parc
        context['vehicules_total'] = in_parc + out_parc
        vehicules_by_cat = (
            vehicules_qs.values('category__category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        context['vehicules_by_cat_labels'] = json.dumps(
            [v['category__category'] or 'N/A' for v in vehicules_by_cat]
        )
        context['vehicules_by_cat_data'] = json.dumps([v['count'] for v in vehicules_by_cat])
        context['vehicules_by_cat_in'] = list(
            vehicules_qs.filter(car_statut=True)
            .values('category__category')
            .annotate(count=Count('id'))
        )
        context['vehicules_by_cat_out'] = list(
            vehicules_qs.filter(car_statut=False)
            .values('category__category')
            .annotate(count=Count('id'))
        )

        # --- Querysets métier (période + véhicules gérant) ---
        def scoped(model, date_field='date_saisie', vehicule_path='vehicule'):
            qs = model.objects.all()
            qs = _filter_by_vehicle_path(qs, vehicule_path, vehicule_ids)
            if form.is_valid() and form.cleaned_data.get('immatriculation'):
                qs = qs.filter(**{f'{vehicule_path}__immatriculation__icontains': form.cleaned_data['immatriculation']})
            if categorie_filter and vehicule_path:
                qs = qs.filter(**{f'{vehicule_path}__category': categorie_filter})
            return qs.filter(**{f'{date_field}__range': [date_debut, date_fin]})

        recette_qs = scoped(Recette)
        chargfix_qs = scoped(ChargeFixe)
        chargvar_qs = scoped(ChargeVariable)
        reparation_qs = scoped(Reparation)
        entretien_qs = scoped(Entretien)
        autrarret_qs = scoped(Autrarret)
        piece_qs = _filter_by_vehicle_path(Piece.objects.all(), 'reparation__vehicule', vehicule_ids)
        piece_qs = piece_qs.filter(date_saisie__range=[date_debut, date_fin])
        if form.is_valid() and form.cleaned_data.get('immatriculation'):
            piece_qs = piece_qs.filter(
                reparation__vehicule__immatriculation__icontains=form.cleaned_data['immatriculation']
            )
        if categorie_filter:
            piece_qs = piece_qs.filter(reparation__vehicule__category=categorie_filter)
        piechange_qs = scoped(PiecEchange)

        def scoped_global(model, date_field='date_saisie'):
            return model.objects.filter(**{f'{date_field}__range': [date_debut, date_fin]})

        chargadmin_qs = scoped_global(ChargeAdminis)
        encaissement_qs = scoped_global(Encaissement)
        decaissement_qs = scoped_global(Decaissement)
        vignette_qs = scoped(Vignette)
        patente_qs = scoped(Patente)
        stationnement_qs = scoped(Stationnement)
        assurance_qs = scoped(Assurance)
        visite_qs = scoped(VisiteTechnique)

        totals = {
            'recettes': recette_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'charges_fixes': chargfix_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'charges_variables': chargvar_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'charges_admin': chargadmin_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'reparations': reparation_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'pieces': piece_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'pieces_echange': piechange_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'entretiens': entretien_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'arrets': autrarret_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'encaissements': encaissement_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'decaissements': decaissement_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'vignettes': vignette_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'patentes': patente_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'stationnements': stationnement_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'assurances': assurance_qs.aggregate(s=Sum('montant'))['s'] or 0,
            'visites': visite_qs.aggregate(s=Sum('montant'))['s'] or 0,
        }
        totals['charges_total'] = (
            totals['charges_fixes'] + totals['charges_variables'] + totals['charges_admin']
        )
        totals['marge'] = totals['recettes'] - totals['charges_fixes'] - totals['charges_variables']

        context['totals'] = totals
        context['totals_fmt'] = {key: _fmt_amount(val) for key, val in totals.items()}

        counts = {
            'recettes': recette_qs.count(),
            'charges_fixes': chargfix_qs.count(),
            'charges_variables': chargvar_qs.count(),
            'charges_admin': chargadmin_qs.count(),
            'reparations': reparation_qs.count(),
            'pannes': reparation_qs.filter(motif='Panne').count(),
            'accidents': reparation_qs.filter(motif='Accident').count(),
            'entretiens': entretien_qs.count(),
            'arrets': autrarret_qs.count(),
            'pieces': piece_qs.count(),
            'pieces_echange': piechange_qs.count(),
            'encaissements': encaissement_qs.count(),
            'decaissements': decaissement_qs.count(),
            'vignettes': vignette_qs.count(),
            'patentes': patente_qs.count(),
            'stationnements': stationnement_qs.count(),
            'assurances': assurance_qs.count(),
            'visites': visite_qs.count(),
            'documents': DocumentVehicule.objects.filter(date_saisie__range=[date_debut, date_fin]).count(),
            'billetages': Billetage.objects.filter(date_saisie__range=[date_debut, date_fin]).count(),
            'soldes': SoldeJour.objects.filter(date_saisie__range=[date_debut, date_fin]).count(),
            'previsions': Prevision.objects.filter(mois__range=[date_debut, date_fin]).count(),
            'categories': CategoVehi.objects.count(),
        }
        context['counts'] = counts

        # --- Graphiques financiers ---
        labels, recette_data = _dashboard_aggregate_montant(
            recette_qs, 'date_saisie', date_debut, date_fin, chart_granularity,
        )
        _, chargfix_data = _dashboard_aggregate_montant(
            chargfix_qs, 'date_saisie', date_debut, date_fin, chart_granularity,
        )
        _, chargvar_data = _dashboard_aggregate_montant(
            chargvar_qs, 'date_saisie', date_debut, date_fin, chart_granularity,
        )
        _, reparation_data = _dashboard_aggregate_montant(
            reparation_qs, 'date_saisie', date_debut, date_fin, chart_granularity,
        )
        context['chart_labels_json'] = json.dumps(labels)
        context['chart_recettes_json'] = json.dumps(recette_data)
        context['chart_chargfix_json'] = json.dumps(chargfix_data)
        context['chart_chargvar_json'] = json.dumps(chargvar_data)
        context['chart_reparations_json'] = json.dumps(reparation_data)

        repar_by_motif = list(
            reparation_qs.values('motif').annotate(count=Count('id')).order_by('-count')
        )
        context['repar_motif_labels'] = json.dumps([r['motif'] for r in repar_by_motif])
        context['repar_motif_data'] = json.dumps([r['count'] for r in repar_by_motif])

        charges_pie_labels = ['Fixes', 'Variables', 'Administratives']
        charges_pie_data = [
            totals['charges_fixes'],
            totals['charges_variables'],
            totals['charges_admin'],
        ]
        context['charges_pie_labels'] = json.dumps(charges_pie_labels)
        context['charges_pie_data'] = json.dumps(charges_pie_data)

        # --- Notifications ---
        notif_qs = Notification.objects.filter(created_at__range=[start_dt, end_dt])
        if user.user_type == '4':
            notif_qs = notif_qs.filter(user=user)
        context['notif_total'] = notif_qs.count()
        context['notif_unread'] = notif_qs.filter(lu=False).count()
        context['notif_alerts'] = notif_qs.filter(type_notif='alert').count()
        context['notif_recent'] = notif_qs.select_related('user').order_by('-created_at')[:15]
        notif_by_type = list(notif_qs.values('type_notif').annotate(count=Count('id')))
        context['notif_type_labels'] = json.dumps([n['type_notif'] for n in notif_by_type])
        context['notif_type_data'] = json.dumps([n['count'] for n in notif_by_type])
        notif_by_cat = list(notif_qs.values('categorie').annotate(count=Count('id')).order_by('-count')[:8])
        context['notif_by_category'] = notif_by_cat

        # --- Piste d'audit ---
        context['audit_trail'] = _build_audit_trail(date_debut, date_fin, vehicule_ids)
        audit_by_action = _audit_action_counts(date_debut, date_fin, vehicule_ids)
        context['audit_by_action_labels'] = json.dumps(list(audit_by_action.keys()))
        context['audit_by_action_data'] = json.dumps(list(audit_by_action.values()))

        # --- Top réparations / recettes ---
        context['top_reparations'] = (
            reparation_qs.values('vehicule__immatriculation', 'motif')
            .annotate(total=Count('id'), montant=Sum('montant'))
            .order_by('-total')[:5]
        )
        context['top_recettes'] = (
            recette_qs.values('vehicule__immatriculation')
            .annotate(total=Sum('montant'))
            .order_by('-total')[:5]
        )

        period_labels = {
            'today': "Aujourd'hui",
            'week': 'Cette semaine',
            'month': 'Ce mois',
            'year': 'Cette année',
            'custom': f'{date_debut.strftime("%d/%m/%Y")} — {date_fin.strftime("%d/%m/%Y")}',
        }
        context.update({
            'form': form,
            'selected_period': selected_period,
            'period_label': period_labels.get(selected_period, period_labels['month']),
            'date_debut': date_debut,
            'date_fin': date_fin,
            'chart_axis_hint': _dashboard_chart_axis_hint(selected_period, chart_granularity),
            'user_type_choices': dict(CustomUser._meta.get_field('user_type').choices),
        })
        return context
