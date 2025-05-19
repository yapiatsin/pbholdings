import random
import string
from typing import Any
from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from .utils import send_email_with_html_body
from django.http import HttpResponse, JsonResponse
from userauths.forms import EditUserProfileForm, CustomUserCreationForm, PasswordChangingForm, CreateUserProfileForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings 
from userauths.models import CustomUser
from datetime import datetime
from django.views.generic import ListView, DetailView,CreateView, DeleteView, UpdateView, TemplateView
from django.views import View, generic
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
#User = settings.AUTH_USER_MODEL
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .models import *
from userauths.forms import *
from .models import CustomUser
# Create your views here.
# from .utils import generate_greeting, generate_goodbye
from django.core.mail import send_mail
# from .utils import send_email_with_html_body
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
# Vue pour vérifier l'OTP envoyé par email
CustomUser = get_user_model()
from django.utils import timezone

def list_users(request):
    users = CustomUser.objects.filter(is_superuser=False)
    return render(request, 'liste_compte.html', {'users': users})

@login_required
def edit_user_permissions(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserPermissionForm(request.POST)
        # form = UserPermissionForm(initial={'permissions': user.custom_permissions.all()})
        if form.is_valid():
            permissions = form.cleaned_data['permissions']
            user.custom_permissions.set(permissions)
            messages.success(request, 'Permissions mises à jour avec succès.')
            return redirect('edit_user_permissions', user.id)  
    else:
        form = UserPermissionForm(initial={
            'permissions': user.custom_permissions.all()
        })
    return render(request, 'modif_user_perm.html', {
        'form': form,
        'user': user
    })

def generate_random_password(length=8):
    # characters = string.ascii_letters + string.digits #+ string.punctuation
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choice(characters) for i in range(length))

@login_required(login_url='/login/')
def add_administrateur(request):
    cxt = {}
    adm = Administ.objects.all()
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        adminform = AdministForm(request.POST)
        if userform.is_valid() and adminform.is_valid():
            try:
                user = userform.save(commit=False)
                password = generate_random_password()
                user.set_password(password)
                user.user_type = "1"
                user.save()
                adminst = adminform.save(commit=False)
                adminst.user = user
                adminst.save()
                
                subjet = 'Création de Compte Administrateur'
                receivers = [user.email]
                template = 'compte_success.html'
                context = {
                    'username': user.username,
                    'password': password,
                    'date': datetime.today().date,
                    'user_email':user.email
                }
                print('')
                print('----------------------------------------', context)
                print('')
                has_send=send_email_with_html_body(
                    subjet=subjet, 
                    receivers= receivers, 
                    template= template, 
                    context=context
                )
                if has_send:
                    messages.success(request, 'Compte créé avec succès. Un email a été envoyé.')
                else:
                    messages.error(request, 'Centre de santé enregistré avec succès, mais l\'email n\'a pas pu être envoyé.')
                return redirect('addadministrateur')
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            for field, errors in userform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
            for field, errors in adminform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
    else:
        userform = CustomUserCreationForm()
        adminform = AdministForm()
    return render(request, 'add_admin.html', {
        'user_form': userform,
        'admin_form': adminform,
        'cxt': cxt,
        'admins': adm,
    })

