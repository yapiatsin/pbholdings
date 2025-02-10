from datetime import date, datetime, timedelta, timezone
from typing import Any
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView,CreateView, UpdateView, TemplateView
from django.contrib import messages

from userauths.models import *
from .models import *
from .forms import *
from django.contrib.auth import logout
from django.db.models import Count
from django.db.models import Sum,F
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models.functions import Coalesce
# Create your views here.
from .forms import DateForm

from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
def temp_arr(request):
    # return render(request, 'perfect/dashboard.html')
    return render(request, 'perfect/tmp_arr.html')

def base(request):
    # return render(request, 'perfect/dashboard.html')
    return render(request, 'perfect/bases.html')

class ResumeView(TemplateView):
    template_name = 'pbent/resume_to_day.html'

class CarFluxView(TemplateView):
    model = Vehicule
    template_name = 'perfect/car_flux.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = Vehicule.objects.all()
        context={
            'vehicule':vehicule,
        }
        return context

class CarFluxDetailsView(DetailView):
    model = Vehicule
    form_class = DateForm
    template_name = 'perfect/car_flux.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        vehicule = Vehicule.objects.all()
        vehi = self.get_object()
    #-----------------------------------Pour Faire les filtre selon les dates entrées---------------------------------
        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_piece= Piece.objects.filter(reparation__in = total_reparation, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(reparation__in = list_reparation, date_saisie__range=[date_debut, date_fin])
            
            total_assurances = Assurance.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_patente = Patente.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_vignette = Vignette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin])
            
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
           
        else:
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(vehicule=vehi, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie=date.today())
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_var = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_admin = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(vehicule=vehi,date_saisie=date.today())
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(reparation__in = list_reparation,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(reparation__in = list_reparation,date_saisie=date.today())
            
            total_assurances = Assurance.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_patente = Patente.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_vignette = Vignette.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            
        context={
            'car':vehi,
            'vehicule':vehicule,
            'total_recettes':total_recettes,
            
            'total_charg':total_charg,
            'taux_marge_format':taux_marge_format,
            'taux_marge':taux_marge,
            'total_piece':total_piece,
            'list_piece':list_piece,
            
            'total_piec_echange':total_piec_echange,
            'list_piec_echange':list_piec_echange,
            
            'total_charg_fix':total_charg_fix,
            'list_charg_fix':list_charg_fix,
            
            'total_charg_var':total_charg_var,
            'list_charg_var':list_charg_var,
            
            'total_charg_admin':total_charg_admin,
            'list_charg_admin':list_charg_admin,
            
            'total_reparation':total_reparation,
            'list_reparation':list_reparation,
            
            'total_assurances':total_assurances,
            'list_assurance':list_assurance,
            
            'total_visite':total_visite,
            'list_visite':list_visite,
            
            'total_entretien':total_entretien,
            'list_entretien':list_entretien,
            
            'total_patente':total_patente,
            'list_patente':list_patente,
            
            'total_vignette':total_vignette,
            'list_vignette':list_vignette,
            
            'labels':label,
            'form':form,
            'dates':dates
        }
        return context
    
class Bilanday(TemplateView):
    form_class = DateForm
    template_name = 'perfect/bilan_day.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
#-----------------------------------Pour Faire les filtre selon les dates entrées---------------------------------
        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin])
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin])
            total_recettes = total_recettes_vtc + total_recettes_taxi
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_assurances = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_visite = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_entretien = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_patente = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_vignette = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_encaissement = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_encaissement = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_decaissement = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_decaissement = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
           
        else:
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC', date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC', date_saisie=date.today())
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI', date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI', date_saisie=date.today())
            total_recettes = total_recettes_vtc + total_recettes_vtc
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(date_saisie=date.today())
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(date_saisie=date.today())
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_var = ChargeVariable.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_admin = ChargeVariable.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie=date.today())
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(date_saisie=date.today())
            
            total_assurances = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(date_saisie=date.today())
            
            total_visite = VisiteTechnique.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(date_saisie=date.today())
            
            total_entretien = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(date_saisie=date.today())
            
            total_patente = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(date_saisie=date.today())
            
            total_vignette = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(date_saisie=date.today())
            
            total_encaissement = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_encaissement = Encaissement.objects.filter(date_saisie=date.today())
            
            total_decaissement = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_decaissement = Decaissement.objects.filter(date_saisie=date.today())
            
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            
        context={
            'total_recettes_taxi':total_recettes_taxi,
            'list_recettes_taxi':list_recettes_taxi,
            'total_recettes_vtc':total_recettes_vtc,
            'list_recettes_vtc':list_recettes_vtc,
            
            'total_recettes':total_recettes,
            'total_piece':total_piece,
            'list_piece':list_piece,
            
            'total_piec_echange':total_piec_echange,
            'list_piec_echange':list_piec_echange,
            
            'total_charg_fix':total_charg_fix,
            'list_charg_fix':list_charg_fix,
            
            'total_charg_var':total_charg_var,
            'list_charg_var':list_charg_var,
            
            'total_charg_admin':total_charg_admin,
            'list_charg_admin':list_charg_admin,
            
            'total_reparation':total_reparation,
            'list_reparation':list_reparation,
            
            'total_assurances':total_assurances,
            'list_assurance':list_assurance,
            
            'total_visite':total_visite,
            'list_visite':list_visite,
            
            'total_entretien':total_entretien,
            'list_entretien':list_entretien,
            
            'total_patente':total_patente,
            'list_patente':list_patente,
            
            'total_vignette':total_vignette,
            'list_vignette':list_vignette,
            
            'total_encaissement':total_encaissement,
            'list_encaissement':list_encaissement,
            
            'total_decaissement':total_decaissement,
            'list_decaissement':list_decaissement,
            
            'labels':label,
            'form':form,
            'dates':dates
        }
        return context
    
from calendar import monthrange
class TableaustopView(TemplateView):
    model = Vehicule
    template_name = "perfect/temp_arret.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get month and year from the request; default to the current month and year
        month = self.request.GET.get('month', timezone.now().month)
        year = self.request.GET.get('year', timezone.now().year)
        # Convert month and year to integers
        month = int(month)
        year = int(year)
        days_in_month = monthrange(year, month)[1]
        month_name = datetime(year, month, 1).strftime("%B")
        # vehicules = Vehicule.objects.all()
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        context['current_date'] = date.today()
        total_actions_sum = 0
        total_cost_parts_sum = 0
        total_income_sum = 0
        total_piece_sum = 0
        
        total_visit_sum = 0
        total_panne_sum = 0
        total_accident_sum = 0
        total_autrarret_sum = 0
        
        total_visitechique_sum = 0 
        total_entretien_sum = 0 
        
        total_repairs_by_motifs = 0 
        total_motif_arrets = 0 
        
        vehicule_data = []
        for vehicule in vehicules:
            total_actions = (
                Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Visite", date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Panne", date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            )
            total_cost_parts = Piece.objects.filter(
                reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).aggregate(total_cost=models.Sum('montant'))['total_cost'] or 0

            total_income = Recette.objects.filter(
                vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).aggregate(total_income=models.Sum('montant'))['total_income'] or 0

            part_details_queryset = Piece.objects.filter(
                reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).values('libelle').annotate(count=models.Count('libelle'), total_price=models.Sum('montant'))
            
            all_piece = Piece.objects.filter(reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            all_visitechnique = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            all_entretien = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()

            part_details = "; ".join(
                f"{part['libelle']} ({part['count']}) {part['total_price']}" for part in part_details_queryset
            )

            daily_actions = [0] * days_in_month
            for day in range(1, days_in_month + 1):
                for model in [Reparation, VisiteTechnique, Entretien, Autrarret]:
                    count = model.objects.filter(
                        vehicule=vehicule, date_saisie__day=day, date_saisie__month=month, date_saisie__year=year
                    ).count()
                    daily_actions[day - 1] += count
            
            repairs_by_motif = {
                'P-vis': Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count(),
                'pan': Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count(),
                'acc': Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count(),
            }
            total_repairs_by_motif = (
                Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count()+
                Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count()+
                Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            )
            motif_arret = {
                'vis': VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie__month=month, date_saisie__year=year).count(),
                'ent': Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count(),
                'aut': Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count(),
            }
            total_motif_arret = (
                VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie__month=month, date_saisie__year=year).count()+
                Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()+
                Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            )
            total_repairs_by_motifs += total_repairs_by_motif
            total_motif_arrets += total_motif_arret 
            
            all_rep_visit = Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count()
            all_rep_panne = Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count()
            all_rep_accident = Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            all_autre_arret = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            
            vehicule_data.append({
                'immatriculation': vehicule.immatriculation,
                'marque': vehicule.marque,
                'total_actions': total_actions,
                'total_cost_parts': total_cost_parts,
                'total_income': total_income,
                'part_details': part_details,
                'daily_actions': daily_actions,
                'repairs_by_motif': repairs_by_motif,
                'motif_arret': motif_arret,
            })
            total_actions_sum += total_actions
            total_cost_parts_sum += total_cost_parts
            total_income_sum += total_income
            total_piece_sum += all_piece
    
            total_visitechique_sum += all_visitechnique
            total_entretien_sum += all_entretien
    
            total_visit_sum += all_rep_visit
            total_panne_sum += all_rep_panne
            total_accident_sum += all_rep_accident
            total_autrarret_sum += all_autre_arret
    
        context['vehicule_data'] = vehicule_data
        
        context['total_repairs_by_motifs'] = total_repairs_by_motifs
        context['total_motif_arrets'] = total_motif_arrets
        
        context['total_visit_sum'] = total_visit_sum
        context['total_panne_sum'] = total_panne_sum
        context['total_accident_sum'] = total_accident_sum
        context['total_autrarret_sum'] = total_autrarret_sum
        
        context['total_visitechique_sum'] = total_visitechique_sum
        context['total_entretien_sum'] = total_entretien_sum
        
        context['total_actions_sum'] = total_actions_sum
        context['total_cost_parts_sum'] = total_cost_parts_sum
        context['total_income_sum'] = total_income_sum
        context['total_piece_sum'] = total_piece_sum
        
        context['days_in_month'] = range(1, days_in_month + 1)
        context['month_name'] = month_name
        context['month'] = month
        context['year'] = year
        context['years'] = range(timezone.now().year - 4, timezone.now().year + 1)
        context['month_range'] = range(1, 13)
        context['days_in_month_plus_two'] = days_in_month + 2
        return context

class SuiviFinancierView(TemplateView):
    model = Vehicule
    template_name = 'news/applist/suivie_financier_vehi.html' 
    context_object_name = 'vehicule'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        user_group = self.request.user.groups.first() 
        context['user_group'] = user_group.name if user_group else None 
        all_vehicule = Vehicule.objects.all() 
        resultat_vehicule = [] 
        form = DateForm(self.request.GET) 
        if form.is_valid(): 
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            if all_vehicule: 
                for vehicule in all_vehicule: 
                    recettes = Recette.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 1
                    charge_fix = ChargeFixe.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    charge_var = ChargeVariable.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    
                    Total_charge = charge_fix + charge_var
                    marg_contr = recettes - charge_var
                    taux_marge = (marg_contr*100/(recettes))
                    taux_marge_format ='{:.2f}'.format(taux_marge)
                    resultat = recettes-Total_charge
                    reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicule)
                    context['som_piece'] = Piece.objects.filter(date_achat__range=[date_debut, date_fin],reparation__in = reparations).aggregate(total_piece=Sum('cout'))['total_piece'] or 0
                    resultat_vehicule.append({'vehicule': vehicule, 'recettes':recettes, 'charge_fix':charge_fix, 'charge_var':charge_var, 'Total_charge':Total_charge, 'marg_contr':marg_contr, 'taux_marge_format':taux_marge_format, 'resultat': resultat, 'som_piece':context['som_piece'] or 0 })
            else:
                charge_fix =0
                charge_var =0
                Total_charge = 0
                marg_contr = 0
                taux_marge_format = 0
                resultat = 0
                marg_contr = 0
                resultat_vehicule = 0
                recettes = 0
        else:
            if all_vehicule:
                for vehicule in all_vehicule:
                    recettes = Recette.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 1
                    charge_fix = ChargeFixe.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    charge_var = ChargeVariable.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0

                    Total_charge = charge_fix + charge_var
                    marg_contr = recettes - charge_var
                    taux_marge = (marg_contr*100/(recettes))
                    taux_marge_format ='{:.2f}'.format(taux_marge)
                    resultat = recettes-Total_charge
                    reparations = Reparation.objects.filter(vehicule = vehicule)
                    context['som_piece'] = Piece.objects.filter(reparation__in = reparations).aggregate(total_piece=Sum('cout'))['total_piece'] or 0
                    resultat_vehicule.append({'vehicule': vehicule, 'recettes':recettes, 'charge_fix':charge_fix, 'charge_var':charge_var, 'Total_charge':Total_charge, 'marg_contr':marg_contr, 'taux_marge_format':taux_marge_format, 'resultat': resultat, 'som_piece':context['som_piece'] or 0 })
            else:
                charge_fix =0
                charge_var =0
                Total_charge = 0
                marg_contr = 0
                taux_marge_format = 0
                resultat = 0
                marg_contr = 0
                resultat_vehicule = 0
                recettes = 0
        #context['som_piece'] = som_piece 
        context['catego_vehi'] = CategoVehi.objects.all()
        context['charge_fix'] = charge_fix
        context['charge_var'] = charge_var
        context['Total_charge'] = Total_charge
        context['marg_contr'] = marg_contr
        context['taux_marge_format'] = taux_marge_format
        context['resultat'] = resultat
        context['resultat_vehicule'] = resultat_vehicule
        context['all_vehicule'] = all_vehicule
        context['total_recet_verse'] = recettes
        context['form'] = form
        return context

