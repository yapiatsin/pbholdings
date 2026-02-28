from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('B', base, name='base'),
    path('recette journaliere', MyRecetteView.as_view(), name='rec_day'),
    path('recette journaliere/export-excel/', ExportRecetteMensuelleExcelView.as_view(), name='export_recette_mensuelle_excel'),
    # path('bilan day', Bilanday.as_view(), name='bilanday'),
    # path('bilan-day/export-excel/', ExportBilandayExcelView.as_view(), name='export_bilanday_excel'),
    path('temps arret', TableaustopView.as_view(), name='temps'),
    path('temps-arret/export-excel/', ExportTempsArretExcelView.as_view(), name='export_temps_arret_excel'),
    path('Tableau de bord', DashboardView.as_view(), name='dash'),
    path('Saisie comptable /', SaisiComptaView.as_view(), name='saisi_compta'),
    path('dashboard Garage /', DashboardGaragView.as_view(), name='dashgarage'),
    path('alertes', GestionalerteView.as_view(), name='alerte'),

    path('fiche-analytique-exploitation', AnalytiqueFicheView.as_view(), name='analytique_fiche'),
    path('fiche-analytique-exploitation/export-excel/', ExportAnalytiqueFicheExcelView.as_view(), name='export_analytique_fiche_excel'),

    path('saisie garage', SaisieGaragView.as_view(), name='saisi_garag'),
    path('saisie temps arret', TempsArretsView.as_view(), name='temps_arrets'),

    path('charge administive', AddChargeAdminisView.as_view(), name='add_chargadminist'),
    path('charge administrative /<int:pk>/ delet', delete_chargadmin, name='delet_charge_admin'),
    path('charge administrative /<int:pk>/ modifier', UpdateChargeAdminView.as_view(), name='updat_charg_administ'),
    path("charge administrative/export-excel/", ExportChargeAdminisExcelView.as_view(), name="export_charge_admin_excel"),
    
    path('caisse', BilletageView.as_view(), name='billetage'),
    path('caisse/export-excel/', ExportCaisseExcelView.as_view(), name='export_caisse_excel'),
    path('Saisie solde jour', AddSoldeJourView.as_view(), name='add_solde'),
    path('solde jour /<int:pk>/ delet', delete_solde, name='delet_solde'),
    path('solde jour/export-excel/', ExportSoldeJourExcelView.as_view(), name='export_solde_jour'),
    
    path('Saisie decaissement', AddDecaissementView.as_view(), name='add_decaisse'),
    path('decaissement /<int:pk>/ modifier', UpdatDecaissementView.as_view(), name='updat_decaisse'),
    path('decaissement /<int:pk>/ delet', delete_sortie_caisse, name='delet_socaisse'),
    path('decaissements/export-excel/', ExportDecaissementExcelView.as_view(), name='export_decaissements'),

    path('Saisie encaissement', AddEncaissementView.as_view(), name='addencaisse'),
    path('encaissement /<int:pk>/ modifier', UpdatEncaissementView.as_view(), name='updat_encaisse'),
    path('encaissement /<int:pk>/ delet', delete_entre_caisse, name='delet_encaisse'),
    path('Encaissements/export-excel/', ExportEncaissementExcelView.as_view(), name='export_encaissements'),
    
    #-------------------------------------------Categorie Véhicule--------------------------------------------- 
    path('Ajouter categorie véhicule', AddCategoriVehi.as_view(), name='add_catego_vehi'),
    path('categorie /<int:pk>/ modifier', UpdateCategoView.as_view(), name='updat_catego_vehi'),
    path('vehicule /<cid>/', views.CategoVehiculeListView, name='catego_vehi_list'),
    path('categorie /<int:pk>/ delet', delete_catego, name='delete_catego'),

    #-------------------------------------------Categorie Véhicule & Véhicule--------------------------------- 
    path('Véhicule', AllVehiculeView.as_view(), name='all_vehi'),
    path('Véhicule hors parc', AllVehiculeHorsParrcView.as_view(), name='all_vehi_hors_parc'),
    path('historique véhicule',HistoriqueVehiculeView.as_view(), name="historique_vehicule"),
    path('historique-vehicule/export-excel/', ExportHistoriqueVehiculeExcelView.as_view(), name='export_historique_vehicule_excel'),
    path('Nouveau #<int:pk> véhicule', AddVehiculeExcelView.as_view(), name='add_vehi'),
    path('vehicule /detail_financier', CarFinanceView.as_view(), name='detail_car_financier'),
    path('vehicule /<int:pk>/ modifier', UpdatVehiculeView.as_view(), name='updat_car'),
    path('vehicule /<int:pk>/ toggle-statut/', toggle_car_statut, name='toggle_car_statut'),
    path('vehicules /delete-multiple/', delete_multiple_vehicules, name='delete_multiple_vehicules'),
    path('vehicules/export-excel/', ExportVehiculeExcelView.as_view(), name='export_vehicules_excel'),
    path('vehicules-hors-parc/export-excel/', ExportVehiculeHorsParcExcelView.as_view(), name='export_vehicules_hors_parc_excel'),

    #-------------------------------------------------------Recette---------------------------------------------
    path('vehicule /<int:pk>/ recette', AddRecetteView.as_view(), name="add_recettes"),
    path('Meilleure recette',BestRecetView.as_view(), name="best_recets"),
    path('meilleures-recettes/export-excel/', ExportBestRecetteExcelView.as_view(), name='export_best_recette_excel'),
    path('liste recette',ListRecetView.as_view(), name="list_recet"),
    path('historique recette',HistoriqueRecetteView.as_view(), name="historique_recette"),
    path('historique-recettes/export-excel/', ExportHistoriqueRecetteExcelView.as_view(), name='export_historique_recettes_excel'),
    path('recette /<int:pk>/ modifier', UpdateRecetView.as_view(), name="updat_recet"),
    path('recettes /delete-selected/', views.delete_selected_recettes, name='delete_selected_recettes'),
    path('recettes /export-excel/', ExportRecetteExcelView.as_view(), name='export_recettes_excel'),
    #-------------------------------------------CHARGE---------------------------------------------
    path('vehicule /<int:pk>/ acharge fixe',AddChargeFixView.as_view(), name="addcharg_fix"),
    path('acharge fixe /<int:pk>/ modifier',UpdateChargFixView.as_view(), name="upd_charg_fix"),
    path('charge fixe /delete-selected/', views.delete_selected_chargfix, name='delete_selected_chargfix'),
    path('liste-charge-fixe',ListChargeFixView.as_view(), name="list_charg_fix"),
    path('historique charge fixe',HistoriqueChargeFixeView.as_view(), name="historique_charge_fixe"),
    path('charge fixe /export-excel/', ExportChargeFixeExcelView.as_view(), name='export_charge_fixe_excel'),

    path('vehicule /<int:pk>/ charg_var',AddChargeVarView.as_view(), name="addcharg_var"),
    path('charge variable /<int:pk>/ modifier',UpdateChargeVarView.as_view(), name="updat_charg_var"),
    path('charge variable /delete-selected/', views.delete_selected_chargvar, name='delete_selected_chargvar'),
    path('liste charge variable',ListChargeVarView.as_view(), name="list_charg_var"),
    path('historique charge variable',HistoriqueChargeVariableView.as_view(), name="historique_charge_variable"),
    path('historique-charge-variable/export-excel/', ExportHistoriqueChargeVariableExcelView.as_view(), name='export_historique_charge_variable_excel'),
    path('charges variables/export-excel/', ExportChargeVariableExcelView.as_view(), name='export_charges_variables_excel'),

    #---------ENTRETIEN-------VISITE------REPARATION-------ASSURANCE-------PIECE-----VIGNETTE-----PATENTE--------PERTE-------ACCIDENT--------#
    path('vehicule /<int:pk>/ addautarret',AddAutrarretView.as_view(), name="add_autarrets"),
    path('autre-arret/<int:pk>/modifier', views.UpdateAutrarretView.as_view(), name='updat_autarret'),
    path('Liste-autres-arrets', ListarretView.as_view(), name='liste_aut_arrets'),
    path('autres-arrets/delete-selected/', views.delete_selected_autarret, name='delete_selected_autarret'),
    path('autre-arret/export-excel/', ExportAutrarretExcelView.as_view(), name='export_autrarrets_excel'),

    path('vehicule /<int:pk>/ addvisite', AddVisitView.as_view(), name="add_visit"), 
    path('visite/<int:pk>/ modifier', UpdateVisiteView.as_view(), name="updat_visit"), 
    path('liste/visites-techniques', ListVisitTechniqueView.as_view(), name="list_visit"), 
    path('visite /delete-selected/', views.delete_selected_visite, name='delete_selected_visite'),
    path('visites-techniques/export-excel/', ExportVisiteTechniqueExcelView.as_view(), name='export_visite_excel'),

    path('vehicule/<int:pk>/add_entretien',AddEntretienView.as_view(), name="add_entretien"),
    path('entretien /<int:pk>/ update',UpdatEntretienView.as_view(), name="updat_entretien"),
    path('liste/entretien',ListEntretienView.as_view(), name="list_entretien"),
    path('entretien /delete-selected/', views.delete_selected_entretien, name='delete_selected_entretien'),
    path('entretien/export-excel/', ExportEntretienExcelView.as_view(), name='export_entretien_excel'),
    
    path('vehicule /<int:pk>/ reparation',AddReparationView.as_view(), name="add_reparation"),
    path('liste reparation',ListReparationView.as_view(), name="list_repa"),
    path('top vehicule reparation',BestReparationView.as_view(), name="top_repa"),
    path('top-reparations/export-excel/', ExportBestReparationExcelView.as_view(), name='export_top_reparation_excel'),
    path('reparation /<int:pk>/ modifier', UpdateReparationView.as_view(), name="update_reparation"),
    path('reparation /<int:pk>/ detail', DetailReparatView.as_view(), name="detail_reparat"),
    path('reparation /<int:pk>/ export-pdf/', ExportReparationPDFView.as_view(), name='export_reparation_pdf'),
    path('reparation /delete-selected/', views.delete_selected_reparation, name='delete_selected_reparation'),
    path('reparation/export-excel/', ExportReparationExcelView.as_view(), name='export_reparation_excel'),
    
    path('liste /pieces', ListPieceView.as_view(), name="list_piece"),
    path('liste /pieces/ changees', ListPiechangeView.as_view(), name="list_piechange"),
    path('piece echange /<int:pk>/ vehicule', AddPiecEchangeView.as_view(), name='add_piechange'),
    path('piece echange /delete-selected/', views.delete_selected_piechange, name='delete_selected_piechange'),
    path('export_piec_echange_excel/', ExportPiecEchangeExcelView.as_view(), name='export_piec_echange_excel'),
    path('export_piece_excel/', ExportPieceExcelView.as_view(), name='export_piece_excel'),
    
    path('vehicule /<int:pk>/ assurance',AddAssuranceView.as_view(), name="add_assurance"),
    path('assurance /<int:pk>/ modifier',UpdateAssuranceView.as_view(), name="updat_assurance"),
    path('liste /assurance',ListAssuranceView.as_view(), name="liste_assurance"),
    path('assurance /delete-selected/', views.delete_selected_assurance, name='delete_selected_assurance'),
    path('export_assurance_excel/', ExportAssuranceExcelView.as_view(), name='export_assurance_excel'),
    
    path('vehicule /<int:pk>/ vignette',AddVignetteView.as_view(), name="add_vignet"),
    path('vignette /<int:pk>/ modifier',UpdatVignetteView.as_view(), name="updat_vignet"),
    path('liste /vignette',ListVignetteView.as_view(), name="liste_vignette"),
    path('vignette /delete-selected/', views.delete_selected_vignette, name='delete_selected_vignette'),
    path('vignette/export-excel/', ExportVignetteExcelView.as_view(), name='export_vignette_excel'),

    path('vehicule/<int:pk>/stationnement',AddCartStationnementView.as_view(), name="add_station"),
    path('carte stationnement/<int:pk>/modifier',UpdatCartStationView.as_view(), name="updat_station"),
    path('liste-carte-stationnement',ListCartStationView.as_view(), name="liste_station"),
    path('carte-stationnement/delete-selected/', views.delete_selected_stat, name='delete_selected_stat'),
    path('carte-stationnement/export-excel/', ExportStationnementExcelView.as_view(), name='export_stationnement_excel'),
    
    path('vehicule /<int:pk>/ patente',AddPatenteView.as_view(), name="add_patente"),
    path('patente /<int:pk>/ modifier', UpdatPatenteView.as_view(), name="updat_patente"),
    path('liste patente', ListPatenteView.as_view(), name="liste_patente"),
    path('patente /delete-selected/', views.delete_selected_patente, name='delete_selected_patente'),
    path('patente/export-excel/', ExportPatenteExcelView.as_view(), name='export_patente_excel'),
    
    path('Audit annuel', historique, name='historique'), 
]