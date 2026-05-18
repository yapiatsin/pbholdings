"""Template tags & filters pour les liens dynamiques stockés en CharField.

Usage dans un template :

    {% load pb_links %}

    <a href="{{ categorie.lien|pb_link }}">{{ categorie.libelle }}</a>

Accepte :
  - un nom d'URL Django (ex: 'home', 'contact')
  - un chemin interne ('/a-propos/')
  - une URL absolue ('https://…')
  - une ancre ('#services')
  - vide → '#'
"""
from django import template
from PBFinance.views import resolve_link

register = template.Library()


@register.filter(name='pb_link')
def pb_link(value):
    return resolve_link(value)


@register.simple_tag
def pb_lien_app_icon(titre):
    """Icône Font Awesome selon le titre du lien application."""
    t = (titre or '').lower()
    if 'google' in t or 'play' in t or 'android' in t:
        return 'fa-brands fa-google-play'
    if 'apple' in t or 'app store' in t or 'ios' in t:
        return 'fa-brands fa-apple'
    if any(k in t for k in ('web', 'navigateur', 'browser', 'internet', 'site')):
        return 'fa-solid fa-globe'
    return 'fa-solid fa-mobile-screen-button'


def _lien_app_is_web_obj(lien):
    if not lien:
        return False
    t = (getattr(lien, 'titre', None) or '').lower()
    if any(k in t for k in ('web', 'navigateur', 'browser', 'internet', 'site')):
        return True
    if getattr(lien, 'lien_store', None) and not any(
        k in t for k in ('google', 'play', 'android', 'apple', 'app store', 'ios')
    ):
        return True
    return False


@register.filter
def pb_lien_app_is_web(lien):
    """True si le lien correspond au bouton « navigateur / web »."""
    return _lien_app_is_web_obj(lien)
