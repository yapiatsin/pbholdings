"""
Middleware de tracking automatique :
- Enregistre chaque visite (ordinateur, téléphone, tablette) dans `Visite`
- Met à jour la table `StatistiqueAgregee` journalière à chaque requête
Les tables `Visite`, `Clic` et `StatistiqueAgregee` sont donc alimentées
automatiquement et n'ont pas besoin de CRUD manuel.
"""
from datetime import date
from django.db.models import F
from django.utils.deprecation import MiddlewareMixin
from .models import Visite, StatistiqueAgregee, PageSiteSearch


# URLs à ignorer (admin, assets statiques, gestion interne, API tracking)
IGNORED_PREFIXES = (
    '/admin',
    '/static',
    '/media',
    '/manage',
    '/favicon.ico',
    '/track-click',
)


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class TrackingMiddleware(MiddlewareMixin):
    """À chaque requête HTML, crée une entrée Visite + maj StatistiqueAgregee journalière."""

    def process_response(self, request, response):
        try:
            path = request.path or '/'

            # Ignore les chemins techniques
            if any(path.startswith(p) for p in IGNORED_PREFIXES):
                return response

            # Ignore les réponses non-HTML (images, json, etc.)
            content_type = response.get('Content-Type', '')
            if 'text/html' not in content_type:
                return response

            # Ignore les erreurs et redirections
            if response.status_code >= 300:
                return response

            # Assure qu'une session existe (pour session_key)
            if not request.session.session_key:
                request.session.save()

            # Rapproche l'URL d'une page référentielle si définie
            page = PageSiteSearch.objects.filter(url_path=path).first()

            # Création de la visite
            Visite.objects.create(
                page=page,
                url_visitee=path[:500],
                titre_page='',
                session_key=request.session.session_key or '',
                ip_address=_client_ip(request),
                user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:500],
            )

            # Pages cibles (Chauffeurs, Services, Blog, …) → comptées comme clics (IP dédupliquée)
            from PBFinance.views import register_tracked_page_click
            register_tracked_page_click(request, path)

            # Mise à jour de la statistique agrégée journalière (get_or_create + F)
            today = date.today()
            stat, created = StatistiqueAgregee.objects.get_or_create(
                periode='jour',
                date_debut=today,
                url_visitee=path[:500],
                defaults={'date_fin': today, 'nombre_visites': 1},
            )
            if not created:
                StatistiqueAgregee.objects.filter(pk=stat.pk).update(
                    nombre_visites=F('nombre_visites') + 1
                )
        except Exception:
            # Le tracking ne doit jamais casser la navigation
            pass

        return response
