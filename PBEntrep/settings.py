import contextlib
from pathlib import Path
import os
import sys
from decouple import config 
# type: ignore

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
# # # ✅ correct
SECRET_KEY = config('SECRET_KEY')
# DEBUG = True--  django-insecure-of03a0_f)5yamk9g&p9p2f^a*l8!6t#+r_c4oq42+sb&#y5znt

ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['localhost','127.0.0.1','192.168.100.157']

# ALLOWED_HOSTS = ['pbholdingsite.com','www.pbholdingsite.com','45.92.109.86']
# CSRF_TRUSTED_ORIGINS = [
#     'https://pbholdingsite.com',
# ]

handler403 = 'PB_Entreprise.views.permission_denied_view'
handler404 = 'PB_Entreprise.views.custom_404_view'
# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'PBFinance',
    'userauths',
    'PB_Entreprise',
    'simple_history',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'PBFinance.middleware.TrackingMiddleware',
    # Ajoute CSP, X-Frame-Options: DENY, X-Content-Type-Options et Referrer-Policy.
    # Corrige le rapport de pentest §4.2 / §6.1.
    'PBEntrep.security_headers.SecurityHeadersMiddleware',
]

# --- En-têtes de sécurité (pentest 14/04/2026 §6.1) ---
# Clickjacking : forcer X-Frame-Options: DENY (Django par défaut = SAMEORIGIN)
X_FRAME_OPTIONS = 'DENY'
# MIME-sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True
# Cookies en HTTPS uniquement (la prod est derrière Caddy en HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
# HSTS — recommandé par §4.2 (Optionnel mais bonne pratique)
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = 'PBEntrep.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR, 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'PB_Entreprise.context_processors.grouped_user_permissions',
                'PB_Entreprise.context_processors.navbar_context',
                'PB_Entreprise.context_processors.alertes_count',
                'PBFinance.context_processors.pb_navigation',
                'PBFinance.context_processors.pb_reseaux_sociaux',
                'PBFinance.context_processors.pb_footer_links',
                'PBFinance.context_processors.pb_footer',
                'PBFinance.context_processors.pb_site_config',
                'PBFinance.context_processors.pb_langues',
                'PBFinance.context_processors.pb_qrcode_app',
                'PBFinance.context_processors.pb_liens_application',
                'PBFinance.context_processors.pb_sections_visibility',
            ],
        },
    },
]

WSGI_APPLICATION = 'PBEntrep.wsgi.application'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# DEBUG = True
DEBUG = False
# DEBUG = config('DEBUG') 

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': config('DB_NAME'),
    #     'USER':config('DB_USER'),
    #     'PASSWORD': config('DB_PASSWORD'),
    #     'HOST':config('DB_HOST'),
    #     'PORT':config('DB_PORT'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# WhiteNoise indexe les fichiers statiques UNE SEULE FOIS au démarrage : tout
# fichier ajouté ensuite renvoie 404 (avec une page HTML, d'où les erreurs
# « MIME type text/html is not executable » côté navigateur) jusqu'au
# redémarrage du serveur. Sous runserver on lui demande donc de relire le
# disque à chaque requête, et de servir directement depuis STATICFILES_DIRS
# pour ne pas avoir à relancer collectstatic à chaque modification.
# En production (gunicorn/uwsgi), les deux restent désactivés : index en
# mémoire et fichiers compressés de STATIC_ROOT.
_RUNSERVER = 'runserver' in sys.argv
WHITENOISE_AUTOREFRESH = DEBUG or _RUNSERVER
WHITENOISE_USE_FINDERS = DEBUG or _RUNSERVER

# Jazzmin 3.x + AdminLTE 4
JAZZMIN_UI_TWEAKS = {
    'theme': 'default',
    'navbar': 'navbar-white navbar-light',
    'sidebar': 'sidebar-dark-primary',
    'brand_colour': 'navbar-primary',
    'accent': 'accent-primary',
    'navbar_fixed': True,
    'sidebar_fixed': True,
    'footer_fixed': False,
    'sidebar_nav_flat_style': True,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'body_small_text': False,
}
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
# FRONTEND_URL = config('FRONTEND_URL', default='https://pbholdingsite.com').rstrip('/')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:8004').rstrip('/')
########################---o---#######################---o---######################---o---###################
JAZZMIN_SETTINGS = {
    'site_title': 'P&B Entreprise',
    'site_header': 'P&B Entreprise',
    'site_brand': 'P&B Entreprise',
    'site_logo': 'vendor/adminlte/img/AdminLTELogo.png',
    'site_logo_classes': 'img-circle elevation-3',
    'site_icon': 'vendor/adminlte/img/AdminLTELogo.png',
    'welcome_sign': 'Bienvenue',
    'copyright': 'P&B Entreprise 2025',
    'show_sidebar': True,
    'navigation_expanded': True,
    'show_ui_builder': False,
    'use_google_fonts_cdn': True,
    'custom_css': 'admin/css/pb_jazzmin_fix.css',
    'topmenu_links': [
        {'name': 'Tableau de bord', 'url': 'dash', 'permissions': ['userauths.User']},
        {'model': 'userauths.User'},
    ],
}
AUTH_USER_MODEL = 'userauths.CustomUser'
