"""Tags d'affichage des cartes de statistiques (mini-graphique en SVG)."""
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

_SPARK_WIDTH = 84
_SPARK_HEIGHT = 30


def _serie_numerique(valeurs):
    """Normalise une série hétérogène (None, str, Decimal…) en liste de float."""
    serie = []
    for valeur in valeurs or []:
        try:
            serie.append(float(valeur))
        except (TypeError, ValueError):
            serie.append(0.0)
    return serie


@register.simple_tag
def kpi_sparkline(valeurs, type_graphe='line'):
    """Mini-graphique SVG (courbe ou barres) tracé à partir d'une série de nombres.

    Rend une chaîne vide si la série est absente ou trop courte : la carte
    s'affiche alors sans mini-graphique, sans donnée inventée.
    """
    serie = _serie_numerique(valeurs)
    if len(serie) < 2:
        return ''

    mini, maxi = min(serie), max(serie)
    amplitude = (maxi - mini) or 1.0
    haut, bas = 2.0, _SPARK_HEIGHT - 2.0
    hauteur_utile = bas - haut

    def _y(valeur):
        return bas - ((valeur - mini) / amplitude) * hauteur_utile

    if type_graphe == 'bar':
        n = len(serie)
        pas = _SPARK_WIDTH / n
        largeur = max(pas * 0.55, 2.0)
        barres = []
        for i, valeur in enumerate(serie):
            y = _y(valeur)
            x = i * pas + (pas - largeur) / 2
            barres.append(
                '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.2" fill="currentColor"/>'
                % (x, y, largeur, max(bas - y, 1.5))
            )
        corps = ''.join(barres)
    else:
        pas = _SPARK_WIDTH / (len(serie) - 1)
        points = ' '.join(
            '%.2f,%.2f' % (i * pas, _y(valeur)) for i, valeur in enumerate(serie)
        )
        corps = (
            '<polyline points="%s" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/>' % points
        )

    return mark_safe(
        '<span class="pb-kpi__spark" aria-hidden="true">'
        '<svg viewBox="0 0 %d %d" preserveAspectRatio="none">%s</svg>'
        '</span>' % (_SPARK_WIDTH, _SPARK_HEIGHT, corps)
    )


@register.filter
def has_sparkline(valeurs):
    """Vrai si la série permet de tracer un mini-graphique (au moins 2 points)."""
    return len(_serie_numerique(valeurs)) >= 2
