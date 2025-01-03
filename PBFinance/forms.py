from django import forms
from django.forms import DateInput
from .models import *

class PhotoForm(forms.ModelForm):
    date_saisie = forms.DateTimeField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Photo
        fields = ('title','image','date_saisie')
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
        }

class UpdatPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('title','image','date_saisie')
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'date_saisie' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        } 
    def __init__(self, *args, **kwargs):
        super(UpdatPhotoForm, self).__init__(*args, **kwargs)
        self.fields["date_saisie"].input_formats = ("%Y-%m-%d",)
    

class VideoForm(forms.ModelForm):
    date_saisie = forms.DateField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Video
        fields = ('title','video','date_saisie')
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
        }
        
class UpdatVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title','video','date_saisie')
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'date' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        } 
    def __init__(self, *args, **kwargs):
        super(UpdatVideoForm, self).__init__(*args, **kwargs)
        self.fields["date_saisie"].input_formats = ("%Y-%m-%d",)       
        
         
class EvenementForm(forms.ModelForm):
    date_saisie = forms.DateField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Evenement
        fields = ('auteur','title','image','text','date_saisie')
        widgets = {
            'auteur': forms.TextInput(attrs={'class':'form-control','value':'', 'id': 'elder','type':'hidden'}),
            #'auteur': forms.Select(attrs={'class':'form-control',}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'text': forms.Textarea(attrs={'class':'form-control','rows':'4'}),  
        }

class UpdatEvenementForm(forms.ModelForm):
    date_saisie= forms.DateField(widget= forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'format':'yyyy-mm-dd', 'type':'date'}))
    class Meta:
        model = Evenement
        fields = ('title','image','text','date_saisie')
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'text': forms.Textarea(attrs={'class':'form-control','rows':'4'}),
        }
    def __init__(self, *args, **kwargs):
        super(UpdatEvenementForm, self).__init__(*args, **kwargs)
        self.fields["date_saisie"].input_formats = ("%Y-%m-%d",)
        
        
        