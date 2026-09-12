"""Agrégations mensuelles pour les grilles Temps d'arrêt et Recettes.

Les vues historiques faisaient une requête par véhicule, par jour et par
modèle. Ici tout est regroupé en quelques requêtes, puis assemblé en JSON.
"""
from calendar import SUNDAY, monthrange
from collections import defaultdict
from datetime import datetime

from django.db.models import Count, Sum
from django.db.models.functions import ExtractDay
from django.utils import timezone

from .models import (
    Autrarret,
    CategoVehi,
    Entretien,
    Piece,
    Recette,
    Reparation,
    UserProfile,
    Vehicule,
    VisiteTechnique,
)

MOIS_FR = (
    '',
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
)

REPAIR_MOTIF_KEYS = {
    'Visite': 'P-vis',
    'Panne': 'pan',
    'Accident': 'acc',
}


def wants_json(request):
    if (request.GET.get('format') or '').lower() == 'json':
        return True
    return request.headers.get('X-PB-Grid') == 'json'


def parse_month_year(request):
    today = timezone.now()
    try:
        month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        month = today.month
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year
    if month < 1 or month > 12:
        month = today.month
    days = monthrange(year, month)[1]
    return month, year, days, MOIS_FR[month]


def parse_categorie_id(request):
    raw = (request.GET.get('categorie') or '').strip()
    if not raw:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def grid_shell_context(request):
    month, year, days, month_name = parse_month_year(request)
    now = timezone.now()
    return {
        'month': month,
        'year': year,
        'month_name': month_name,
        'days_in_month': range(1, days + 1),
        'month_choices': [(i, MOIS_FR[i]) for i in range(1, 13)],
        'years': range(now.year - 4, now.year + 1),
        'categories_list': CategoVehi.objects.all().order_by('category'),
        'selected_categorie_id': parse_categorie_id(request),
    }


def active_vehicules_qs(user, categorie_id=None, require_in_parc=True, restrict_gerant=True):
    qs = Vehicule.objects.select_related('category')
    if require_in_parc:
        qs = qs.filter(car_statut=True)
    if restrict_gerant and getattr(user, 'user_type', None) == '4':
        try:
            cats = user.profile.gerant_voiture.all()
            qs = qs.filter(category__in=cats) if cats.exists() else qs.none()
        except UserProfile.DoesNotExist:
            qs = qs.none()
    if categorie_id:
        qs = qs.filter(category_id=categorie_id)
    return qs.order_by('immatriculation')


def _as_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _month_kwargs(year, month):
    return {'date_saisie__year': year, 'date_saisie__month': month}


def _count_by_vehicle(model, vehicle_ids, year, month, extra=None):
    if not vehicle_ids:
        return {}
    qs = model.objects.filter(vehicule_id__in=vehicle_ids, **_month_kwargs(year, month))
    if extra:
        qs = qs.filter(**extra)
    return {
        row['vehicule_id']: _as_int(row['c'])
        for row in qs.values('vehicule_id').annotate(c=Count('id'))
    }


def _count_by_vehicle_on_date(model, vehicle_ids, on_date):
    if not vehicle_ids:
        return {}
    return {
        row['vehicule_id']: _as_int(row['c'])
        for row in model.objects.filter(
            vehicule_id__in=vehicle_ids, date_saisie=on_date
        ).values('vehicule_id').annotate(c=Count('id'))
    }


def _counts_by_vehicle_day(model, vehicle_ids, year, month):
    grid = defaultdict(lambda: defaultdict(int))
    if not vehicle_ids:
        return grid
    rows = (
        model.objects.filter(vehicule_id__in=vehicle_ids, **_month_kwargs(year, month))
        .annotate(day=ExtractDay('date_saisie'))
        .values('vehicule_id', 'day')
        .annotate(c=Count('id'))
    )
    for row in rows:
        grid[row['vehicule_id']][_as_int(row['day'])] = _as_int(row['c'])
    return grid


def _sum_by_vehicle_day(model, vehicle_ids, year, month, field='montant'):
    grid = defaultdict(lambda: defaultdict(int))
    if not vehicle_ids:
        return grid
    rows = (
        model.objects.filter(vehicule_id__in=vehicle_ids, **_month_kwargs(year, month))
        .annotate(day=ExtractDay('date_saisie'))
        .values('vehicule_id', 'day')
        .annotate(total=Sum(field))
    )
    for row in rows:
        grid[row['vehicule_id']][_as_int(row['day'])] = _as_int(row['total'])
    return grid


def _sum_by_vehicle(model, vehicle_ids, year, month, field='montant'):
    if not vehicle_ids:
        return {}
    return {
        row['vehicule_id']: _as_int(row['total'])
        for row in model.objects.filter(
            vehicule_id__in=vehicle_ids, **_month_kwargs(year, month)
        ).values('vehicule_id').annotate(total=Sum(field))
    }


