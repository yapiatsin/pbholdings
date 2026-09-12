from django.shortcuts import redirect, render, get_object_or_404
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models import Count, Sum, F
import calendar
import hashlib
import json
import re
from django.db.models.functions import ExtractMonth, Coalesce, TruncDate, TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone as dj_timezone
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# =====================================================================
# VUES PUBLIQUES DU SITE (existantes)
# =====================================================================

def _sections_intro_for(categori_page):
    """Blocs intro image + texte liés à une CategoriPage (FK SectionIntroPage.page)."""
    if categori_page is None:
        return []
    return list(
        SectionIntroPage.objects
        .filter(actif=True, page=categori_page)
        .order_by('ordre', 'pk')
    )

def _chauffeur_gains_calculator_data():
    """Lit GainsChauffeur en base.
    Règles d'affichage :
    - presets (boutons « revenu souhaité ») = tous les `montant` des lignes
      `ordre >= 1`, dans l'ordre de la base.
    - hourly_rate (taux horaire utilisé par le simulateur) = dernier
      `montant_base` saisi en base (la dernière ligne dans l'ordre du modèle).
    - weekly_default (valeur par défaut « hebdomadaire ») = dernier `montant`
      saisi en base.
    Toutes les valeurs absentes → 0.
    """
    rows = list(
        GainsChauffeur.objects.filter(actif=True).order_by('ordre', 'pk')
    )

    last_row = rows[-1] if rows else None
    last_montant = float(last_row.montant) if last_row is not None else 0.0

    rows_with_base = [r for r in rows if r.montant_base is not None]
    last_row_base = rows_with_base[-1] if rows_with_base else None
    last_montant_base = (
        float(last_row_base.montant_base) if last_row_base is not None else None
    )

    hourly_rate = last_montant_base if last_montant_base is not None else 0.0

    presets = [int(round(float(r.montant))) for r in rows if r.ordre >= 1]

    return {
        'available': bool(rows),
        'hourly_rate': hourly_rate,
        'weekly_default': last_montant,
        'last_montant': last_montant,
        'last_montant_base': last_montant_base,
        'has_montant_base': last_montant_base is not None,
        'presets': presets,
    }

def _format_fcfa_space_int(value: int) -> str:
    """Affichage français des milliers (espaces insécables)."""
    s = str(int(value))
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return '\u00a0'.join(reversed(parts))


CHAUFFEUR_BRANDING_MULT = 1.12
def chauffeur_gains_compute(request):
    """Endpoint AJAX du simulateur chauffeur.

    Lit `GainsChauffeur` à chaque appel (toujours frais).

    Paramètres GET :
        mode      : 'preset' (renvoie la valeur du bouton cliqué telle quelle)
                    ou 'compute' (heures × jours × montant_base × branding)
        value     : montant du preset (mode = 'preset')
        hours     : nombre d'heures par jour (mode = 'compute')
        days      : nombre de jours par semaine (mode = 'compute')
        branding  : '1' applique le multiplicateur 1.12 ; sinon ignoré

    Réponse JSON : weekly, hourly, weeklyFormatted, hourlyFormatted, hourlyRate.
    """
    calc = _chauffeur_gains_calculator_data()
    hourly_rate = float(calc['hourly_rate'])  # dernier montant_base en BDD

    branding_on = request.GET.get('branding') == '1'
    multiplier = CHAUFFEUR_BRANDING_MULT if branding_on else 1.0
    hourly_eff = hourly_rate * multiplier

    mode = request.GET.get('mode', 'compute')

    if mode == 'preset':
        try:
            weekly = float(request.GET.get('value', '') or 0)
        except (TypeError, ValueError):
            weekly = 0.0
    else:
        try:
            hours = int(request.GET.get('hours', '') or 0)
        except (TypeError, ValueError):
            hours = 0
        try:
            days = int(request.GET.get('days', '') or 0)
        except (TypeError, ValueError):
            days = 0
        weekly = hours * days * hourly_eff

    weekly_int = int(round(weekly))
    hourly_int = int(round(hourly_eff))

    return JsonResponse({
        'mode': mode,
        'weekly': weekly,
        'hourly': hourly_eff,
        'weeklyFormatted': _format_fcfa_space_int(weekly_int),
        'hourlyFormatted': _format_fcfa_space_int(hourly_int),
        'hourlyRate': hourly_rate,
        'brandingMultiplier': multiplier,
    })


class Home(TemplateView):
    template_name = 'pb_site/index-3.html'
    timeout_minutes = 100

    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_slides'] = HeroSlide.objects.filter(actif=True).order_by('ordre')[:4]
        context['promo_sections'] = PromoSection.objects.filter(actif=True).order_by('ordre')[:3]
        context['page_accueil'] = PageAccueil.objects.filter(actif=True).prefetch_related('piliers').order_by('ordre').first()
        context['categoservices'] = CategorieService.objects.filter(actif=True).prefetch_related('caracteristiques').order_by('ordre')[:4]
        context['compteurs'] = Compteur.objects.filter(actif=True).order_by('ordre').first()
        # ---- Location voiture : onglets TypeVehiculeLocation + panneau VehiculeLocation + features
        cars_list = []
        types_qs = (TypeVehiculeLocation.objects
                    .filter(actif=True)
                    .prefetch_related('vehicules__features')
                    .order_by('ordre', 'nom'))
        for t in types_qs:
            vehicule = (t.vehicules.filter(actif=True)
                        .order_by('ordre', 'titre')
                        .first())
            if not vehicule:
                continue

            specs = {}
            if vehicule.modele:
                specs['Modèle'] = vehicule.modele
            if vehicule.nb_portes is not None:
                specs['Portes'] = str(vehicule.nb_portes)
            if vehicule.nb_sieges is not None:
                specs['Sièges'] = str(vehicule.nb_sieges)
            if vehicule.bagages:
                specs['Bagages'] = vehicule.bagages
            specs['Transmission'] = 'Automatique' if vehicule.transmission_auto else 'Manuelle'
            specs['Climatisation'] = 'Oui' if vehicule.climatisation else 'Non'
            if vehicule.age_minimum is not None:
                specs['Âge minimum'] = f"{vehicule.age_minimum} ans"

            slug = t.slug or f"type-{t.pk}"
            tab_image = ''
            if t.icone_image:
                tab_image = t.icone_image.url
            elif vehicule.image:
                tab_image = vehicule.image.url

            cars_list.append({
                'slug': slug,
                'tab_label': t.nom,
                'tab_image': tab_image,
                'image': vehicule.image.url if vehicule.image else '',
                'title': vehicule.titre,
                'desc': vehicule.description,
                'features': [f.texte for f in vehicule.features.all()],
                'price': f"{vehicule.prix}",
                'unit': vehicule.unite_prix,
                'button_text': vehicule.bouton_texte,
                'button_link': resolve_link(vehicule.bouton_lien),
                'specs': specs,
            })

        context['cars_list'] = cars_list
        context['cars_json'] = {c['slug']: c for c in cars_list}
        context['piec_detac'] = PieceDetachee.objects.filter(actif=True).order_by('ordre')[:3]

        context['blog_arti'] = (
            Article.objects.filter(actif=True)
            .select_related('categorie')
            .order_by('ordre')[:2]
        )

        # ---- Applications mobiles : catégorie + cartes associées (max 4)
        categorie_application = CategorieApplication.objects.filter(actif=True).order_by('ordre').first()
        applications_qs = (
            ApplicationCarte.objects
            .filter(actif=True)
            .select_related('categorie')
            .order_by('ordre', '-date_creation')
        )
        if categorie_application:
            applications_qs = applications_qs.filter(categorie=categorie_application)
        context['categorie_application'] = categorie_application
        context['applications'] = applications_qs[:4]
        
        context['temoignages'] = Temoignage.objects.filter(actif=True).order_by('ordre')
        context['temoignages_page'] = TemoignagePage.objects.filter(actif=True).order_by('ordre').first()
        context['sponsors'] = PartenSpons.objects.filter(actif=True).order_by('ordre')

        return context

class Apropos(TemplateView):
    template_name = 'pb_site/a_propos.html'
    timeout_minutes = 100

    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_accueil'] = PageAccueil.objects.filter(actif=True).prefetch_related('piliers').order_by('ordre').first()

        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Apropos')
            .prefetch_related(
                'statistiques',
                'question__questions',
            )
            .order_by('ordre')
            .first()
        )
        context['categori_page'] = categori_page
        if categori_page:
            context['statistiques_procedure'] = categori_page.statistiques.filter(actif=True).order_by('ordre')
            question_page = categori_page.question.filter(actif=True).order_by('ordre').first()
            context['question_page'] = question_page
            if question_page:
                context['questions'] = question_page.questions.filter(actif=True).order_by('ordre')
            else:
                context['questions'] = []
        else:
            context['caracteristiques_procedure'] = []
            context['statistiques_procedure'] = []
            context['question_page'] = None
            context['questions'] = []
        return context

