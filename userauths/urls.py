from django.urls import path
from userauths.views import *
from django.contrib.auth import views as auth_views
from .views import PasswordChangeView
name = "userauths"

urlpatterns = [
    
    path("se connecter", loginview, name="login"),
    path("deconnexion", logout_view, name="log_out"),
    path("pb", pb_home, name="pb_holdind"),

    path("liste des comptes", list_users, name="compte"),
    path('Utilisateur/<int:user_id>/permissions/', edit_user_permissions, name='edit_user_permissions'),
    
    path('Créer admin', add_administrateur, name="addadministrateur"),
    path('Créer chef exploitation', add_chefexploit, name="addchefexploit"),
    path('Créer comptable', add_comptable, name="addcomptable"),
    path('Créer gerant', add_gerant, name="addgerant"),
    path('modifier gerant/<int:pk>/', edit_gerant, name="edit_gerant"),
    path('modifier gerant par user/<int:user_id>/', edit_gerant_by_user, name="edit_gerant_by_user"),
   
    path('supprimer compte gerant/<int:pk>/delete', delete_gerant, name="del_gernt"),
    path('supprimer compte comptable/<int:pk>/delete', delete_comptable, name="del_comptable"),
    path('supprimer compte chefexploit/<int:pk>/delete', delete_chefexploit, name="del_chef_exploit"),
    path('supprimer compte admin/<int:pk>/delete', delete_admin, name="del_admins"),
    
    path('mot de passe oublié', ForgotPasswordView.as_view(), name="mot_passe_oublie"),
    
    path('otp/', OptValid.as_view(), name='otp'),
    path('request-email/', RequestEmailView.as_view(), name='request_email'),
    
    path('verify-otp/', VerifyOtpView.as_view(), name='verify_otp'),
    path('password_change/', PasswordChangeView.as_view(), name='change_password'),
    
    path('Changer mot de passe/',PasswordChangeView.as_view(template_name="userauths/chang_password.html"), name="chang_pass"),
    path('password_success/',password_success, name="password_success"),

    path('toggle-active/<int:pk>/', toggle_active_user, name='toggle_active_user'),
    
    # ==================== GESTION DES PERMISSIONS ====================
    path('permissions/', PermissionListView.as_view(), name='list_permissions'),
    path('permissions/creer/', PermissionCreateView.as_view(), name='create_permission'),
    path('permissions/<int:pk>/modifier/', PermissionUpdateView.as_view(), name='update_permission'),
    path('permissions/<int:pk>/supprimer/', delete_permission, name='delete_permission'),
    path('permissions/export-excel/', ExportPermissionExcelView.as_view(), name='export_permissions_excel'),
    path('permissions/import-excel/', ImportPermissionExcelView.as_view(), name='import_permissions_excel'),
    
    # ==================== GESTION DES CATÉGORIES ====================
    path('categories/', CategorieListView.as_view(), name='list_categories'),
    path('categories/creer/', CategorieCreateView.as_view(), name='create_categorie'),
    path('categories/<int:pk>/modifier/', CategorieUpdateView.as_view(), name='update_categorie'),
    path('categories/<int:pk>/supprimer/', delete_categorie, name='delete_categorie'),
    path('categories/export-excel/', ExportCategoriesExcelView.as_view(), name='export_categories_excel'),
]