from calendar import SUNDAY
from django.db.models import Sum
from django.utils.timezone import now
class MyRecetteView(TemplateView):
    template_name = "perfect/myrecette.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenir la date actuelle
        today = now().date()
        month = self.request.GET.get('month', today.month)
        year = self.request.GET.get('year', today.year)
        month = int(month)
        year = int(year)
        days_in_month = monthrange(year, month)[1]
        month_name = datetime(year, month, 1).strftime("%B")
        # Calculer les dimanches dans le mois
        dimanches = [
            day for day in range(1, days_in_month + 1)
            if datetime(year, month, day).weekday() == SUNDAY
        ]
        jours_ouvrables = days_in_month - len(dimanches)
        
        # Initialisation des variables
        vehicules = Vehicule.objects.select_related('category').all()
        recette_details = []
        # Totaux cumulés
        total_recette_mensuelle = 0
        total_recette_annuelle = 0
        sum_recets_jours = 0
        sum_difference_mensuelle = 0
        sum_recettes_vehicule_mois = 0
        sum_difference = 0
        sum_motif_arrets = 0
        
        for vehicule in vehicules:
            # Recette journalière
            recettes_vehicule_jour = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie=date.today()
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette mensuelle
            recettes_vehicule_mois = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie__month=month,
                date_saisie__year=year
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette annuelle
            recettes_vehicule_an = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie__year=year
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette par défaut de la catégorie
            recette_defaut = vehicule.category.recette_defaut
            # Calcul de la recette mensuelle attendue sans dimanches
            recette_attendue_mensuelle = recette_defaut * jours_ouvrables
            # Calcul de la différence pour aujourd'hui
            difference = recettes_vehicule_jour - recette_defaut
            difference_mensuelle = recettes_vehicule_mois - recette_attendue_mensuelle
            sum_difference_mensuelle += difference_mensuelle
            sum_recettes_vehicule_mois += recettes_vehicule_mois
            sum_difference += difference
            
            motif_arrets = {
                'vis': VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie=date.today()).count(),
                'ent': Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).count(),
                'rep': Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).count(),
            }
            visite = VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie=date.today()).count()
            entretien = Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).count()
            reparation = Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).count()
            som_des_motifs = visite+entretien+reparation
            
            sum_motif_arrets += som_des_motifs
            
            sum_recets_jours += recettes_vehicule_jour
            
            daily_actions = [0] * days_in_month
            for day in range(1, days_in_month + 1):
                for model in [Recette]:
                    motant = model.objects.filter(
                        vehicule=vehicule, date_saisie__day=day, date_saisie__month=month, date_saisie__year=year
                    ).aggregate(somme=Sum('montant'))['somme'] or 0
                    daily_actions[day - 1] += motant
            # Ajouter les détails journaliers au contexte
            recette_details.append({
                'vehicule': vehicule.immatriculation,
                'marque': vehicule.marque,
                'recette_versee': recettes_vehicule_jour,
                'recette_attendue': recette_defaut,
                'daily_actions': daily_actions,
                'difference': difference,
                'difference_mensuelle': difference_mensuelle,
                'recette_mensuelle': recettes_vehicule_mois,
                'recette_annuelle': recettes_vehicule_an,
                'motif_arrets': motif_arrets,
            })
            
        catevtc = CategoVehi.objects.filter(category='VTC').first()
        catetaxi = CategoVehi.objects.filter(category='TAXI').first()
        recette_vtc_attendue = catevtc.recette_defaut * jours_ouvrables if catevtc else 0
        recette_taxi_attendue = catetaxi.recette_defaut * jours_ouvrables if catetaxi else 0
        
        context['sum_motif_arrets'] = sum_motif_arrets
        context['sum_difference'] = sum_difference
        context['sum_recettes_vehicule_mois'] = sum_recettes_vehicule_mois
        context['sum_difference_mensuelle'] = sum_difference_mensuelle
        context['sum_recets_jours'] = sum_recets_jours
        context['recette_details'] = recette_details
        context['recette_vtc_attendue'] = recette_vtc_attendue
        context['recette_taxi_attendue'] = recette_taxi_attendue
        context['total_recette_mensuelle'] = total_recette_mensuelle
        context['total_recette_annuelle'] = total_recette_annuelle
        context['current_date'] = today
        context['days_in_month'] = range(1, days_in_month + 1)
        context['month_name'] = month_name
        context['month'] = month
        context['year'] = year
        context['years'] = range(today.year - 4, today.year + 1)
        context['month_range'] = range(1, 13)
        context['days_in_month_plus_two'] = days_in_month + 2
        return context
    