class Chauffeurs(TemplateView):
    template_name = 'pb_site/chauffeurs.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # CategoriPage « Chauffeur » + données liées (caractéristiques, statistiques, questions)
        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Chauffeur')
            .prefetch_related(
                'caracteristiques',
                'statistiques',
                'question__questions',
                'sections_intro',
            )
            .order_by('ordre', 'page')
            .first()
        )
        context['categori_page'] = categori_page
        context['sections_intro'] = _sections_intro_for(categori_page)
        if categori_page:
            context['caracteristiques_procedure'] = categori_page.caracteristiques.filter(actif=True).order_by('ordre')
            context['statistiques_procedure'] = categori_page.statistiques.filter(actif=True).order_by('ordre')
            question_page = categori_page.question.filter(actif=True).order_by('ordre').first()
            context['question_page'] = question_page
            if question_page:
                context['questions'] = question_page.questions.filter(actif=True).order_by('ordre')
            else:
                context['questions'] = []
        else:
            context['caracteristiques_procedure'] = []
            context['statistiques_procedure'] = []
            context['question_page'] = None
            context['questions'] = []
        calc = _chauffeur_gains_calculator_data()
        hourly_float = float(calc['hourly_rate'])
        weekly_default = int(round(calc['weekly_default']))

        context['chauffeur_calc_available'] = calc['available']
        context['chauffeur_calc_has_montant_base'] = calc['has_montant_base']
        context['chauffeur_calc_presets'] = calc['presets']
        context['chauffeur_calc_preset_buttons'] = [
            {'value': p, 'label': _format_fcfa_space_int(p)} for p in calc['presets']
        ]
        context['chauffeur_calc_hourly_float'] = hourly_float
        context['chauffeur_calc_hourly_display'] = _format_fcfa_space_int(round(hourly_float))
        context['chauffeur_calc_weekly_display'] = _format_fcfa_space_int(weekly_default)
        context['chauffeur_calc_montant_base_display'] = (
            _format_fcfa_space_int(int(round(calc['last_montant_base'])))
            if calc['last_montant_base'] is not None
            else _format_fcfa_space_int(0)
        )
        context['chauffeur_calc_montant_display'] = _format_fcfa_space_int(
            int(round(calc['last_montant']))
        )
        context['chauffeur_calc_json'] = json.dumps({
            'hourlyRate': hourly_float,
            'weeklyDefault': weekly_default,
            'lastMontant': calc['last_montant'],
            'lastMontantBase': calc['last_montant_base'],
            'presets': calc['presets'],
        })
        return context

class Livreur(TemplateView):
    template_name = 'pb_site/livreur.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # CategoriPage « Livreur » + données liées
        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Livreur')
            .prefetch_related(
                'caracteristiques',
                'statistiques',
                'question__questions',
                'sections_intro',
            )
            .order_by('ordre')
            .first()
        )
        context['categori_page'] = categori_page
        context['sections_intro'] = _sections_intro_for(categori_page)
        if categori_page:
            context['caracteristiques_procedure'] = categori_page.caracteristiques.filter(actif=True).order_by('ordre')
            context['statistiques_procedure'] = categori_page.statistiques.filter(actif=True).order_by('ordre')
            question_page = categori_page.question.filter(actif=True).order_by('ordre').first()
            context['question_page'] = question_page
            if question_page:
                context['questions'] = question_page.questions.filter(actif=True).order_by('ordre')
            else:
                context['questions'] = []
        else:
            context['caracteristiques_procedure'] = []
            context['statistiques_procedure'] = []
            context['question_page'] = None
            context['questions'] = []
        return context

class Clients(TemplateView):
    template_name = 'pb_site/clients.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoservices'] = CategorieService.objects.filter(actif=True).prefetch_related('caracteristiques').order_by('ordre')[:4]
        # CategoriPage « Client » + données liées (caractéristiques, statistiques, questions)
        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Client')
            .prefetch_related(
                'caracteristiques',
                'statistiques',
                'question__questions',
                'sections_intro',
            )
            .order_by('ordre', 'page')
            .first()
        )
        context['categori_page'] = categori_page
        context['sections_intro'] = _sections_intro_for(categori_page)
        if categori_page:
            context['caracteristiques_procedure'] = categori_page.caracteristiques.filter(actif=True).order_by('ordre')
            context['statistiques_procedure'] = categori_page.statistiques.filter(actif=True).order_by('ordre')
            question_page = categori_page.question.filter(actif=True).order_by('ordre').first()
            context['question_page'] = question_page
            if question_page:
                context['questions'] = question_page.questions.filter(actif=True).order_by('ordre')
            else:
                context['questions'] = []
        else:
            context['caracteristiques_procedure'] = []
            context['statistiques_procedure'] = []
            context['question_page'] = None
            context['questions'] = []
        return context

class Assistance(TemplateView):
    template_name = 'pb_site/assistance.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoservices'] = CategorieService.objects.filter(actif=True).prefetch_related('caracteristiques').order_by('ordre')[:4]
        # CategoriPage « Assistance » + données liées (caractéristiques, statistiques, questions)
        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Assistance')
            .prefetch_related(
                'caracteristiques',
                'statistiques',
                'question__questions',
                'sections_intro',
            )
            .order_by('ordre', 'page')
            .first()
        )
        context['categori_page'] = categori_page
        context['sections_intro'] = _sections_intro_for(categori_page)
        if categori_page:
            context['caracteristiques_procedure'] = categori_page.caracteristiques.filter(actif=True).order_by('ordre')
            context['statistiques_procedure'] = categori_page.statistiques.filter(actif=True).order_by('ordre')
            question_page = categori_page.question.filter(actif=True).order_by('ordre').first()
            context['question_page'] = question_page
            if question_page:
                context['questions'] = question_page.questions.filter(actif=True).order_by('ordre')
            else:
                context['questions'] = []
        else:
            context['caracteristiques_procedure'] = []
            context['statistiques_procedure'] = []
            context['question_page'] = None
            context['questions'] = []
        return context

class Service(TemplateView):
    template_name = 'pb_site/service.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categori_page = (
            CategoriPage.objects
            .filter(actif=True, page__iexact='Service')
            .prefetch_related('sections_intro')
            .order_by('ordre', 'page')
            .first()
        )
        context['sections_intro'] = _sections_intro_for(categori_page)
        context['categoservices'] = (
            CategorieService.objects.filter(actif=True)
            .prefetch_related('caracteristiques')
            .order_by('ordre', 'nom')
        )
        context['promo_sections'] = (
            PromoSection.objects.filter(actif=True).order_by('ordre')[:6]
        )
        context['nos_services'] = (
            NosService.objects.filter(actif=True).order_by('ordre')[:9]
        )

        service_articles_qs = (
            Article.objects.filter(actif=True)
            .select_related('categorie')
            .prefetch_related('tags')
            .order_by('-date_publication')[:3]
        )
        context['service_articles'] = service_articles_qs

        articles_payload = []
        for a in service_articles_qs:
            cat = a.categorie
            articles_payload.append({
                'titre': a.titre,
                'slug': a.slug,
                'image': a.image_principale.url if a.image_principale else '',
                'extrait': a.extrait or '',
                'contenu': a.contenu or '',
                'auteur_nom': a.auteur_nom or '',
                'date_publication': dj_timezone.localtime(a.date_publication).isoformat()
                if a.date_publication else '',
                'nb_vues': a.nb_vues,
                'categorie_slug': cat.slug if cat else '',
                'categorie_nom': cat.nom if cat else '',
                'tags': [{'nom': t.nom, 'slug': t.slug} for t in a.tags.all()],
            })
        context['articles_json'] = json.dumps(articles_payload, ensure_ascii=False)

        _ph = 'pbarticlevueplaceholder'
        context['blog_vue_url_template'] = reverse(
            'blog_article_vue',
            kwargs={'slug': _ph},
        )
        return context

class Blog(TemplateView):
    template_name = 'pb_site/blog.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles_qs = (
            Article.objects.filter(actif=True)
            .select_related('categorie')
            .prefetch_related('tags')
            .order_by('ordre', '-date_publication')
        )
        context['articles'] = articles_qs

        articles_payload = []
        for a in articles_qs:
            cat = a.categorie
            articles_payload.append({
                'titre': a.titre,
                'slug': a.slug,
                'image': a.image_principale.url if a.image_principale else '',
                'extrait': a.extrait or '',
                'contenu': a.contenu or '',
                'auteur_nom': a.auteur_nom or '',
                'date_publication': dj_timezone.localtime(a.date_publication).isoformat()
                if a.date_publication else '',
                'nb_vues': a.nb_vues,
                'categorie_slug': cat.slug if cat else '',
                'categorie_nom': cat.nom if cat else '',
                'tags': [{'nom': t.nom, 'slug': t.slug} for t in a.tags.all()],
            })
        context['articles_json'] = json.dumps(articles_payload, ensure_ascii=False)

        categories_qs = CategorieBlog.objects.filter(actif=True).order_by('ordre', 'nom')
        context['categories'] = categories_qs
        context['categories_json'] = json.dumps(
            [{'name': c.nom, 'slug': c.slug} for c in categories_qs],
            ensure_ascii=False,
        )

        tags_qs = TagBlog.objects.all().order_by('nom')
        context['tags'] = tags_qs
        context['tags_json'] = json.dumps(
            [{'name': t.nom, 'slug': t.slug} for t in tags_qs],
            ensure_ascii=False,
        )

        _ph = 'pbarticlevueplaceholder'
        context['blog_vue_url_template'] = reverse(
            'blog_article_vue',
            kwargs={'slug': _ph},
        )
        return context

