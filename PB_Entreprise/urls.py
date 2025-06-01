from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('B', base, name='base'),
    
    path('recette journaliere', MyRecetteView.as_view(), name='rec_day'),
    path('bilan_day', Bilanday.as_view(), name='bilanday'),
    path('bilan_car', CarFluxView.as_view(), name='bilan-car'),
    path('bilan_car_detail/<int:pk>/vehicule', CarFluxDetailsView.as_view(), name='bilan-car-detail'),
    
    path('temps arret', TableaustopView.as_view(), name='temps'),
    path('Tableau de bord', DashboardView.as_view(), name='dash'),
    path('Saisie comptable/', SaisiComptaView.as_view(), name='saisi_compta'),
    path('dashboard Garage/', DashboardGaragView.as_view(), name='dashgarage'),
    path('vehicule/<int:pk>/detailgarag', DashboardGaragecarView.as_view(), name='dashgaragcar'),
    
    path('alertes', GestionalerteView.as_view(), name='alerte'),
    path('suivi financier', SuiviFinancierView.as_view(), name='suivi_finance'),
    path('saisie garage', SaisieGaragView.as_view(), name='saisi_garag'),
    path('saisie temps arret', TempsArretsView.as_view(), name='temps_arrets'),
    path('charge administive', AddChargeAdminisView.as_view(), name='add_chargadminist'),

    path('charge administrative/<int:pk>/supprimer', delete_chargadmin, name='delet_charge_admin'),
    path('charge administrative <int:pk>/modifier', UpdateChargeAdminView.as_view(), name='updat_charg_administ'),
    
    path('caisse', BilletageView.as_view(), name='billetage'),
    path('Saisie solde jour', AddSoldeJourView.as_view(), name='add_solde'),
    path('solde jour/<int:pk>/supprimer', delete_solde, name='delet_solde'),
    
    path('Saisie decaissement', AddDecaissementView.as_view(), name='add_decaisse'),
    path('decaissement/<int:pk>/modifier', UpdatDecaissementView.as_view(), name='updat_decaisse'),
    path('decaissement/<int:pk>/supprimer', delete_sortie_caisse, name='delet_socaisse'),
    
    path('Saisie encaissement', AddEncaissementView.as_view(), name='addencaisse'),
    path('encaissement/<int:pk>/modifier', UpdatEncaissementView.as_view(), name='updat_encaisse'),
    path('encaissement/<int:pk>/supprimer', delete_entre_caisse, name='delet_encaisse'),
    
    #-------------------------------Categorie Véhicule & Véhicule--------------------------------- 
    path('Ajouter nouveau véhicule', AddVehiculeView.as_view(), name='add_car'),
    path('vehicule/<int:pk>/detail', DetailVehiculeView.as_view(), name='detavehi'),
    path('vehicule/detail_financier', CarFinanceView.as_view(), name='detail_car_financier'),
    path('vehicule/<int:pk>/modifier', UpdatVehiculeView.as_view(), name='updatecar'),
    path('vehicule/<int:pk>/delet', delete_vehicule, name='delvehi'),

    #-------------------------------Categorie Véhicule--------------------------------------------- 
    path('Ajouter categorie véhicule', AddCategoriVehi.as_view(), name='add_catego_vehi'),
    path('vehicule/<cid>/', views.CategoVehiculeListView, name='catego_vehi_list'),
    path('categorie/<int:pk>/delet', delete_catego, name='delete_catego'),
    
    #-------------------------------Recette---------------------------------------------
    path('vehicule/<int:pk>/recette', AddRecetteView.as_view(), name="add_recettes"),
    path('liste recette',ListRecetView.as_view(), name="list_recet"),
    path('recette/<int:pk>/modifier', UpdateRecetView.as_view(), name="updat_recet"),
    path('recette/<int:pk>/delet', delete_recette, name='delete_recets'),
    
    #-------------------------------CHARGE---------------------------------------------
    path('vehicule/<int:pk>/acharge fixe',AddChargeFixView.as_view(), name="addcharg_fix"),
    path('acharge fixe/<int:pk>/modifier',UpdateChargFixView.as_view(), name="upd_charg_fix"),
    path('charge fixe/<int:pk>/delet', delete_charg_fixe, name='delete_chargfix'),
    path('liste charge fixe',ListChargeFixView.as_view(), name="list_charg_fix"),

    path('vehicule/<int:pk>/charg_var',AddChargeVarView.as_view(), name="addcharg_var"),
    path('charge variable/<int:pk>/modifier',UpdateChargeVarView.as_view(), name="updat_charg_var"),
    path('charge variable/<int:pk>/delet', delete_charg_var, name='delete_chargvar'),
    path('liste charge variable',ListChargeVarView.as_view(), name="list_charg_var"),
    
    #---------ENTRETIEN-------VISITE------REPARATION-------ASSURANCE-------PIECE-----VIGNETTE-----PATENTE--------PERTE-------ACCIDENT--------#
    
    path('vehicule/<int:pk>/addautarret',AddAutrarretView.as_view(), name="add_autarrets"), 
    path('Liste autres arrets', ListarretView.as_view(), name='liste_aut_arrets'),
    path('autres arrets/<int:pk>/delet', delete_autarret, name='delete_autarrets'),
    
    path('vehicule/<int:pk>/addvisite',AddVisitView.as_view(), name="add_visit"), 
    path('visite/<int:pk>/modifier',UpdateVisiteView.as_view(), name="updat_visit"), 
    path('vehicule/liste/visites',ListVisitView.as_view(), name="list_visit"), 
    path('visite/<int:pk>/delet', delete_visite, name='delete_visit'),
    
    path('vehicule/<int:pk>/entretien',AddEntretienView.as_view(), name="add_entretien"),
    path('entretien/<int:pk>/modifier',UpdatEntretienView.as_view(), name="updat_entretien"),
    path('liste/entretiens',ListEntretienView.as_view(), name="list_entretien"),
    
    path('vehicule/<int:pk>/reparation',AddReparationView.as_view(), name="add_reparation"),
    path('liste reparation',ListReparationView.as_view(), name="list_repa"),
    path('reparation/<int:pk>/detail', DetailReparatView.as_view(), name="detail_reparat"),
    path('reparation/<int:pk>/delete', delete_reparation, name='delete_reparation'),
    
    path('liste/pieces/changees', ListPiechangeView.as_view(), name="list_piechange"),
    path('piece echange/<int:pk>/vehicule', AddPiecEchangeView.as_view(), name='add_piechange'),
    path('piece echange/<int:pk>/delete', delete_piecechange, name='delete_piechange'),
    
    path('vehicule/<int:pk>/assurance',AddAssuranceView.as_view(), name="add_assurance"),
    path('assurance/<int:pk>/modifier',UpdateAssuranceView.as_view(), name="updat_assurance"),
    path('liste/assurance',ListAssuranceView.as_view(), name="liste_assurance"),
    path('assurance/<int:pk>/delete', delete_assurance, name='delete_ass'),
    
    path('vehicule/<int:pk>/vignette',AddVignetteView.as_view(), name="add_vignet"),
    path('vignette/<int:pk>/modifier',UpdatVignetteView.as_view(), name="updat_vignet"),
    path('liste/vignette',ListVignetteView.as_view(), name="liste_vignette"),
    path('vignette/<int:pk>/delete', delete_vignette, name='delete_vignets'),    
    
    path('vehicule/<int:pk>/stationnement',AddCartStationView.as_view(), name="add_station"),
    path('carte stationnement/<int:pk>/modifier',UpdatCartStationView.as_view(), name="updat_station"),
    path('liste Carte Stationnement',ListCartStationView.as_view(), name="liste_station"),
    path('carte stationnement/<int:pk>/delete', delete_stat, name='delete_stations'),    
    
    path('vehicule/<int:pk>/patente',AddPatenteView.as_view(), name="add_patente"),
    path('patente/<int:pk>/modifier', UpdatPatenteView.as_view(), name="updat_patente"),
    path('liste patente', ListPatenteView.as_view(), name="liste_patente"),
    path('patente/<int:pk>/delete', delete_patente, name='delete_patentes'),     
]