class DashboardView(TemplateView):
    template_name = 'perfect/dashboard.html'
    form_class = DateForm
    timeout_minutes = 600
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().post(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        vehicules = Vehicule.objects.all()
#-----------------------------------Pour Faire les filtre selon les dates entrées---------------------------------
        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_vtc_format ='{:,}'.format(total_recettes_vtc).replace('',' ')
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_taxi_format ='{:,}'.format(total_recettes_taxi).replace('',' ')
            
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            
            ################################----Graphiques----#############################
            recet_data_vtc = Recette.objects.filter(vehicule__category__category ='VTC', date_saisie__range=[date_debut, date_fin])
            recet_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_vtc:
                recet_mois_vtc_data[commande.date_saisie.month] += commande.montant
            recet_mois_vtc_data = [recet_mois_vtc_data[month] for month in range(1, 13)]
            
            recet_data_taxi = Recette.objects.filter(vehicule__category__category ='TAXI', date_saisie__range=[date_debut, date_fin])
            recet_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_taxi:
                recet_mois_taxi_data[commande.date_saisie.month] += commande.montant
            recet_mois_taxi_data = [recet_mois_taxi_data[month] for month in range(1, 13)]
            
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
            chargfix_vtc_data = ChargeFixe.objects.filter(vehicule__category__category ='VTC', date_saisie__range=[date_debut, date_fin])
            chargfix_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_vtc_data:
                chargfix_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_vtc_data = [chargfix_mois_vtc_data[month] for month in range(1, 13)]
            
            chargfix_taxi_data = ChargeFixe.objects.filter(vehicule__category__category ='TAXI', date_saisie__range=[date_debut, date_fin])
            chargfix_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_taxi_data:
                chargfix_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_taxi_data = [chargfix_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            chargvar_vtc_data = ChargeVariable.objects.filter(vehicule__category__category ='VTC',date_saisie__range=[date_debut, date_fin])
            chargvar_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_vtc_data:
                chargvar_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_vtc_data = [chargvar_mois_vtc_data[month] for month in range(1, 13)]
            
            chargvar_taxi_data = ChargeVariable.objects.filter(vehicule__category__category ='TAXI',date_saisie__range=[date_debut, date_fin])
            chargvar_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_taxi_data:
                chargvar_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_taxi_data = [chargvar_mois_taxi_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            recet_taux_data = {month: 0 for month in range(1, 13)}
            chargvar_taux_data = {month: 0 for month in range(1, 13)}
            marge_data_vtc = [recet_mois_vtc_data[i] - chargvar_mois_data[i] for i in range(12)]
            taux_data_vtc = [(marge_data_vtc[i] * 100) / recet_mois_vtc_data[i] if recet_mois_vtc_data[i] > 0 else 0 for i in range(12)]
            
            ################################TAXI################################
            marge_data_taxi = [recet_mois_taxi_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data_taxi = [(marge_data_taxi[i] * 100) / recet_mois_taxi_data[i] if recet_mois_taxi_data[i] > 0 else 0 for i in range(12)]
            #########################################---Meilleur---####################################
            marge_contri = []
            all_vehicule = Vehicule.objects.all()[:6]
            all_recettes = Recette.objects.all()[:6]
            best_recets = []
            best_marge = []
            best_taux = []
            for vehicule in all_vehicule:
                recs = Recette.objects.filter(vehicule=vehicule,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
                rece_all = recs if recs is not None else 0
                charges_variables = ChargeVariable.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
                chargvari_all = charges_variables if charges_variables is not None else 0
                marge_cont = rece_all - chargvari_all
                marge = marge_cont if marge_cont is not None else 0
                if rece_all == 0:
                    taux=0
                else:
                    taux = round((marge*100)/rece_all,2)
                    taux = taux if taux is not None else 0
                    
                best_taux.append({'vehicule': vehicule, 'taux':taux})
                best_marge.append({'vehicule': vehicule, 'marge_cont':marge_cont})
                best_recets.append({'vehicule': vehicule, 'recs':recs})
            best_marge = sorted([x for x in best_marge if x['marge_cont'] is not None], key=lambda x: x['marge_cont'], reverse=True)[:5] 
            best_taux = sorted(best_taux, key=lambda x: x['taux'], reverse=True)[:5]  
            best_recets = sorted([x for x in best_recets if x['recs'] is not None], key=lambda x: x['recs'], reverse=True)[:5]
            
        else:
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category="VTC",date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_vtc_format ='{:,}'.format(total_recettes_vtc).replace('',' ')
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category="TAXI",date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_taxi_format ='{:,}'.format(total_recettes_taxi).replace('',' ')
            
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################-----#----Pieces echanges----#-----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            
            ################################----Graphiques----#############################
            recet_data_vtc = Recette.objects.filter(vehicule__category__category="VTC", date_saisie__year=datetime.now().year)
            recet_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_vtc:
                recet_mois_vtc_data[commande.date_saisie.month] += commande.montant
            recet_mois_vtc_data = [recet_mois_vtc_data[month] for month in range(1, 13)]
            
            recet_data_taxi = Recette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__year=datetime.now().year)
            recet_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_taxi:
                recet_mois_taxi_data[commande.date_saisie.month] += commande.montant
            recet_mois_taxi_data = [recet_mois_taxi_data[month] for month in range(1, 13)]
            
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__year=datetime.now().year)
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__year=datetime.now().year)
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(date_saisie__year=datetime.now().year)
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            ###########################################################################################################################################################
            
            chargfix_vtc_data = ChargeFixe.objects.filter(vehicule__category__category ='VTC', date_saisie__year=datetime.now().year)
            chargfix_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_vtc_data:
                chargfix_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_vtc_data = [chargfix_mois_vtc_data[month] for month in range(1, 13)]
            
            chargfix_taxi_data = ChargeFixe.objects.filter(vehicule__category__category ='TAXI', date_saisie__year=datetime.now().year)
            chargfix_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_taxi_data:
                chargfix_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_taxi_data = [chargfix_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            chargvar_vtc_data = ChargeVariable.objects.filter(vehicule__category__category ='VTC',date_saisie__year=datetime.now().year)
            chargvar_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_vtc_data:
                chargvar_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_vtc_data = [chargvar_mois_vtc_data[month] for month in range(1, 13)]
            
            chargvar_taxi_data = ChargeVariable.objects.filter(vehicule__category__category ='TAXI',date_saisie__year=datetime.now().year)
            chargvar_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_taxi_data:
                chargvar_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_taxi_data = [chargvar_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            
            recet_taux_data = {month: 0 for month in range(1, 13)}
            chargvar_taux_data = {month: 0 for month in range(1, 13)}
            
            ################################VTC################################
            marge_data_vtc = [recet_mois_vtc_data[i] - chargvar_mois_data[i] for i in range(12)]
            taux_data_vtc = [(marge_data_vtc[i] * 100) / recet_mois_vtc_data[i] if recet_mois_vtc_data[i] > 0 else 0 for i in range(12)]
            
            ################################TAXI################################
            marge_data_taxi = [recet_mois_taxi_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data_taxi = [(marge_data_taxi[i] * 100) / recet_mois_taxi_data[i] if recet_mois_taxi_data[i] > 0 else 0 for i in range(12)]
            #########################################---Meilleur---####################################
            marge_contri = []
            all_vehicule = Vehicule.objects.all()[:6]
            all_recettes = Recette.objects.all()[:6]
            best_recets = []
            best_marge = []
            best_taux = []
            for vehicule in all_vehicule:
                recs = Recette.objects.filter(vehicule=vehicule,date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
                rece_all = recs if recs is not None else 0
                charges_variables = ChargeVariable.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
                chargvari_all = charges_variables if charges_variables is not None else 0
                marge_cont = rece_all - chargvari_all
                marge = marge_cont if marge_cont is not None else 0
                if rece_all == 0:
                    taux=0
                else:
                    taux = round((marge*100)/rece_all,2)
                    taux = taux if taux is not None else 0
                best_taux.append({'vehicule': vehicule, 'taux':taux})
                best_marge.append({'vehicule': vehicule, 'marge_cont':marge_cont})
                best_recets.append({'vehicule': vehicule, 'recs':recs})
            best_marge = sorted([x for x in best_marge if x['marge_cont'] is not None], key=lambda x: x['marge_cont'], reverse=True)[:5] 
            best_taux = sorted(best_taux, key=lambda x: x['taux'], reverse=True)[:5]  
            best_recets = sorted([x for x in best_recets if x['recs'] is not None], key=lambda x: x['recs'], reverse=True)[:5]

        context={
            'tot_recets':total_recette_format,
            'total_recette_taxi_format':total_recette_taxi_format,
            'total_recette_vtc_format':total_recette_vtc_format,
            
            'vehicules':vehicules,
            'tot_piece':total_piece_format,
            'tot_piec_echang':total_piece_echang_format,
            'tot_chargfix':total_chargfix_format,
            'tot_chargvar':total_chargvar_format,
            'charge_totale':total_charge_format,
            'marge_brute_format':marge_brute_format,
            'taux_marge':taux_marge_format,
            'best_recettes':best_recets,
            'bests_taux':best_taux,
            'mois':libelle_mois_en_cours,
            
            #################---###############-----Graphiq-----#################---###############
            'recet_mois_vtc_data':recet_mois_vtc_data,
            'recet_mois_taxi_data':recet_mois_taxi_data,
            
            'chargevar_data':chargvar_mois_data,
            
            'taux_data_vtc':taux_data_vtc,
            'taux_data_taxi':taux_data_taxi,
            
            'chargvar_mois_taxi_data':chargvar_mois_taxi_data,
            'chargvar_mois_vtc_data':chargvar_mois_vtc_data,
            
            'chargfix_mois_taxi_data':chargfix_mois_taxi_data,
            'chargfix_mois_vtc_data':chargfix_mois_vtc_data,
            
            'piecha_mois_vtc_data':piecha_mois_vtc_data,
            'piec_mois_vtc_data':piec_mois_vtc_data,
            'piecha_mois_taxi_data':piecha_mois_taxi_data,
            'piec_mois_taxi_data':piec_mois_taxi_data,
            
            'labels':label,
            'form':form,
            'dates':dates
        }
        return context
    
class BilletageView(CreateView):
    model = Billetage
    form_class = BilletageForm
    template_name = 'perfect/caisse.html'
    success_message = 'Saisie enrégistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('billetage')
    timeout_minutes = 230
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        form = self.get_form()
        forms = DatebilanForm(self.request.GET)
        if forms.is_valid():
            date_bilan = forms.cleaned_data['date_bilan']
            encaisser = Encaissement.objects.filter(date_saisie=date_bilan)
            decaisser = Decaissement.objects.filter(date_saisie=date_bilan)
            solde_jour = SoldeJour.objects.filter(date_saisie=date_bilan).aggregate(Sum('montant'))['montant__sum'] or 0
            # Calculer le total des encaissements pour la journée actuelle
            tot_entree = Encaissement.objects.filter(date_saisie=date_bilan).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sortie = Decaissement.objects.filter(date_saisie=date_bilan).aggregate(somme=Sum('montant'))['somme'] or 0
            
            solde_initial = None
            # Vérifier le solde des 3 derniers jours, en commençant par hier
            for i in range(1, 4):
                solde_temp = SoldeJour.objects.filter(date_saisie=date_bilan - timedelta(days=i)).first()
                if solde_temp:
                    solde_initial = solde_temp.montant
                    break
                
            # Si aucun solde trouvé dans les 3 derniers jours, utiliser le premier solde initial enregistré
            if not solde_initial:
                solde_initial_record = SoldeJour.objects.filter(date_saisie=date_bilan - timedelta(days=1)).first()
                solde_initial = solde_initial_record.montant if solde_initial_record else 0
                
            som_entree = tot_entree + solde_initial
            solde_fin_journee = som_entree - tot_sortie
            
            som_billets = Billetage.objects.filter(type='Billet', date_saisie=date_bilan).aggregate(somme=Sum('valeur'))['somme'] or 0
            
            som_pieces = Billetage.objects.filter(type='Pièce', date_saisie=date_bilan).aggregate(somme=Sum('valeur'))['somme'] or 0
            som_billets = som_billets
            som_pieces = som_pieces

            bill = Billetage.objects.filter(type='Billet', date_saisie=date_bilan)
            bil = []
            som_tot_bil = 0
            for b in bill:
                val = b.valeur
                nb = b.nombre
                res = b.valeur * b.nombre
                som_tot_bil += res or 0
                bil.append({'val': val, 'nb':nb,'res':res})
            som_tot_bil = som_tot_bil
            bil = bil

            piece = Billetage.objects.filter(type='Pièce', date_saisie=date_bilan)
            pie = []
            som_tot_piec = 0
            for p in piece:
                val = p.valeur or 0
                nb = p.nombre or 0
                res = p.valeur * p.nombre
                som_tot_piec += res or 0
                pie.append({'val': val, 'nb':nb,'res':res})
            som_tot_piec = som_tot_piec
            pie = pie
            
            Total_piec_bill = som_tot_piec + som_tot_bil
            ecart = solde_fin_journee - Total_piec_bill
            self.request.user.save()
            
        else:
            encaisser = Encaissement.objects.filter(date_saisie=date.today())
            decaisser = Decaissement.objects.filter(date_saisie=date.today())
            solde_jour = SoldeJour.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            # Calculer le total des encaissements pour la journée actuelle
            tot_entree = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sortie = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            solde_initial = None

            # Vérifier le solde des 3 derniers jours, en commençant par hier
            for i in range(1, 4):
                solde_temp = SoldeJour.objects.filter(date_saisie=date.today() - timedelta(days=i)).first()
                if solde_temp:
                    solde_initial = solde_temp.montant
                    break
            # Si aucun solde trouvé dans les 3 derniers jours, utiliser le premier solde initial enregistré
            if not solde_initial:
                solde_initial_record = SoldeJour.objects.filter(date_saisie=date.today() - timedelta(days=1)).first()
                solde_initial = solde_initial_record.montant if solde_initial_record else 0
            som_entree = tot_entree + solde_initial
            solde_fin_journee = som_entree - tot_sortie
            
            som_billets = Billetage.objects.filter(type='Billet', date_saisie=date.today()).aggregate(somme=Sum('valeur'))['somme'] or 0
            nb_bill = Billetage.objects.filter(type='Billet', date_saisie=date.today()).count() 

            som_pieces = Billetage.objects.filter(type='Pièce', date_saisie=date.today()).aggregate(somme=Sum('valeur'))['somme'] or 0
            som_billets = som_billets
            som_pieces = som_pieces

            bill = Billetage.objects.filter(type='Billet', date_saisie=date.today())
            bil = []
            som_tot_bil = 0
            for b in bill:
                val = b.valeur
                nb = b.nombre
                res = b.valeur * b.nombre
                som_tot_bil += res or 0
                bil.append({'val': val, 'nb':nb,'res':res})
            som_tot_bil = som_tot_bil
            bil = bil

            piece = Billetage.objects.filter(type='Pièce', date_saisie=date.today())
            pie = []
            som_tot_piec = 0
            for p in piece:
                val = p.valeur or 0
                nb = p.nombre or 0
                res = p.valeur * p.nombre
                som_tot_piec += res or 0
                pie.append({'val': val, 'nb':nb,'res':res})
            som_tot_piec = som_tot_piec
            pie = pie
            
            Total_piec_bill = som_tot_piec + som_tot_bil
            ecart = solde_fin_journee - Total_piec_bill

            self.request.user.save()
            
        context={
            'forms':forms,
            'solde_initial':solde_initial,
            
            'ent':encaisser,
            'sort':decaisser,
            'ecart':ecart,
            
            'piecs':pie,
            'biels':bil,
            
            'sompiecs':som_tot_piec,
            'sombiels':som_tot_bil ,
            
            'tot_ent':tot_entree,
            'tot_sor':tot_sortie,
            'form':form,
            
            'solde_day':solde_jour,
            'tot_bi_pi':Total_piec_bill,
            'dates':dates,
        }
        return context

class AddDecaissementView(CreateView):
    model = Decaissement
    form_class = DecaissementForm
    template_name = 'perfect/sortie_caiss.html'
    success_message = 'Sortie de caisse enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('add_decaisse')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today = date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            sortie_liste = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin])  
            
            result_filtre = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_jour = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_mois = Decaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_annuel = Decaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
              
        else:
            sortie_liste = Decaissement.objects.filter(date_saisie=date.today())  
            result_filtre = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            tot_sort_jour = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_mois =  Decaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_annuel = Decaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
        context = {
            'form': form,
            'forms': forms,
            'tot_sort_jours': tot_sort_jour,
            'tot_sort_mois': tot_sort_mois,
            'tot_sort_annuel': tot_sort_annuel,
            'sorties_liste': sortie_liste,
            'resuults_filtre': result_filtre,
            
            'dates': today,
            'mois': libelle_mois_en_cours,
            'mois': libelle_mois_en_cours,
            'annee': annee_en_cours,
        }
        return context

def delete_sortie_caisse(request, pk):
    try:
        decaissements = get_object_or_404(Decaissement, id=pk)
        decaissements.delete()
        messages.success(request, f"la sortie de caisse de {decaissements.Num_piece} - {decaissements.libelle} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_decaisse')

class UpdatDecaissementView(UpdateView):
    model = Decaissement
    form_class = UpdatDecaissementForm
    template_name = 'news/appl/updat_decaissement.html'
    success_message = 'Sortir de caisse Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('list_decaissement')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context


class AddEncaissementView(CreateView):
    model = Encaissement
    form_class = EncaissementForm
    template_name = 'perfect/entre_caiss.html'
    success_message = 'Entrée de caisse enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('addencaisse')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today =date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            enter_liste = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin])  
            result_filtre = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
    
            tot_entre_jour = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_mois = Encaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_annuel = Encaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
              
        else:
            enter_liste = Encaissement.objects.filter(date_saisie=date.today())  
            result_filtre = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            tot_entre_jour = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_mois = Encaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_annuel = Encaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
        context = {
            'form': form,
            'tot_entre_jours': tot_entre_jour,
            'tot_entre_mois': tot_entree_mois,
            'tot_entre_annuel': tot_entree_annuel,
            'enters_liste': enter_liste,
            'resuults_filtre': result_filtre,
            
            'dates': today,
            'mois': libelle_mois_en_cours,
            'mois': libelle_mois_en_cours,
            'annee': annee_en_cours,
            'forms': forms,
        }
        return context
    
def delete_entre_caisse(request, pk):
    try:
        encaissements = get_object_or_404(Encaissement, id=pk)
        encaissements.delete()
        messages.success(request, f"l'entrée de caisse de {encaissements.Num_piece} - {encaissements.libelle} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addencaisse')

class AddSoldeJourView(CreateView):
    model = SoldeJour
    form_class = Solde_JourForm
    template_name = 'perfect/solde.html'
    success_message = 'le solde de la journée a été enregistré avec succès.👍✓✓'
    error_message = "Un solde existe deja pour cette journée ✘✘ "
    success_url = reverse_lazy ('add_solde')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        # Vérifie si un solde existe déjà pour la date spécifiée
        date = form.cleaned_data['date_saisie']
        messages.success(self.request, self.success_message)
        solde_exist = SoldeJour.objects.filter(date_saisie=date).exists()
        if solde_exist:
            # Si un solde existe déjà pour cette date, renvoie une erreur
            form.add_error('date', 'Un solde existe déjà pour cette date.')
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            solde_liste = SoldeJour.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            solde_liste = SoldeJour.objects.filter(date_saisie__month=date.today().month).order_by('-id')
        context = {
            'form': form,
            'soldes_liste': solde_liste,
            'forms': forms,
        }
        return context
 
def delete_solde(request, pk):
    try:
        solde = get_object_or_404(SoldeJour, id=pk)
        solde.delete()
        messages.success(request, f"le solde de la journee du {solde.date_saisie} - {solde.montant} frscfa a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_solde')
   
class UpdatEncaissementView(UpdateView):
    model = Encaissement
    form_class = UpdatEncaissementForm
    template_name = 'news/appl/updat_encaissement.html'
    success_message = 'Entrée de caisse Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('list_encaissement')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context
    
from django.core.mail import send_mail
class GestionalerteView(TemplateView):                                                                          
    template_name = 'perfect/alerte.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def send_alert_email(self, vehicle_reference, alert_types):
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Vérifie si l'alerte a déjà été envoyée aujourd'hui
        last_sent_alerts = self.request.session.get('last_sent_alerts', {})
        if last_sent_alerts.get(vehicle_reference) == today_date:
            return  
        # Si une alerte a déjà été envoyée aujourd'hui, on quitte la fonction
        
        # Formater les types d'alertes pour le message
        alert_message = ", ".join(alert_types)
        subject = "Alerte : Maintenance du véhicule requise"
        message = (
            f"Le véhicule avec l'immatriculation {vehicle_reference} requiert une attention pour : {alert_message}. "
            "Veuillez vérifier les alertes associées."
        )
        recipient_list = ['sorothodaniel@gmail.com', 'yapiatsin0@gmail.com']
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        
        # Mettre à jour la session pour éviter un envoi multiple le même jour
        last_sent_alerts[vehicle_reference] = today_date
        self.request.session['last_sent_alerts'] = last_sent_alerts
        
    def get_context_data(self,*args, **kwargs):  
        context = super().get_context_data(*args,**kwargs)  
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        resultat_vehicule = []
        alert_color = " "
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            assu_all = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            entretiens = Entretien.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            visites = VisiteTechnique.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            reparations = Reparation.objects.filter(Q(date_saisie__lte=now) & Q(date_sortie__gte=now)).count()
            assurances = Assurance.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()

            vignette = Vignette.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                
            patente = Patente.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                 
            cartstation = Stationnement.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()
            
            
            for vehicule in vehicules:
                visite = VisiteTechnique.objects.filter(vehicule = vehicule).order_by('date_saisie')
                entretien = Entretien.objects.filter(vehicule = vehicule).order_by('date_saisie')
                assurances = Assurance.objects.filter(vehicule = vehicule).order_by('date_saisie')
                vignettes = Vignette.objects.filter(vehicule = vehicule).order_by('date_saisie')
                patentes = Patente.objects.filter(vehicule = vehicule).order_by('date_saisie')
                cartstaions = Stationnement.objects.filter(vehicule = vehicule).order_by('date_saisie')

                jours_cartsta_restant = cartstaions
                if jours_cartsta_restant:
                    for cartstaion in jours_cartsta_restant:
                        jours_cartsta_restant = cartstaion.jours_cartsta_restant
                        alert_cartsta_color = 'red' if jours_cartsta_restant <=10 else 'orange' if jours_cartsta_restant < 30 else 'green'
                else: 
                    jours_cartsta_restant = "0"    
                    alert_cartsta_color = "#e0e7eb"
                # 
                jours_pate_restant = patentes
                if jours_pate_restant:
                    for patente in jours_pate_restant:
                        jours_pate_restant = patente.jours_pate_restant
                        alert_pate_color = 'red' if jours_pate_restant <=10 else 'orange' if jours_pate_restant < 30 else 'green'
                else: 
                    jours_pate_restant = "0"    
                    alert_pate_color = "#e0e7eb"
                    # 
                jours_vign_restant = vignettes
                if jours_vign_restant:
                    for vignette in jours_vign_restant:
                        jours_vign_restant = vignette.jours_vign_restant
                        alert_vign_color = 'red' if jours_vign_restant <=10 else 'orange' if jours_vign_restant < 334 else 'green'
                else: 
                    jours_vign_restant = "0"    
                    alert_vign_color = "#e0e7eb"
                    # 
                jours_assu_restant = assurances
                if jours_assu_restant:
                    for assurance in jours_assu_restant:
                        jours_assu_restant = assurance.jours_assu_restant
                        alert_assu_color = 'red' if jours_assu_restant <=7 else 'orange' if jours_assu_restant < 15 else 'green'
                else: 
                    jours_assu_restant = "0"    
                    alert_assu_color = "#e0e7eb"
                    # 
                jours_ent_restant = entretien
                if jours_ent_restant:
                    for entretien in jours_ent_restant:
                        jours_ent_restant = entretien.jours_ent_restant
                        alert_ent_color = 'red' if jours_ent_restant <=3 else 'orange' if jours_ent_restant < 8 else 'green'
                else: 
                    jours_ent_restant = "0"     
                    alert_ent_color = "#e0e7eb"    
                jours_restant = visite  
                # 
                if jours_restant:       
                    for visit in jours_restant:         
                        jours_restant = visit.jour_restant      
                        alert_color = 'red' if jours_restant <=32 else 'orange' if jours_restant <92 else 'green'
                else: 
                    jours_restant = "0"    
                    alert_color = "#e0e7eb"
                def safe_int(value):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0
                
                alert_types = []
                # Ajoutez les types d'alerte en fonction des jours restants
                if 1 <= safe_int(jours_restant) <= 5:
                    alert_types.append("visite technique")
                if 1 <= safe_int(jours_ent_restant) <= 5:
                    alert_types.append("entretien")
                if 1 <= safe_int(jours_assu_restant) <= 5:
                    alert_types.append("assurance")
                if 1 <= safe_int(jours_vign_restant) <= 5:
                    alert_types.append("vignette")
                if 1 <= safe_int(jours_pate_restant) <= 5:
                    alert_types.append("patente")
                if 1 <= safe_int(jours_cartsta_restant) <= 5:
                    alert_types.append("stationnement")
                # Envoie l'email d'alerte si nécessaire
                if alert_types:
                    self.send_alert_email(vehicule.immatriculation, alert_types) 
                resultat_vehicule.append({'vehicule': vehicule, 'jours_restant':jours_restant, 'alert_color':alert_color, 'alert_ent_color':alert_ent_color, 'jours_ent_restant':jours_ent_restant,'alert_assu_color':alert_assu_color,'jours_assu_restant':jours_assu_restant,'jours_vign_restant':jours_vign_restant,'alert_vign_color':alert_vign_color, 'jours_pate_restant':jours_pate_restant,'alert_pate_color':alert_pate_color, 'jours_cartsta_restant':jours_cartsta_restant,'alert_cartsta_color':alert_cartsta_color,})
            
        else:
            
            assu_all = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            visites = VisiteTechnique.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            reparations = Reparation.objects.filter(Q(date_saisie__lte=now) & Q(date_sortie__gte=now)).count()
            assurances = Assurance.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            vignette = Vignette.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                
            patente = Patente.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                 
            cartstation = Stationnement.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()
            # -------------------------#-*-#------------------------- #
            for vehicule in vehicules:
                visite = VisiteTechnique.objects.filter(vehicule = vehicule).order_by('date_saisie')
                entretien = Entretien.objects.filter(vehicule = vehicule).order_by('date_saisie')
                assurances = Assurance.objects.filter(vehicule = vehicule).order_by('date_saisie')
                vignettes = Vignette.objects.filter(vehicule = vehicule).order_by('date_saisie')
                patentes = Patente.objects.filter(vehicule = vehicule).order_by('date_saisie')
                cartstaions = Stationnement.objects.filter(vehicule = vehicule).order_by('date_saisie')
                jours_cartsta_restant = cartstaions
                if jours_cartsta_restant:
                    for cartstaion in jours_cartsta_restant:
                        jours_cartsta_restant = cartstaion.jours_cartsta_restant
                        alert_cartsta_color = 'red' if jours_cartsta_restant <=10 else 'orange' if jours_cartsta_restant < 30 else 'green'
                else: 
                    jours_cartsta_restant = "0"    
                    alert_cartsta_color = "#e0e7eb"
                # 
                jours_pate_restant = patentes
                if jours_pate_restant:
                    for patente in jours_pate_restant:
                        jours_pate_restant = patente.jours_pate_restant
                        alert_pate_color = 'red' if jours_pate_restant <=10 else 'orange' if jours_pate_restant < 30 else 'green'
                else: 
                    jours_pate_restant = "0"    
                    alert_pate_color = "#e0e7eb"
                    # 
                jours_vign_restant = vignettes
                if jours_vign_restant:
                    for vignette in jours_vign_restant:
                        jours_vign_restant = vignette.jours_vign_restant
                        alert_vign_color = 'red' if jours_vign_restant <=10 else 'orange' if jours_vign_restant < 334 else 'green'
                else: 
                    jours_vign_restant = "0"    
                    alert_vign_color = "#e0e7eb"
                    # 
                jours_assu_restant = assurances
                if jours_assu_restant:
                    for assurance in jours_assu_restant:
                        jours_assu_restant = assurance.jours_assu_restant
                        alert_assu_color = 'red' if jours_assu_restant <=7 else 'orange' if jours_assu_restant < 15 else 'green'
                else: 
                    jours_assu_restant = "0"    
                    alert_assu_color = "#e0e7eb"
                    # 
                jours_ent_restant = entretien
                if jours_ent_restant:
                    for entretien in jours_ent_restant:
                        jours_ent_restant = entretien.jours_ent_restant
                        alert_ent_color = 'red' if jours_ent_restant <=3 else 'orange' if jours_ent_restant < 8 else 'green'
                else: 
                    jours_ent_restant = "0"     
                    alert_ent_color = "#e0e7eb"    
                jours_restant = visite  
                # 
                if jours_restant:       
                    for visit in jours_restant:         
                        jours_restant = visit.jour_restant      
                        alert_color = 'red' if jours_restant <=32 else 'orange' if jours_restant <92 else 'green'
                else: 
                    jours_restant = "0"    
                    alert_color = "#e0e7eb"   
                
                def safe_int(value):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0
                
                alert_types = []
                # Ajoutez les types d'alerte en fonction des jours restants
                if 1 <= safe_int(jours_restant) <= 5:
                    alert_types.append("visite technique")
                if 1 <= safe_int(jours_ent_restant) <= 5:
                    alert_types.append("entretien")
                if 1 <= safe_int(jours_assu_restant) <= 5:
                    alert_types.append("assurance")
                if 1 <= safe_int(jours_vign_restant) <= 5:
                    alert_types.append("vignette")
                if 1 <= safe_int(jours_pate_restant) <= 5:
                    alert_types.append("patente")
                if 1 <= safe_int(jours_cartsta_restant) <= 5:
                    alert_types.append("stationnement")
                # Envoie l'email d'alerte si nécessaire
                if alert_types:
                    self.send_alert_email(vehicule.immatriculation, alert_types) 
                resultat_vehicule.append({'vehicule': vehicule, 'jours_restant':jours_restant, 'alert_color':alert_color, 'alert_ent_color':alert_ent_color, 'jours_ent_restant':jours_ent_restant,'alert_assu_color':alert_assu_color,'jours_assu_restant':jours_assu_restant,'jours_vign_restant':jours_vign_restant,'alert_vign_color':alert_vign_color, 'jours_pate_restant':jours_pate_restant,'alert_pate_color':alert_pate_color, 'jours_cartsta_restant':jours_cartsta_restant,'alert_cartsta_color':alert_cartsta_color,})
        context={
            'dates':dates,
            'vehicules':vehicules,
            'resultat_vehicule':resultat_vehicule,
            'annees':annee,
            'visites':visites,
            'assu_all':assu_all,
            'vign_all':vign_all,
            'pat_all':patente_all,
            'stat_all':stat_all,
            'entr_all':entretiens,
            'form':forms,
            'mois_en_cours':libelle_mois_en_cours,
        }
        return context 

class AddVehiculeView(CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'perfect/add_vehicule.html'
    success_message = 'véhicule enregistré avec succès👍✓✓'
    error_message = "Erreur de saisie un véhicule enregistré utilise déjà ces informations verifié l'immatriculation, Numero chassis ou la carte grise ✘✘ "
    success_url = reverse_lazy ('add_car')
    timeout_minutes = 120
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse = super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours = date.today().year
        today = date.today()
        mois_en_cours = date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        else:
            vehicules = Vehicule.objects.all()
        form_admin = DateForm(self.request.GET)
        if form_admin.is_valid():
            date_debut = form_admin.cleaned_data['date_debut']       
            date_fin = form_admin.cleaned_data['date_fin']
            car_count = Vehicule.objects.filter(date_saisie__range=[date_debut, date_fin]).count()
            car_event = Vehicule.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
            vehicules = Vehicule.objects.filter(date_saisie__range=[date_debut, date_fin])
            car_vtc_count = Vehicule.objects.filter(category__category ='VTC', date_saisie__range=[date_debut, date_fin]).count()
            car_taxi_count = Vehicule.objects.filter(category__category ='TAXI', date_saisie__range=[date_debut, date_fin]).count()
            
            car_vtc_invent = Vehicule.objects.filter(category__category ='VTC', date_saisie__range=[date_debut, date_fin]).aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
            car_taxi_invent = Vehicule.objects.filter(category__category ='TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
              
        else:
            car_count = Vehicule.objects.all().count()
            #vehicules = Vehicule.objects.all()
            car_event = Vehicule.objects.all().aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
            #vehicule__category__category#
            car_vtc_count = Vehicule.objects.filter(category__category= 'VTC').count()
            car_taxi_count = Vehicule.objects.filter(category__category = 'TAXI').count()
            
            car_vtc_invent = Vehicule.objects.filter(category__category = 'VTC').aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
            car_taxi_invent = Vehicule.objects.filter(category__category = 'TAXI').aggregate(Sum('cout_acquisition'))['cout_acquisition__sum'] or 0
            
        context={
            'car_vtc_counts':car_vtc_count,
            'car_taxi_counts':car_taxi_count,
            'car_vtc_invent':car_vtc_invent,
            'car_taxi_invent':car_taxi_invent,
            'car_counts':car_count,
            'list_cars':vehicules,
            'forms':forms,
            'form':form_admin,
            'dates':today,
            'mois':libelle_mois_en_cours,
            'annee':annee_en_cours,
            'cars_events':car_event,
            
        }
        return context

def delete_vehicule(request, pk):
    try:
        vehicule = get_object_or_404(Vehicule, id=pk)
        vehicule.delete()
        messages.success(request, f"le véhicule {vehicule.immatriculation} - {vehicule.marque} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_car')

class UpdatVehiculeView(UpdateView):
    model = Vehicule
    form_class = UpdatVehiculeForm
    template_name = 'perfect/car_update.html'
    success_message = 'véhicule Modifié avec succès👍✓✓'
    error_message = "Erreur de saisie un véhicule enregistré utilise déjà des informations verifié l'immatriculation, Numero chassis ou la carte grise ✘✘ "
    # success_url = reverse_lazy ('listvehi')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicules = Vehicule.objects.all()
        context.update({
            'vehicules':vehicules,
        })
        return context
    def get_success_url(self):
        return reverse('updatecar', kwargs={'pk': self.kwargs['pk']})


class DashboardGaragView(TemplateView):
    model = Vehicule
    template_name = 'perfect/dash_garag.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        else:
            vehicules = Vehicule.objects.all()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            nb_reparatvtc = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='VTC').count()
            total_reparatvtc = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='VTC').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparatvtc_format ='{:,}'.format(total_reparatvtc).replace('',' ')
            
            nb_reparataxi = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='TAXI').count()
            total_reparataxi = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='TAXI').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparataxi_format ='{:,}'.format(total_reparataxi).replace('',' ')
            
            nb_reparat = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).count()
            total_reparat = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparat_format ='{:,}'.format(total_reparat).replace('',' ')
            
            total_visit = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_visit_format ='{:,}'.format(total_visit).replace('',' ')
            
            total_entret = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_ent_format ='{:,}'.format(total_entret).replace('',' ')
            
            total_piece = Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            
            total_piecechang = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piececha_format ='{:,}'.format(total_piecechang).replace('',' ')
            
            total_piece_int = Piece.objects.filter(date_saisie__range=[date_debut, date_fin], lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_piecechang_int = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin], lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_pieces_int = total_piece_int + total_piecechang_int
            total_pieces_format_int = '{:,}'.format(total_pieces_int).replace('',' ')
            
            total_patent = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_pat_format ='{:,}'.format(total_patent).replace('',' ')
            
            total_statio = Stationnement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_sta_format ='{:,}'.format(total_statio).replace('',' ')
            
            total_vigne = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_vign_format ='{:,}'.format(total_vigne).replace('',' ')
            
            ################################----Graphiques----#############################
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            vis_vtc_data = VisiteTechnique.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            vis_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in vis_vtc_data:
                vis_mois_vtc_data[commande.date_saisie.month] += 1
            vis_mois_vtc_data = [vis_mois_vtc_data[month] for month in range(1, 13)]
            vis_taxi_data = VisiteTechnique.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            vis_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in vis_taxi_data:
                vis_mois_taxi_data[commande.date_saisie.month] += 1
            vis_mois_taxi_data = [vis_mois_taxi_data[month] for month in range(1, 13)]
            
            ent_vtc_data = Entretien.objects.filter(vehicule__category__category="VTC", date_saisie__range=[date_debut, date_fin])
            ent_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in ent_vtc_data:
                ent_mois_vtc_data[commande.date_saisie.month] += 1
            ent_mois_vtc_data = [ent_mois_vtc_data[month] for month in range(1, 13)]
            
            ent_taxi_data = Entretien.objects.filter(vehicule__category__category="TAXI", date_saisie__range=[date_debut, date_fin])
            ent_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in ent_taxi_data:
                ent_mois_taxi_data[commande.date_saisie.month] += 1
            ent_mois_taxi_data = [ent_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
            
        else:
            nb_reparat = Reparation.objects.filter(date_saisie__month=date.today().month).count()
            total_reparat = Reparation.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparat_format ='{:,}'.format(total_reparat).replace('',' ')
            
            nb_reparatvtc = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='VTC').count()
            total_reparatvtc = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='VTC').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparatvtc_format ='{:,}'.format(total_reparatvtc).replace('',' ')
            
            nb_reparataxi = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='TAXI').count()
            total_reparataxi = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='TAXI').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparataxi_format ='{:,}'.format(total_reparataxi).replace('',' ')
            
            total_visit = VisiteTechnique.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_visit_format ='{:,}'.format(total_visit).replace('',' ')
            
            total_entret = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_ent_format ='{:,}'.format(total_entret).replace('',' ')
            
            total_piece = Piece.objects.filter(date_saisie__month=date.today().month,).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            
            total_piecechang = PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piececha_format ='{:,}'.format(total_piecechang).replace('',' ')
            
            total_piece_int = Piece.objects.filter(date_saisie__month=date.today().month, lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_piecechang_int = PiecEchange.objects.filter(date_saisie__month=date.today().month, lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_pieces_int = total_piece_int + total_piecechang_int
            total_pieces_format_int = '{:,}'.format(total_pieces_int).replace('',' ')
            
            total_patent = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_pat_format ='{:,}'.format(total_patent).replace('',' ')
            
            total_statio = Stationnement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_sta_format ='{:,}'.format(total_statio).replace('',' ')
            
            total_vigne = Vignette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_vign_format ='{:,}'.format(total_vigne).replace('',' ')
            
            ################################----Graphiques----#############################
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            vis_vtc_data = VisiteTechnique.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            vis_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in vis_vtc_data:
                vis_mois_vtc_data[commande.date_saisie.month] += 1
            vis_mois_vtc_data = [vis_mois_vtc_data[month] for month in range(1, 13)]
            vis_taxi_data = VisiteTechnique.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            vis_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in vis_taxi_data:
                vis_mois_taxi_data[commande.date_saisie.month] += 1
            vis_mois_taxi_data = [vis_mois_taxi_data[month] for month in range(1, 13)]
            
            ent_vtc_data = Entretien.objects.filter(vehicule__category__category="VTC", date_saisie__year=datetime.now().year)
            ent_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in ent_vtc_data:
                ent_mois_vtc_data[commande.date_saisie.month] += 1
            ent_mois_vtc_data = [ent_mois_vtc_data[month] for month in range(1, 13)]
            
            ent_taxi_data = Entretien.objects.filter(vehicule__category__category="TAXI", date_saisie__year=datetime.now().year)
            ent_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in ent_taxi_data:
                ent_mois_taxi_data[commande.date_saisie.month] += 1
            ent_mois_taxi_data = [ent_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__year=datetime.now().year)
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__year=datetime.now().year)
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
        context.update({
                'rep_mois_vtc_data':rep_mois_vtc_data,
                'rep_mois_taxi_data':rep_mois_taxi_data,
                
                'vis_mois_vtc_data':vis_mois_vtc_data,
                'vis_mois_taxi_data':vis_mois_taxi_data,
                
                'ent_mois_vtc_data':ent_mois_vtc_data,
                'ent_mois_taxi_data':ent_mois_taxi_data,
                
                'piec_mois_vtc_data':piec_mois_vtc_data,
                'piec_mois_taxi_data':piec_mois_taxi_data,
                
                'piecha_mois_vtc_data':piecha_mois_vtc_data,
                'piecha_mois_taxi_data':piecha_mois_taxi_data,
                
                'nb_reparat':nb_reparat,
                'total_reparat_format':total_reparat_format,
                'total_visit_format':total_visit_format,
                'total_ent_format':total_ent_format,
                'total_piece_format':total_piece_format,
                'total_piececha_format':total_piececha_format,
                'total_pat_format':total_pat_format,
                'total_sta_format':total_sta_format,
                'total_vign_format':total_vign_format, 
                
                'nb_reparatvtc':nb_reparatvtc,
                'total_reparatvtc_format':total_reparatvtc_format,

                'nb_reparataxi':nb_reparataxi,
                'total_reparataxi_format':total_reparataxi_format,
                'total_pieces_format_int':total_pieces_format_int,
                
                'labels':label,
                'form':form,
                'dates':dates,
                'vehicules':vehicules  
            })
        return context 

class DashboardGaragecarView(DetailView):
    model = Vehicule
    template_name = 'perfect/dash_garag_car.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        context['catego_vehi'] = CategoVehi.objects.all()
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        else:
            vehicules = Vehicule.objects.all()
        vehicule = self.get_object()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            reparations_mois = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            reparations = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            visitechniques = VisiteTechnique.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piecerep = Piece.objects.filter(reparation__in = reparations_mois).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vignettes = Vignette.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            patentes = Patente.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            stations = Stationnement.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            
            tot_reparation = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).count()
            tot_piecerep_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__range=[date_debut, date_fin], lieu='INTERNE').count()
            tot_piece_cout_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__range=[date_debut, date_fin], lieu='INTERNE').aggregate(Sum('montant'))['montant__sum'] or 0
            tot_piechange = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).count()
            
            ###########################################################################################################################################################
            rep_data = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            rep_mois_data = {month: 0 for month in range(1, 13)}
            for commande in rep_data:
                rep_mois_data[commande.date_saisie.month] += commande.montant
            rep_mois_data = [rep_mois_data[month] for month in range(1, 13)]
            
            entret_data = Entretien.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            entret_mois_data = {month: 0 for month in range(1, 13)}
            for commande in entret_data:
                entret_mois_data[commande.date_saisie.month] += commande.montant
            entret_mois_data = [entret_mois_data[month] for month in range(1, 13)]
            
            piece_data = Piece.objects.filter(reparation__in=rep_data, date_saisie__range=[date_debut, date_fin])
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piecha_data = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            piecha_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_data:
                piecha_mois_data[commande.date_saisie.month] += commande.montant
            piecha_mois_data = [piecha_mois_data[month] for month in range(1, 13)]
            
        else:
            reparations_mois = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month)
            reparations = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            visitechniques = VisiteTechnique.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piecerep = Piece.objects.filter(reparation__in = reparations_mois).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignettes = Vignette.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            patentes = Patente.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            stations = Stationnement.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            
            tot_reparation = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).count()
            tot_piecerep_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__month=date.today().month, lieu='INTERNE').count()
            tot_piece_cout_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__month=date.today().month, lieu='INTERNE').aggregate(Sum('montant'))['montant__sum'] or 0
            tot_piechange = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).count()
            
            ###########################################################################################################################################################
            rep_data = Reparation.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            rep_mois_data = {month: 0 for month in range(1, 13)}
            for commande in rep_data:
                rep_mois_data[commande.date_saisie.month] += commande.montant
            rep_mois_data = [rep_mois_data[month] for month in range(1, 13)]
            
            entret_data = Entretien.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            entret_mois_data = {month: 0 for month in range(1, 13)}
            for commande in entret_data:
                entret_mois_data[commande.date_saisie.month] += commande.montant
            entret_mois_data = [entret_mois_data[month] for month in range(1, 13)]
            
            piece_data = Piece.objects.filter(reparation__in=rep_data, date_saisie__year=datetime.now().year)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piecha_data = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            piecha_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_data:
                piecha_mois_data[commande.date_saisie.month] += commande.montant
            piecha_mois_data = [piecha_mois_data[month] for month in range(1, 13)]
            
        context.update({
                'reparations':reparations,
                'visitechniques':visitechniques,
                'entretiens':entretiens,
                'piecerep':piecerep,
                'piechang':piechang,
                'vignettes':vignettes,
                'patentes':patentes,
                'stations':stations,
                
                'tot_reparation':tot_reparation,
                'tot_piecerep_int':tot_piecerep_int,
                'tot_piece_cout_int':tot_piece_cout_int,
                'tot_piechange':tot_piechange,
                'vehicule':vehicule,
                'vehicules':vehicules,
                ####################Graphe##################
                'rep_mois_data':rep_mois_data,
                'entret_mois_data':entret_mois_data,
                'piece_mois_data':piece_mois_data,
                'piecha_mois_data':piecha_mois_data,
                'label':label,
                'form':form,
        })
        return context 
    
    
