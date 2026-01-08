from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from userauths.models import *
from .models import GENDER_SELECTION
from PB_Entreprise.models import Gerant, CategoVehi

#forms pour changer le mot de passe
class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ancien mot de passe'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le nouveau mot de passe'}))

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"username",'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"email",'class':'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_SELECTION, widget=forms.Select(attrs={"placeholder": "gender", 'class': 'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['username','email','gender']

class CustomPermissionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la permission'})
    )
    categorie = forms.ModelChoiceField(
        queryset=TypeCustomPermission.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Sélectionner une catégorie"
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL (ex: dash)'})
    )
    class Meta:
        model = CustomPermission
        fields = ['name', 'categorie', 'url']

class TypeCustomPermissionForm(forms.ModelForm):
    categorie = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'})
    )
    class Meta:
        model = TypeCustomPermission
        fields = ['categorie']

class UserPermissionForm(forms.Form):
    permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class AdministForm(forms.ModelForm):
    class Meta:
        model = Administ
        fields = ('nom', 'prenom', 'commune', 'tel1', 'tel2',)
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Nom"}),
            'prenom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Prenom"}),
            'commune': forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune",}),
            'tel1': forms.TextInput(attrs={'class':'form-control',"placeholder":"Tel 1",}),
            'tel2': forms.TextInput(attrs={'class':'form-control',"placeholder":"Tel 2",}),
        }

class ChefexploitationForm(forms.ModelForm):
    class Meta:
        model = Chefexploitation
        fields = ('nom','prenom', 'commune', 'tel1', 'tel2',)
        widgets = {
            # 'create_by': forms.Select(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'nom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Nom"}),
            'prenom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Prenoms"}),
            'gerant_voiture': forms.Select(attrs={'class':'form-control', "placeholder":"A, O, A, B, AB"}),
            'commune': forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune",}),
            'tel1': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 1",}),
            'tel2': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 2",}),
        }

class ComptableForm(forms.ModelForm):
    class Meta:
        model = Comptable
        fields = ('nom','prenom', 'commune', 'tel1', 'tel2',)
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Ville"}),
            'prenom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Ville"}),
            'gerant_voiture': forms.Select(attrs={'class':'form-control', "placeholder":"A, O, A, B, AB"}),
            'commune': forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune",}),
            'tel1': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 1",}),
            'tel2': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 2",}),
        }

class GerantForm(forms.ModelForm):
    gerant_voiture = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Véhicules gérés"
    )
    class Meta:
        model = Gerant
        fields = ('nom','prenom', 'gerant_voiture', 'commune', 'tel1', 'tel2',)
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Nom"}),
            'prenom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Prénoms"}),
            'commune': forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune",}),
            'tel1': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 1",}),
            'tel2': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 2",}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from PB_Entreprise.models import CategoVehi
        self.fields['gerant_voiture'].queryset = CategoVehi.objects.all()

class GerantEditForm(forms.Form):
    # Champs CustomUser
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"username",'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"email",'class':'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_SELECTION, widget=forms.Select(attrs={"placeholder": "gender", 'class': 'form-control'}))
    
    # Champs Gerant
    nom = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Nom"}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Prénoms"}))
    commune = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune"}), required=False)
    tel1 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 1"}), required=False)
    tel2 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 2"}), required=False)
    
    # Champs ManyToMany
    gerant_voiture = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Véhicules gérés"
    )
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        from PB_Entreprise.models import CategoVehi
        try:
            self.fields['gerant_voiture'].queryset = CategoVehi.objects.all()
        except Exception as e:
            # Si les catégories ne sont pas disponibles, utiliser un queryset vide
            self.fields['gerant_voiture'].queryset = CategoVehi.objects.none()
        
        # Pré-remplir les champs si une instance est fournie
        if instance:
            try:
                if hasattr(instance, 'user'):
                    # C'est une instance de Gerant
                    gerant = instance
                    user = gerant.user
                    self.fields['username'].initial = user.username if user.username else ''
                    self.fields['email'].initial = user.email if user.email else ''
                    self.fields['gender'].initial = user.gender if user.gender else ''
                    self.fields['nom'].initial = gerant.nom if gerant.nom else ''
                    self.fields['prenom'].initial = gerant.prenom if gerant.prenom else ''
                    self.fields['commune'].initial = gerant.commune if gerant.commune else ''
                    self.fields['tel1'].initial = gerant.tel1 if gerant.tel1 else ''
                    self.fields['tel2'].initial = gerant.tel2 if gerant.tel2 else ''
                    self.fields['gerant_voiture'].initial = list(gerant.gerant_voiture.all())
                else:
                    # C'est une instance de CustomUser
                    user = instance
                    try:
                        gerant = user.gerants.get()
                        self.fields['username'].initial = user.username if user.username else ''
                        self.fields['email'].initial = user.email if user.email else ''
                        self.fields['gender'].initial = user.gender if user.gender else ''
                        self.fields['nom'].initial = gerant.nom if gerant.nom else ''
                        self.fields['prenom'].initial = gerant.prenom if gerant.prenom else ''
                        self.fields['commune'].initial = gerant.commune if gerant.commune else ''
                        self.fields['tel1'].initial = gerant.tel1 if gerant.tel1 else ''
                        self.fields['tel2'].initial = gerant.tel2 if gerant.tel2 else ''
                        self.fields['gerant_voiture'].initial = list(gerant.gerant_voiture.all())
                    except Gerant.DoesNotExist:
                        pass
            except Exception as e:
                # Passer silencieusement pour éviter les erreurs d'initialisation
                pass

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={"type":"password",'class':'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={"type":"password",'class':'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={"type":"password",'class':'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['old_password','new_password1','new_password2']
 
class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('gender','profession','commune')
        widgets = {
            'gender' : forms.Select(choices=GENDER_SELECTION,attrs={'class': 'form-control'}),
            'profession' : forms.TextInput(attrs={'class':'form-control'}),
            'commune': forms.TextInput(attrs={'class':'form-control'}),
           
        } 
    def __init__(self, *args, **kwargs):
        super(EditUserProfileForm, self).__init__(*args, **kwargs)
        self.fields["commune"].widget.attrs['class']='form-control'
        self.fields["profession"].widget.attrs['class']='form-control'
           
        
class CreateUserProfileForm(forms.ModelForm):
    profession = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    commune = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_SELECTION, widget=forms.Select(attrs={"placeholder": "gender",'class':'form-control'}))
    class Meta:
        model = UserProfile
        fields = ('profession', 'commune', 'gender')
        
