"""
Middleware d'en-têtes de sécurité HTTP pour P&B Entreprise.

Corrige les vulnérabilités identifiées dans le rapport de pentest du 14/04/2026 :
- §4.2 « En-têtes de sécurité absents » (Content-Security-Policy, X-Frame-Options,
  X-Content-Type-Options)
- §6.1 « Corrections urgentes » : ajout de CSP + X-Frame-Options: DENY.

Implémenté sous forme de middleware natif (pas de dépendance django-csp) pour
ne pas alourdir requirements.txt.
"""

# Politique Content-Security-Policy.
# Les sources autorisées correspondent aux CDN actuellement référencés dans les
# templates (jQuery, Bootstrap, Chart.js, FontAwesome, Lordicon, Google Fonts,
# Ionicons, daterangepicker, etc.). À ajuster si un nouveau CDN est ajouté.
CSP_DIRECTIVES = {
    "default-src": ["'self'"],
    "script-src": [
        "'self'",
        "'unsafe-inline'",   # nombreux scripts inline existants dans les templates
        "'unsafe-eval'",     # requis par certaines libs (chart.js dataLabels, jqvmap…)
        "https://code.jquery.com",
        "https://ajax.googleapis.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://cdn.lordicon.com",
        "https://kit.fontawesome.com",
        "https://unpkg.com",  # Leaflet, Leaflet Routing Machine (pages publiques / contact)
    ],
    "style-src": [
        "'self'",
        "'unsafe-inline'",   # styles inline présents partout dans le thème AdminLTE
        "https://fonts.googleapis.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.jsdelivr.net",
        "https://code.ionicframework.com",
        "https://unpkg.com",  # leaflet.css, leaflet-routing-machine.css
    ],
    "font-src": [
        "'self'",
        "data:",
        "https://fonts.gstatic.com",
        "https://cdnjs.cloudflare.com",
        "https://code.ionicframework.com",
    ],
    "img-src": ["'self'", "data:", "blob:", "https:"],
    "connect-src": [
        "'self'",
        "https://cdn.lordicon.com",
        "https://kit.fontawesome.com",
        "https://router.project-osrm.org",  # Leaflet Routing Machine (itinéraires)
        "https://translation.googleapis.com",  # traduction site (script base)
    ],
    "frame-ancestors": ["'none'"],   # équivalent moderne de X-Frame-Options: DENY
    "form-action": ["'self'"],
    "base-uri": ["'self'"],
    "object-src": ["'none'"],
}

def _build_csp_header() -> str:
    """Assemble la valeur du header Content-Security-Policy."""
    return "; ".join(
        f"{directive} {' '.join(sources)}"
        for directive, sources in CSP_DIRECTIVES.items()
    )

CSP_HEADER_VALUE = _build_csp_header()

class SecurityHeadersMiddleware:
    """Ajoute les en-têtes de sécurité manquants à toutes les réponses HTTP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content-Security-Policy : couvre XSS / injection de ressources tierces.
        # setdefault pour respecter un éventuel header déjà posé par une vue.
        response.setdefault("Content-Security-Policy", CSP_HEADER_VALUE)

        # X-Frame-Options: DENY — protection clickjacking explicite.
        # Django pose déjà DENY/SAMEORIGIN via XFrameOptionsMiddleware, mais on
        # force DENY ici pour garantir la valeur demandée par l'auditeur.
        response["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options : empêche le MIME sniffing (cf. §4.2 du rapport).
        response.setdefault("X-Content-Type-Options", "nosniff")

        # Referrer-Policy : limite la fuite d'URL vers les sites tiers.
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        return response
