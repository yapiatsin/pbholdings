from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import os
from PIL import Image, UnidentifiedImageError
from userauths.models import *
from .models import GENDER_SELECTION, USER
from PB_Entreprise.models import UserProfile, CategoVehi, LANGUE_CHOICES

PROFILE_FIELDS = ('nom', 'prenom', 'commune', 'tel1', 'tel2', 'profession', 'gerant_voiture')

WIDGET_TEXT = {'class': 'form-control'}
WIDGET_SELECT = {'class': 'form-control'}
WIDGET_CHECKBOX = {'class': 'pb-modal-permissions__checkbox'}

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ancien mot de passe'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le nouveau mot de passe'}))

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
        queryset=CustomPermission.objects.select_related('categorie').order_by(
            'categorie__categorie', 'name'
        ),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class UserProfileForm(forms.Form):
    """Formulaire unique de création de compte (admin, chef, comptable, gérant)."""
    user_type = forms.ChoiceField(
        choices=USER,
        label="Rôle",
        widget=forms.Select(attrs={**WIDGET_SELECT, 'id': 'id_user_type'}),
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Username'}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={**WIDGET_TEXT, 'placeholder': 'Email'}),
    )
    gender = forms.ChoiceField(
        choices=GENDER_SELECTION,
        label="Genre",
        widget=forms.Select(attrs=WIDGET_SELECT),
    )
    nom = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Nom'}),
    )
    prenom = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Prénom'}),
    )
    commune = forms.CharField(
        label="Commune",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Commune'}),
    )
    tel1 = forms.CharField(
        label="Téléphone 1",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Téléphone 1'}),
    )
    tel2 = forms.CharField(
        label="Téléphone 2",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Téléphone 2'}),
    )
    profession = forms.CharField(
        label="Profession",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Profession'}),
    )
    gerant_voiture = forms.ModelMultipleChoiceField(
        queryset=CategoVehi.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs=WIDGET_CHECKBOX),
        required=False,
        label="Catégories de véhicules gérées",
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.select_related('categorie').order_by(
            'categorie__categorie', 'name'
        ),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permissions",
    )

    class Meta:
        fields = PROFILE_FIELDS

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('user_type') != '4':
            cleaned['gerant_voiture'] = []
        return cleaned


class UserProfileEditForm(forms.Form):
    """Formulaire unique d'édition de compte."""
    username = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={**WIDGET_TEXT, 'placeholder': 'Email'}))
    gender = forms.ChoiceField(choices=GENDER_SELECTION, widget=forms.Select(attrs=WIDGET_SELECT))
    nom = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Nom'}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Prénoms'}))
    commune = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Commune'}), required=False)
    tel1 = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Contact 1'}), required=False)
    tel2 = forms.CharField(widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Contact 2'}), required=False)
    gerant_voiture = forms.ModelMultipleChoiceField(
        queryset=CategoVehi.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs=WIDGET_CHECKBOX),
        required=False,
        label="Catégories de véhicules gérées",
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        profile = None
        user = None
        if instance is not None:
            if hasattr(instance, 'user') and hasattr(instance, 'nom'):
                profile = instance
                user = profile.user
            else:
                user = instance
                try:
                    profile = user.profile
                except UserProfile.DoesNotExist:
                    profile = None
        self.user = user
        self.profile = profile
        if user:
            self.fields['username'].initial = user.username or ''
            self.fields['email'].initial = user.email or ''
            self.fields['gender'].initial = user.gender or ''
        if profile:
            self.fields['nom'].initial = profile.nom or ''
            self.fields['prenom'].initial = profile.prenom or ''
            self.fields['commune'].initial = profile.commune or ''
            self.fields['tel1'].initial = profile.tel1 or ''
            self.fields['tel2'].initial = profile.tel2 or ''
            self.fields['gerant_voiture'].initial = list(profile.gerant_voiture.all())

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if self.user and CustomUser.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Un autre compte utilise déjà cet email.")
        return email


class MyProfileForm(forms.Form):
    """Formulaire d'édition du profil par l'utilisateur connecté."""
    prenom = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Prénom'}),
    )
    nom = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Nom'}),
    )
    telephone = forms.CharField(
        label="Téléphone",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': '+2250700000000'}),
    )
    gender = forms.ChoiceField(
        label="Sexe",
        choices=GENDER_SELECTION,
        widget=forms.Select(attrs=WIDGET_SELECT),
    )
    date_naissance = forms.DateField(
        label="Date de naissance",
        required=False,
        widget=forms.DateInput(attrs={**WIDGET_TEXT, 'type': 'date'}),
    )
    adresse = forms.CharField(
        label="Adresse",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Adresse'}),
    )
    commune = forms.CharField(
        label="Commune",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Commune'}),
    )
    tel2 = forms.CharField(
        label="Téléphone 2",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Téléphone secondaire'}),
    )
    profession = forms.CharField(
        label="Profession",
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_TEXT, 'placeholder': 'Profession'}),
    )
    avatar = forms.ImageField(
        label="Photo de profil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
    )
    bio = forms.CharField(
        label="Biographie",
        required=False,
        widget=forms.Textarea(attrs={**WIDGET_TEXT, 'rows': 3, 'placeholder': 'Quelques mots sur vous…'}),
    )
    langue = forms.ChoiceField(
        label="Langue",
        choices=UserProfile.LANGUE_CHOICES,
        widget=forms.Select(attrs=WIDGET_SELECT),
    )
    notif_email = forms.BooleanField(
        label="Notifications par e-mail",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    notif_site = forms.BooleanField(
        label="Notifications sur le site",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.profile = profile
        if user:
            self.fields['prenom'].initial = user.prenom or (profile.prenom if profile else '')
            self.fields['nom'].initial = user.nom or (profile.nom if profile else '')
            self.fields['telephone'].initial = user.telephone or (profile.tel1 if profile else '')
            self.fields['gender'].initial = user.gender or ''
            self.fields['date_naissance'].initial = user.date_naissance or (profile.date_naissance if profile else None)
            self.fields['adresse'].initial = user.adresse or ''
        if profile:
            self.fields['commune'].initial = profile.commune or ''
            self.fields['tel2'].initial = profile.tel2 or ''
            self.fields['profession'].initial = profile.profession or ''
            self.fields['bio'].initial = profile.bio or ''
            self.fields['langue'].initial = profile.langue or 'fr'
            self.fields['notif_email'].initial = profile.notif_email
            self.fields['notif_site'].initial = profile.notif_site


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={"type": "password", 'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={"type": "password", 'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={"type": "password", 'class': 'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profession', 'commune', 'nom', 'prenom', 'tel1', 'tel2')
        widgets = {
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'tel1': forms.TextInput(attrs={'class': 'form-control'}),
            'tel2': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CreateUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profession', 'commune', 'nom', 'prenom', 'tel1', 'tel2')
        widgets = {
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'tel1': forms.TextInput(attrs={'class': 'form-control'}),
            'tel2': forms.TextInput(attrs={'class': 'form-control'}),
        }
