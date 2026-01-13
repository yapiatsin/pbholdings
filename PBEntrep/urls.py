from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
import os

name = 'PBFinance'
urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('',include('PBFinance.urls')),
    path('auth/',include('userauths.urls')),
    path('pbentreprise/',include('PB_Entreprise.urls')),
]
# Servir les fichiers média
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Servir les fichiers statiques même avec DEBUG=False (pour le développement local)
if not settings.DEBUG:
    # Servir depuis STATICFILES_DIRS (le dossier static principal)
    static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': static_dir}),
    ]

