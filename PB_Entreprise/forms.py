from django import forms
from django.forms import DateInput
from .models import *
from userauths.models import CustomUser
from django.forms import inlineformset_factory, modelformset_factory, BaseModelFormSet
LIEU_PIECE = (
    ('INTERNE', 'INTERNE'),
    ('EXTERNE', 'EXTERNE'),
)

MOTIF_REPARATION = (
    ('Visite', 'Visite'),
    ('Panne', 'Panne'),
    ('Accident', 'Accident'),
)

class DateForm(forms.Form):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}))

class DateFormMJR(forms.Form):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    categorie = forms.ModelChoiceField(queryset=CategoVehi.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    immatriculation = forms.CharField(required=False, max_length=30, widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder':"Saisissez l'immatriculation"}),label="Immatriculation")
    motif = forms.ChoiceField(
        choices=[('', '--- Tous les motifs ---')] + list(MOTIF_REPARATION),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class DatebilanForm(forms.Form):
    date_bilan = forms.DateField(widget=forms.DateInput(attrs={'type':'date','class':'form-control'}))

class DateFormPiece(forms.Form):
    categorie = forms.ModelChoiceField(queryset=CategoVehi.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    immatriculation = forms.CharField(required=False, max_length=30, widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder':"Saisissez l'immatriculation"}),label="Immatriculation")
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    lieu = forms.ChoiceField(
        choices=[('', "--- Tous les lieux d'achat ---")] + list(LIEU_PIECE),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
class DateFormRepar(forms.Form):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    motif = forms.ChoiceField(
        choices=[('', '--- Tous les motifs ---')] + list(MOTIF_REPARATION),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class DateFormAnalytique(forms.Form):
    """Formulaire de filtre pour la fiche analytique exploitation"""
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False, label="Date début")
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False, label="Date fin")
    categorie = forms.ModelChoiceField(queryset=CategoVehi.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}), label="Catégorie")
    immatriculation = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez l'immatriculation"}), label="Immatriculation")

class DateFormListRepar(forms.Form):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}), required=False)
    motif = forms.ChoiceField(
        choices=[('', '--- Tous les motifs ---')] + list(MOTIF_REPARATION),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categorie = forms.ModelChoiceField(queryset=CategoVehi.objects.all(),required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    immatriculation = forms.CharField(required=False, max_length=30, widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder':"Saisissez l'immatriculation"}),label="Immatriculation")

class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategoVehi
        fields = ('category','recette_defaut','perte_par_30min')
        widgets = {
            # 'cid': forms.TextInput(attrs={'class':'form-control',}),
            'category':forms.TextInput(attrs={'class':'form-control'}),
            'recette_defaut':forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'perte_par_30min':forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }

class Solde_JourForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget=forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = SoldeJour
        fields = ('montant','date_saisie',)
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }

class AutrarretForm(forms.ModelForm):
    class Meta:
        model = Autrarret
        fields = ('auteur','libelle','date_sortie','date_arret','numfich','montant')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'numfich': forms.TextInput(attrs={'class':'form-control'}),
            'date_arret' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
        }
    def __init__(self, *args, **kwargs):
        super(AutrarretForm, self).__init__(*args, **kwargs)
        self.fields["date_arret"].input_formats = ("%Y-%m-%dT%H:%M",) 
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",) 

class UpdatAutrarretForm(forms.ModelForm):
    class Meta:
        model = Autrarret
        fields = ('auteur','libelle','date_sortie','date_arret','numfich','montant')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'numfich': forms.TextInput(attrs={'class':'form-control'}),
            'date_arret': DateInput(attrs={'class':'form-control', 'type':"datetime-local","class":"form-control"}, format='%Y-%m-%dT%H:%M'),  
            'date_sortie': DateInput(attrs={'class':'form-control', 'type':"datetime-local","class":"form-control"}, format='%Y-%m-%dT%H:%M'),  
        }
    def __init__(self, *args, **kwargs):
        super(UpdatAutrarretForm, self).__init__(*args, **kwargs)
        self.fields["date_arret"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",)

class ChargeAdminisForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateTimeInput(format=('%m/%d/%Y %H:%M'), attrs={'class':'form-control','format':'yyyy-mm-dd HH-ii ss', 'type':'date'}))
    class Meta:
        model = ChargeAdminis
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie',)
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
        }

class updatChargeAdminisForm(forms.ModelForm):
    class Meta:
        model = ChargeAdminis
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie')
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.NumberInput(attrs={'class':'form-control'}),
            'date_saisie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        super(updatChargeAdminisForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        formatted_date = date.strftime('%Y-%m-%d',)
        return formatted_date 