class CarFinanceView(TemplateView):
    model = Vehicule
    template_name = 'perfect/dash_car.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # vehicule = Vehicule.objects.all()
        
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        context={
            'vehicule':vehicules,
        }
        return context

class DetailVehiculeView(DetailView):
    model = Vehicule
    template_name = 'perfect/dash_car.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        
        
        vehicule = Vehicule.objects.all()
        vehicules = self.get_object()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            recettes = Recette.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            charge_var = ChargeVariable.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            charge_fix = ChargeFixe.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piecechang = PiecEchange.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            Total_charge = charge_fix + charge_var
            marg_contr = recettes - charge_var
            taux_marge = (marg_contr*100/(recettes))
            
            taux_marge_format='{:.2f}'.format(taux_marge)
            resultat = recettes-Total_charge
            
            nbreparation = Reparation.objects.filter(date_entree__range=[date_debut, date_fin], vehicule = vehicules).count() 
            
            reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicules)
            som_piece = Piece.objects.filter(reparation__in=reparations).aggregate(somme=Sum('montant'))['somme'] or 0
            
            ################################----Graphiques----#############################
            recet_data = Recette.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            recet_mois_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data:
                recet_mois_data[commande.date_saisie.month] += commande.montant
            recet_mois_data = [recet_mois_data[month] for month in range(1, 13)]
            
            chargfix_data = ChargeFixe.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            chargfix_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_data:
                chargfix_mois_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_data = [chargfix_mois_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicules)
            piece_data = Piece.objects.filter(reparation__in = reparations)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piechag_data = PiecEchange.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            piechang_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piechag_data:
                piechang_mois_data[commande.date_saisie.month] += commande.montant
            piechang_mois_data = [piechang_mois_data[month] for month in range(1, 13)]
            
            # label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            # marges_mensuelles = recet_mois_data - chargvar_mois_data
            marge_data = [recet_mois_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data = [(marge_data[i] * 100) / recet_mois_data[i] if recet_mois_data[i] > 0 else 0 for i in range(12)]
        else:
            recettes = Recette.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            charge_fix = ChargeFixe.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            charge_var = ChargeVariable.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piecechang = PiecEchange.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0

            Total_charge = charge_fix + charge_var
            marg_contr = recettes - charge_var
            taux_marge = (marg_contr*100/(recettes))
            
            taux_marge_format='{:.2f}'.format(taux_marge)
            resultat = recettes-Total_charge
            
            
            nbreparation = Reparation.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).count()
            reparations = Reparation.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month)
            som_piece = Piece.objects.filter(reparation__in = reparations).aggregate(somme=Sum('montant'))['somme'] or 0
            
            # reparation_mois = Reparation.objects.filter(vehicule = vehicule).annotate(month=ExtractMonth("date_entree")).values("month").annotate(total=Count("id")).values("month","total").order_by('month')

            recet_data = Recette.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            recet_mois_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data:
                recet_mois_data[commande.date_saisie.month] += commande.montant
            recet_mois_data = [recet_mois_data[month] for month in range(1, 13)]
            
            chargfix_data = ChargeFixe.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            chargfix_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_data:
                chargfix_mois_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_data = [chargfix_mois_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            piechag_data = PiecEchange.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            piechang_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piechag_data:
                piechang_mois_data[commande.date_saisie.month] += commande.montant
            piechang_mois_data = [piechang_mois_data[month] for month in range(1, 13)]
            
            reparations = Reparation.objects.filter(vehicule = vehicules,date_saisie__month=date.today().month)
            piece_data = Piece.objects.filter(reparation__in = reparations)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]

            marge_data = [recet_mois_data[i] - chargvar_mois_data[i] for i in range(12)]

            # Calcul des taux mensuels
            taux_data = [(marge_data[i] * 100) / recet_mois_data[i] if recet_mois_data[i] > 0 else 0 for i in range(12)]

        context.update({
            'recettes':recettes,
            'charge_fix':charge_fix,
            'charge_var':charge_var,
            # 'taux_marge':taux_marge,
            'taux_marge_format':taux_marge_format,
            'resultat':resultat,
            'nbreparation':nbreparation,
            'resultat':resultat,
            'som_piece':som_piece,
            'piecechang':piecechang,
            
            'recet_mois_data':recet_mois_data,
            'chargfix_mois_data':chargfix_mois_data,
            'chargvar_mois_data':chargvar_mois_data,
            'piece_mois_data':piece_mois_data,
            'piechang_mois_data':piechang_mois_data,
            
            'taux_data':taux_data,
            
            'dates':dates,
            'vehicules':vehicules,
            'vehicule':vehicule,
            'annees':annee,
            'mois_en_cours':libelle_mois_en_cours,
            
            'form':form,
            'labels':label,
        })    
        return context 
    
