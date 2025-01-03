from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

name = 'PBFinance'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('PBFinance.urls')),
    path('users/',include('userauths.urls')),
    path('entreprise/',include('PB_Entreprise.urls')),
    # path('vente/',include('PB_Auto_Pieces.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