def _sum_by_vehicle_on_date(model, vehicle_ids, on_date, field='montant'):
    if not vehicle_ids:
        return {}
    return {
        row['vehicule_id']: _as_int(row['total'])
        for row in model.objects.filter(
            vehicule_id__in=vehicle_ids, date_saisie=on_date
        ).values('vehicule_id').annotate(total=Sum(field))
    }


def _sum_by_vehicle_year(model, vehicle_ids, year, field='montant'):
    if not vehicle_ids:
        return {}
    return {
        row['vehicule_id']: _as_int(row['total'])
        for row in model.objects.filter(
            vehicule_id__in=vehicle_ids, date_saisie__year=year
        ).values('vehicule_id').annotate(total=Sum(field))
    }


def _repair_motif_counts(vehicle_ids, year, month):
    out = defaultdict(lambda: {'P-vis': 0, 'pan': 0, 'acc': 0})
    if not vehicle_ids:
        return out
    rows = (
        Reparation.objects.filter(
            vehicule_id__in=vehicle_ids,
            motif__in=REPAIR_MOTIF_KEYS.keys(),
            **_month_kwargs(year, month),
        )
        .values('vehicule_id', 'motif')
        .annotate(c=Count('id'))
    )
    for row in rows:
        key = REPAIR_MOTIF_KEYS.get(row['motif'])
        if key:
            out[row['vehicule_id']][key] = _as_int(row['c'])
    return out


def _piece_details(vehicle_ids, year, month):
    details = defaultdict(list)
    totals = defaultdict(lambda: {'cost': 0, 'count': 0})
    if not vehicle_ids:
        return details, totals
    qs = Piece.objects.filter(
        reparation__vehicule_id__in=vehicle_ids,
        **_month_kwargs(year, month),
    )
    for row in qs.values('reparation__vehicule_id', 'libelle').annotate(
        count=Count('id'), total_price=Sum('montant')
    ):
        vid = row['reparation__vehicule_id']
        count = _as_int(row['count'])
        price = _as_int(row['total_price'])
        details[vid].append({
            'libelle': row['libelle'] or '—',
            'count': count,
            'total_price': price,
        })
        totals[vid]['cost'] += price
        totals[vid]['count'] += count
    return details, totals


def build_temps_arret_payload(request, require_in_parc=True):
    month, year, days, month_name = parse_month_year(request)
    categorie_id = parse_categorie_id(request)
    vehicules = list(active_vehicules_qs(
        request.user, categorie_id, require_in_parc=require_in_parc, restrict_gerant=True
    ))
    ids = [v.id for v in vehicules]

    daily_rep = _counts_by_vehicle_day(Reparation, ids, year, month)
    daily_vis = _counts_by_vehicle_day(VisiteTechnique, ids, year, month)
    daily_ent = _counts_by_vehicle_day(Entretien, ids, year, month)
    daily_aut = _counts_by_vehicle_day(Autrarret, ids, year, month)
    vis_counts = _count_by_vehicle(VisiteTechnique, ids, year, month)
    ent_counts = _count_by_vehicle(Entretien, ids, year, month)
    aut_counts = _count_by_vehicle(Autrarret, ids, year, month)
    motifs = _repair_motif_counts(ids, year, month)
    incomes = _sum_by_vehicle(Recette, ids, year, month)
    parts, part_totals = _piece_details(ids, year, month)

    vehicles = []
    daily_totals = [0] * days
    totals = {
        'actions': 0,
        'cost_parts': 0,
        'income': 0,
        'pieces': 0,
        'repairs_by_motif': 0,
        'motif_arrets': 0,
        'visit': 0,
        'panne': 0,
        'accident': 0,
        'autrarret': 0,
        'visite_technique': 0,
        'entretien': 0,
    }

    for vehicule in vehicules:
        vid = vehicule.id
        repair = motifs[vid]
        vis = vis_counts.get(vid, 0)
        ent = ent_counts.get(vid, 0)
        aut = aut_counts.get(vid, 0)
        daily_actions = [
            daily_rep[vid][day] + daily_vis[vid][day] + daily_ent[vid][day] + daily_aut[vid][day]
            for day in range(1, days + 1)
        ]
        for i, value in enumerate(daily_actions):
            daily_totals[i] += value
        total_actions = vis + ent + aut + repair['P-vis'] + repair['pan'] + repair['acc']
        cost = part_totals[vid]['cost']
        income = incomes.get(vid, 0)
        piece_count = part_totals[vid]['count']
        motif_arret = {'vis': vis, 'ent': ent, 'aut': aut}
        vehicles.append({
            'immatriculation': vehicule.immatriculation,
            'marque': vehicule.marque,
            'category': vehicule.category.category if vehicule.category_id else '',
            'daily_actions': daily_actions,
            'total_actions': total_actions,
            'total_cost_parts': cost,
            'total_income': income,
            'part_details': parts[vid],
            'repairs_by_motif': dict(repair),
            'motif_arret': motif_arret,
        })
        totals['actions'] += total_actions
        totals['cost_parts'] += cost
        totals['income'] += income
        totals['pieces'] += piece_count
        totals['repairs_by_motif'] += repair['P-vis'] + repair['pan'] + repair['acc']
        totals['motif_arrets'] += vis + ent + aut
        totals['visit'] += repair['P-vis']
        totals['panne'] += repair['pan']
        totals['accident'] += repair['acc']
        totals['autrarret'] += aut
        totals['visite_technique'] += vis
        totals['entretien'] += ent

    return {
        'month': month,
        'year': year,
        'month_name': month_name,
        'days': list(range(1, days + 1)),
        'vehicles': vehicles,
        'daily_totals': daily_totals,
        'totals': totals,
        'selected_categorie_id': categorie_id,
    }