class SaisieGaragView(TemplateView):
    template_name = 'perfect/saisi_garag.html'
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            assu_all = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
        else:
            assu_all = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
        
        context={
            
            'dates':dates,
            'vehicule':vehicules,
            'assu_all':assu_all,
            'vign_all':vign_all,
            'patente_all':patente_all,
            'stat_all':stat_all,
            'form':forms,
        }
        return context
 
class TempsArretsView(TemplateView):
    template_name = 'perfect/saisi_temp_arret.html'
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            autarre_som = Autrarret.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            autarre_cpt = Autrarret.objects.filter(date_saisie__range=[date_debut, date_fin]).count()
            
            vis_all = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            rep_vtc = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            rep_vtc_cpte = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin]).count()
            rep_taxi_count = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin]).count()
            rep_taxi = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
        else:
            autarre_som = Autrarret.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            autarre_cpt = Autrarret.objects.filter(date_saisie__month=date.today().month).count()
            
            vis_all = VisiteTechnique.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            rep_vtc_cpte = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__month=date.today().month).count()
            rep_taxi_count = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__month=date.today().month).count()
            rep_vtc = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            rep_taxi = Reparation.objects.filter(vehicule__category__category="TAXI", date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
        context={
            'dates':dates,
            'vehicules':vehicules,
            'vis_all':vis_all,
            'ent_all':ent_all,
            'rep_vtc':rep_vtc,
            'rep_taxi':rep_taxi,
            'autarre_som':autarre_som,
            'autarre_cpt':autarre_cpt,
            'rep_vtc_cpte':rep_vtc_cpte,
            'rep_taxi_count': rep_taxi_count,
            'form':forms,
        }
        return context
  
class SaisiComptaView(TemplateView):
    template_name = 'perfect/saisi_comptable.html'
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            charvars = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            charfixe = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargtot = charvars + charfixe
            margcontrib = recettes - charvars
            
            if recettes == 0:
                taux = 0
            else:
                taux = (margcontrib*100/(recettes))
            taux_marge = '{:.2f}'.format(taux).replace('',' ')
            
            result = recettes - chargtot
            
        else:
            recettes = Recette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            charvars = ChargeVariable.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            charfixe = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargtot = charvars + charfixe
            margcontrib = recettes - charvars
            
            if recettes == 0:
                taux = 0
            else:
                taux = (margcontrib*100/(recettes))
            taux_marge = '{:.2f}'.format(taux).replace('','')
            
            result = recettes - chargtot
        
        context={
            'dates':dates,
            'vehicules':vehicules,
            'recette':recettes,
            'charvars':charvars,
            'charfixe':charfixe,
            'margcontrib':margcontrib,
            'taux_marge':taux_marge,
            'chargtot':chargtot,
            'result':result,
            
            'form':forms,
        }
        return context

#------------------------------COMPTABLE-------------------------------
from django.shortcuts import get_object_or_404
class AddRecetteView(CreateView):
    model = Recette
    form_class = RecetteForm
    template_name= "perfect/add_recet.html"
    success_message = 'Recette Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            recets_result = Recette.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_list = Recette.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).order_by('-id')
            recets_jours = Recette.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_mois = Recette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_an = Recette.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
           
        else:
            recets_list = Recette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            recets_result = Recette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_jours = Recette.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_mois = Recette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            recets_an = Recette.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "recets_result": recets_result,
            "recets_list": recets_list,
            "recets_jours": recets_jours,
            "recets_mois": recets_mois,
            "recets_an": recets_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_recettes', kwargs={'pk': self.kwargs['pk']})

class AddAutrarretView(CreateView):
    model = Autrarret
    form_class = AutrarretForm
    template_name= "perfect/add_autarret.html"
    success_message = "Autre d'arrêt Ajouté avec succès ✓✓"
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            autarret_result = Autrarret.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_list = Autrarret.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).order_by('-id')
            autarret_jours = Autrarret.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_mois = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_an = Autrarret.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
           
        else:
            autarret_list = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            autarret_result = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_jours = Autrarret.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_mois = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            autarret_an = Autrarret.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "autarret_result": autarret_result,
            "autarret_list": autarret_list,
            "autarret_jours": autarret_jours,
            "autarret_mois": autarret_mois,
            "autarret_an": autarret_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_autarrets', kwargs={'pk': self.kwargs['pk']})