class VehiculeForm(forms.ModelForm):
    date_acquisition = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    dat_edit_carte_grise = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    date_mis_service = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Vehicule
        # fields = ('immatriculation','marque','duree','image','photo_carte_grise','num_cart_grise','num_Chassis','date_acquisition','cout_acquisition','dat_edit_carte_grise','date_mis_service','category',)
        fields = ('immatriculation','marque','duree','num_cart_grise','num_Chassis','date_acquisition','cout_acquisition','dat_edit_carte_grise','date_mis_service')
        widgets = {
            'immatriculation': forms.TextInput(attrs={'class':'form-control'}),
            'marque': forms.TextInput(attrs={'class':'form-control'}),
            # 'category':forms.Select(attrs={'class':'form-control'}),
            'duree': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            'num_cart_grise': forms.TextInput(attrs={'class':'form-control'}),
            'num_Chassis': forms.TextInput(attrs={'class':'form-control'}),
            'cout_acquisition': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
            # 'image': forms.ClearableFileInput(attrs={
            #     'class': 'form-control form-control-lg border p-5',
            #     'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            # }),
        }
        
class UpdatVehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ('immatriculation','marque','duree','num_cart_grise','num_Chassis','date_acquisition','cout_acquisition','dat_edit_carte_grise','date_mis_service','category',)
        widgets = {
            'immatriculation': forms.TextInput(attrs={'class':'form-control'}),
            'marque': forms.TextInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'duree': forms.NumberInput(attrs={'class':'form-control'}),
            'num_cart_grise': forms.TextInput(attrs={'class':'form-control'}),
            'num_Chassis': forms.TextInput(attrs={'class':'form-control'}),
            'cout_acquisition': forms.NumberInput(attrs={'class':'form-control'}),
            'date_acquisition' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'dat_edit_carte_grise' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_mis_service' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatVehiculeForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date_acquisition = self.cleaned_data['date_acquisition']
        formatted_date = date_acquisition.strftime('%Y-%m-%d',)
        return formatted_date 

class BilletageForm(forms.ModelForm):
    class Meta:
        model = Billetage
        fields = ('valeur','nombre','type','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'valeur': forms.Select(attrs={'class':'form-control'}),
            'nombre': forms.NumberInput(attrs={'class':'form-control'}),
            'type': forms.Select(attrs={'class':'form-control'}),
        }
BilletageFormSet = modelformset_factory(
    Billetage,
    form=BilletageForm,
    extra=1,    
    can_delete=True
)

class CartStationForm(forms.ModelForm):
    date_saisie = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'placeholder': 'Sélectionner une date...', 'type': 'date'}))
    date_proch = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'placeholder': 'Sélectionner une date...', 'type': 'date'}))
    class Meta:
        model = Stationnement
        fields = ('montant','date_proch','date_saisie','image',)
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(CartStationForm, self).__init__(*args, **kwargs)
        # Format ISO (YYYY-MM-DD) pour type="date" du navigateur, puis format US
        self.fields["date_saisie"].input_formats = ("%Y-%m-%d", "%m/%d/%Y")
        self.fields["date_proch"].input_formats = ("%Y-%m-%d", "%m/%d/%Y")
      
class UpdatCartStationForm(forms.ModelForm):
    class Meta:
        model = Stationnement
        fields = ('montant', 'date_saisie', 'date_proch','image')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie': DateInput(attrs={'class':'form-control', 'type':"datetime-local","class":"form-control"}, format='%Y-%m-%dT%H:%M')  ,  
            'date_proch': DateInput(attrs={'class':'form-control', 'type':"datetime-local","class":"form-control"}, format='%Y-%m-%dT%H:%M'),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatCartStationForm, self).__init__(*args, **kwargs)
        self.fields["date_saisie"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_proch"].input_formats = ("%Y-%m-%dT%H:%M",)

class PatenteForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    date_proch = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Patente
        fields = ('montant','date_proch','date_saisie','image',)
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
        
class UpdatPatenteForm(forms.ModelForm):
    class Meta:
        model = Patente
        fields = ('montant', 'date_saisie', 'date_proch','image')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_proch': DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatPatenteForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        date = self.cleaned_data['date_proch']
        formatted_date = date.strftime('%Y-%m-%d')
        return formatted_date   
    
class VignetteForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    date_proch = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Vignette
        fields = ('montant','date_proch','montant','date_saisie','image')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
        
class UpdatVignetteForm(forms.ModelForm):
    class Meta:
        model = Vignette
        fields = ('montant', 'date_saisie', 'date_proch','image',)
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_proch': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatVignetteForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        formatted_date = date.strftime('%Y-%m-%d')
        return formatted_date   
        
class DecaissementForm(forms.ModelForm):
    class Meta:
        model = Decaissement
        fields = ('Num_piece','libelle','montant',)
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }
DecaissementFormSet = modelformset_factory(
    Decaissement,
    form=DecaissementForm,
    extra=1,    
    can_delete=True
)