def _client_ip(request):
    """IP client (premier hop si X-Forwarded-For, sinon REMOTE_ADDR)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip() or ''
    return (request.META.get('REMOTE_ADDR') or '').strip()

def _blog_vue_cache_key(ip: str, slug: str) -> str:
    digest = hashlib.sha256(f'{ip}|{slug}'.encode('utf-8')).hexdigest()
    return f'blog_article_vue:{digest}'

BLOG_VUE_IP_COOLDOWN_SECONDS = 30 * 60

@require_POST
def blog_article_increment_vues(request, slug):
    """Incrémente nb_vues pour un article, au plus une fois par IP toutes les 30 minutes."""
    if not Article.objects.filter(actif=True, slug=slug).exists():
        return JsonResponse({'ok': False, 'error': 'not_found'}, status=404)

    ip = _client_ip(request)
    cache_key = _blog_vue_cache_key(ip, slug)
    if not cache.add(cache_key, 1, BLOG_VUE_IP_COOLDOWN_SECONDS):
        nb_vues = Article.objects.filter(slug=slug).values_list('nb_vues', flat=True).first()
        return JsonResponse({'ok': True, 'nb_vues': nb_vues, 'counted': False})

    Article.objects.filter(actif=True, slug=slug).update(nb_vues=F('nb_vues') + 1)
    nb_vues = Article.objects.filter(slug=slug).values_list('nb_vues', flat=True).first()
    return JsonResponse({'ok': True, 'nb_vues': nb_vues, 'counted': True})

class Contact(TemplateView):
    template_name = 'pb_site/contact.html'
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agences_qs = Agence.objects.filter(actif=True).order_by('ordre', 'nom')
        context['agences'] = agences_qs
        context['agences_json'] = [
            {
                'name': a.nom,
                'lat': float(a.latitude),
                'lng': float(a.longitude),
                'address': a.adresse,
                'phone': a.telephone or '',
                'email': a.email or '',
                'horaires': a.horaires or '',
            }
            for a in agences_qs
        ]
        return context


class DetailService(DetailView):
    """Détail d'une PromoSection (page service-details)."""
    model = PromoSection
    template_name = 'pb_site/service-details.html'
    context_object_name = 'promo'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return PromoSection.objects.filter(actif=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['autres_promos'] = (PromoSection.objects
                                    .filter(actif=True)
                                    .exclude(pk=self.object.pk)
                                    .order_by('ordre'))
        context['promo_sections'] = PromoSection.objects.filter(actif=True).order_by('ordre')[:3]
        context['categories'] = CategorieBlog.objects.filter(actif=True).order_by('ordre', 'nom')
        return context


class PiecesDetacheesPage(ListView):
    """Catalogue public des pièces détachées Suzuki (pagination 10 / page, filtre catégorie)."""
    template_name = 'pb_site/piecepage.html'
    context_object_name = 'pieces_catalogue'
    model = PieceDetachee
    paginate_by = 10

    _pieces_catalogue_order = ('categorie__ordre', 'categorie__nom', 'ordre', 'titre')

    def get_queryset(self):
        qs = (
            PieceDetachee.objects.filter(actif=True)
            .select_related('categorie')
        )
        cat = (self.request.GET.get('categorie') or '').strip()
        if cat == 'none':
            qs = qs.filter(categorie__isnull=True)
        elif cat.isdigit():
            qs = qs.filter(categorie_id=int(cat))
        return qs.order_by(*self._pieces_catalogue_order)

    def get(self, request, *args, **kwargs):
        piece_param = request.GET.get('piece')
        if piece_param and str(piece_param).strip().isdigit():
            pk = int(str(piece_param).strip())
            base_qs = (
                PieceDetachee.objects.filter(actif=True)
                .select_related('categorie')
                .order_by(*self._pieces_catalogue_order)
            )
            if base_qs.filter(pk=pk).exists():
                pks = list(base_qs.values_list('pk', flat=True))
                idx = pks.index(pk)
                page_num = idx // self.paginate_by + 1
                cur = request.GET.get('page') or '1'
                if str(cur) != str(page_num):
                    q = request.GET.copy()
                    q.pop('piece', None)
                    q['page'] = str(page_num)
                    url = reverse('pieces_detachees') + '?' + q.urlencode()
                    return HttpResponseRedirect(url + f'#piece-{pk}')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories_piece'] = (
            CategoriePiece.objects.filter(actif=True).order_by('ordre', 'nom')
        )
        all_active = PieceDetachee.objects.filter(actif=True)
        context['pieces_recentes'] = (
            all_active.select_related('categorie')
            .order_by('-date_creation', '-pk')[:8]
        )
        context['pieces_sans_cat_count'] = all_active.filter(categorie__isnull=True).count()
        context['current_categorie'] = (self.request.GET.get('categorie') or '').strip()
        if context.get('is_paginated'):
            context['elided_pages'] = list(
                context['paginator'].get_elided_page_range(
                    context['page_obj'].number,
                    on_each_side=1,
                    on_ends=1,
                )
            )
        else:
            context['elided_pages'] = []
        return context


# =====================================================================
# HELPER CRUD GÉNÉRIQUE — ajouter / lister / modifier / supprimer
# sur la même page HTML.
#
# URL: /manage/<slug>/            → lister + ajouter
#      /manage/<slug>/?edit=<id>  → lister + formulaire pré-rempli
#      /manage/<slug>/?delete=<id> → suppression avec confirmation
# POST: crée (si pas d'edit_id), sinon met à jour.
# =====================================================================

TEMPLATE_CRUD = 'pb_site/manage/manage_crud.html'


# =====================================================================
# HELPER — Résolution des liens « mixtes » (CharField)
#
# Plusieurs modèles (CategorieOnglet, SousCategorieOnglet, NosService,
# Equipe, PageSEO, HeroSlide, PromoSection, LienFooter…) stockent
# dans un CharField soit :
#   • un nom d'URL Django (ex: "home", "a_propos", "contact") résolu via
#     reverse()  — la cible change automatiquement si urls.py change.
#   • un chemin interne "/something/"
#   • une URL externe "https://…"
#   • un fragment "#section"
#
# resolve_link() transforme la valeur en URL utilisable dans un <a href=...>
# sans jamais planter. Utilisable côté vue ET côté template via le filter
# défini dans PBFinance/templatetags/pb_links.py.
# =====================================================================

def resolve_link(value):
    """Retourne une URL exploitable à partir d'un lien stocké en base.

    Ordre de résolution :
      1. Si vide → '#'
      2. Si c'est un nom d'URL Django connu → reverse()
      3. Sinon → la valeur telle quelle (path, URL, ancre)
    """
    if not value:
        return '#'
    value = str(value).strip()
    if not value:
        return '#'
    # URL absolue, chemin, ancre → on ne tente pas de reverse
    if value.startswith(('http://', 'https://', '/', '#', 'mailto:', 'tel:')):
        return value
    try:
        return reverse(value)
    except NoReverseMatch:
        return value


def _crud_generic(request, model_cls, form_cls, titre, url_name,
                  queryset=None, template_name=TEMPLATE_CRUD,
                  search_fields=None):
    """Gestionnaire CRUD factorisé: liste + ajouter + modifier + supprimer sur 1 page."""
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    # Suppression (GET ?delete=<id>)
    if delete_id:
        obj = get_object_or_404(model_cls, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        # GET = page de confirmation (même template, drapeau de confirmation)
        return render(request, template_name, {
            'titre': titre,
            'url_name': url_name,
            'objets': (queryset if queryset is not None else model_cls.objects.all()),
            'form': None,
            'edit_obj': None,
            'confirm_delete': obj,
            'model_name': model_cls.__name__,
        })

    # Édition (GET ?edit=<id>)
    instance = None
    if edit_id:
        instance = get_object_or_404(model_cls, pk=edit_id)

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = form_cls(instance=instance)

    # Recherche simple (GET ?q=...)
    qs = queryset if queryset is not None else model_cls.objects.all()
    q = request.GET.get('q', '').strip()
    if q and search_fields:
        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": q})
        qs = qs.filter(query)

    # Pagination
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, template_name, {
        'titre': titre,
        'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'form': form,
        'edit_obj': instance,
        'confirm_delete': None,
        'q': q,
        'model_name': model_cls.__name__,
    })


# =====================================================================
# VUES CRUD — une fonction par table
# =====================================================================

# --- 1. Configuration globale ---
@login_required(login_url='login')
def manage_siteconfig(request):
    return _crud_generic(
        request,
        SiteConfig,
        SiteConfigForm,
        "Configuration du site",
        'manage_siteconfig',
        search_fields=['nom_site', 'slogan'],
    )

@login_required(login_url='login')
def manage_lienapplication(request):
    return _crud_generic(request, LienApplication, LienApplicationForm,
                         "Liens applications", 'manage_lienapplication',
                         search_fields=['titre'])

@login_required(login_url='login')
def manage_monqrcode(request):
    return _crud_generic(request, MonQrcode, MonQrcodeForm,
                         "QR Codes", 'manage_monqrcode',
                         search_fields=['titre', 'lien'],
                         template_name='pb_site/manage/manage_monqrcode.html')


@login_required(login_url='login')
def regenerer_qrcode(request, pk):
    """Régénère le QR code d'une instance MonQrcode existante.
    Appelé par le bouton 'Générer' sur la liste."""
    qr = get_object_or_404(MonQrcode, pk=pk)
    try:
        qr.save()
        messages.success(request, f"QR code « {qr.titre} » généré avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération : {e}")
    return redirect('manage_monqrcode')

@login_required(login_url='login')
def manage_langue(request):
    return _crud_generic(request, Langue, LangueForm,
                         "Langues du site", 'manage_langue',
                         search_fields=['nom', 'slug'])

@login_required(login_url='login')
def manage_gainschauffeur(request):
    """CRUD des montants du simulateur chauffeurs (taux horaire ordre=0 + paliers)."""
    return _crud_generic(
        request,
        GainsChauffeur,
        GainsChauffeurForm,
        "Simulateur gains chauffeurs",
        'manage_gainschauffeur',
        queryset=GainsChauffeur.objects.all().order_by('ordre', 'pk'),
        search_fields=[],
    )

