from django.urls import path
from userauths.views import *
from .views import EditProfilView
from django.contrib.auth import views as auth_views
from .views import PasswordChangeView, CreateUserProfile
name = "userauths"

urlpatterns = [
    
    path("sign_in", loginview, name="login"),
    path("decon", logout_view, name="log_out"),
    path("interne", interneView, name="intern"),
    
    path('add_admin', add_administrateur, name="addadministrateur"),
    path('add_chefexploit', add_chefexploit, name="addchefexploit"),
    path('add_comptable', add_comptable, name="addcomptable"),
    path('add_gerant', add_gerant, name="addgerant"),
   
    path('del_gerant/<int:pk>/delete', delete_gerant, name="del_gernt"),
    path('del_comptable/<int:pk>/delete', delete_comptable, name="del_comptable"),
    path('del_chefexploit/<int:pk>/delete', delete_chefexploit, name="del_chef_exploit"),
    path('del_admin/<int:pk>/delete', delete_admin, name="del_admins"),
    
    path('password_forgot', ForgotPasswordView.as_view(), name="mot_passe_oublie"),
    
    path('otp/', OptValid.as_view(), name='otp'),
    path('request-email/', RequestEmailView.as_view(), name='request_email'),
    
    path('verify-otp/', VerifyOtpView.as_view(), name='verify_otp'),
    path('password_change/', PasswordChangeView.as_view(), name='change_password'),
    
    path('createprofile', CreateUserProfile.as_view(), name="creat_profil"),
    path('edit_profile',EditProfilView.as_view(), name="edit_profil"),
    path('passwordchange/',PasswordChangeView.as_view(template_name="userauths/chang_password.html"), name="chang_pass"),
    path('password_success/',password_success, name="password_success"),
]
