from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('B', base, name='base'),
    
    path('recette_day', MyRecetteView.as_view(), name='rec_day'),
    path('bilan_day', Bilanday.as_view(), name='bilanday'),
    path('bilan_car', CarFluxView.as_view(), name='bilan-car'),
    path('bilan_car_detail/<int:pk>/vehicule', CarFluxDetailsView.as_view(), name='bilan-car-detail'),
    
    path('temps_arret', TableaustopView.as_view(), name='temps'),
    path('dashboard', DashboardView.as_view(), name='dash'),
    path('comptable/', SaisiComptaView.as_view(), name='saisi_compta'),
    path('dashboardGarag/', DashboardGaragView.as_view(), name='dashgarage'),
    path('vehicule/<int:pk>/detailgarag', DashboardGaragecarView.as_view(), name='dashgaragcar'),
    
    path('alertes', GestionalerteView.as_view(), name='alerte'),
    path('suivi_financier', SuiviFinancierView.as_view(), name='suivi_finance'),
    path('saisie_garage', SaisieGaragView.as_view(), name='saisi_garag'),
    path('saisie_temps_arret', TempsArretsView.as_view(), name='temps_arrets'),
    path('chargadminist', AddChargeAdminisView.as_view(), name='add_chargadminist'),

    path('chargadminist/<int:pk>/supprimer', delete_chargadmin, name='delet_charge_admin'),
    path('chargadminist/<int:pk>/modifier', UpdateChargeAdminView.as_view(), name='updat_charg_administ'),
    
    path('caisse', BilletageView.as_view(), name='billetage'),
    # path('bilanjournalier', BilanJournalierView.as_view(), name='bilan_journalier'),
    path('addsoldejour', AddSoldeJourView.as_view(), name='add_solde'),
    path('soldejour/<int:pk>/supprimer', delete_solde, name='delet_solde'),
    # path('tabtempsarret', TableauTempsArretView.as_view(), name='tabletemparret'),
    
    path('adddecaissement', AddDecaissementView.as_view(), name='add_decaisse'),
    path('decaissement/<int:pk>/modifier', UpdatDecaissementView.as_view(), name='updat_decaisse'),
    path('decaissement/<int:pk>/supprimer', delete_sortie_caisse, name='delet_socaisse'),
    
    path('addencaissement', AddEncaissementView.as_view(), name='addencaisse'),
    path('encaissement/<int:pk>/modifier', UpdatEncaissementView.as_view(), name='updat_encaisse'),
    path('encaissement/<int:pk>/supprimer', delete_entre_caisse, name='delet_encaisse'),
    
    #-------------------------------Categorie Véhicule & Véhicule--------------------------------- 
    path('add_veh', AddVehiculeView.as_view(), name='add_car'),
    path('vehicule/<int:pk>/detail', DetailVehiculeView.as_view(), name='detavehi'),
    path('vehicule/detail_financier', CarFinanceView.as_view(), name='detail_car_financier'),
    path('vehicule/<int:pk>/modifier', UpdatVehiculeView.as_view(), name='updatecar'),
    path('vehicule/<int:pk>/delet', delete_vehicule, name='delvehi'),

    #-------------------------------Categorie Véhicule--------------------------------------------- 
    path('addcategovehi', AddCategoriVehi.as_view(), name='add_catego_vehi'),
    path('vehicule/<cid>/', views.CategoVehiculeListView, name='catego_vehi_list'),
    path('categorie/<int:pk>/delet', delete_catego, name='delete_catego'),
    
    #-------------------------------Recette---------------------------------------------
    path('vehicule/<int:pk>/recette', AddRecetteView.as_view(), name="add_recettes"),
    path('list_recet',ListRecetView.as_view(), name="list_recet"),
    path('recette/<int:pk>/modifier', UpdateRecetView.as_view(), name="updat_recet"),
    path('recette/<int:pk>/delet', delete_recette, name='delete_recets'),
    
    #-------------------------------CHARGE---------------------------------------------
    path('vehicule/<int:pk>/acharg_fix',AddChargeFixView.as_view(), name="addcharg_fix"),
    path('acharg_fix/<int:pk>/modifier',UpdateChargFixView.as_view(), name="upd_charg_fix"),
    path('acharg_fix/<int:pk>/detail',DetailChargeFixeView.as_view(), name="detail_charg_fix"),
    #path('acharg_fix/<int:pk>/supprimer',DeletChargFixView.as_view(), name="del_charg_fix"),
    
    path('vehicule/<int:pk>/charg_var',AddChargeVarView.as_view(), name="addcharg_var"),
    path('charg_var/<int:pk>/modifier',UpdateChargeVarView.as_view(), name="updat_charg_var"),
    path('charg_var/<int:pk>/detail',DetailChargeVarView.as_view(), name="detail_charg_var"),
    #path('charg_var/<int:pk>/supprimer',DeletChargeVarView.as_view(), name="del_charg_var"),
    
    path('listcharfix',ListChargeFixView.as_view(), name="list_charg_fix"),
    path('listcharvar',ListChargeVarView.as_view(), name="list_charg_var"),
    
    #---------ENTRETIEN-------VISITE------REPARATION-------ASSURANCE-------PIECE-----VIGNETTE-----PATENTE--------PERTE-------ACCIDENT#
    
    path('vehicule/<int:pk>/addvisite',AddVisitView.as_view(), name="add_visit"), 
    path('visite/<int:pk>/modifier',UpdateVisiteView.as_view(), name="updat_visit"), 
    path('visite/<int:pk>/detail',DetailVisiteView.as_view(), name="detail_visit"), 
    #path('visite/<int:pk>/supprimer',DeletVisiteView.as_view(), name="delet_visit"),
    path('vehicule/liste/visites',ListVisitView.as_view(), name="list_visit"), 
    
    path('vehicule/<int:pk>/entretien',AddEntretienView.as_view(), name="add_entretien"),
    path('entretien/<int:pk>/modifier',UpdatEntretienView.as_view(), name="updat_entretien"),
    path('entretien/<int:pk>/detail',DetailEntretienView.as_view(), name="detail_entretien"),
    #path('entretien/<int:pk>/supprimer',DeletEntretienView.as_view(), name="delet_entretien"),
    path('liste/entretiens',ListEntretienView.as_view(), name="list_entretien"),
    
    path('vehicule/<int:pk>/reparation',AddReparationView.as_view(), name="add_reparation"),
    path('listrepa',ListReparationView.as_view(), name="list_repa"),
    path('reparation/<int:pk>/modifier',UpdateReparationView.as_view(), name="updat_reparation"),
    path('reparation/<int:pk>/detail', DetailReparatView.as_view(), name="detail_reparat"),
    path('reparation/<int:pk>/delete', delete_reparation, name='delete_reparation'),
    
    #path('piece/<int:pk>/supprimer',DeletPieceView.as_view(), name="delet_piece"),
    path('liste/pieces/changees', ListPiechangeView.as_view(), name="list_piechange"),
    
    path('piechange/<int:pk>/vehicule', AddPiecEchangeView.as_view(), name='add_piechange'),
    path('piechange/<int:pk>/delete', delete_piecechange, name='delete_piechange'),
    
    path('vehicule/<int:pk>/assurance',AddAssuranceView.as_view(), name="add_assurance"),
    path('assurance/<int:pk>/modifier',UpdateAssuranceView.as_view(), name="updat_assurance"),
    path('assurance/<int:pk>/detail',DetailAssuranceView.as_view(), name="detail_assurance"),
   # path('assurance/<int:pk>/supprimer',DeletAssuranceView.as_view(), name="delet_assurance"),
    path('liste/assurance',ListAssuranceView.as_view(), name="liste_assurance"),

    path('vehicule/<int:pk>/vignette',AddVignetteView.as_view(), name="add_vignet"),
    path('vignette/<int:pk>/modifier',UpdatVignetteView.as_view(), name="updat_vignet"),
    path('vignette/<int:pk>/detail',DetailVignetteView.as_view(), name="detail_vignet"),
   # path('vignette/<int:pk>/supprimer',DeletVignetteView.as_view(), name="delet_vignet"),
    path('vignette/<int:pk>/detail',DetailCartStationView.as_view(), name="detail_vignet"),
    path('liste/vignette',ListVignetteView.as_view(), name="liste_vignette"),
    
    path('vehicule/<int:pk>/cartestation',AddCartStationView.as_view(), name="add_station"),
    path('cartestation/<int:pk>/modifier',UpdatCartStationView.as_view(), name="updat_station"),
   # path('cartestation/<int:pk>supprimer',DeletCartStationView.as_view(), name="delet_cart_station"),
    path('cartestation/<int:pk>detail',DetailCartStationView.as_view(), name="detail_station"),
    path('liste-Carte-Stationnement',ListCartStationView.as_view(), name="liste_stationnement"),
    
    path('vehicule/<int:pk>/patente',AddPatenteView.as_view(), name="add_patente"),
    path('patente/<int:pk>/modifier', UpdatPatenteView.as_view(), name="updat_patente"),
    path('patente/<int:pk>/detail', DetailPatenteView.as_view(), name="detail_patente"),
    #path('patente/<int:pk>/supprimer', DeletPatenteView.as_view(), name="delet_patente"),
    path('patente/<int:pk>/detail', DetailPatenteView.as_view(), name="detail_patente"),
    path('liste-patente', ListPatenteView.as_view(), name="liste_patente"),
    
]