class UpdatDecaissementForm(forms.ModelForm):
    class Meta:
        model = Decaissement
        fields = ('Num_piece','libelle','montant','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatDecaissementForm, self).__init__(*args, **kwargs)
    # def clean_date(self):
    #     date = self.cleaned_data['date_saisie']
    #     formatted_date = date.strftime('%Y-%m-%d')
    #     return formatted_date

class EncaissementForm(forms.ModelForm):
    class Meta:
        model = Encaissement
        fields = ('Num_piece','libelle','montant',)
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }
EncaissementFormSet = modelformset_factory(
    Encaissement,
    form=EncaissementForm,
    extra=1,    
    can_delete=True
)
        
class UpdatEncaissementForm(forms.ModelForm):
    class Meta:
        model = Encaissement
        fields = ('Num_piece','libelle','montant')
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d')
        }
    def __init__(self, *args, **kwargs):
        super(UpdatEncaissementForm, self).__init__(*args, **kwargs)
    # def clean_date(self):
    #     date = self.cleaned_data['date_saisie']
    #     formatted_date = date.strftime('%Y-%m-%d')
    #     return formatted_date
        
class RecetteForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Recette
        fields = ('chauffeur','montant','cpte_comptable','Num_piece','numero_fact','date_saisie',)
        widgets = {
            'chauffeur': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'numero_fact': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }

class UpdateRecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        fields = ('chauffeur','montant','cpte_comptable','Num_piece','numero_fact','date_saisie')
        widgets = {
            'chauffeur': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'numero_fact': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        super(UpdateRecetteForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        formatted_date = date.strftime('%Y-%m-%d',)
        return formatted_date

class HistoriqueRecetteFilterForm(forms.Form):
    """Formulaire de filtre pour l'historique des recettes avec tous les champs"""
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date fin"
    )
    date_saisie_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie début"
    )
    date_saisie_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie fin"
    )
    categorie = forms.ModelChoiceField(
        queryset=CategoVehi.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Catégorie"
    )
    immatriculation = forms.CharField(
        required=False, 
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez l'immatriculation"}),
        label="Immatriculation"
    )
    chauffeur = forms.CharField(
        required=False, 
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le chauffeur"}),
        label="Chauffeur"
    )
    cpte_comptable = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le compte comptable"}),
        label="Compte comptable"
    )
    numero_fact = forms.CharField(
        required=False, 
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de facture"}),
        label="Numéro facture"
    )
    Num_piece = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de pièce"}),
        label="Numéro pièce"
    )
    montant_min = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant minimum"}),
        label="Montant minimum"
    )
    montant_max = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant maximum"}),
        label="Montant maximum"
    )
    auteur = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Auteur"
    )
    history_type = forms.ChoiceField(
        choices=[
            ('', '--- Tous les types ---'),
            ('+', 'Créé'),
            ('~', 'Modifié'),
            ('-', 'Supprimé')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type d'historique"
    )
                
class ChargeFixForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = ChargeFixe
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie',)
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
        }

class UpdatChargeFixForm(forms.ModelForm):
    class Meta:
        model = ChargeFixe
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie')
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatChargeFixForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        formatted_date = date.strftime('%Y-%m-%d',)
        return formatted_date