class ListRecetView(ListView):
    model = Recette
    template_name = 'perfect/liste_recette.html'
    context_object = 'listrecet'
    timeout_minutes = 220
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            recets_mois_all = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_mois_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_mois_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            recets_an_fil_vtc = Recette.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_an_fil_taxi = Recette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            recets_an_all = Recette.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_mois_recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            recets_mois_all = Recette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_mois_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_mois_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            recets_an_fil_vtc = Recette.objects.filter(vehicule__category__category='VTC', date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_an_fil_taxi = Recette.objects.filter(vehicule__category__category='TAXI', date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_an_all = Recette.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_mois_recettes = Recette.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_mois_recettes':list_mois_recettes,
            
            'recets_mois_all':recets_mois_all,
            'recets_mois_taxi':recets_mois_taxi,
            'recets_mois_vtc':recets_mois_vtc,
            
            'recets_an_fil_vtc':recets_an_fil_vtc,
            'recets_an_fil_taxi':recets_an_fil_taxi,
            'recets_an_all':recets_an_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            'form':forms,
            }
        return context 
    

class UpdateRecetView(UpdateView):
    model = Recette
    form_class = UpdateRecetteForm
    template_name = "news/appl/update_recette.html"
    context_object = 'listvehi'  
    success_message = 'Recette Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('listrecet')
    timeout_minutes = 20
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse = super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    
def delete_visite(request, pk):
    try:
        visites = get_object_or_404(VisiteTechnique, id=pk)
        visites.delete()
        messages.success(request, f"la recette du véhicule {visites.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_visit')

def delete_recette(request, pk):
    try:
        recettres = get_object_or_404(Recette, id=pk)
        recettres.delete()
        messages.success(request, f"la recette du véhicule {recettres.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_recet')

def delete_charg_var(request, pk):
    try:
        charg_variables = get_object_or_404(ChargeVariable, id=pk)
        charg_variables.delete()
        messages.success(request, f"la Charge variable du véhicule {charg_variables.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_charg_var')

def delete_charg_fixe(request, pk):
    try:
        charg_fixes = get_object_or_404(ChargeFixe, id=pk)
        charg_fixes.delete()
        messages.success(request, f"la Charge fixe du véhicule {charg_fixes.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_charg_fix')
    

class DetailRecetteView(DetailView):
    model = Recette
    template_name = "news/applist/detail_recette.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    

class AddChargeFixView(CreateView):
    model = ChargeFixe
    form_class = ChargeFixForm
    template_name= "perfect/add_charg_fixe.html"
    success_message = 'Charge fixe Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            chargfix_result = ChargeFixe.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_list = ChargeFixe.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            chargfix_jours = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_mois = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_an = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0 
           
        else:
            chargfix_list = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            chargfix_result = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_jours = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_mois = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargfix_an = ChargeFixe.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "chargfix_result": chargfix_result,
            "chargfix_list": chargfix_list,
            "chargfix_jours": chargfix_jours,
            "chargfix_mois": chargfix_mois,
            "chargfix_an": chargfix_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('addcharg_fix', kwargs={'pk': self.kwargs['pk']})
   
class DetailChargeFixeView(DetailView):
    model = ChargeFixe
    template_name = "news/applist/detail_charg_fix.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    
class ListChargeFixView(ListView):
    model = ChargeFixe
    template_name = 'perfect/liste_charg_fix.html'
    context_object = 'list_charg_fix'
    timeout_minutes = 320
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates =date.today()
        annee =date.today().year
        mois =date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            chargefixe_all = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_all_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_all_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_jour = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_jour_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_mois_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_jour_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_mois_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_mois_all = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            recets_an_fil_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_an_fil_taxi = Recette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_chargefixe = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
             
        else:
            
            chargefixe_all = ChargeFixe.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_all_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_all_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_jour = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_jour_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_mois_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_jour_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargefixe_mois_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargefixe_mois_all = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0

            recets_an_fil_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            recets_an_fil_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            list_chargefixe = ChargeFixe.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'recets_an_fil_vtc' : recets_an_fil_vtc,
            'recets_an_fil_taxi': recets_an_fil_taxi,
            
            'list_chargefixe':list_chargefixe,
            
            'chargefixe_jour':chargefixe_jour,
            'chargefixe_jour_vtc':chargefixe_jour_vtc,
            'chargefixe_mois_vtc':chargefixe_mois_vtc,
            
            'chargefixe_mois_taxi':chargefixe_mois_taxi,
            
            'chargefixe_jour_taxi':chargefixe_jour_taxi,
            # 'chargefixe_an_cour':chargefixe_an_cour,
            
            'chargefixe_all':chargefixe_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'chargefixe_mois_all':chargefixe_mois_all,
            
            'chargefixe_all_vtc':chargefixe_all_vtc,
            'chargefixe_all_taxi':chargefixe_all_taxi,
            'form':forms,
            }
        return context

class UpdateChargFixView(UpdateView):
    model = ChargeFixe
    form_class = UpdatChargeFixForm
    template_name = "news/appl/update_charg_fix.html"
    context_object = 'listvehi'  
    success_message = 'Charge Fixe Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_charg_fix')
    timeout_minutes = 10

    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] =user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 

class AddChargeVarView(CreateView):
    model = ChargeVariable
    form_class = ChargeVarForm
    template_name= "perfect/add_charg_var.html"
    success_message = 'Charge variable Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none()
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            chargvar_result = ChargeVariable.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_list = ChargeVariable.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            chargvar_jours = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_mois = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_an = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0   
        else:
            chargvar_list = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            chargvar_result = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_jours = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_mois = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            chargvar_an = ChargeVariable.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "chargvar_result": chargvar_result,
            "chargvar_list": chargvar_list,
            "chargvar_jours": chargvar_jours,
            "chargvar_mois": chargvar_mois,
            "chargvar_an": chargvar_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('addcharg_var', kwargs={'pk': self.kwargs['pk']})

class DetailChargeVarView(DetailView):
    model = ChargeVariable
    template_name = "news/applist/detail_charg_vari.html"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    
class ListChargeVarView(ListView):
    model = ChargeVariable
    template_name = 'perfect/liste_charg_var.html'
    context_object = 'list_charg_var'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            chargvar_all = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_all_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_all_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_jour = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_jour_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_mois_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_jour_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_mois_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_mois_all = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_an_fil_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_an_fil_taxi = Recette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_chargevar = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
             
        else:
            
            chargvar_all = ChargeFixe.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_all_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_all_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_jour = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_jour_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_mois_vtc = ChargeFixe.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_jour_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_mois_taxi = ChargeFixe.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            chargevar_mois_all = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0

            chargevar_an_fil_vtc = ChargeFixe.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            chargevar_an_fil_taxi = ChargeFixe.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            list_chargevar = ChargeFixe.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'chargevar_an_fil_vtc' : chargevar_an_fil_vtc,
            'chargevar_an_fil_taxi': chargevar_an_fil_taxi,
            
            'list_chargevar':list_chargevar,
            'chargevar_jour':chargevar_jour,
            
            'chargevar_jour_vtc':chargevar_jour_vtc,
            'chargevar_mois_vtc':chargevar_mois_vtc,
            
            'chargevar_jour_taxi':chargevar_jour_taxi,
            'chargevar_mois_taxi':chargevar_mois_taxi,
            
            'chargevar_mois_all':chargevar_mois_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'chargvar_all':chargvar_all,
            
            'chargevar_all_vtc':chargevar_all_vtc,
            'chargevar_all_taxi':chargevar_all_taxi,
            'form':forms,
            }
        return context

class UpdateChargeVarView(UpdateView):
    model = ChargeVariable
    form_class = updatChargeVarForm
    template_name = "news/appl/update_charg_vari.html"
    context_object = 'listvehi'  
    success_message = 'Charge Variable Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('list_charg_var')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    
class UpdateChargeAdminView(UpdateView):
    model = ChargeAdminis
    form_class = updatChargeAdminisForm
    template_name = "news/appl/add_charg_admin.html"
    success_message = 'Charge Administrative Modifiée avec succès👍✓✓'
    success_url = reverse_lazy('add_charg_administ')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        context['chargadminist'] = ChargeAdminis.objects.all()
        return context 
    

class AddChargeAdminisView(CreateView):
    model = ChargeAdminis
    form_class = ChargeAdminisForm
    template_name = 'perfect/add_charg_admin.html'
    success_message = 'Charge administrative enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('add_chargadminist')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today =date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
         
        form_admin = DateForm(self.request.GET)
        if form_admin.is_valid():
            date_debut = form_admin.cleaned_data['date_debut']       
            date_fin = form_admin.cleaned_data['date_fin']
            charg_administ = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
            
            charg_adm_jour = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_jour_format ='{:,}'.format(charg_adm_jour).replace('',' ')
            charg_adm_mois = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_mois_format ='{:,}'.format(charg_adm_mois).replace('',' ')
            charg_adm_annuel = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_annuel_format ='{:,}'.format(charg_adm_annuel).replace('',' ')
            
            charg_adm_result = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            
            charg_admin_data = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin])
            chargadmin_mois_data = {month: 0 for month in range(1, 13)}
            for commande in charg_admin_data:
                chargadmin_mois_data[commande.date_saisie.month] += commande.montant
            chargadmin_mois_data = [chargadmin_mois_data[month] for month in range(1, 13)]
            label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            total_recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            
            if total_recettes == 0:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            resultat = marge_brute-charg_adm_mois
            resultat_format ='{:,}'.format(resultat).replace('',' ')
        else:
            charg_administ = ChargeAdminis.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
            charg_adm_jour = ChargeAdminis.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_jour_format ='{:,}'.format(charg_adm_jour).replace('',' ')
            charg_adm_mois = ChargeAdminis.objects.filter(date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_mois_format ='{:,}'.format(charg_adm_mois).replace('',' ')
            charg_adm_annuel = ChargeAdminis.objects.filter(date_saisie__year=date.today().year).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_annuel_format ='{:,}'.format(charg_adm_annuel).replace('',' ')
            
            charg_adm_result = ChargeAdminis.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            
            charg_admin_data = ChargeAdminis.objects.filter(date_saisie__year=date.today().year)
            chargadmin_mois_data = {month: 0 for month in range(1, 13)}
            for commande in charg_admin_data:
                chargadmin_mois_data[commande.date_saisie.month] += commande.montant
            chargadmin_mois_data = [chargadmin_mois_data[month] for month in range(1, 13)]
            label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            total_recettes = Recette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            total_piece= Piece.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            
            if total_recettes == 0:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            resultat = marge_brute-charg_adm_mois
            resultat_format ='{:,}'.format(resultat).replace('',' ')
            
        context={
            'total_recette_format':total_recette_format,
            
            'list_charge_adminis':charg_administ,
            'taux_marge_format':taux_marge_format,
            'total_chargfix_format':total_chargfix_format,
            'total_chargvar_format':total_chargvar_format,
            'total_piece_format':total_piece_format,
            'total_piece_echang_format':total_piece_echang_format,
            'marge_brute_format':marge_brute_format,
            'total_charge_format':total_charge_format,
            
            'labels':label,
            'forms':forms,
            'form':form_admin,
            'resultat_format':resultat_format,
            
            'dates':today,
            'mois':libelle_mois_en_cours,
            'annee':annee_en_cours,
            
            'charg_adm_jour_format':charg_adm_jour_format,
            'charg_adm_mois_format':charg_adm_mois_format,
            'charg_adm_annuel_format':charg_adm_annuel_format,
            
            'charg_adm_result':charg_adm_result,
            'chargadmin_data':chargadmin_mois_data,
        }  
        return context   
    
def delete_chargadmin(request, pk):
    try:
        chargadmin = get_object_or_404(ChargeAdminis, id=pk)
        chargadmin.delete()
        messages.success(request, f"la charge administrative {chargadmin.Num_fact}-{chargadmin.date_saisie} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_chargadminist')

#--------------/-/---------------@-----------------/-/--------------Garage---------------/-/--------------@----------------/-/------------#

class AddCartStationView(CreateView):
    model = Stationnement
    form_class = CartStationForm
    template_name= "perfect/add_station.html"
    success_message = 'Carte de Stationnement enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            stat_result = Stationnement.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_list = Stationnement.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            stat_jours = Stationnement.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_mois = Stationnement.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_an = Stationnement.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
        else:
            stat_list = Stationnement.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            stat_result = Stationnement.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_jours = Stationnement.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_mois = Stationnement.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            stat_an = Stationnement.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "stat_result": stat_result,
            "stat_list": stat_list,
            "stat_jours": stat_jours,
            "stat_mois": stat_mois,
            "stat_an": stat_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_station', kwargs={'pk': self.kwargs['pk']})
     
class UpdatCartStationView(UpdateView):
    model = Stationnement
    form_class = UpdatCartStationForm
    template_name= "news/appl/updat_cartestation.html"
    success_message = 'Modification de carte de station éffectuée avec succès👍✓✓'
    success_url = reverse_lazy ('list_cart_station')
    timeout_minutes = 20
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] =user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class DetailCartStationView(DetailView):
    model = Stationnement
    template_name = "news/applist/detail_cartestation.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
         
class ListCartStationView(ListView):
    model = Stationnement
    template_name = 'perfect/liste_stationnement.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates =date.today()
        annee =date.today().year
        mois =date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            station_all = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            station_all_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_all_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_vtc = Patente.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_taxi = Patente.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_all = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_an_fil_vtc = Patente.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            station_an_fil_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_station = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            station_all = Patente.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            station_all_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_all_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_vtc = Patente.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_jour_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_taxi = Patente.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_mois_all = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            station_an_fil_vtc = Patente.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            station_an_fil_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_station = Patente.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_station':list_station,
            'station_jour':station_jour,
            'station_jour_vtc':station_jour_vtc,
            'station_mois_vtc':station_mois_vtc,
            
            'station_mois_taxi':station_mois_taxi,
            'station_jour_taxi':station_jour_taxi,
            
            'station_all':station_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'station_mois_all':station_mois_all,
            
            'station_all_vtc':station_all_vtc,
            'station_all_taxi':station_all_taxi,
            'form':forms,
            'station_an_fil_vtc' : station_an_fil_vtc,
            'station_an_fil_taxi': station_an_fil_taxi,
            }
        return context

