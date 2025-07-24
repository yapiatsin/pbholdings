import contextlib
from pathlib import Path
import os
from decouple import config 
# type: ignore

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # ✅ correct

SECRET_KEY = config('SECRET_KEY')
# DEBUG = True--  django-insecure-of03a0_f)5yamk9g&p9p2f^a*l8!6t#+r_c4oq42+sb&#y5znt

ALLOWED_HOSTS = ['*']
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'PBEntrep.wsgi.application'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DEBUG = True
# DEBUG = True
# DEBUG = config('DEBUG') 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER':config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':config('DB_HOST'),
        'PORT':config('DB_PORT'),
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

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')

########################---o---#######################---o---######################---o---###################
JAZZMIN_SETTINGS = {
    "site_header": "P&BEntrepprise",
    "site_brand": "P&BEntreprise",
    #"site_logo": "assetts/img/icon.png",
    "copyright" : "P&BEntreprise 2025", 
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Tableau de bord", "url": "dash", "permissions": ["userauths.User"]},
        # model admin to link to (Permissions checked against model)
        {"model": "userauths.User"},
    ],
}
AUTH_USER_MODEL = 'userauths.CustomUser'