class HistoriqueChargeFixeFilterForm(forms.Form):
    """Formulaire de filtre pour l'historique des charges fixes avec tous les champs"""
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique fin"
    )
    date_saisie_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie début"
    )
    date_saisie_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie fin"
    )
    categorie = forms.ModelChoiceField(
        queryset=CategoVehi.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Catégorie"
    )
    immatriculation = forms.CharField(
        required=False, 
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez l'immatriculation"}),
        label="Immatriculation"
    )
    libelle = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le libellé"}),
        label="Libellé"
    )
    cpte_comptable = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le compte comptable"}),
        label="Compte comptable"
    )
    Num_piece = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de pièce"}),
        label="Numéro pièce"
    )
    Num_fact = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de facture"}),
        label="Numéro facture"
    )
    montant_min = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant minimum"}),
        label="Montant minimum"
    )
    montant_max = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant maximum"}),
        label="Montant maximum"
    )
    auteur = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Auteur"
    )
    history_type = forms.ChoiceField(
        choices=[
            ('', '--- Tous les types ---'),
            ('+', 'Créé'),
            ('~', 'Modifié'),
            ('-', 'Supprimé')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type d'historique"
    )

class HistoriqueChargeVariableFilterForm(forms.Form):
    """Formulaire de filtre pour l'historique des charges variables avec tous les champs"""
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique fin"
    )
    date_saisie_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie début"
    )
    date_saisie_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date saisie fin"
    )
    categorie = forms.ModelChoiceField(
        queryset=CategoVehi.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Catégorie"
    )
    immatriculation = forms.CharField(
        required=False, 
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez l'immatriculation"}),
        label="Immatriculation"
    )
    libelle = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le libellé"}),
        label="Libellé"
    )
    cpte_comptable = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le compte comptable"}),
        label="Compte comptable"
    )
    Num_piece = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de pièce"}),
        label="Numéro pièce"
    )
    Num_fact = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le numéro de facture"}),
        label="Numéro facture"
    )
    montant_min = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant minimum"}),
        label="Montant minimum"
    )
    montant_max = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': "Montant maximum"}),
        label="Montant maximum"
    )
    auteur = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Auteur"
    )
    history_type = forms.ChoiceField(
        choices=[
            ('', '--- Tous les types ---'),
            ('+', 'Créé'),
            ('~', 'Modifié'),
            ('-', 'Supprimé')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type d'historique"
    )

class HistoriqueVehiculeFilterForm(forms.Form):
    """Formulaire de filtre pour l'historique des véhicules"""
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique début"
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False,
        label="Date historique fin"
    )
    immatriculation = forms.CharField(
        required=False, 
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez l'immatriculation"}),
        label="Immatriculation"
    )
    categorie = forms.ModelChoiceField(
        queryset=CategoVehi.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Catégorie"
    )
    marque = forms.CharField(
        required=False, 
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez la marque"}),
        label="Marque"
    )
    motif_sorti = forms.CharField(
        required=False, 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Saisissez le motif de sortie"}),
        label="Motif de sortie"
    )
    annee_sortie = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Année de sortie (ex: 2026)", 'min': 2000, 'max': 2100}),
        label="Année de sortie"
    )
    annee_enregistrement = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Année d'enregistrement (ex: 2026)", 'min': 2000, 'max': 2100}),
        label="Année d'enregistrement"
    )
    history_type = forms.ChoiceField(
        choices=[
            ('', '--- Tous les types ---'),
            ('+', 'Créé'),
            ('~', 'Modifié'),
            ('-', 'Supprimé')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type d'historique"
    )
        
class ChargeVarForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = ChargeVariable
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
        }