class AddPatenteView(CreateView):
    model = Patente
    form_class = PatenteForm
    template_name= "perfect/add_patente.html"
    success_message = 'Patente enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            pate_result = Patente.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_list = Patente.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            pate_jours = Patente.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_mois = Patente.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_an = Patente.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
           
        else:
            pate_list = Patente.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            pate_result = Patente.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_jours = Patente.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_mois = Patente.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            pate_an = Patente.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "pate_result": pate_result,
            "pate_list": pate_list,
            "pate_jours": pate_jours,
            "pate_mois": pate_mois,
            "pate_an": pate_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_patente', kwargs={'pk': self.kwargs['pk']})

def delete_patente(request, pk):
    try:
        patentes = get_object_or_404(Patente, id=pk)
        vehicule_pk = patentes.vehicule.id 
        patentes.delete()
        messages.success(request, f"La patente du véhicule {patentes.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_patente', pk=vehicule_pk)

def delete_stat(request, pk):
    try:
        stat = get_object_or_404(Stationnement, id=pk)
        vehicule_pk = stat.vehicule.id 
        stat.delete()
        messages.success(request, f"Le carte de stationnement du véhicule {stat.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_station', pk=vehicule_pk)

def delete_autarret(request, pk):
    try:
        autar = get_object_or_404(Autrarret, id=pk)
        vehicule_pk = autar.vehicule.id 
        autar.delete()
        messages.success(request, f"L'arrêt du véhicule {autar.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_autarrets', pk=vehicule_pk)

class UpdatPatenteView(UpdateView):
    model = Patente
    form_class = UpdatPatenteForm
    template_name= "news/appl/updat_patente.html"
    success_message = 'Saisie de Patente modifiée avec succès👍✓✓'
    success_url = reverse_lazy ('list_patente')
    timeout_minutes = 20
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['visites'] = VisiteTechnique.objects.all()
        context['catego_vehi'] = CategoVehi.objects.all()
        return context


class DetailPatenteView(DetailView):
    model = Patente
    template_name = "news/applist/detail_patente.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class ListPatenteView(ListView):
    model = Patente
    template_name = 'perfect/liste_patente.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates =date.today()
        annee =date.today().year
        mois =date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            patente_all = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_vtc = Patente.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_taxi = Patente.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_all = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_an_fil_vtc = Patente.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_an_fil_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_patente = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            patente_all = Patente.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour_vtc = Patente.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_vtc = Patente.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_jour_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_taxi = Patente.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_mois_all = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_an_fil_vtc = Patente.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_an_fil_taxi = Patente.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_patente':list_patente,
            'patente_jour':patente_jour,
            'patente_jour_vtc':patente_jour_vtc,
            'patente_mois_vtc':patente_mois_vtc,
            
            'patente_mois_taxi':patente_mois_taxi,
            'patente_jour_taxi':patente_jour_taxi,
            
            'patente_all':patente_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'patente_mois_all':patente_mois_all,
            
            'patente_all_vtc':patente_all_vtc,
            'patente_all_taxi':patente_all_taxi,
            'form':forms,
            'patente_an_fil_vtc' : patente_an_fil_vtc,
            'patente_an_fil_taxi': patente_an_fil_taxi,
            }
        return context


class AddVignetteView(CreateView):
    model = Vignette
    form_class = VignetteForm
    template_name= "perfect/add_vignette.html"
    success_message = 'Vignette enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            vigne_result = Vignette.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_list = Vignette.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            vigne_jours = Vignette.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_mois = Vignette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_an = Vignette.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
           
        else:
            vigne_list = Vignette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            vigne_result = Vignette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_jours = Vignette.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_mois = Vignette.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            vigne_an = Vignette.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "vigne_result": vigne_result,
            "vigne_list": vigne_list,
            "vigne_jours": vigne_jours,
            "vigne_mois": vigne_mois,
            "vigne_an": vigne_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }     
        return context  
    def get_success_url(self):
        return reverse('add_vignet', kwargs={'pk': self.kwargs['pk']})


class DetailVignetteView(DetailView):
    model = Vignette
    template_name = "news/applist/detail_vignette.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class UpdatVignetteView(UpdateView):
    model = Vignette
    form_class = UpdatVignetteForm
    template_name = "news/appl/updat_vignette.html"
    success_message = 'Saisie de Vignette effectuée avec succès👍✓✓'
    success_url = reverse_lazy ('list_vignet')
    timeout_minutes = 15
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] =user_group.name if user_group else None
        context['visites'] = VisiteTechnique.objects.all()
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class DetailVignetteView(DetailView):
    model = Vignette
    template_name = "news/applist/detail_vignette.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class ListVignetteView(ListView):
    model = Vignette
    template_name = 'perfect/liste_vignette.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates =date.today()
        annee =date.today().year
        mois =date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            vignette_all = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_all_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_all_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_jour = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_jour_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_mois_vtc = Vignette.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_jour_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_mois_taxi = Vignette.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_mois_all = Vignette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_an_fil_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_an_fil_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_vignette = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            vignette_all = Vignette.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_all_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_all_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_jour = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_jour_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_mois_vtc = Vignette.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_jour_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_mois_taxi = Vignette.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_mois_all = Vignette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            vignette_an_fil_vtc = Vignette.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            vignette_an_fil_taxi = Vignette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
            list_vignette = Vignette.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_vignette':list_vignette,
            
            'vignette_jour':vignette_jour,
            'vignette_jour_vtc':vignette_jour_vtc,
            'vignette_mois_vtc':vignette_mois_vtc,
            
            'vignette_mois_taxi':vignette_mois_taxi,
            'vignette_jour_taxi':vignette_jour_taxi,
            # 'recets_an_cour':recets_an_cour,
            
            'vignette_all':vignette_all,
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'vignette_mois_all':vignette_mois_all,
            
            'vignette_all_vtc':vignette_all_vtc,
            'vignette_all_taxi':vignette_all_taxi,
            'form':forms,
            
            'vignette_an_fil_vtc' : vignette_an_fil_vtc,
            'vignette_an_fil_taxi': vignette_an_fil_taxi,
            }
        return context 

class AddVisitView(CreateView):
    model = VisiteTechnique
    form_class = VisiteTechniqueForm
    template_name= "perfect/add_visite.html"
    success_message = 'Visite Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            visite_result = VisiteTechnique.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_list = VisiteTechnique.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            visite_jours = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_mois = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_an = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0   
        else:
            visite_list = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            visite_result = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_jours = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_mois = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            visite_an = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "visite_result": visite_result,
            "visite_list": visite_list,
            "visite_jours": visite_jours,
            "visite_mois": visite_mois,
            "visite_an": visite_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_visit', kwargs={'pk': self.kwargs['pk']})

class ListVisitView(ListView):
    model = VisiteTechnique
    template_name = 'perfect/liste_visites.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates =date.today()
        annee =date.today().year
        mois =date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            viste_all = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_all_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_all_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour = VisiteTechnique.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_vtc = VisiteTechnique.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_taxi = VisiteTechnique.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_all = VisiteTechnique.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_an_fil_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_an_fil_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_viste = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            viste_all = VisiteTechnique.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_all_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_all_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour = VisiteTechnique.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_vtc = VisiteTechnique.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_jour_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_taxi = VisiteTechnique.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_mois_all = VisiteTechnique.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_an_fil_vtc = VisiteTechnique.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            viste_an_fil_taxi = VisiteTechnique.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_viste = VisiteTechnique.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_viste':list_viste,
            'viste_jour':viste_jour,
            
            'viste_jour_vtc':viste_jour_vtc,
            'viste_mois_vtc':viste_mois_vtc,
            
            'viste_mois_taxi':viste_mois_taxi,
            'viste_jour_taxi':viste_jour_taxi,
            
            'viste_all':viste_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'viste_mois_all':viste_mois_all,
            
            'viste_all_vtc': viste_all_vtc,
            'viste_all_taxi': viste_all_taxi,
            'form':forms,
            'viste_an_fil_vtc' : viste_an_fil_vtc,
            'viste_an_fil_taxi': viste_an_fil_taxi,
            }
        return context

class DetailVisiteView(DetailView):
    model = VisiteTechnique
    template_name = "news/applist/detail_visite.html"
    ordoring = ['date_saisie']
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 

class UpdateVisiteView(UpdateView):
    model = VisiteTechnique
    form_class = UpdatVisiteTechniqueForm
    template_name = "news/appl/updat_visit.html" 
    success_message = 'Charge Variable Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('list_visit')
    timeout_minutes = 20
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    
class AddAssuranceView(CreateView):
    model = Assurance
    form_class = AssuranceForm
    template_name= "perfect/add_assurance.html"
    success_message = 'Assurance enregistré avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            assur_result = Assurance.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_list = Assurance.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            assur_jours = Assurance.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_mois = Assurance.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_an = Assurance.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
           
        else:
            assur_list = Assurance.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            assur_result = Assurance.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_jours = Assurance.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_mois = Assurance.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            assur_an = Assurance.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "assur_result": assur_result,
            "assur_list": assur_list,
            "assur_jours": assur_jours,
            "assur_mois": assur_mois,
            "assur_an": assur_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }    
        return context  
    def get_success_url(self):
        return reverse('add_assurance', kwargs={'pk': self.kwargs['pk']})


class DetailAssuranceView(DetailView):
    model = Assurance
    template_name = "news/applist/detail_assurance.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

  
