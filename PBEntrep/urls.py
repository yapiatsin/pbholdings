from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

name = 'PBFinance'

urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('',include('PBFinance.urls')),
    path('auths/',include('userauths.urls')),
    path('entreprise/',include('PB_Entreprise.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

