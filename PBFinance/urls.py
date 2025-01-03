from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('',Home.as_view(), name='home'),
    path('identites', Apropos.as_view(), name='Apropos'),
    path('contacts', Contact.as_view(), name='contact'),
    
    path('equips', Equip.as_view(), name='equipes'),
    path('politiqs', Politiq.as_view(), name='politiq_pb'),
    
    path('Vtcs', Vtc.as_view(), name='vtc'),
    path('VentPiec', Vent_piece.as_view(), name='ventpiec'),
    path('Locations', Location.as_view(), name='locations'),
    path('Hyrocarbures', hyrocarbure.as_view(), name='hyrocarbures'),
    
    path('Photos', Photos.as_view(), name='photo'),
    path('add_photo', AddPhotoView.as_view(), name='addphoto'),
    path('photo/<int:pk>/modifier', UpdatPhotoView.as_view(), name='updatphoto'),
    path('photo/<int:pk>/supprimer', DeletPhotoView.as_view(), name='deletphoto'),
    
    path('Videos', Videos.as_view(), name='video'),
    path('add_video', AddVideoView.as_view(), name='addvideo'),
    path('video/<int:pk>/modifier', UpdatVideoView.as_view(), name='updatvideo'),
    path('video/<int:pk>/supprimer', DeletVideoView.as_view(), name='deletvideo'),
    
    path('Events', Evenements.as_view(), name='event'),
    path('add_event', AddEvenementView.as_view(), name='addevent'),
    path('event/<int:pk>/modifier', UpdatEvenementView.as_view(), name='updatevent'),
    path('event/<int:pk>/supprimer', DeletEvenementView.as_view(), name='deletevent'),
    path('event/<int:pk>/detail', DetailEvenementtView.as_view(), name='detailtevent'),
    
    path('Service', Activite.as_view(), name='service'),
]