class ListAssuranceView(ListView):
    model = Assurance
    template_name = 'perfect/liste_assurance.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates=date.today()
        annee=date.today().year
        mois=date.today().month
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            assurance_all = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_all_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_all_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            assurance_jour = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_jour_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_mois_vtc = Assurance.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_jour_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_mois_taxi = Assurance.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            assurance_mois_all = Assurance.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_an_fil_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_an_fil_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_assurances = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            assurance_all = Assurance.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_all_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_all_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_jour = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_jour_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_mois_vtc = Assurance.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_jour_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_mois_taxi = Assurance.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            
            assurance_mois_all = Assurance.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_an_fil_vtc = Assurance.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            assurance_an_fil_taxi = Assurance.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurances = Assurance.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_assurances':list_assurances,
            'assurance_jour':assurance_jour,
            'assurance_jour_vtc':assurance_jour_vtc,
            'assurance_mois_vtc':assurance_mois_vtc,
            'assurance_mois_taxi':assurance_mois_taxi,
            'assurance_jour_taxi':assurance_jour_taxi,
            'assurance_all':assurance_all,
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            'assurance_mois_all':assurance_mois_all,
            'assurance_all_vtc':assurance_all_vtc,
            'assurance_all_taxi':assurance_all_taxi,
            'form':forms,
            'assurance_an_fil_vtc' : assurance_an_fil_vtc,
            'assurance_an_fil_taxi': assurance_an_fil_taxi,
            }
        return context 

class UpdateAssuranceView(UpdateView):
    model = Assurance
    form_class = UpdatAssuranceForm
    template_name = "news/appl/updat_assurance.html" 
    success_message = 'Assurance Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('journal_garag')
    timeout_minutes = 20
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
 

class AddReparationView(CreateView):
    model = Reparation
    form_class = ReparationForm
    template_name= "perfect/add_reparation.html"
    success_message = 'Réparation enregistrée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        # now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if self.request.POST:
            piece_formset = PieceFormSet(self.request.POST, instance=self.object)
        else:
            piece_formset = PieceFormSet(instance=self.object)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            repare_result = Reparation.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_list = Reparation.objects.filter(vehicule=vehicule, date_saisie__range=[date_debut, date_fin]).order_by('-id')
            repare_jours = Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_mois = Reparation.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_an = Reparation.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1 
        else:
            repare_list = Reparation.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            repare_result = Reparation.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_jours = Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_mois = Reparation.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1 
            repare_an = Reparation.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "piece_formset": piece_formset,
            "repare_result": repare_result,
            "repare_list": repare_list,
            "repare_jours": repare_jours,
            "repare_mois": repare_mois,
            "repare_an": repare_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }
        return context
    def form_valid(self, form):
        context=self.get_context_data()
        piece_formset=context['piece_formset']
        form.instance.vehicule_id=self.kwargs['pk']
        if form.is_valid() and piece_formset.is_valid():
            self.object=form.save()
            piece_formset.instance=self.object
            piece_formset.save()
            messages.success(self.request, self.success_message)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)
    def get_success_url(self):
        return reverse('add_reparation', kwargs={'pk': self.kwargs['pk']})

def delete_reparation(request, pk):
    try:
        reparation = get_object_or_404(Reparation, id=pk)
        vehicule_pk = reparation.vehicule.id 
        reparation.delete()
        messages.success(request, f"La réparation du véhicule {reparation.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_reparation', pk=vehicule_pk)

def delete_assurance(request, pk):
    try:
        assur = get_object_or_404(Assurance, id=pk)
        vehicule_pk = assur.vehicule.id 
        assur.delete()
        messages.success(request, f"L'assurance du véhicule {assur.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_assurance', pk=vehicule_pk)

def delete_vignette(request, pk):
    try:
        vig = get_object_or_404(Vignette, id=pk)
        vehicule_pk = vig.vehicule.id 
        vig.delete()
        messages.success(request, f"La vignette du véhicule {vig.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_vignet', pk=vehicule_pk)

class AddPiecEchangeView(CreateView):
    model = PiecEchange
    form_class = PiecEchangeForm
    template_name= "perfect/add_piecechange.html"
    success_message = 'Pièces enregistrées avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            piechange_list = PiecEchange.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            piechange_result = PiecEchange.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_jours = PiecEchange.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_mois = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_an = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0 
           
        else:
            piechange_list = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            piechange_result = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_jours = PiecEchange.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_mois = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            piechange_an = PiecEchange.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "piechange_result": piechange_result,
            "piechange_list": piechange_list,
            "piechange_jours": piechange_jours,
            "piechange_mois": piechange_mois,
            "piechange_an": piechange_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }      
        return context  
    def get_success_url(self):
        return reverse('add_piechange', kwargs={'pk': self.kwargs['pk']})
    
def delete_piecechange(request, pk):
    try:
        piecechange = get_object_or_404(PiecEchange, id=pk)
        vehicule_pk = piecechange.vehicule.id 
        piecechange.delete()
        messages.success(request, f"la pièce changé du {piecechange.vehicule.immatriculation}- saisie le: {piecechange.date} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_piechange', pk=vehicule_pk)


from datetime import datetime, timedelta, time
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.timezone import make_aware
import calendar

class DetailReparatView(DetailView):
    model = Reparation
    template_name = 'perfect/detail_reparat.html'
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def calculate_effective_hours(self, start, end):
        total_seconds = 0
        current = start
        while current < end:
            next_hour = (current + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            if next_hour > end:
                next_hour = end

            if time(5, 0) <= current.time() < time(22, 0):
                total_seconds += (next_hour - current).total_seconds()
            
            current = next_hour
        return total_seconds / 3600  # Convertir en heures
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        reparation = get_object_or_404(Reparation, pk=self.kwargs['pk'])
        # reparations  = self.get_object()
        vehicule = reparation.vehicule
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
            
        # Calcul de la durée en heures effectives
        date_entree = reparation.date_entree
        date_sortie = reparation.date_sortie
        duree_effective_heures = self.calculate_effective_hours(date_entree, date_sortie)

        # Calcul des pertes
        if vehicule.category.category == "TAXI":
            perte_par_30min = 550
            recette_categorie = 20000
        elif vehicule.category.category == "VTC":
            perte_par_30min = 600
            recette_categorie = 22000
        else:
            perte_par_30min = 0
            recette_categorie = 0

        perte = (duree_effective_heures * 2) * perte_par_30min
        # Calcul de la recette nette
        recette_nette = recette_categorie - perte
        #-------------------------------------------------------------------------------------------------------------------------------
        # list_reparation = Reparation.objects.filter(vehicule=vehicule)
        ################################----Pieces----#############################
        total_piece= Piece.objects.filter(reparation = reparation,).aggregate(somme=Sum('montant'))['somme'] or 0
        list_piece= Piece.objects.filter(reparation = reparation,)
        
        context={
            'reparation':reparation,
            'duree_effective_heures':duree_effective_heures,
            'perte':perte,
            'recette_nette':recette_nette,
            'vehicules':vehicules,
            'total_piece':total_piece,
            'list_piece':list_piece,
            # 'list_reparation':list_reparation,
            'dates':dates
        }
        return context

class UpdateReparationView(UpdateView):
    model = Reparation
    form_class = UpdatReparationForm
    template_name = "news/appl/updat_reparation.html"
    context_object = 'listvehi'  
    success_message = 'Réparation Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_repa')
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 

class ListPiechangeView(ListView):
    model = PiecEchange
    template_name = 'perfect/liste_piechange.html'
    ordering = ['date_saisie']
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates=date.today()
        annee=date.today().year
        mois=date.today().month
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            piechang_all = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_all_taxi = PiecEchange.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_all_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour = PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_vtc = PiecEchange.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour_taxi= PiecEchange.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_taxi= PiecEchange.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_all = PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_an_fil_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_an_fil_taxi= PiecEchange.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_piechang = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            piechang_all = PiecEchange.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_all_taxi = PiecEchange.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_all_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour = PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_vtc = PiecEchange.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_jour_taxi = PiecEchange.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_taxi = PiecEchange.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_mois_all = PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_an_fil_vtc = PiecEchange.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang_an_fil_taxi = PiecEchange.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piechang = PiecEchange.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_piechang':list_piechang,
            'piechang_jour':piechang_jour,
            'piechang_jour_vtc':piechang_jour_vtc,
            'piechang_mois_vtc':piechang_mois_vtc,
            'piechang_mois_taxi':piechang_mois_taxi,
            'piechang_jour_taxi':piechang_jour_taxi,
            'piechang_all':piechang_all,
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'piechang_mois_all':piechang_mois_all,
            'piechang_all_vtc':piechang_all_vtc,
            'piechang_all_taxi':piechang_all_taxi,
            'form':forms,
            'piechang_an_fil_vtc' : piechang_an_fil_vtc,
            'piechang_an_fil_taxi': piechang_an_fil_taxi,
            }
        return context 
    
    
class ListReparationView(ListView):
    model = Reparation
    template_name = 'perfect/liste_reparations.html'
    ordering = ['date_saisie']
    context_object = 'listereparation'
    timeout_minutes = 300
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            reparat_all = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_all_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_all_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour = Reparation.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_vtc = Reparation.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_taxi = Reparation.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_all = Reparation.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_an_fil_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_an_fil_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparat = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            reparat_all = Reparation.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_all_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_all_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour = Reparation.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_vtc = Reparation.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_jour_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_taxi = Reparation.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_mois_all = Reparation.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_an_fil_vtc = Reparation.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            reparat_an_fil_taxi = Reparation.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparat = Reparation.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'form':forms,
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            'reparat_all':reparat_all,       
            'reparat_all_taxi':reparat_all_taxi,
            'reparat_all_vtc':reparat_all_vtc ,
            'reparat_jour':reparat_jour   ,   
            'reparat_jour_vtc':reparat_jour_vtc,
            'reparat_mois_vtc':reparat_mois_vtc,  
            'reparat_jour_taxi':reparat_jour_taxi, 
            'reparat_mois_taxi':reparat_mois_taxi, 
            'reparat_mois_all':reparat_mois_all,      
            'reparat_an_fil_vtc':reparat_an_fil_vtc  ,  
            'reparat_an_fil_taxi':reparat_an_fil_taxi ,  
            'list_reparat':list_reparat   ,              
            
            }
        return context 
    
     
class AddEntretienView(CreateView):
    model = Entretien
    form_class = EntretienForm
    template_name= "perfect/add_entretien.html"
    success_message = 'Entretien effectué avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('journal_garag')
    timeout_minutes = 30
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['entretiens'] = Entretien.objects.all()
        context['catego_vehi'] = CategoVehi.objects.all()
        return context
    
class AddEntretienView(CreateView):
    model = Entretien
    form_class = EntretienForm
    template_name= "perfect/add_entre.html"
    success_message = 'Entretien Ajouté avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            entre_result = Entretien.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_list = Entretien.objects.filter(vehicule=vehicule, date__range=[date_debut, date_fin]).order_by('-id')
            entre_jours = Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_mois = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_an = Entretien.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0   
        else:
            entre_list = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).order_by('-id')
            entre_result = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_jours = Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_mois = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0 
            entre_an = Entretien.objects.filter(vehicule=vehicule, date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "entre_result": entre_result,
            "entre_list": entre_list,
            "entre_jours": entre_jours,
            "entre_mois": entre_mois,
            "entre_an": entre_an,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_entretien', kwargs={'pk': self.kwargs['pk']})

class DetailEntretienView(DetailView):
    model = Entretien
    template_name = "news/applist/detail_entretien.html"
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context
  
class ListEntretienView(ListView):
    model = Entretien
    template_name = 'perfect/liste_entretien.html'
    ordering = ['date_saisie']
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates=date.today()
        annee=date.today().year
        mois=date.today().month
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            ent_all = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_vtc = Entretien.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_taxi = Entretien.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_all = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_ent = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            ent_all = Entretien.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_vtc = Entretien.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_taxi = Entretien.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_all = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_ent = Entretien.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_ent':list_ent,
            'ent_jour':ent_jour,
            'ent_jour_vtc':ent_jour_vtc,
            'ent_mois_vtc':ent_mois_vtc,
            
            'ent_mois_taxi':ent_mois_taxi,
            'ent_jour_taxi':ent_jour_taxi,
            
            'ent_all':ent_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'ent_mois_all':ent_mois_all,
            
            'ent_all_vtc':ent_all_vtc,
            'ent_all_taxi':ent_all_taxi,
            'form':forms,
            'ent_an_fil_vtc' : ent_an_fil_vtc,
            'ent_an_fil_taxi': ent_an_fil_taxi,
            }
        return context 
    
class UpdatEntretienView(UpdateView):
    model = Entretien
    form_class = UpdatEntretienForm
    template_name = "news/appl/update_entretien.html"
    context_object = 'listvehi'  
    success_message = 'Entretien Modifiée avec succès👍✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_entretien')
    timeout_minutes = 5
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 
    

class AddCategoriVehi(CreateView):  
    model = CategoVehi      
    form_class = CategorieForm      
    template_name = 'perfect/add_categorie.html'
    success_message = 'Categorie enregistré avec succès👍✓✓'
    error_message = "Erreur de saisie, cette categorie ou cet identifiant existe✘✘"
    success_url= reverse_lazy('add_catego_vehi')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        messages.success(self.request,self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['catego_vehi'] = CategoVehi.objects.all()
        
        return context
    
def delete_catego(request, pk):
    try:
        catego = get_object_or_404(CategoVehi, id=pk)
        catego.delete()
        messages.success(request, f"la categorie de véhicule {catego.category} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_catego_vehi')
    
def CategoVehiculeListView(request, cid):
    categorys= CategoVehi.objects.get(cid=cid)
    cars = Vehicule.objects.filter(category=categorys)
    user_group = request.user.groups.first()
    user_group = user_group.name if user_group else None
    context = {
        'user_group':user_group,
        'categorys':categorys,
        'cars':cars,
    }
    return render(request, 'news/applist/list_vehi_categor.html',context)
