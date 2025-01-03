from django.contrib import admin
from .models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ['title','date_saisie']
    list_filter = ['title','date_saisie']

class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title','date_saisie']
    list_filter = ['title','date_saisie']

class EvenementAdmin(admin.ModelAdmin):
    list_display = ['title','auteur','date_saisie']
    list_filter = ['title','date_saisie']

admin.site.register(Video, VideoAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Evenement, EvenementAdmin)