class updatChargeVarForm(forms.ModelForm):
    #date = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = ChargeVariable
        fields = ('libelle','montant','cpte_comptable','Num_piece','Num_fact','date_saisie','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'cpte_comptable': forms.TextInput(attrs={'class':'form-control'}),
            'Num_piece': forms.TextInput(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'Num_fact': forms.TextInput(attrs={'class':'form-control'}),
            'date_saisie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        super(updatChargeVarForm, self).__init__(*args, **kwargs)
    def clean_date(self):
        date = self.cleaned_data['date_saisie']
        formatted_date = date.strftime('%Y-%m-%d',)
        return formatted_date
  
class VisiteTechniqueForm(forms.ModelForm):
    date_proch = forms.DateField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = VisiteTechnique
        fields = ('date_proch','date_vis','montant','image','date_sortie',)
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_vis' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        } 
    def __init__(self, *args, **kwargs):
        super(VisiteTechniqueForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields["date_vis"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",) 

class UpdatVisiteTechniqueForm(forms.ModelForm):
    # date_proch = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Sélectionner une date...',
    #             'type': 'date'
    #         }
    #     ),
    #     input_formats=['%Y-%m-%d']  # format standard HTML5
    # )
    class Meta:
        model = VisiteTechnique
        fields = ('date_proch','date_vis','date_sortie','montant','image','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_vis' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_proch' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        } 
    def __init__(self, *args, **kwargs):
        super(UpdatVisiteTechniqueForm, self).__init__(*args, **kwargs)
        self.fields["date_vis"].input_formats = ("%Y-%m-%d",)
        self.fields["date_sortie"].input_formats = ("%Y-%m-%d",)
        self.fields["date_proch"].input_formats = ("%Y-%m-%d",)
        
class AssuranceForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    date_proch = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Assurance
        fields = ('date_saisie','date_proch','montant','image')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }

class UpdatAssuranceForm(forms.ModelForm):
    class Meta:
        model = Assurance
        fields = ('date_saisie','date_proch','montant','image')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_saisie' : forms.DateInput(attrs={'class':'form-control','type':'date'}, format='%Y-%m-%d'),
            'date_proch' : forms.DateInput(attrs={'class':'form-control','type':'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatAssuranceForm, self).__init__(*args, **kwargs)
        self.fields["date_saisie"].input_formats = ("%Y-%m-%d",)
        self.fields["date_proch"].input_formats = ("%Y-%m-%d",) 
        
class EntretienForm(forms.ModelForm):
    date_proch = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','placeholder':'Selection une date...', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Entretien
        fields = ('montant','date_Entret','date_proch','image','date_sortie')
        widgets = {
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_Entret' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(EntretienForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_Entret"].input_formats = ("%Y-%m-%dT%H:%M",) 

class UpdatEntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ('montant','date_sortie','date_Entret','date_proch','image','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'date_proch' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_Entret' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_sortie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatEntretienForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields["date_Entret"].input_formats = ("%Y-%m-%d",)
        self.fields["date_proch"].input_formats = ("%Y-%m-%d",) 

class ReparationForm(forms.ModelForm):
    class Meta:
        model = Reparation
        exclude = ('montant', "auteur", "vehicule")
        widgets = {
            'motif': forms.Select(attrs={'class':'form-control'}),
            'prestation': forms.NumberInput(attrs={'class':'form-control'}),
            'num_fich': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':'3'}),
            'date_entree' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg border p-5',
                'style': 'height: 100px; background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ddd 10px, #ddd 20px); text-align: center;',
            }),
        } 
    def __init__(self, *args, **kwargs):
        super(ReparationForm, self).__init__(*args, **kwargs)
        self.fields["date_entree"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",)   
 
class UpdatReparationForm(forms.ModelForm):
    class Meta:
        model = Reparation
        fields = ('date_entree','date_sortie','num_fich','description','montant','image','auteur')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'num_fich': forms.NumberInput(attrs={'class':'form-control'}),
            'identification': forms.Textarea(attrs={'class':'form-control','rows':'3'},),
            'date_entree' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
            'date_sortie' :DateInput(attrs={"type": "datetime-local","class":"form-control"}, format="%Y-%m-%dT%H:%M",),
        } 
    def __init__(self, *args, **kwargs):
        super(UpdatReparationForm, self).__init__(*args, **kwargs)
        self.fields["date_entree"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",)   

class PieceForm(forms.ModelForm):
    class Meta:
        model = Piece
        fields = ('libelle', 'montant', 'lieu', 'quantite')
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'lieu' :forms.Select(attrs={"class":"form-control"},),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),  
        }
PieceFormSet = inlineformset_factory(Reparation, Piece, form=PieceForm, extra=1, can_delete=True)
# Formset pour la modification : afficher les pièces existantes, suppression possible, pas d'ajout
PieceFormSetUpdate = inlineformset_factory(Reparation, Piece, form=PieceForm, extra=0, can_delete=True)

class PiecEchangeForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control','format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = PiecEchange
        fields = ('date_saisie',)

class LignePiecEchangeForm(forms.ModelForm):
    class Meta:
        model = LignePiecEchange
        fields = ["libelle", "lieu", "montant", "quantite"]
        widgets = {
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
            'lieu' :forms.Select(attrs={"class":"form-control"},),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),  
        }
# Formset lié à PiecEchange
LignePiecEchangeFormSet = inlineformset_factory(
    PiecEchange, LignePiecEchange, 
    form=LignePiecEchangeForm, 
    extra=1, can_delete=True
)

class UpdatPieceForm(forms.ModelForm):
    class Meta:
        model = Piece
        fields = ('libelle','montant','lieu')
        widgets = {
            'lieu': forms.Select(attrs={'class':'form-control'}),
            'montant': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'libelle': forms.TextInput(attrs={'class':'form-control'}),
        }

        
    # def __init__(self, *args, **kwargs):
    #     super(EntretienForm, self).__init__(*args, **kwargs)
    #     # input_formats to parse HTML5 datetime-local input to datetime field
    #     self.fields["date_sortie"].input_formats = ("%Y-%m-%dT%H:%M",)
    #     self.fields["date_Entret"].input_formats = ("%Y-%m-%dT%H:%M",) 