from django.urls import path
from . import views
from .views import *

urlpatterns = [
    # ----- Site public -----
    path('', Home.as_view(), name='home'),
    path('A-propos/', Apropos.as_view(), name='a_propos'),
    path('Chauffeurs/', Chauffeurs.as_view(), name='chauffeurs'),
    path('Livreur/', Livreur.as_view(), name='livreur'),
    path('Clients/', Clients.as_view(), name='clients'),
    path('Assistances/', Assistance.as_view(), name='assistances'),
    path('Contact/', Contact.as_view(), name='contact'),
    path('Services/', Service.as_view(), name='services'),
    path('Services <int:pk> info/', DetailService.as_view(), name='detail_service'),
    path('Pieces-detachees/', PiecesDetacheesPage.as_view(), name='pieces_detachees'),
    path('Blog/', Blog.as_view(), name='blogs'),
    path(
        'Blog/article/<slug:slug>/vue/',
        views.blog_article_increment_vues,
        name='blog_article_vue',
    ),
    # ----- Tableau de bord de gestion -----
    path('manage/', views.ManageDashboardView.as_view(), name='manage_dashboard'),

    # ----- Configuration & SEO -----
    path('manage/siteconfig/', views.manage_siteconfig, name='manage_siteconfig'),
    path('manage/langue/', views.manage_langue, name='manage_langue'),
    path('manage/lien-application/', views.manage_lienapplication, name='manage_lienapplication'),
    path('manage/qrcode/', views.manage_monqrcode, name='manage_monqrcode'),
    path('manage/qrcode/<int:pk>/generer/', views.regenerer_qrcode, name='regenerer_qrcode'),

    # ----- Menu / Navigation -----
    path('manage/categorie-onglet/', views.manage_categorieonglet, name='manage_categorieonglet'),
    path('manage/sous-categorie-onglet/', views.manage_souscategorieonglet, name='manage_souscategorieonglet'),

    # ----- Page d'accueil -----
    path('manage/hero-slide/', views.manage_heroslide, name='manage_heroslide'),
    path('manage/promo-section/', views.manage_promosection, name='manage_promosection'),
    path('manage/page-accueil/', views.manage_pageaccueil, name='manage_pageaccueil'),
    path('manage/compteur/', views.manage_compteur, name='manage_compteur'),
    path('manage/categorie-gestion-section/', views.manage_categoriegestionsection, name='manage_categoriegestionsection'),
    path('manage/gestion-section/', views.manage_gestionsection, name='manage_gestionsection'),

    # ----- Catégories de procédures (avec formsets imbriqués) -----
    path('manage/categorie-page/', views.manage_categoripage, name='manage_categoripage'),
    path('manage/section-intro-page/', views.manage_sectionintropage, name='manage_sectionintropage'),
    path('manage/gains-chauffeur/', views.manage_gainschauffeur, name='manage_gainschauffeur'),

    # ----- Services & Mobilité -----
    path('manage/nos-service/', views.manage_nosservice, name='manage_nosservice'),
    path('manage/categorie-service/', views.manage_categorieservice, name='manage_categorieservice'),
    path('manage/caracteristique-service/', views.manage_caracteristiqueservice, name='manage_caracteristiqueservice'),

    # ----- Location véhicules -----
    path('manage/type-vehicule-location/', views.manage_typevehiculelocation, name='manage_typevehiculelocation'),
    path('manage/vehicule-location/', views.manage_vehiculelocation, name='manage_vehiculelocation'),

    # ----- Pièces détachées -----
    path('manage/categorie-piece/', views.manage_categoriepiece, name='manage_categoriepiece'),
    path('manage/piece-detachee/', views.manage_piecedetachee, name='manage_piecedetachee'),

    # ----- Processus -----
    path('manage/processus-etape/', views.manage_processusetape, name='manage_processusetape'),

    # ----- Présentation / À propos -----
    path('manage/presentation/', views.manage_presentation, name='manage_presentation'),
    path('manage/point-fort/', views.manage_pointfort, name='manage_pointfort'),

    # ----- Annonces / Bannières -----
    path('manage/annonce-evenement/', views.manage_annonceevenement, name='manage_annonceevenement'),
    path('manage/annonce-information/', views.manage_annonceinformation, name='manage_annonceinformation'),
    path('manage/banniere/', views.manage_banniere, name='manage_banniere'),

    # ----- Réseaux sociaux / Partenaires -----
    path('manage/reseau-social/', views.manage_reseausocial, name='manage_reseausocial'),
    path('manage/partenaire-sponsor/', views.manage_partenspons, name='manage_partenspons'),

    # ----- Témoignages -----
    path('manage/temoignage-page/', views.manage_temoignagepage, name='manage_temoignagepage'),

    # ----- FAQ -----
    path('manage/faq/', views.manage_faq, name='manage_faq'),

    # ----- Équipe / Agences -----
    path('manage/equipe/', views.manage_equipe, name='manage_equipe'),
    path('manage/agence/', views.manage_agence, name='manage_agence'),

    # ----- Contact -----
    path('manage/page-contact/', views.manage_pagecontact, name='manage_pagecontact'),
    path('manage/sujet-contact/', views.manage_sujetcontact, name='manage_sujetcontact'),
    path('manage/message-contact/', views.manage_messagecontact, name='manage_messagecontact'),

    # ----- Footer -----
    path('manage/footer/', views.manage_footer, name='manage_footer'),
    path('manage/lien-categorie-footer/', views.manage_liencategoriefooter, name='manage_liencategoriefooter'),
    path('manage/lien-footer/', views.manage_lienfooter, name='manage_lienfooter'),

    # ----- Applications mobiles -----
    path('manage/application-carte/', views.manage_applicationcarte, name='manage_applicationcarte'),

    # ----- Blog -----
    path('manage/categorie-blog/', views.manage_categorieblog, name='manage_categorieblog'),
    path('manage/tag-blog/', views.manage_tagblog, name='manage_tagblog'),
    path('manage/article/', views.manage_article, name='manage_article'),
    path('manage/commentaire-blog/', views.manage_commentaireblog, name='manage_commentaireblog'),

    # ----- Statistiques (référentiel seulement — les autres tables sont alimentées automatiquement) -----
    path('manage/page-site-search/', views.manage_pagesitesearch, name='manage_pagesitesearch'),

    # ----- Tableau de bord statistiques -----
    path('manage/statistiques/', views.StatsDashboardView.as_view(), name='stats_dashboard'),

    # ----- Endpoint AJAX : simulateur de gains chauffeur -----
    path('api/chauffeur/gains-calc/', views.chauffeur_gains_compute, name='chauffeur_gains_compute'),

    # ----- Endpoint AJAX : tracking automatique des clics -----
    path('track-click/', views.track_click, name='track_click'),

    # ----- Tracking clic sur une icône de réseau social (compteur + redirection) -----
    path('reseau-social/<int:pk>/click/', views.reseau_social_click, name='reseau_social_click'),
]
