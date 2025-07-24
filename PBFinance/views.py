from django.shortcuts import redirect, render
from datetime import date, datetime, timedelta, timezone
from typing import Any
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView,CreateView, DeleteView, UpdateView, TemplateView
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models import Count
from django.db.models import Sum,F
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from django.contrib.auth import logout

# Create your views here.
class Home(TemplateView):
    template_name = 'pbent/index.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['evenement'] = Evenement.objects.all().order_by('-date_saisie')[:5]
        return context
    
class Apropos(TemplateView):
    template_name = 'pbent/about.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("Apropos")
        return super().dispatch(request, *args, **kwargs)

class Contact(TemplateView):
    template_name = 'pbent/contacts.html' 
    timeout_minutes = 100 
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("service")
        return super().dispatch(request, *args, **kwargs)
#-----------présentation-----------#

class Equip(TemplateView):
    template_name = 'pbent/equipe.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("equipes")
        return super().dispatch(request, *args, **kwargs)


class Identite(TemplateView):
    template_name = 'pbent/identite.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)


class Politiq(TemplateView):
    template_name = 'pbent/politiq.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("politiq_pb")
        return super().dispatch(request, *args, **kwargs)

#-----------Services-----------#
class Vtc(TemplateView):
    template_name = 'pbent/details_vtc.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("vtc")
        return super().dispatch(request, *args, **kwargs)


class Location(TemplateView):
    template_name = 'pbent/details_location.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("locations")
        return super().dispatch(request, *args, **kwargs)
    
class Vent_piece(TemplateView):
    template_name = 'pbent/details_ventepiece.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("event")
        return super().dispatch(request, *args, **kwargs)

class hyrocarbure(TemplateView):
    template_name = 'pbent/details_hydro.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("hyrocarbures")
        return super().dispatch(request, *args, **kwargs)
#-----------media-----------#
class Photos(TemplateView):
    template_name = 'pbent/photo.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("photo")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['tof'] = Photo.objects.all().order_by('-date_saisie')
        return context
    
class AddPhotoView(CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'news/site/add_photo.html'
    success_message = 'Photo Ajoutée avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('addphoto')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
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
        context['user_group'] = user_group.name if user_group else None,
        context['phot'] = Photo.objects.all()
        return context
    
class UpdatPhotoView(UpdateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'news/site/add_photo.html'
    success_message = 'Photo modifiée avec succès👍✓✓'
    success_url = reverse_lazy ('addphoto')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context

class DeletPhotoView(DeleteView):
    model = Photo
    template_name = 'news/site/delet_photo.html' 
    success_message = 'Photo Supprimée avec succès👍✓✓'
    success_url =reverse_lazy ('addphoto')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context

class Videos(TemplateView):
    template_name = 'pbent/video.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("video")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['deo'] = Video.objects.all().order_by('-date_saisie')
        return context

class AddVideoView(CreateView):
    model = Video
    form_class = VideoForm
    template_name = 'news/site/add_video.html'
    success_message = 'Vidéo Ajoutée avec succès👍✓✓'
    success_url = reverse_lazy ('addvideo')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['vid'] = Video.objects.all()
        return context
    
class UpdatVideoView(UpdateView):
    model = Video
    form_class = UpdatVideoForm
    template_name = 'news/site/add_video.html'
    success_message = 'Video modifiée avec succès👍✓✓'
    success_url = reverse_lazy ('addvideo')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context
    
class DeletVideoView(DeleteView):
    model = Video
    template_name = 'news/site/delet_video.html' 
    success_message = 'Video Supprimée avec succès👍✓✓'
    success_url =reverse_lazy ('addvideo')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] =user_group.name if user_group else None
        return context
    
class Evenements(TemplateView):
    template_name = 'pbent/evenement.html'
    ordering = ['-date_saisie']
    paginate_by = 4
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("event")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        #context['event'] = Evenement.objects.all().order_by('-date_saisie')
        events_list = Evenement.objects.all().order_by("-date_saisie")
        paginator = Paginator(events_list, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            events = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            events = paginator.page(paginator.num_pages)
        context['event'] = events
        return context      

class AddEvenementView(CreateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'news/site/add_event.html'
    success_message = 'Evenement Ajouté avec succès👍✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('addevent')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
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
        context['event'] = Evenement.objects.all().order_by('-date_saisie')
        return context
   
class UpdatEvenementView(UpdateView):
    model = Evenement
    form_class = UpdatEvenementForm
    template_name = 'news/site/add_event.html'
    success_message = 'Evenement modifié avec succès👍✓✓'
    success_url = reverse_lazy ('addevent')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context

class DetailEvenementtView(DetailView):
    model = Evenement
    template_name = 'pbent/detail_evenement.html'
    timeout_minutes = 100
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
        context['Event'] = Evenement.objects.all().order_by('-date_saisie')[:5]
        return context
    
class DeletEvenementView(DeleteView):
    model = Evenement
    template_name = 'news/site/delet_event.html' 
    success_message = 'Evenement Supprimé avec succès👍✓✓'
    success_url =reverse_lazy ('addevent')
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        return context 
       
#-----------actualite-----------#
class Activite(TemplateView):
    template_name = 'pbent/activites.html' 
    timeout_minutes = 100
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("service")
        return super().dispatch(request, *args, **kwargs)