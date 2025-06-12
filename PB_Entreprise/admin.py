from django.contrib import admin
from .models import *

class ChargeAdminisAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'cpte_comptable', 'Num_piece', 'Num_fact', 'montant','date','auteur']
    list_filter = ['libelle', 'date_saisie']

class AssuranceAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'date', 'date_proch', 'montant', 'date_saisie','auteur']
    list_filter = ['vehicule', 'date_saisie', 'auteur']

class ReparationAdmin(admin.ModelAdmin):
    list_display = ['vehicule','date_entree','date_sortie','montant','prestation','date_saisie','date','auteur']
    list_filter = ['vehicule','date_saisie']

class PieceAdmin(admin.ModelAdmin):
    list_display = ['reparation','libelle','lieu','montant','date_saisie']
    list_filter = ['libelle','date_saisie','lieu']
 
class PiecEchangeAdmin(admin.ModelAdmin):
    list_display = ['vehicule','libelle','lieu','montant','date_saisie','auteur','date','auteur']
    list_filter = ['libelle','date_saisie','lieu']
 
class AccidentAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'date_saisie', 'auteur','date','auteur']
    list_filter = ['vehicule', 'date_saisie']
    
class VisiteTechniqueAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'date_vis', 'montant', 'auteur', 'date_saisie','date','auteur']
    list_filter = ['vehicule', 'montant', 'date_saisie']
  
class EntretienAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'date_Entret', 'date_proch', 'montant','date_saisie','auteur']
    list_filter = ['vehicule', 'montant', 'date_saisie']
     
class RecetteAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'montant', 'cpte_comptable', 'Num_piece', 'chauffeur', 'date', 'date_saisie','auteur']
    list_filter = ['vehicule', 'montant', 'date_saisie']
    
class PrevisionAdmin(admin.ModelAdmin):
    list_display = ['mois', 'montant_previs',]
    list_filter =  ['mois', 'montant_previs']
      
class ContraventionAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'montant','auteur']
    list_filter = ['vehicule', 'montant',]
       
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ['immatriculation', 'marque', "category",'photo_carte_grise' ,'date_saisie','auteur']
    list_filter = ['immatriculation','marque', 'category']
       
class AutrarretAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'libelle', 'auteur', 'date_arret', 'date_saisie']
    list_filter = ['vehicule','libelle', 'date_arret', 'date_saisie']

class CategoVehiAdmin(admin.ModelAdmin):
    list_display =['cid','category','recette_defaut' ]
    
class ChargeVariableAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'Num_piece','cpte_comptable','libelle','date', 'date_saisie','montant','auteur']
    list_filter = ['vehicule','libelle','cpte_comptable', 'date_saisie']
       
class ChargeFixeAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'Num_piece','cpte_comptable','libelle','montant','date','date_saisie','auteur']
    list_filter = ['vehicule', 'libelle', 'cpte_comptable', 'date_saisie']
 
class VignetteAdmin(admin.ModelAdmin):
    list_display = ['vehicule','montant', 'date_saisie', 'date','auteur']
    list_filter = ['vehicule', 'date_saisie']
    
class PatenteAdmin(admin.ModelAdmin):
    list_display = ['vehicule','montant','auteur', 'date_saisie', 'date']
    list_filter = ['vehicule','date', 'date_saisie']
    
class StationnementAdmin(admin.ModelAdmin):
    list_display = ['vehicule','montant','auteur', 'date_saisie', 'date']
    list_filter = ['vehicule','date', 'date_saisie']
    
class EncaissementAdmin(admin.ModelAdmin):
    list_display = ['libelle','montant','date_saisie', 'date','auteur']
    list_filter = ['libelle','date_saisie', 'date_saisie']

class DecaissementAdmin(admin.ModelAdmin):
    list_display = ['libelle','montant','date_saisie','auteur','auteur']
    list_filter = ['libelle','date_saisie']

class BilletageAdmin(admin.ModelAdmin):
    list_display = ['valeur','nombre','type', 'date_saisie','auteur']
    list_filter = ['valeur','nombre']

class SoldeJourAdmin(admin.ModelAdmin):
    list_display = ['montant', 'date', 'date_saisie', 'auteur']
    list_filter = ['montant', 'date']

admin.site.register(Autrarret, AutrarretAdmin)
admin.site.register(SoldeJour, SoldeJourAdmin)
admin.site.register(Billetage, BilletageAdmin)
admin.site.register(Encaissement, EncaissementAdmin)
admin.site.register(Decaissement, DecaissementAdmin)
admin.site.register(Vignette, VignetteAdmin)
admin.site.register(Patente, PatenteAdmin)
admin.site.register(Stationnement, StationnementAdmin)
admin.site.register(Prevision, PrevisionAdmin)
admin.site.register(Vehicule, VehiculeAdmin)
admin.site.register(ChargeAdminis, ChargeAdminisAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(PiecEchange, PiecEchangeAdmin)
admin.site.register(Recette, RecetteAdmin)
admin.site.register(Reparation,ReparationAdmin)
admin.site.register(VisiteTechnique, VisiteTechniqueAdmin)
admin.site.register(Entretien, EntretienAdmin)
admin.site.register(CategoVehi, CategoVehiAdmin)
admin.site.register(ChargeFixe, ChargeFixeAdmin)
admin.site.register(Assurance, AssuranceAdmin)
admin.site.register(ChargeVariable, ChargeVariableAdmin)
