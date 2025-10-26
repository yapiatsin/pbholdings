from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from userauths.models import *
from .models import GENDER_SELECTION

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
    class Meta:
        model = CustomPermission
        fields = ['name', 'categorie', 'url']

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
    class Meta:
        model = Gerant
        fields = ('nom','prenom', 'gerant_voiture', 'commune', 'tel1', 'tel2',)
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Nom"}),
            'prenom': forms.TextInput(attrs={'class':'form-control',"placeholder":"Prénoms"}),
            'gerant_voiture': forms.Select(attrs={'class':'form-control',}),
            'commune': forms.TextInput(attrs={'class':'form-control',"placeholder":"Commune",}),
            'tel1': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 1",}),
            'tel2': forms.TextInput(attrs={'class':'form-control',"placeholder":"Contact 2",}),
        }


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
        
