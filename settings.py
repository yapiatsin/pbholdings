import contextlib
from pathlib import Path
import os
#from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

with contextlib.suppress(Exception):
    from django.contrib.messages import constants as messages
    MESSAGE_TAGS = {
        messages.DEBUG: 'Alert-info',
        messages.INFO: 'Alert-info',
        messages.SUCCESS: 'Alert-success',
        messages.WARNING: 'Alert-warning',
        messages.ERROR: 'Alert-danger'
    }
# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = 'django-insecure-of03a0_f)5yamk9g&p9p2f^a*l8!6t#+r_c4oq42+sb&#y5znt'
#SECRET_KEY = config('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

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
    # 'PB_Auto_Pieces',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'PBEntrep.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "railway",
        'USER': "postgres",
        'PASSWORD': "*2Ab43aDDfgC36AA*313EcD3gC-dFg4c",
        'HOST': "viaduct.proxy.rlwy.net",
        'PORT': "51273",
        
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'pbedata',
        # 'USER':'postgres',
        # 'PASSWORD':'admin',
        # 'HOST':'localhost', 
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"),]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    "site_header": "P&BEntrepprise",
    "site_brand": "P&BEntreprise",
    #"site_logo": "assetts/img/icon.png",
    "copyright" : "P&BEntreprise 2023", 
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Mon Site", "url": "home", "permissions": ["userauths.User"]},
        # model admin to link to (Permissions checked against model)
        {"model": "userauths.User"},
    ],

}
AUTH_USER_MODEL = 'userauths.User'
LOGOUT_REDIRECT_URL = 'login'

# Configuration de email

#EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST=config('EMAIL_HOST')
#EMAIL_PORT = config('EMAIL_PORT')
#EMAIL_HOST_USER=config('EMAIL_HOST_USER')
#EMAIL_HOST_PASSWORD=('EMAIL_HOST_PASSWORD')
#EMAIL_USER_TLS=config('EMAIL_USER_TLS')
