from django.db import models
from userauths.models import CustomUser

class Video(models.Model):
    title = models.CharField(max_length =50)
    video = models.FileField(upload_to ='video/%y')
    date = models.DateField(auto_now_add=True)
    date_saisie = models.DateField()
    def __str__(self):
        return '%s - %s' % (self.title, self.video)

class Photo(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to ='photo')
    date = models.DateField(auto_now_add=True)
    date_saisie = models.DateField()
    def __str__(self):
        return '%s - %s' % (self.title, self.image)

class Evenement(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='author_events')
    title = models.CharField(max_length =50)
    image = models.FileField(upload_to='evenement')
    text = models.TextField(max_length=5000)
    date_saisie = models.DateField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s - %s - %s' % (self.title, self.image, self.auteur)

