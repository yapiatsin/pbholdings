# from gtts import gTTS
import os
import threading
import time
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models import Q

logger = logging.getLogger(__name__)

def send_email_with_html_body(subjet:str, receivers:list, template:str, context:dict):
    ##la fonction qui aide a envoyer les email a des users specifique
    try:
        message = render_to_string(template, context)
        send_mail(
            subjet,
            message,
            settings.EMAIL_HOST_USER,
            receivers,
            fail_silently=True,
            html_message=message
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
    return False

#utils
def search_vehicules(queryset, search_query):
    """
    Filtre les véhicules selon l'immatriculation, le numéro de carte grise ou le numéro de châssis
    """
    if search_query:
        queryset = queryset.filter(
            Q(immatriculation__icontains=search_query) |
            Q(num_cart_grise__icontains=search_query) |
            Q(num_Chassis__icontains=search_query) |
            Q(marque__icontains=search_query)
        )
    return queryset


#logging.basicConfig(level=logging.INFO)
##la fonction de suppression
#def delete_file_after_delay(filename, delay):
#    time.sleep(delay)
#    if os.path.exists(filename):
#        os.remove(filename)
        
#def generate_greeting(username):
#    directory = 'media/welcome'
#    if not os.path.exists(directory):
#        os.makedirs(directory)
#    
#    text = f"Bienvenue {username} à Health smart"
#    filename = os.path.join(directory, f"{username}.mp4")
#    tts = gTTS(text=text, lang='fr')
#    tts.save(filename)
#    #supprimer le fichier générer après 10s
#    delay = 10
#    threading.Thread(target=delete_file_after_delay, args=(filename, delay)).start()
#    return filename
#
##la fonction de goodBye
#def generate_goodbye(username):
#    directory = 'media/goodbye'
#    if not os.path.exists(directory):
#        os.makedirs(directory)
#    
#    text = f"Au revoir et à bientôt {username}"
#    filename = os.path.join(directory, f"{username}.mp3")
#    tts = gTTS(text=text, lang='fr')
#    tts.save(filename)
#    #suppression apres 10s
#    delay = 10
#    threading.Thread(target=delete_file_after_delay, args=(filename, delay)).start()
#    return filename    
    
    
    



