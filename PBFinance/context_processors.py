"""Context processors pour le site public PBFinance.

Expose globalement les catégories d'onglets (CategorieOnglet) et leurs
sous-catégories actives (SousCategorieOnglet) afin de construire la barre
de navigation dynamiquement depuis l'interface d'administration.
"""
from django.db.models import Prefetch

from .models import (
    CategorieOnglet,
    SousCategorieOnglet,
    ReseauSocial,
    Footer,
    Liencategoriefooter,
    LienFooter,
    SiteConfig,
    Langue,
    MonQrcode,
    GestionSection,
    LienApplication,
)


def pb_site_config(request):
    """Expose la configuration globale du site (singleton) aux templates.

    Accessible via `site_config` dans tous les templates :
        {% if site_config.logo_principal %}
            <img src="{{ site_config.logo_principal.url }}" alt="{{ site_config.nom_site }}">
        {% endif %}
    """
    try:
        config = SiteConfig.objects.filter(actif=True).first()
    except Exception:
        config = None
    return {'site_config': config}


def pb_langues(request):
    """Expose la liste des langues actives pour le sélecteur de langue."""
    try:
        langues = list(Langue.objects.filter(actif=True).order_by('ordre', 'nom'))
    except Exception:
        langues = []
    return {'pb_langues': langues}


def pb_navigation(request):
    """Charge les catégories d'onglets actives + sous-catégories actives."""
    sous_qs = SousCategorieOnglet.objects.filter(actif=True).order_by('ordre', 'libelle')
    categories = (
        CategorieOnglet.objects
        .filter(actif=True)
        .prefetch_related(Prefetch('sous_categories', queryset=sous_qs, to_attr='sous_actives'))
        .order_by('ordre', 'libelle')
    )
    return {'pb_navigation_categories': categories}


def pb_reseaux_sociaux(request):
    """Expose la liste des réseaux sociaux actifs pour les templates publics."""
    return {
        'pb_reseaux_sociaux': list(
            ReseauSocial.objects.filter(actif=True).order_by('ordre', 'nom')
        )
    }


def pb_qrcode_app(request):
    """Expose le premier QR code actif pour la modale de téléchargement de l'app.

    Accessible dans tous les templates via `pb_qrcode_app` :
        {% if pb_qrcode_app %}
            <img src="{{ pb_qrcode_app.qrcode_image.url }}" alt="{{ pb_qrcode_app.titre }}">
        {% endif %}
    """
    try:
        qrcode = MonQrcode.objects.filter(actif=True).order_by('ordre', '-date_creation').first()
    except Exception:
        qrcode = None
    return {'pb_qrcode_app': qrcode}


def _lien_app_is_web(lien):
    """True si le lien correspond au bouton « navigateur / web »."""
    if not lien:
        return False
    t = (lien.titre or '').lower()
    if any(k in t for k in ('web', 'navigateur', 'browser', 'internet', 'site')):
        return True
    if lien.lien_store and not any(k in t for k in ('google', 'play', 'android', 'apple', 'app store', 'ios')):
        return True
    return False


def _lien_app_web_candidate(liens):
    """Retourne le lien « navigateur / web » si identifiable par le titre."""
    for lien in liens:
        if _lien_app_is_web(lien):
            return lien
    return None


def pb_liens_application(request):
    """Liens stores / web (Google Play, App Store, navigateur) pour le site public."""
    try:
        liens = list(
            LienApplication.objects.filter(actif=True).order_by('ordre', 'titre')
        )
        lien_ordre_1 = LienApplication.objects.filter(actif=True, ordre=1).first()
        lien_ordre_2 = LienApplication.objects.filter(actif=True, ordre=2).first()
        lien_ordre_3 = LienApplication.objects.filter(actif=True, ordre=3).first()
    except Exception:
        liens = []
        lien_ordre_1 = None
        lien_ordre_2 = None
        lien_ordre_3 = None
    return {
        'pb_liens_application': liens,
        'pb_lien_app_web': _lien_app_web_candidate(liens),
        'pb_lien_app_ordre_1': lien_ordre_1,
        'pb_lien_app_ordre_2': lien_ordre_2,
        'pb_lien_app_ordre_3': lien_ordre_3,
    }


def pb_sections_visibility(request):
    """Expose la visibilité des grandes sections de la page d'accueil.

    Accessible dans les templates via ``pb_section_visible`` :

        {% if pb_section_visible.promo %} ... {% endif %}
        {% if pb_section_visible.nos_services %} ... {% endif %}
        {% if pb_section_visible.compteur %} ... {% endif %}
        {% if pb_section_visible.vehicule_location %} ... {% endif %}
        {% if pb_section_visible.piece_detachee %} ... {% endif %}
        {% if pb_section_visible.temoignage %} ... {% endif %}

    Les sections non encore configurées en base sont visibles par défaut.
    """
    # Fallback de sécurité pour la home : visible par défaut tant qu'aucune
    # règle n'est définie en base.
    home_defaults = {
        'promo': True,
        'nos_services': True,
        'compteur': True,
        'vehicule_location': True,
        'piece_detachee': True,
        'temoignage': True,
    }
    visibility = dict(home_defaults)
    visibility_by_category = {}
    try:
        qs = GestionSection.objects.select_related('categorie').all()
        for entry in qs:
            section_key = (entry.titre_section or '').strip()
            if not section_key:
                continue
            category = entry.categorie
            category_code = (category.code if category else '').strip().lower()

            # Règle métier demandée :
            # - catégorie inactive => toutes ses sections masquées
            # - catégorie active => la section suit son booléen "active"
            section_visible = bool(entry.active)
            if category is not None:
                section_visible = bool(category.actif) and section_visible
                visibility_by_category.setdefault(category_code, {})[section_key] = section_visible
    except Exception:
        pass

    # Applique les règles de la catégorie de page courante (si définie).
    current_code = ''
    try:
        if request.resolver_match and request.resolver_match.url_name:
            current_code = str(request.resolver_match.url_name).strip().lower()
    except Exception:
        current_code = ''

    if current_code and current_code in visibility_by_category:
        visibility.update(visibility_by_category[current_code])

    # Page Services : section « processus » visible par défaut si non définie en gestion
    if current_code == 'services':
        visibility.setdefault('processus', True)

    return {'pb_section_visible': visibility}


def pb_footer_links(request):
    """Charge les catégories du footer + leurs liens actifs.

    Accessible dans les templates via `pb_footer_categories` :
        {% for cat in pb_footer_categories %}
            <h3>{{ cat.libelle }}</h3>
            {% for l in cat.liens_actifs %}
                <a href="{{ l.lien|pb_link }}">{{ l.libelle }}</a>
            {% endfor %}
        {% endfor %}
    """
    liens_qs = LienFooter.objects.filter(actif=True).order_by('ordre', 'libelle')
    categories = (
        Liencategoriefooter.objects
        .filter(actif=True)
        .prefetch_related(
            Prefetch(
                'liens_categorie_footer',
                queryset=liens_qs,
                to_attr='liens_actifs',
            )
        )
        .order_by('ordre', 'libelle')
    )
    return {'pb_footer_categories': categories}


def pb_footer(request):
    """Expose la configuration active du footer aux templates publics.

    Accessible via `footers` pour conserver la compatibilité des templates
    existants qui itèrent avec `{% for foot in footers %}`.
    """
    try:
        footers = list(Footer.objects.filter(actif=True).order_by('ordre'))
    except Exception:
        footers = []
    return {'footers': footers}