def build_recette_payload(request, require_in_parc=True):
    month, year, days, month_name = parse_month_year(request)
    categorie_id = parse_categorie_id(request)
    today = timezone.now().date()
    dimanches = [
        day for day in range(1, days + 1)
        if datetime(year, month, day).weekday() == SUNDAY
    ]
    jours_ouvrables = days - len(dimanches)
    vehicules = list(active_vehicules_qs(
        request.user,
        categorie_id,
        require_in_parc=require_in_parc,
        restrict_gerant=False,
    ))
    ids = [v.id for v in vehicules]

    daily_grid = _sum_by_vehicle_day(Recette, ids, year, month)
    month_sums = _sum_by_vehicle(Recette, ids, year, month)
    year_sums = _sum_by_vehicle_year(Recette, ids, year)
    today_sums = _sum_by_vehicle_on_date(Recette, ids, today)
    vis_today = _count_by_vehicle_on_date(VisiteTechnique, ids, today)
    ent_today = _count_by_vehicle_on_date(Entretien, ids, today)
    rep_today = _count_by_vehicle_on_date(Reparation, ids, today)

    vehicles = []
    daily_totals = [0] * days
    totals = {
        'today': 0,
        'a_verser': 0,
        'ecart': 0,
        'recette_mois': 0,
        'a_payer': 0,
        'motifs': 0,
        'recette_annuelle': 0,
    }

    for vehicule in vehicules:
        vid = vehicule.id
        recette_defaut = _as_int(getattr(vehicule.category, 'recette_defaut', 0))
        daily_actions = [daily_grid[vid][day] for day in range(1, days + 1)]
        for i, value in enumerate(daily_actions):
            daily_totals[i] += value
        recette_jour = today_sums.get(vid, 0)
        recette_mois = month_sums.get(vid, 0)
        recette_an = year_sums.get(vid, 0)
        difference = recette_jour - recette_defaut
        difference_mensuelle = recette_mois - (recette_defaut * jours_ouvrables)
        vis = vis_today.get(vid, 0)
        ent = ent_today.get(vid, 0)
        rep = rep_today.get(vid, 0)
        vehicles.append({
            'immatriculation': vehicule.immatriculation,
            'marque': vehicule.marque,
            'category': vehicule.category.category if vehicule.category_id else '',
            'daily_actions': daily_actions,
            'recette_versee': recette_jour,
            'recette_attendue': recette_defaut,
            'difference': difference,
            'recette_mensuelle': recette_mois,
            'difference_mensuelle': difference_mensuelle,
            'recette_annuelle': recette_an,
            'motif_arrets': {'vis': vis, 'ent': ent, 'rep': rep},
        })
        totals['today'] += recette_jour
        totals['a_verser'] += recette_defaut
        totals['ecart'] += difference
        totals['recette_mois'] += recette_mois
        totals['a_payer'] += difference_mensuelle
        totals['motifs'] += vis + ent + rep
        totals['recette_annuelle'] += recette_an

    verse_rows = Recette.objects.filter(**_month_kwargs(year, month))
    if categorie_id:
        verse_rows = verse_rows.filter(vehicule__category_id=categorie_id)
    verse_dict = {
        row['vehicule__category__id']: _as_int(row['total_verse'])
        for row in verse_rows.values('vehicule__category__id').annotate(total_verse=Sum('montant'))
    }

    by_category = defaultdict(lambda: {'nb': 0, 'defaut': 0, 'label': ''})
    for vehicule in vehicules:
        cat = by_category[vehicule.category_id]
        cat['nb'] += 1
        cat['defaut'] = _as_int(getattr(vehicule.category, 'recette_defaut', 0))
        cat['label'] = vehicule.category.category if vehicule.category_id else ''

    recap = []
    for cat_id, info in sorted(by_category.items(), key=lambda item: item[1]['label']):
        attendue = info['defaut'] * jours_ouvrables * info['nb']
        verse = verse_dict.get(cat_id, 0)
        recap.append({
            'categorie': info['label'],
            'nb_vehicules': info['nb'],
            'recette_defaut': info['defaut'],
            'recette_attendue': attendue,
            'recette_verse': verse,
            'ecart': verse - attendue,
        })

    return {
        'month': month,
        'year': year,
        'month_name': month_name,
        'days': list(range(1, days + 1)),
        'vehicles': vehicles,
        'daily_totals': daily_totals,
        'totals': totals,
        'recap': recap,
        'selected_categorie_id': categorie_id,
    }
