from django.contrib import admin
from .models import *

class CategorieOngletAdmin(admin.ModelAdmin):
    list_display = ['libelle']
    list_filter = ['libelle']
    search_fields = ['libelle']

class SousCategorieOngletAdmin(admin.ModelAdmin):
    list_display = ['libelle']
    list_filter = ['libelle']
    search_fields = ['libelle']

class PageAccueilAdmin(admin.ModelAdmin):
    list_display = ['titre','sous_titre','image','actif']
    list_filter = ['actif']
    search_fields = ['titre','sous_titre','description']

class NosServiceAdmin(admin.ModelAdmin):
    list_display = ['libelle','image','description','lien_detail']
    list_filter = ['libelle','image','description','lien_detail']
    search_fields = ['libelle','image','description','lien_detail']

class PresentationAdmin(admin.ModelAdmin):
    list_display = ['libelle','description','image']
    list_filter = ['libelle','description','image']
    search_fields = ['libelle','description','image']

class AnnonceEvenementAdmin(admin.ModelAdmin):
    list_display = ['image','libelle','lien','date_debut','date_fin']
    list_filter = ['image','libelle','lien','date_debut','date_fin']
    search_fields = ['image','libelle','lien','date_debut','date_fin']

class AnnonceInformationAdmin(admin.ModelAdmin):
    list_display = ['titre','contenu','image','date_publication']
    list_filter = ['titre','contenu','image','date_publication']
    search_fields = ['titre','contenu','image','date_publication']

class BanniereAdmin(admin.ModelAdmin):
    list_display = ['texte','contact']
    list_filter = ['texte','contact']
    search_fields = ['texte','contact']

class ReseauSocialAdmin(admin.ModelAdmin):
    list_display = ['nom','icon','lien']
    list_filter = ['nom','icon','lien']
    search_fields = ['nom','icon','lien']

class PartenSponsAdmin(admin.ModelAdmin):
    list_display = ['nom','type_entite']
    list_filter = ['nom','type_entite']
    search_fields = ['nom','type_entite']

class FooterAdmin(admin.ModelAdmin):
    list_display = ['localisation_bp','contact_1','contact_2','contact_3','email']
    list_filter = ['localisation_bp','contact_1','contact_2','contact_3','email']
    search_fields = ['localisation_bp','contact_1','contact_2','contact_3','email']

class PageContactAdmin(admin.ModelAdmin):
    list_display = ['titre','introduction','adresse','telephone','email','horaires','carte_embed']
    list_filter = ['titre','introduction','adresse','telephone','email','horaires','carte_embed']
    search_fields = ['titre','introduction','adresse','telephone','email','horaires','carte_embed']

class MessageContactAdmin(admin.ModelAdmin):
    list_display = ['nom','email','sujet','message','date_envoi','lu']
    list_filter = ['nom','email','sujet','message','date_envoi','lu']
    search_fields = ['nom','email','sujet','message','date_envoi','lu']

class EquipeAdmin(admin.ModelAdmin):
    list_display = ['nom','role','description','image']
    list_filter = ['nom','role','description','image']
    search_fields = ['nom','role','description','image']

class PageSiteSearchAdmin(admin.ModelAdmin):
    list_display = ['nom','slug']
    list_filter = ['nom','slug']
    search_fields = ['nom','slug']

class VisiteAdmin(admin.ModelAdmin):
    list_display = ['page','url_visitee','titre_page','date_visite','session_key','ip_address','user_agent']
    list_filter = ['page','url_visitee','titre_page','date_visite','session_key','ip_address','user_agent']
    search_fields = ['page','url_visitee','titre_page','date_visite','session_key','ip_address','user_agent']

class ClicAdmin(admin.ModelAdmin):
    list_display = ['element','url_page','date_clic','session_key','ip_address']
    list_filter = ['element','url_page','date_clic','session_key','ip_address']
    search_fields = ['element','url_page','date_clic','session_key','ip_address']

admin.site.register(PartenSpons, PartenSponsAdmin)
admin.site.register(CategorieOnglet, CategorieOngletAdmin)
admin.site.register(SousCategorieOnglet, SousCategorieOngletAdmin)
admin.site.register(PageSiteSearch, PageSiteSearchAdmin)
admin.site.register(Visite, VisiteAdmin)
admin.site.register(Clic, ClicAdmin)
admin.site.register(PageAccueil, PageAccueilAdmin)
admin.site.register(NosService, NosServiceAdmin)
admin.site.register(Presentation, PresentationAdmin)
admin.site.register(AnnonceEvenement, AnnonceEvenementAdmin)
admin.site.register(AnnonceInformation, AnnonceInformationAdmin)
admin.site.register(Banniere, BanniereAdmin)
admin.site.register(ReseauSocial, ReseauSocialAdmin)
admin.site.register(Footer, FooterAdmin)
admin.site.register(PageContact, PageContactAdmin)
admin.site.register(MessageContact, MessageContactAdmin)
admin.site.register(Equipe, EquipeAdmin)
admin.site.register(SectionIntroPage)
admin.site.register(GainsChauffeur)
  
@admin.register(GestionSection)
class GestionSectionAdmin(admin.ModelAdmin):
    """Active/désactive en un clic les grandes sections de la page d'accueil."""

    list_display = ['titre_section', 'active', 'date_modification']
    list_filter = ['active']
    list_editable = ['active']
    search_fields = ['titre_section']
    ordering = ['titre_section']