def delete_admin(request, pk):
    try:
        admin = get_object_or_404(Administ, id=pk)
        user = admin.user  
        admin.delete()
        user.delete()
        messages.success(request, f"le compte administrateur de {admin.user.username} et le profile associé ont été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addadministrateur')


@login_required(login_url='/login/')
def add_chefexploit(request):
    user=request.user
    try:
        # admins = Administ.objects.get(user=user)
        # chefexp = Chefexploitation.objects.select_related('user',).filter(create_by=admins)
        chefexp = Chefexploitation.objects.all()
    except Administ.DoesNotExist:
        chefexp = Chefexploitation.objects.none()
    cxt = {}
    employ = CustomUser.objects.all()
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        chefexploitform = ChefexploitationForm(request.POST)
        permission_form = UserPermissionForm(request.POST)
        if userform.is_valid() and chefexploitform.is_valid() and permission_form.is_valid():
            try:
                user = userform.save(commit=False)
                password = generate_random_password()
                user.set_password(password)
                user.user_type = "2"  # CentreSante
                user.save()
                
                chefexploitation = chefexploitform.save(commit=False)
                chefexploitation.user = user
                
                create_by = Administ.objects.get(user=request.user)
                chefexploitation.create_by = create_by
                chefexploitation.save()

                ################ Ajouter des permissions #################
                permissions = permission_form.cleaned_data['permissions']
                user.custom_permissions.set(permissions)
                
                subjet = "Création de Compte de chef d'exploitation"
                receivers = [user.email]
                template = 'compte_success.html'
                context = {
                    'username': user.username,
                    'password': password,
                    'date': datetime.today().date,
                    'user_email':user.email
                }
                has_send=send_email_with_html_body(
                    subjet=subjet, 
                    receivers= receivers, 
                    template= template, 
                    context=context
                )
                if has_send:
                    messages.success(request, 'Compte créé avec succès. Un email a été envoyé.')
                else:
                    messages.error(request, 'Centre de santé enregistré avec succès, mais l\'email n\'a pas pu être envoyé.')
                return redirect('add_centre_sante')
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            for field, errors in userform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
            for field, errors in chefexploitform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
    else:
        userform = CustomUserCreationForm()
        chefexploitform = AdministForm()
        permission_form = UserPermissionForm()
    return render(request, 'add_chef_exploitation.html', {
        'user_form': userform,
        'chefexp_form': chefexploitform,
        'permission_form': permission_form,
        'cxt': cxt,
        'employes': employ,
        'list_chefexp': chefexp,
    })

def delete_chefexploit(request, pk):
    try:
        chefexploit = get_object_or_404(Chefexploitation, id=pk)
        user = chefexploit.user  
        chefexploit.delete()
        user.delete()
        messages.success(request, f"le compte Chef exploitation de {chefexploit.user.username} et le profile associé ont été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addchefexploit')

@login_required(login_url='/login/')
def add_comptable(request):
    user=request.user
    try:
        # admins = Administ.objects.get(user=user)
        compt = Comptable.objects.all()
    except Administ.DoesNotExist:
        compt = Comptable.objects.none()
    cxt = {}
    employ = CustomUser.objects.all()
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        comptableform = ComptableForm(request.POST)
        if userform.is_valid() and comptableform.is_valid():
            try:
                user = userform.save(commit=False)
                password = generate_random_password()
                user.set_password(password)
                user.user_type = "3"  
                user.save()
                
                comptable = comptableform.save(commit=False)
                comptable.user = user
                
                create_by = Administ.objects.get(user=request.user)
                comptable.create_by = create_by
                comptable.save()
                
                subjet = 'Création de Compte Comptable'
                receivers = [user.email]
                template = 'compte_success.html'
                context = {
                    'username': user.username,
                    'password': password,
                    'date': datetime.today().date,
                    'user_email':user.email
                }
                has_send=send_email_with_html_body(
                    subjet=subjet, 
                    receivers= receivers, 
                    template= template, 
                    context=context
                )
                if has_send:
                    messages.success(request, 'Compte créé avec succès. Un email a été envoyé.')
                else:
                    messages.error(request, 'Centre de santé enregistré avec succès, mais l\'email n\'a pas pu être envoyé.')
                return redirect('add_centre_sante')
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            for field, errors in userform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
            for field, errors in comptableform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
    else:
        userform = CustomUserCreationForm()
        comptableform = AdministForm()
    return render(request, 'add_comptable.html', {
        'user_form': userform,
        'comptable_form': comptableform,
        'cxt': cxt,
        'employes': employ,
        'list_compt': compt,
    })

def delete_comptable(request, pk):
    try:
        comptable = get_object_or_404(Comptable, id=pk)
        user = comptable.user  
        comptable.delete()
        user.delete()
        messages.success(request, f"le compte comptable de {comptable.user.username} et le profile associé ont été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addcomptable')

@login_required(login_url='/login/')
def add_gerant(request):
    user=request.user
    try:
        # admins = Administ.objects.get(user=user)
        gerant = Comptable.objects.all()
    except Administ.DoesNotExist:
        gerant = Comptable.objects.none()
    cxt = {}
    employ = CustomUser.objects.all()
    if request.method == 'POST':
        userform = CustomUserCreationForm(request.POST)
        gerantform = GerantForm(request.POST)
        if userform.is_valid() and gerantform.is_valid():
            try:
                user = userform.save(commit=False)
                password = generate_random_password()
                user.set_password(password)
                user.user_type = "4"  
                user.save()
                gerant = gerantform.save(commit=False)
                gerant.user = user
                
                create_by = Administ.objects.get(user=request.user)
                gerant.create_by = create_by
                gerant.save()
                
                subjet = 'Création de Compte de Gérante'
                receivers = [user.email]
                template = 'compte_success.html'
                context = {
                    'username': user.username,
                    'password': password,
                    'date': datetime.today().date,
                    'user_email':user.email
                }
                has_send=send_email_with_html_body(
                    subjet=subjet, 
                    receivers= receivers, 
                    template= template, 
                    context=context
                )
                if has_send:
                    messages.success(request, 'Compte créé avec succès. Un email a été envoyé.')
                else:
                    messages.error(request, 'Centre de santé enregistré avec succès, mais l\'email n\'a pas pu être envoyé.')
                return redirect('add_centre_sante')
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            for field, errors in userform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
            for field, errors in gerantform.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
    else:
        userform = CustomUserCreationForm()
        gerantform = GerantForm()
    return render(request, 'add_gerant.html', {
        'user_form': userform,
        'gerantform_form': gerantform,
        'cxt': cxt,
        'employes': employ,
        'list_gerant': gerant,
    })

def delete_gerant(request, pk):
    try:
        gerant = get_object_or_404(Gerant, id=pk)
        user = gerant.user  

        gerant.delete()
        user.delete()
        messages.success(request, "Le gérantà été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addgerant')

def password_success(request):
    return render(request,'userauths/success.html')

class CreateUserProfile(CreateView):
    model = UserProfile
    template_name = 'userauths/create_profil.html'
    form_class = CreateUserProfileForm
    success_message = 'Profil créé avec succès👍✓✓'
    success_url = reverse_lazy('profil_user')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    
class EditProfilView(UpdateView):
    model = UserProfile
    form_class = EditUserProfileForm
    template_name = "userauths/edit_profil.html"
    success_url = reverse_lazy('profil_user')
    success_message = 'Profil modifié avec succès👍✓✓'
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_object(self):
        return self.request.user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context   

def pb_home(request):
    return render(request,'perfect/pb_home.html')
    
def loginview(request):
    if request.user.is_authenticated:
        messages.warning(request,f"hey you are already logged In")
        return redirect("home")
    if request.method == "POST": 
        email = request.POST.get("email")  
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user_type=user.user_type
                if user_type == '1':
                    messages.success(request, f"Bienvenue Administrateur")
                    return redirect('dash')
                elif user_type == '2':
                    messages.success(request, "Bienvenue Chef d'exploitation")
                    return redirect('dash')
                elif user_type == '3':
                    messages.success(request, "Bienvenue Comptable")
                    return redirect('dash')
                elif user_type == '4':
                    messages.success(request,  "Bienvenue Gérant")
                    return redirect('dashgarage')
                else:
                   return redirect('login')
            else:
                messages.error(request,  f"Mot de passe ou email invalide")
        except:
            messages.error(request, "Détails de connexion invalides!!!")
    return render(request, "perfect/logins.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes deconnecté.")
    return redirect("pb_holdind")

def interneView(request):
    return render(request,"userauths/interne.html")
# Vue pour afficher le formulaire de saisie de l'email
class ForgotPasswordView(View):
    def get(self, request):
        # return render(request, 'saisie_otp.html')
        return render(request, 'perfect/forgot_password.html')    

class RequestEmailView(View):
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = ''.join(random.choices('0123456789', k=4))
            PWD_FORGET.objects.create(user_id=user, otp=otp, status='0')

            subject = 'Votre OTP de réinitialisation de mot de passe'
            from_email = settings.EMAIL_HOST_USER
            to = [email]

            # HTML message
            html_content = f'''
           <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Réinitialisation du mot de passe</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="text-align: center; color: #333;">REINITIALISATION DE MOT DE PASSE</h2>
                    <p>Bonjour cher {user.username},</p>
                    <p>Vous avez demandé à réinitialiser votre mot de passe. Veuillez utiliser le code OTP ci-dessous pour compléter cette action :</p>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <p style="font-size: 20px; font-weight: bold; color: #2c3e50;">Votre code OTP : <span style="color: #e74c3c;">{otp}</span></p>
                    </div>
                    
                    <p style="color: #555;">Ce code est valable pour une durée limitée. Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail. Pour toute assistance, veuillez nous contacter immédiatement.</p>
            
                    <p>Merci de votre confiance.</p>
            
                    <p>Cordialement,<br>L'équipe support</p>
            
                    <footer style="margin-top: 20px; text-align: center; font-size: 12px; color: #999;">
                        &copy; 2024-2025 Bradi One. Tous droits réservés.
                    </footer>
                </div>
            </body>
            </html>
            '''
            # Create email message with HTML content
            email_message = EmailMultiAlternatives(subject, 'Votre OTP est {otp}', from_email, to)
            email_message.attach_alternative(html_content, 'text/html')
            email_message.send()
            return redirect("otp")
        except CustomUser.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")
            return  render(request, "perfect/forgot_password.html")

# Vue pour vérifier l'OTP envoyé par email
CustomUser = get_user_model()
from django.utils import timezone
class VerifyOtpView(View):
    def get(self, request):
        return render(request, 'perfect/reinitialise.html')
    def post(self, request):
        otp = request.session.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not otp or not new_password or not confirm_password:
            return JsonResponse({'error': 'Tous les champs sont obligatoires.'}, status=400)
        
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return  render(request, "perfect/reinitialise.html")
        try:
            reset_request = PWD_FORGET.objects.get(otp=otp, status='0')
            # Vérifiez si l'OTP à expirer
            if (timezone.now() - reset_request.creat_at).total_seconds() > 300:  # 2 minutes
                messages.error(request, "OTP expiré")
                return redirect('otp')
            # Marquer l'OTP comme utilisé
            reset_request.status = '1'
            reset_request.save()

            # Réinitialiser le mot de passe
            user = reset_request.user_id
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Mot de passe réinitialisé avec succès.')
            return redirect('login')
        
        except PWD_FORGET.DoesNotExist:
            messages.error(request, 'OTP non valide.')
            return  render(request, "perfect/otp.html")

class OptValid(View):
    def get(self, request):
        return render(request, 'perfect/otp.html')
    def post(self, request):
        otp = request.POST.get('otp')
        try :
            reset_request = PWD_FORGET.objects.get(otp=otp, status='0')
            request.session['otp'] = otp
            if reset_request :
                return redirect("verify_otp")
        except PWD_FORGET.DoesNotExist:
                 messages.error(request, "OTP non valide.")
                 return  render(request, "perfect/otp.html")
                     
from .forms import ChangePasswordForm
from django.contrib.auth.views import PasswordChangeView 
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class PasswordChangeView(PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'profil.html'
    success_message = "Mot de passe réinitialisé avec succès👍✓✓"
    error_message = "Erreur de saisie ✘✘"
    success_url = reverse_lazy('change_password')
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse = super().form_invalid(form)
        messages.error(self.request, self.error_message)
        return reponse 
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        user = get_object_or_404(CustomUser, id=request.user.id)
        admin_profil = None
        chefexploit_profil = None
        comptable_profil = None
        gerant_profil = None
        
        if user.user_type == "1":
            try:
                admin_profil = Administ.objects.get(user=user)
            except Administ.DoesNotExist:
                admin_profil = None
        elif user.user_type == "2":
            try:
                chefexploit_profil = Chefexploitation.objects.get(user=user)
            except Chefexploitation.DoesNotExist:
                chefexploit_profil = None
                
        elif user.user_type == "3":
            try:
                comptable_profil = Comptable.objects.get(user=user)
            except Comptable.DoesNotExist:
                comptable_profil = None
        
        elif user.user_type == "4":
            try:
                gerant_profil = Gerant.objects.get(user=user)
            except Gerant.DoesNotExist:
                gerant_profil = None
        else: 
            print()

        # Passer les informations récupérées au contexte
        context = {
            'form': form,
            'user': user,
            'admin_profil': admin_profil,
            'chefexploit_profil': chefexploit_profil,
            'comptable_profil': comptable_profil,
            'gerant_profil': gerant_profil,
        }
        return render(request, self.template_name, context)

class PasswordChangeDoneView(View):
    def get(self, request):
         return render(request, 'password_change_done.html')