# --- 2. Menu / Navigation ---
@login_required(login_url='login')
def manage_categorieonglet(request):
    return _crud_generic(request, CategorieOnglet, CategorieOngletForm,
                         "Catégories d'onglets", 'manage_categorieonglet',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_souscategorieonglet(request):
    return _crud_generic(request, SousCategorieOnglet, SousCategorieOngletForm,
                         "Sous-catégories d'onglets", 'manage_souscategorieonglet',
                         search_fields=['libelle'])

# --- 3. Page d'accueil ---
@login_required(login_url='login')
def manage_heroslide(request):
    return _crud_generic(request, HeroSlide, HeroSlideForm,
                         "Slides d'accueil (Hero)", 'manage_heroslide',
                         search_fields=['titre', 'sous_titre'])

@login_required(login_url='login')
def manage_promosection(request):
    return _crud_generic(request, PromoSection, PromoSectionForm,
                         "Sections promo accueil", 'manage_promosection',
                         search_fields=['titre'])

@login_required(login_url='login')
def manage_pageaccueil(request):
    """CRUD PageAccueil + piliers imbriqués (inline formset)."""
    titre = "Blocs page d'accueil"
    url_name = 'manage_pageaccueil'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    if delete_id:
        obj = get_object_or_404(PageAccueil, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_pageaccueil.html', {
            'titre': titre, 'url_name': url_name,
            'objets': PageAccueil.objects.all(),
            'form': None, 'formset': None,
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': PageAccueil.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(PageAccueil, pk=edit_id)

    if request.method == 'POST':
        form = PageAccueilForm(request.POST, request.FILES, instance=instance)
        formset = PilierEntrepriseFormSet(
            request.POST, request.FILES,
            instance=instance or PageAccueil(),
            prefix='piliers',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = PageAccueilForm(instance=instance)
        formset = PilierEntrepriseFormSet(
            instance=instance or PageAccueil(),
            prefix='piliers',
        )

    qs = PageAccueil.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(sous_titre__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_pageaccueil.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form, 'formset': formset,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': PageAccueil.__name__,
    })

@login_required(login_url='login')
def manage_categoripage(request):
    """CRUD CategoriPage + 3 formsets imbriqués (Caractéristiques, Statistiques,
    Pages de questions) + formset imbriqué niveau 2 (Questions sous chaque
    QuestionPage)."""
    titre = "Catégories de procédures"
    url_name = 'manage_categoripage'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    if delete_id:
        obj = get_object_or_404(CategoriPage, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_categoripage.html', {
            'titre': titre, 'url_name': url_name,
            'objets': CategoriPage.objects.all(),
            'form': None, 'formset_carac': None, 'formset_stat': None,
            'formset_qpages': None, 'nested_questions': [],
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': CategoriPage.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(CategoriPage, pk=edit_id)
    parent_instance = instance or CategoriPage()

    def _build_nested_question_formsets(qpages_formset, post_data=None, files=None):
        """Construit un QuestionFormSet par QuestionPage (préfixe
        `questions-<i>`) en utilisant l'index du formset parent. Retourne
        une liste alignée avec qpages_formset.forms."""
        nested = []
        for i, qp_form in enumerate(qpages_formset.forms):
            qp_instance = qp_form.instance if qp_form.instance and qp_form.instance.pk else QuestionPage()
            prefix = f'questions-{i}'
            if post_data is not None:
                nested.append(QuestionFormSet(post_data, files, instance=qp_instance, prefix=prefix))
            else:
                nested.append(QuestionFormSet(instance=qp_instance, prefix=prefix))
        return nested

    if request.method == 'POST':
        form = CategoriPageForm(request.POST, request.FILES, instance=instance)
        formset_carac = CaracteristiqueProcedureFormSet(
            request.POST, request.FILES, instance=parent_instance, prefix='caracteristiques',
        )
        formset_stat = StatistiqueProcedureFormSet(
            request.POST, request.FILES, instance=parent_instance, prefix='statistiques',
        )
        formset_qpages = QuestionPageFormSet(
            request.POST, request.FILES, instance=parent_instance, prefix='qpages',
        )
        nested_questions = _build_nested_question_formsets(
            formset_qpages, post_data=request.POST, files=request.FILES,
        )

        all_valid = (
            form.is_valid()
            and formset_carac.is_valid()
            and formset_stat.is_valid()
            and formset_qpages.is_valid()
            and all(n.is_valid() for n in nested_questions)
        )

        if all_valid:
            parent = form.save()
            formset_carac.instance = parent
            formset_carac.save()
            formset_stat.instance = parent
            formset_stat.save()
            formset_qpages.instance = parent
            saved_qpages = formset_qpages.save()  # liste des QuestionPage créées/modifiées

            # ----- Sauvegarde des Questions imbriquées -----
            # Chaque nested formset est attaché au QuestionPage correspondant via
            # l'index du formset parent. Après save(), on récupère l'instance
            # (nouvellement créée ou éditée) pour rattacher ses Questions.
            for i, nested_fs in enumerate(nested_questions):
                try:
                    qp_form = formset_qpages.forms[i]
                except IndexError:
                    continue
                # Si la QuestionPage a été marquée pour suppression → on ignore
                if qp_form.cleaned_data.get('DELETE'):
                    continue
                qp_instance = qp_form.instance
                if not qp_instance.pk:
                    # Formulaire vierge non rempli → rien à rattacher
                    continue
                nested_fs.instance = qp_instance
                nested_fs.save()

            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = CategoriPageForm(instance=instance)
        formset_carac = CaracteristiqueProcedureFormSet(
            instance=parent_instance, prefix='caracteristiques',
        )
        formset_stat = StatistiqueProcedureFormSet(
            instance=parent_instance, prefix='statistiques',
        )
        formset_qpages = QuestionPageFormSet(
            instance=parent_instance, prefix='qpages',
        )
        nested_questions = _build_nested_question_formsets(formset_qpages)

    # Zip pour le rendu template : chaque QuestionPage a son sous-formset Question
    qpages_zipped = list(zip(formset_qpages.forms, nested_questions))

    qs = CategoriPage.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(page__icontains=q) | Q(titre__icontains=q) | Q(sous_titre__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_categoripage.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form,
        'formset_carac': formset_carac,
        'formset_stat': formset_stat,
        'formset_qpages': formset_qpages,
        'nested_questions': nested_questions,
        'qpages_zipped': qpages_zipped,
        # empty_form avec un prefixe placeholder "__qpIndex__" pour que le JS
        # puisse réécrire à la fois l'index de la QuestionPage et l'index
        # de la Question (le __prefix__ interne par défaut).
        'question_empty_form': QuestionFormSet(prefix='questions-__qpIndex__').empty_form,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': CategoriPage.__name__,
    })


@login_required(login_url='login')
def manage_sectionintropage(request):
    """CRUD : blocs texte + image (Chauffeurs, Livreur, Clients)."""
    return _crud_generic(
        request,
        SectionIntroPage,
        SectionIntroPageForm,
        "Sections d'intro (Chauffeurs, Livreur, Clients)",
        'manage_sectionintropage',
        search_fields=['sous_titre', 'titre', 'texte', 'page'],
        queryset=SectionIntroPage.objects.order_by('page', 'ordre', 'pk'),
    )

@login_required(login_url='login')
def manage_compteur(request):
    return _crud_generic(request, Compteur, CompteurForm,
                         "Compteurs / Chiffres clés", 'manage_compteur',
                         search_fields=['titre', 'sous_titre'])

@login_required(login_url='login')
def manage_categoriegestionsection(request):
    """CRUD CategorieGestionSection + sections de visibilité imbriquées."""
    titre = "Catégories + visibilité des sections"
    url_name = 'manage_categoriegestionsection'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    if delete_id:
        obj = get_object_or_404(CategorieGestionSection, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_categoriegestionsection.html', {
            'titre': titre, 'url_name': url_name,
            'objets': CategorieGestionSection.objects.all(),
            'form': None, 'formset': None,
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': CategorieGestionSection.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(CategorieGestionSection, pk=edit_id)

    if request.method == 'POST':
        form = CategorieGestionSectionForm(request.POST, request.FILES, instance=instance)
        formset = GestionSectionFormSet(
            request.POST, request.FILES,
            instance=instance or CategorieGestionSection(),
            prefix='sections',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mise à jour" if instance else "ajoutée"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = CategorieGestionSectionForm(instance=instance)
        formset = GestionSectionFormSet(
            instance=instance or CategorieGestionSection(),
            prefix='sections',
        )

    qs = CategorieGestionSection.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(libelle__icontains=q) | Q(template_path__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_categoriegestionsection.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form, 'formset': formset,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': CategorieGestionSection.__name__,
    })

@login_required(login_url='login')
def manage_gestionsection(request):
    """CRUD de la table GestionSection : pilote la visibilité des grandes
    sections de la page d'accueil (Promo, Nos services, Compteur,
    Location véhicules, Pièces détachées, Témoignages)."""
    return _crud_generic(request, GestionSection, GestionSectionForm,
                         "Gestion des sections (accueil)", 'manage_gestionsection',
                         search_fields=['titre_section'])

# --- 4. Services ---
@login_required(login_url='login')
def manage_nosservice(request):
    return _crud_generic(request, NosService, NosServiceForm,
                         "Nos Services", 'manage_nosservice',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_categorieservice(request):
    """CRUD CategorieService + caractéristiques imbriquées (inline formset)."""
    titre = "Catégories de service mobilité"
    url_name = 'manage_categorieservice'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    # Suppression (GET ?delete=<id>)
    if delete_id:
        obj = get_object_or_404(CategorieService, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_categorieservice.html', {
            'titre': titre,
            'url_name': url_name,
            'objets': CategorieService.objects.all(),
            'form': None,
            'formset': None,
            'edit_obj': None,
            'confirm_delete': obj,
            'model_name': CategorieService.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(CategorieService, pk=edit_id)

    if request.method == 'POST':
        form = CategorieServiceForm(request.POST, request.FILES, instance=instance)
        formset = CaracteristiqueServiceFormSet(
            request.POST, request.FILES, instance=instance or CategorieService(),
            prefix='caracs',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = CategorieServiceForm(instance=instance)
        formset = CaracteristiqueServiceFormSet(
            instance=instance or CategorieService(),
            prefix='caracs',
        )

    # Recherche + pagination
    qs = CategorieService.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(nom__icontains=q) | Q(tagline__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_categorieservice.html', {
        'titre': titre,
        'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'form': form,
        'formset': formset,
        'edit_obj': instance,
        'confirm_delete': None,
        'q': q,
        'model_name': CategorieService.__name__,
    })

@login_required(login_url='login')
def manage_caracteristiqueservice(request):
    return _crud_generic(request, CaracteristiqueService, CaracteristiqueServiceForm,
                         "Caractéristiques de services", 'manage_caracteristiqueservice',
                         search_fields=['texte'])

# --- 5. Location de véhicules ---
@login_required(login_url='login')
def manage_typevehiculelocation(request):
    return _crud_generic(request, TypeVehiculeLocation, TypeVehiculeLocationForm,
                         "Types de véhicules (location)", 'manage_typevehiculelocation',
                         search_fields=['nom'])

@login_required(login_url='login')
def manage_vehiculelocation(request):
    """CRUD VehiculeLocation + caractéristiques imbriquées (inline formset)."""
    titre = "Véhicules de location"
    url_name = 'manage_vehiculelocation'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    # Suppression (GET ?delete=<id>)
    if delete_id:
        obj = get_object_or_404(VehiculeLocation, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_vehiculelocation.html', {
            'titre': titre,
            'url_name': url_name,
            'objets': VehiculeLocation.objects.all(),
            'form': None,
            'formset': None,
            'edit_obj': None,
            'confirm_delete': obj,
            'model_name': VehiculeLocation.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(VehiculeLocation, pk=edit_id)

    if request.method == 'POST':
        form = VehiculeLocationForm(request.POST, request.FILES, instance=instance)
        formset = CaracteristiqueVehiculeLocationFormSet(
            request.POST, request.FILES,
            instance=instance or VehiculeLocation(),
            prefix='features',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = VehiculeLocationForm(instance=instance)
        formset = CaracteristiqueVehiculeLocationFormSet(
            instance=instance or VehiculeLocation(),
            prefix='features',
        )

    # Recherche + pagination
    qs = VehiculeLocation.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(modele__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_vehiculelocation.html', {
        'titre': titre,
        'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'form': form,
        'formset': formset,
        'edit_obj': instance,
        'confirm_delete': None,
        'q': q,
        'model_name': VehiculeLocation.__name__,
    })

# --- 6. Pièces détachées ---
@login_required(login_url='login')
def manage_categoriepiece(request):
    return _crud_generic(request, CategoriePiece, CategoriePieceForm,
                         "Catégories de pièces", 'manage_categoriepiece',
                         search_fields=['nom'])

@login_required(login_url='login')
def manage_piecedetachee(request):
    return _crud_generic(request, PieceDetachee, PieceDetacheeForm,
                         "Pièces détachées", 'manage_piecedetachee',
                         search_fields=['titre', 'badge'])

# --- 7. Processus ---
@login_required(login_url='login')
def manage_processusetape(request):
    return _crud_generic(request, ProcessusEtape, ProcessusEtapeForm,
                         "Étapes de processus", 'manage_processusetape',
                         search_fields=['titre'])

# --- 8. Présentation / À propos ---
@login_required(login_url='login')
def manage_presentation(request):
    return _crud_generic(request, Presentation, PresentationForm,
                         "Présentations", 'manage_presentation',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_pointfort(request):
    return _crud_generic(request, PointFort, PointFortForm,
                         "Points forts", 'manage_pointfort',
                         search_fields=['texte'])

# --- 9. Annonces / Bannières ---
@login_required(login_url='login')
def manage_annonceevenement(request):
    return _crud_generic(request, AnnonceEvenement, AnnonceEvenementForm,
                         "Annonces évènements", 'manage_annonceevenement',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_annonceinformation(request):
    return _crud_generic(request, AnnonceInformation, AnnonceInformationForm,
                         "Annonces & Informations", 'manage_annonceinformation',
                         search_fields=['titre'])

@login_required(login_url='login')
def manage_banniere(request):
    return _crud_generic(request, Banniere, BanniereForm,
                         "Bannières", 'manage_banniere',
                         search_fields=['texte'])

# --- 10. Réseaux sociaux / Partenaires ---
@login_required(login_url='login')
def manage_reseausocial(request):
    return _crud_generic(request, ReseauSocial, ReseauSocialForm,
                         "Réseaux sociaux", 'manage_reseausocial',
                         search_fields=['nom'])

@login_required(login_url='login')
def manage_partenspons(request):
    return _crud_generic(request, PartenSpons, PartenSponsForm,
                         "Partenaires & Sponsors", 'manage_partenspons',
                         search_fields=['nom'])

# --- 11. Témoignages ---
@login_required(login_url='login')
def manage_temoignagepage(request):
    """CRUD TemoignagePage + témoignages clients imbriqués (inline formset)."""
    titre = "Pages de témoignages"
    url_name = 'manage_temoignagepage'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    # Suppression (GET ?delete=<id>)
    if delete_id:
        obj = get_object_or_404(TemoignagePage, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_temoignagepage.html', {
            'titre': titre, 'url_name': url_name,
            'objets': TemoignagePage.objects.all(),
            'form': None, 'formset': None,
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': TemoignagePage.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(TemoignagePage, pk=edit_id)

    if request.method == 'POST':
        form = TemoignagePageForm(request.POST, request.FILES, instance=instance)
        formset = TemoignageFormSet(
            request.POST, request.FILES,
            instance=instance or TemoignagePage(),
            prefix='temos',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mis à jour" if instance else "ajoutée"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = TemoignagePageForm(instance=instance)
        formset = TemoignageFormSet(
            instance=instance or TemoignagePage(),
            prefix='temos',
        )

    # Recherche + pagination
    qs = TemoignagePage.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(sous_titre__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_temoignagepage.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form, 'formset': formset,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': TemoignagePage.__name__,
    })

# --- 12. FAQ ---
@login_required(login_url='login')
def manage_faq(request):
    return _crud_generic(request, FAQ, FAQForm,
                         "FAQ", 'manage_faq',
                         search_fields=['question', 'reponse'])

# --- 13. Équipe ---
@login_required(login_url='login')
def manage_equipe(request):
    return _crud_generic(request, Equipe, EquipeForm,
                         "Équipe", 'manage_equipe',
                         search_fields=['nom', 'role'])

# --- 14. Agences ---
@login_required(login_url='login')
def manage_agence(request):
    return _crud_generic(request, Agence, AgenceForm,
                         "Agences", 'manage_agence',
                         search_fields=['nom', 'adresse'])

# --- 15. Contact ---
@login_required(login_url='login')
def manage_pagecontact(request):
    return _crud_generic(request, PageContact, PageContactForm,
                         "Page Contact", 'manage_pagecontact',
                         search_fields=['titre'])

@login_required(login_url='login')
def manage_sujetcontact(request):
    return _crud_generic(request, SujetContact, SujetContactForm,
                         "Sujets de contact", 'manage_sujetcontact',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_messagecontact(request):
    return _crud_generic(request, MessageContact, MessageContactForm,
                         "Messages de contact", 'manage_messagecontact',
                         search_fields=['nom', 'email', 'sujet'])

# --- 16. Footer ---
@login_required(login_url='login')
def manage_footer(request):
    return _crud_generic(request, Footer, FooterForm,
                         "Footer", 'manage_footer')

@login_required(login_url='login')
def manage_lienfooter(request):
    return _crud_generic(request, LienFooter, LienFooterForm,
                         "Liens du footer", 'manage_lienfooter',
                         search_fields=['libelle'])

@login_required(login_url='login')
def manage_liencategoriefooter(request):
    """CRUD Liencategoriefooter + liens footer imbriqués (inline formset)."""
    titre = "Catégories de liens footer"
    url_name = 'manage_liencategoriefooter'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    if delete_id:
        obj = get_object_or_404(Liencategoriefooter, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_liencategoriefooter.html', {
            'titre': titre, 'url_name': url_name,
            'objets': Liencategoriefooter.objects.all(),
            'form': None, 'formset': None,
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': Liencategoriefooter.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(Liencategoriefooter, pk=edit_id)

    if request.method == 'POST':
        form = LiencategoriefooterForm(request.POST, request.FILES, instance=instance)
        formset = LienFooterFormSet(
            request.POST, request.FILES,
            instance=instance or Liencategoriefooter(),
            prefix='liens',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mis à jour" if instance else "ajouté"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = LiencategoriefooterForm(instance=instance)
        formset = LienFooterFormSet(
            instance=instance or Liencategoriefooter(),
            prefix='liens',
        )

    qs = Liencategoriefooter.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(libelle__icontains=q)

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_liencategoriefooter.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form, 'formset': formset,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': Liencategoriefooter.__name__,
    })

# --- 17. Applications mobiles ---
@login_required(login_url='login')
def manage_applicationcarte(request):
    """CRUD CategorieApplication + cartes d'application imbriquées (inline formset)."""
    titre = "Catégories applications"
    url_name = 'manage_applicationcarte'
    edit_id = request.GET.get('edit')
    delete_id = request.GET.get('delete')

    if delete_id:
        obj = get_object_or_404(CategorieApplication, pk=delete_id)
        if request.method == 'POST':
            obj.delete()
            messages.success(request, f"{titre} supprimé avec succès.")
            return redirect(url_name)
        return render(request, 'pb_site/manage/manage_categorieapplication.html', {
            'titre': titre, 'url_name': url_name,
            'objets': CategorieApplication.objects.all(),
            'form': None, 'formset': None,
            'edit_obj': None, 'confirm_delete': obj,
            'model_name': CategorieApplication.__name__,
        })

    instance = None
    if edit_id:
        instance = get_object_or_404(CategorieApplication, pk=edit_id)

    if request.method == 'POST':
        form = CategorieApplicationForm(request.POST, request.FILES, instance=instance)
        formset = ApplicationCarteFormSet(
            request.POST, request.FILES,
            instance=instance or CategorieApplication(),
            prefix='apps',
        )
        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            action = "mise à jour" if instance else "ajoutée"
            messages.success(request, f"{titre} {action} avec succès.")
            return redirect(url_name)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = CategorieApplicationForm(instance=instance)
        formset = ApplicationCarteFormSet(
            instance=instance or CategorieApplication(),
            prefix='apps',
        )

    qs = CategorieApplication.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(sous_titre__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'pb_site/manage/manage_categorieapplication.html', {
        'titre': titre, 'url_name': url_name,
        'objets': page.object_list,
        'page_obj': page, 'paginator': paginator,
        'form': form, 'formset': formset,
        'edit_obj': instance, 'confirm_delete': None,
        'q': q, 'model_name': CategorieApplication.__name__,
    })

# --- 18. Blog ---
@login_required(login_url='login')
def manage_categorieblog(request):
    return _crud_generic(request, CategorieBlog, CategorieBlogForm,
                         "Catégories de blog", 'manage_categorieblog',
                         search_fields=['nom'])

@login_required(login_url='login')
def manage_tagblog(request):
    return _crud_generic(request, TagBlog, TagBlogForm,
                         "Tags de blog", 'manage_tagblog',
                         search_fields=['nom'])

@login_required(login_url='login')
def manage_article(request):
    return _crud_generic(request, Article, ArticleForm,
                         "Articles de blog", 'manage_article',
                         search_fields=['titre', 'extrait'])

@login_required(login_url='login')
def manage_commentaireblog(request):
    return _crud_generic(request, CommentaireBlog, CommentaireBlogForm,
                         "Commentaires de blog", 'manage_commentaireblog',
                         search_fields=['nom', 'contenu'])

# --- 20. Statistiques ---
def manage_pagesitesearch(request):
    return _crud_generic(request, PageSiteSearch, PageSiteSearchForm,
                         "Pages (référentiel)", 'manage_pagesitesearch',
                         search_fields=['nom', 'slug'])

# NB : Visite, Clic, StatistiqueAgregee n'ont pas de CRUD — elles sont
# alimentées automatiquement par TrackingMiddleware et /track-click/.

# =====================================================================
# TABLEAU DE BORD DE GESTION — liste des modules accessibles
# =====================================================================

class ManageDashboardView(LoginRequiredMixin, TemplateView):
    """Tableau de bord de gestion du site public."""
    login_url = 'login'
    template_name = 'pb_site/manage/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = [
        ("Configuration & SEO", [
            ('manage_siteconfig', "Configuration du site"),
            ('manage_langue', "Langues du site"),
            ('manage_monqrcode', "QR Codes"),
        ]),
        ("Menu & Navigation", [
            ('manage_categorieonglet', "Catégories d'onglets"),
            ('manage_souscategorieonglet', "Sous-catégories d'onglets"),
        ]),
        ("Page d'accueil", [
            ('manage_heroslide', "Slides Hero"),
            ('manage_promosection', "Sections promo"),
            ('manage_pageaccueil', "Blocs d'accueil"),
            ('manage_compteur', "Compteurs"),
            ('manage_categoriegestionsection', "Catégories + visibilité des sections"),
        ]),
        ("Catégories de procédures", [
            ('manage_categoripage', "Catégories de procédures"),
            ('manage_sectionintropage', "Sections d'intro (Chauffeurs, Livreur, Clients)"),
            ('manage_gainschauffeur', "Simulateur gains chauffeurs (taux + paliers)"),
        ]),
        ("Services & Mobilité", [
            ('manage_nosservice', "Nos services"),
            ('manage_categorieservice', "Catégories de service"),
            ('manage_caracteristiqueservice', "Caractéristiques de service"),
        ]),
        ("Location véhicules", [
            ('manage_typevehiculelocation', "Types de véhicule"),
            ('manage_vehiculelocation', "Véhicules de location"),
        ]),
        ("Pièces détachées", [
            ('manage_categoriepiece', "Catégories de pièces"),
            ('manage_piecedetachee', "Pièces détachées"),
        ]),
        ("Processus", [
            ('manage_processusetape', "Étapes de processus"),
        ]),
        ("Présentation", [
            ('manage_presentation', "Présentations"),
            ('manage_pointfort', "Points forts"),
        ]),
        ("Annonces & Bannières", [
            ('manage_annonceevenement', "Annonces évènements"),
            ('manage_annonceinformation', "Annonces informations"),
            ('manage_banniere', "Bannières"),
        ]),
        ("Réseaux & Partenaires", [
            ('manage_reseausocial', "Réseaux sociaux"),
            ('manage_partenspons', "Partenaires & Sponsors"),
        ]),
        ("Avis clients", [
            ('manage_temoignagepage', "Pages de témoignages"),
        ]),
        ("FAQ", [
            ('manage_faq', "Questions fréquentes"),
        ]),
        ("Équipe & Agences", [
            ('manage_equipe', "Équipe"),
            ('manage_agence', "Agences"),
        ]),
        ("Contact", [
            ('manage_pagecontact', "Page Contact"),
            ('manage_sujetcontact', "Sujets de contact"),
            ('manage_messagecontact', "Messages reçus"),
        ]),
        ("Footer", [
            ('manage_footer', "Configuration footer"),
            ('manage_liencategoriefooter', "Catégories de liens footer"),
            ('manage_lienfooter', "Liens du footer"),
        ]),
        ("Applications mobiles", [
            ('manage_applicationcarte', "Catégories applications + cartes"),
            ('manage_lienapplication', "Liens applications"),
        ]),
        ("Blog", [
            ('manage_categorieblog', "Catégories blog"),
            ('manage_tagblog', "Tags blog"),
            ('manage_article', "Articles"),
            ('manage_commentaireblog', "Commentaires"),
        ]),
        ("Statistiques", [
            ('stats_dashboard', "Tableau de bord statistiques"),
            ('manage_pagesitesearch', "Référentiel pages"),
        ]),
        ]
        return context

# =====================================================================
# TRACKING AUTOMATIQUE — endpoint AJAX des clics
# =====================================================================

def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


@csrf_exempt
@require_POST
def track_click(request):
    """Endpoint appelé par static/pb_site_asset/js/tracking/pb_tracking.js."""
    element = (request.POST.get('element') or '')[:200]
    url_page = (request.POST.get('url_page') or '')[:255]
    try:
        Clic.objects.create(
            element=element,
            url_page=url_page,
            session_key=request.session.session_key or '',
            ip_address=_client_ip(request),
        )
    except Exception:
        return JsonResponse({'ok': False}, status=204)
    return JsonResponse({'ok': True})


RESEAU_CLICK_WINDOW_MINUTES = 30   # même IP + même réseau = 1 clic / 30 min
def reseau_social_click(request, pk):
    """Incrémente le compteur de clics du réseau social puis redirige vers son lien.

    Déduplication : une même adresse IP qui clique sur la même icône de
    réseau social n'est comptée qu'UNE SEULE fois par fenêtre de
    RESEAU_CLICK_WINDOW_MINUTES minutes (30 min par défaut). Au-delà de
    cette fenêtre, un nouveau clic de la même IP incrémente à nouveau.

    À utiliser comme href de l'icône de réseau social dans les templates :
        <a href="{% url 'reseau_social_click' r.pk %}" target="_blank" rel="noopener">
    """
    reseau = get_object_or_404(ReseauSocial, pk=pk, actif=True)
    now = dj_timezone.now()
    ip = _client_ip(request) or ''
    element_key = f"reseau:{reseau.nom}"
    window_start = now - timedelta(minutes=RESEAU_CLICK_WINDOW_MINUTES)

    deja_compte = Clic.objects.filter(
        element=element_key,
        ip_address=ip,
        date_clic__gte=window_start,
    ).exists() if ip else False

    if not deja_compte:
        ReseauSocial.objects.filter(pk=reseau.pk).update(
            counter=F('counter') + 1,
            date_dernier_clic=now,
        )
        try:
            Clic.objects.create(
                element=element_key,
                url_page=request.META.get('HTTP_REFERER', '')[:500],
                session_key=request.session.session_key or '',
                ip_address=ip or None,
            )
        except Exception:
            pass
    return HttpResponseRedirect(reseau.lien)


# =====================================================================
# TABLEAU DE BORD STATISTIQUES
#
# RÈGLE DE COMPTAGE DES VISITES :
# Une même adresse IP n'est comptée qu'UNE SEULE fois par fenêtre de
# 30 minutes. Si la même machine reste/revient sur le site, on attend
# la prochaine tranche de 30 min avant d'incrémenter à nouveau.
#   ex: IP 1.2.3.4 navigue à 10:05, 10:15, 10:25  → 1 visite
#       IP 1.2.3.4 revient  à 10:35               → +1 = 2 visites
#
# Règle appliquée côté vue (agrégation au moment de l'affichage) : ainsi
# les données brutes restent granulaires en base mais les KPI reflètent
# des visites « réelles ».
# =====================================================================

VISIT_WINDOW_MINUTES = 30   # tranche de déduplication par IP
CLICK_WINDOW_MINUTES = VISIT_WINDOW_MINUTES  # même règle pour les clics (IP + fenêtre)

# Pages publiques comptées comme « clic » (1 IP / fenêtre par URL)
_TRACKED_PAGE_DETAIL_RE = re.compile(r'^/Services/\d+ info/?$')
TRACKED_PAGE_CLICK_RULES = (
    {'label': 'À propos', 'paths': frozenset({'/A-propos/', '/A-propos'})},
    {'label': 'Chauffeurs', 'paths': frozenset({'/Chauffeurs/', '/Chauffeurs'})},
    {'label': 'Livreur', 'paths': frozenset({'/Livreur/', '/Livreur'})},
    {'label': 'Clients', 'paths': frozenset({'/Clients/', '/Clients'})},
    {'label': 'Assistances', 'paths': frozenset({'/Assistances/', '/Assistances'})},
    {'label': 'Contact', 'paths': frozenset({'/Contact/', '/Contact'})},
    {'label': 'Services', 'paths': frozenset({'/Services/', '/Services'})},
    {'label': 'Pièces détachées', 'paths': frozenset({'/Pieces-detachees/', '/Pieces-detachees'})},
    {'label': 'Blog', 'paths': frozenset({'/Blog/', '/Blog'})},
)


def _tracked_page_label(path):
    """Libellé affiché pour une URL de page suivie."""
    if _TRACKED_PAGE_DETAIL_RE.match(path or ''):
        return 'Détail service'
    for rule in TRACKED_PAGE_CLICK_RULES:
        if path in rule['paths']:
            return rule['label']
    return path or '—'


def is_tracked_page_click(path):
    """True si l'URL correspond à une page à comptabiliser comme clic."""
    p = path or '/'
    if _TRACKED_PAGE_DETAIL_RE.match(p):
        return True
    return any(p in rule['paths'] for rule in TRACKED_PAGE_CLICK_RULES)


def register_tracked_page_click(request, path):
    """Enregistre une visite de page suivie dans Clic (dédup. IP + fenêtre)."""
    if not is_tracked_page_click(path):
        return
    ip = _client_ip(request) or ''
    element = f"page:{(path or '/')[:490]}"
    now = dj_timezone.now()
    window_start = now - timedelta(minutes=CLICK_WINDOW_MINUTES)
    if ip and Clic.objects.filter(
        element=element,
        ip_address=ip,
        date_clic__gte=window_start,
    ).exists():
        return
    if not request.session.session_key:
        request.session.save()
    try:
        Clic.objects.create(
            element=element,
            url_page=path[:500],
            session_key=request.session.session_key or '',
            ip_address=ip or None,
        )
    except Exception:
        pass

def _visit_bucket(dt, minutes=VISIT_WINDOW_MINUTES):
    """Retourne l'identifiant de la fenêtre de N minutes pour un datetime."""
    if dt is None:
        return None
    # Secondes depuis l'epoch UTC → minutes → id de bucket
    epoch_min = int(dt.timestamp() // 60)
    return epoch_min // minutes


def _count_visites_dedupe(queryset, minutes=VISIT_WINDOW_MINUTES):
    """Nombre de visites dédupliquées : 1 (IP, bucket de N min) = 1 visite."""
    seen = set()
    for ip, dt in queryset.values_list('ip_address', 'date_visite').iterator():
        b = _visit_bucket(dt, minutes)
        if b is None:
            continue
        seen.add((ip or '', b))
    return len(seen)


def _group_visites_dedupe(queryset, period, minutes=VISIT_WINDOW_MINUTES):
    """Regroupe les visites dédupliquées par 'month', 'year_month', 'day' ou 'hour'.
    Retourne un dict { clé : nombre_de_visites_dédupées }.
    """
    buckets = {}  # key -> set of (ip, bucket)
    for ip, dt in queryset.values_list('ip_address', 'date_visite').iterator():
        if dt is None:
            continue
        if period == 'month':
            key = dt.month
        elif period == 'year_month':
            key = (dt.year, dt.month)
        elif period == 'day':
            key = dt.date()
        elif period == 'hour':
            key = dt.hour
        else:
            continue
        b = _visit_bucket(dt, minutes)
        buckets.setdefault(key, set()).add((ip or '', b))
    return {k: len(v) for k, v in buckets.items()}


def _top_pages_dedupe(queryset, limit=10, minutes=VISIT_WINDOW_MINUTES):
    """Top des pages visitées, en dédupliquant par (IP, bucket)."""
    counters = {}   # url -> set of (ip, bucket)
    for url, ip, dt in queryset.values_list('url_visitee', 'ip_address', 'date_visite').iterator():
        if dt is None:
            continue
        counters.setdefault(url or '', set()).add((ip or '', _visit_bucket(dt, minutes)))
    ranked = sorted(
        ({'url_visitee': u, 'total': len(s)} for u, s in counters.items()),
        key=lambda r: r['total'],
        reverse=True,
    )
    return ranked[:limit]

def _count_clics_dedupe(queryset, minutes=CLICK_WINDOW_MINUTES):
    """Nombre de clics dédupliqués : 1 (IP, élément, bucket de N min) = 1 clic."""
    seen = set()
    for ip, element, dt in queryset.values_list('ip_address', 'element', 'date_clic').iterator():
        b = _visit_bucket(dt, minutes)
        if b is None:
            continue
        seen.add((ip or '', element or '', b))
    return len(seen)

def _group_clics_dedupe(queryset, period, minutes=CLICK_WINDOW_MINUTES):
    """Regroupe les clics dédupliqués par 'year_month', 'day' ou 'hour'."""
    buckets = {}
    for ip, element, dt in queryset.values_list('ip_address', 'element', 'date_clic').iterator():
        if dt is None:
            continue
        if period == 'month':
            key = dt.month
        elif period == 'year_month':
            key = (dt.year, dt.month)
        elif period == 'day':
            key = dt.date()
        elif period == 'hour':
            key = dt.hour
        else:
            continue
        b = _visit_bucket(dt, minutes)
        buckets.setdefault(key, set()).add((ip or '', element or '', b))
    return {k: len(v) for k, v in buckets.items()}

def _top_clics_dedupe(queryset, limit=10, minutes=CLICK_WINDOW_MINUTES):
    """Top des éléments cliqués, dédupliqués par (IP, bucket)."""
    counters = {}
    for element, ip, dt in queryset.exclude(element__startswith='reseau:').values_list(
        'element', 'ip_address', 'date_clic'
    ).iterator():
        if dt is None:
            continue
        counters.setdefault(element or '', set()).add((ip or '', _visit_bucket(dt, minutes)))
    ranked = sorted(
        ({'element': e, 'total': len(s)} for e, s in counters.items()),
        key=lambda r: r['total'],
        reverse=True,
    )
    return ranked[:limit]

def _clics_par_pages_stats(queryset, minutes=CLICK_WINDOW_MINUTES):
    """Clics par page suivie (élément page:…), dédupliqués par IP."""
    counters = {}
    for element, ip, dt in queryset.filter(element__startswith='page:').values_list(
        'element', 'ip_address', 'date_clic'
    ).iterator():
        if dt is None:
            continue
        path = element[5:] if element.startswith('page:') else element
        counters.setdefault(path, set()).add((ip or '', _visit_bucket(dt, minutes)))
    results = [
        {
            'path': path,
            'label': _tracked_page_label(path),
            'total': len(seen),
        }
        for path, seen in counters.items()
    ]
    results.sort(key=lambda r: r['total'], reverse=True)
    return results

def _build_stats_dashboard_context(request):
    """Construit le contexte du tableau de bord statistiques (filtres, KPIs, graphiques)."""
    today = date.today()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # ---- Filtre : jour | semaine | mois | annee | custom ----
    periode = request.GET.get('periode', 'annee')
    date_debut_str = request.GET.get('date_debut', '')
    date_fin_str = request.GET.get('date_fin', '')

    def _parse(d):
        try:
            return datetime.strptime(d, '%Y-%m-%d').date()
        except Exception:
            return None
    if periode == 'jour':
        filt_debut, filt_fin = today, today
        prev_debut = today - timedelta(days=1)
        prev_fin = prev_debut
        periode_label = "aujourd'hui"
    elif periode == 'semaine':
        filt_debut = today - timedelta(days=today.weekday())
        filt_fin = today
        prev_fin = filt_debut - timedelta(days=1)
        prev_debut = prev_fin - timedelta(days=6)
        periode_label = "cette semaine"
    elif periode == 'mois':
        filt_debut, filt_fin = start_of_month, today
        prev_fin = start_of_month - timedelta(days=1)
        prev_debut = prev_fin.replace(day=1)
        periode_label = "ce mois"
    elif periode == 'custom':
        filt_debut = _parse(date_debut_str) or start_of_year
        filt_fin = _parse(date_fin_str) or today
        if filt_fin < filt_debut:
            filt_debut, filt_fin = filt_fin, filt_debut
        delta_jours = (filt_fin - filt_debut).days
        prev_fin = filt_debut - timedelta(days=1)
        prev_debut = prev_fin - timedelta(days=delta_jours)
        periode_label = f"du {filt_debut.strftime('%d/%m/%Y')} au {filt_fin.strftime('%d/%m/%Y')}"
    else:
        periode = 'annee'
        filt_debut, filt_fin = start_of_year, today
        prev_debut = start_of_year.replace(year=start_of_year.year - 1)
        prev_fin = start_of_year - timedelta(days=1)
        periode_label = f"l'année {today.year}"

    visites_qs = Visite.objects.filter(date_visite__date__range=(filt_debut, filt_fin))
    clics_qs = Clic.objects.filter(date_clic__date__range=(filt_debut, filt_fin))
    prev_visites_qs = Visite.objects.filter(date_visite__date__range=(prev_debut, prev_fin))
    prev_clics_qs = Clic.objects.filter(date_clic__date__range=(prev_debut, prev_fin))

    # ---- KPIs : tous adaptés à la période sélectionnée ----
    total_visites_filtre = _count_visites_dedupe(visites_qs)
    total_clics_filtre = _count_clics_dedupe(clics_qs)
    visiteurs_uniques = visites_qs.exclude(session_key='').values('session_key').distinct().count()
    pages_uniques_filtre = visites_qs.exclude(url_visitee='').values('url_visitee').distinct().count()

    # Valeurs « aujourd'hui » (toujours affichées en bas de chaque carte)
    visites_today_qs = Visite.objects.filter(date_visite__date=today)
    clics_today_qs = Clic.objects.filter(date_clic__date=today)
    total_visites_jour = _count_visites_dedupe(visites_today_qs)
    total_clics_jour = _count_clics_dedupe(clics_today_qs)
    visiteurs_uniques_jour = (
        visites_today_qs.exclude(session_key='').values('session_key').distinct().count()
    )
    pages_uniques_jour = (
        visites_today_qs.exclude(url_visitee='').values('url_visitee').distinct().count()
    )

    # Période précédente comparable
    prev_total_visites = _count_visites_dedupe(prev_visites_qs)
    prev_total_clics = _count_clics_dedupe(prev_clics_qs)
    prev_visiteurs_uniques = (
        prev_visites_qs.exclude(session_key='').values('session_key').distinct().count()
    )
    prev_pages_uniques = (
        prev_visites_qs.exclude(url_visitee='').values('url_visitee').distinct().count()
    )

    def _pct(curr, prev):
        if not prev:
            return 100.0 if curr else 0.0
        return round(((curr - prev) / prev) * 100, 1)

    def _progress(curr, prev, cap=100):
        if not prev:
            return 100 if curr else 0
        pct = (curr / max(prev, 1)) * 50  # 50% si égal au précédent
        return int(max(5, min(cap, pct)))

    delta_visites = _pct(total_visites_filtre, prev_total_visites)
    delta_clics = _pct(total_clics_filtre, prev_total_clics)
    delta_visiteurs = _pct(visiteurs_uniques, prev_visiteurs_uniques)
    delta_pages = _pct(pages_uniques_filtre, prev_pages_uniques)

    progress_visites = _progress(total_visites_filtre, prev_total_visites)
    progress_clics = _progress(total_clics_filtre, prev_total_clics)
    progress_visiteurs = _progress(visiteurs_uniques, prev_visiteurs_uniques)
    progress_pages = _progress(pages_uniques_filtre, prev_pages_uniques)

    # ---- Top pages (dédupliqué) ----
    top_pages = _top_pages_dedupe(visites_qs, limit=10)

    # ---- Performance Overview : graphique adapté à la période ----
    days_range = (filt_fin - filt_debut).days + 1
    months_short = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                    'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']

    if days_range <= 1:
        # Vue horaire (24h)
        chart_mode = 'hourly'
        perf_labels = [f"{h:02d}h" for h in range(24)]
        visites_hour_map = _group_visites_dedupe(visites_qs, 'hour')
        perf_visites = [visites_hour_map.get(h, 0) for h in range(24)]
        clics_hour_map = _group_clics_dedupe(clics_qs, 'hour')
        perf_clics = [clics_hour_map.get(h, 0) for h in range(24)]
    elif days_range <= 62:
        # Vue journalière
        chart_mode = 'daily'
        all_dates = []
        d = filt_debut
        while d <= filt_fin:
            all_dates.append(d)
            d += timedelta(days=1)
        perf_labels = [d.strftime('%d/%m') for d in all_dates]
        visites_jour_map = _group_visites_dedupe(visites_qs, 'day')
        perf_visites = [visites_jour_map.get(d, 0) for d in all_dates]
        clics_jour_map = _group_clics_dedupe(clics_qs, 'day')
        perf_clics = [clics_jour_map.get(d, 0) for d in all_dates]
    else:
        # Vue mensuelle
        chart_mode = 'monthly'
        months_in_range = []
        y, m = filt_debut.year, filt_debut.month
        end_y, end_m = filt_fin.year, filt_fin.month
        while (y, m) <= (end_y, end_m):
            months_in_range.append((y, m))
            m += 1
            if m > 12:
                m = 1
                y += 1
        same_year = filt_debut.year == filt_fin.year
        perf_labels = [
            months_short[mm - 1] if same_year else f"{months_short[mm - 1]} {yy}"
            for yy, mm in months_in_range
        ]
        visites_ym_map = _group_visites_dedupe(visites_qs, 'year_month')
        perf_visites = [visites_ym_map.get((yy, mm), 0) for yy, mm in months_in_range]
        clics_ym_map = _group_clics_dedupe(clics_qs, 'year_month')
        perf_clics = [clics_ym_map.get((yy, mm), 0) for yy, mm in months_in_range]

    # ---- Évolution journalière (jours présents seulement, pour le mini-chart) ----
    visites_jour_map_full = _group_visites_dedupe(visites_qs, 'day')
    clics_jour_map_full = _group_clics_dedupe(clics_qs, 'day')
    daily_keys = sorted(set(visites_jour_map_full) | set(clics_jour_map_full))
    daily_labels = [d.strftime('%d/%m') for d in daily_keys]
    daily_data = [visites_jour_map_full.get(d, 0) for d in daily_keys]
    daily_clics_data = [clics_jour_map_full.get(d, 0) for d in daily_keys]

    # ---- Top éléments cliqués sur la période ----
    top_clics = _top_clics_dedupe(clics_qs, limit=10)

    # ---- Clics par page suivie (Chauffeurs, Services, Blog, etc.) ----
    clics_par_pages = _clics_par_pages_stats(clics_qs)

    # ---- Statistiques des réseaux sociaux (filtrées sur la période) ----
    # Les clics sont enregistrés dans Clic avec element="reseau:NOM"
    clics_reseaux_periode = (
        clics_qs.filter(element__startswith='reseau:')
        .values('element').annotate(total=Count('id'))
    )
    map_reseau_periode = {
        r['element'].replace('reseau:', '', 1): r['total']
        for r in clics_reseaux_periode
    }

    reseaux_sociaux_stats = list(
        ReseauSocial.objects.all().order_by('ordre', 'nom')
    )
    # Compteur sur la période + tri
    for r in reseaux_sociaux_stats:
        r.counter_periode = map_reseau_periode.get(r.nom, 0)
    reseaux_sociaux_stats.sort(
        key=lambda r: (-r.counter_periode, r.ordre, r.nom)
    )
    total_clics_reseaux = sum(r.counter_periode for r in reseaux_sociaux_stats)
    max_clics_reseau = max(
        (r.counter_periode for r in reseaux_sociaux_stats), default=0
    )
    for r in reseaux_sociaux_stats:
        c = r.counter_periode
        r.pct_du_max = int((c / max_clics_reseau) * 100) if max_clics_reseau else 0
        r.pct_du_total = (
            round((c / total_clics_reseaux) * 100, 1) if total_clics_reseaux else 0
        )

    # ---- Score performance (note 0–5 basée sur la richesse des visites) ----
    # Échelle simple : ≥ 500 visites = 5/5, sinon proportionnel.
    score_perf = round(min(5.0, (total_visites_filtre / 500.0) * 5.0), 1)
    score_perf_pct = int(min(100, (score_perf / 5.0) * 100))

    def _delta_display(val):
        sign = '+' if val >= 0 else ''
        return f'{sign}{val}%'

    def _delta_dir(val):
        return 'up' if val >= 0 else 'down'

    def _delta_tone(val):
        return 'good' if val >= 0 else 'bad'

    chart_axis_hints = {
        'hourly': 'par heure',
        'daily': 'par jour',
        'monthly': 'par mois',
    }

    return {
        # Période
        'periode': periode,
        'periode_label': periode_label,
        'date_debut': filt_debut.strftime('%Y-%m-%d'),
        'date_fin': filt_fin.strftime('%Y-%m-%d'),
        'annee_courante': today.year,
        'visit_window_minutes': VISIT_WINDOW_MINUTES,
        'click_window_minutes': CLICK_WINDOW_MINUTES,
        'reseau_click_window_minutes': RESEAU_CLICK_WINDOW_MINUTES,

        # KPI cards (filtrées)
        'total_visites_filtre': total_visites_filtre,
        'total_clics_filtre': total_clics_filtre,
        'visiteurs_uniques': visiteurs_uniques,
        'pages_uniques_filtre': pages_uniques_filtre,

        # Valeurs « aujourd'hui »
        'total_visites_jour': total_visites_jour,
        'total_clics_jour': total_clics_jour,
        'visiteurs_uniques_jour': visiteurs_uniques_jour,
        'pages_uniques_jour': pages_uniques_jour,

        # Deltas et progressions
        'delta_visites': delta_visites,
        'delta_clics': delta_clics,
        'delta_visiteurs': delta_visiteurs,
        'delta_pages': delta_pages,
        'delta_visites_fmt': _delta_display(delta_visites),
        'delta_clics_fmt': _delta_display(delta_clics),
        'delta_visiteurs_fmt': _delta_display(delta_visiteurs),
        'delta_pages_fmt': _delta_display(delta_pages),
        'delta_visites_dir': _delta_dir(delta_visites),
        'delta_clics_dir': _delta_dir(delta_clics),
        'delta_visiteurs_dir': _delta_dir(delta_visiteurs),
        'delta_pages_dir': _delta_dir(delta_pages),
        'delta_visites_tone': _delta_tone(delta_visites),
        'delta_clics_tone': _delta_tone(delta_clics),
        'delta_visiteurs_tone': _delta_tone(delta_visiteurs),
        'delta_pages_tone': _delta_tone(delta_pages),
        'progress_visites': progress_visites,
        'progress_clics': progress_clics,
        'progress_visiteurs': progress_visiteurs,
        'progress_pages': progress_pages,

        # Top pages + clics
        'top_pages': top_pages,
        'top_clics': top_clics,
        'clics_par_pages': clics_par_pages,

        # Performance overview (adaptatif)
        'chart_mode': chart_mode,
        'chart_axis_hint': chart_axis_hints.get(chart_mode, ''),
        'perf_labels_json': json.dumps(perf_labels),
        'perf_visites_json': json.dumps(perf_visites),
        'perf_clics_json': json.dumps(perf_clics),
        'split_labels_json': json.dumps(['Visites', 'Clics']),
        'split_data_json': json.dumps([total_visites_filtre, total_clics_filtre]),

        # Évolution journalière (mini-chart)
        'daily_labels_json': json.dumps(daily_labels),
        'daily_data_json': json.dumps(daily_data),
        'daily_clics_json': json.dumps(daily_clics_data),

        # Réseaux sociaux
        'reseaux_sociaux_stats': reseaux_sociaux_stats,
        'total_clics_reseaux': total_clics_reseaux,
        'max_clics_reseau': max_clics_reseau,

        # Score performance
        'score_perf': score_perf,
        'score_perf_pct': score_perf_pct,
    }


class StatsDashboardView(LoginRequiredMixin, TemplateView):
    """Tableau de bord statistiques (visites, clics, réseaux sociaux)."""
    login_url = 'login'
    template_name = 'pb_site/manage/stats_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_build_stats_dashboard_context(self.request))
        return context
