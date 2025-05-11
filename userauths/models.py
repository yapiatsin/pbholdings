from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import PermissionsMixin
from django.db.models import Q
from shortuuid.django_fields import ShortUUIDField
from django.conf import settings

USER=(
    ("1","Administrateur"),
    ("2","ChefExploitation"),
    ("3","Comptable"),
    ("4","Gerant"),
    )

GERER_CAR_SELECTION = (
    ('VTC', 'VTC'),
    ('TAXI', 'TAXI'),
)

GENDER_SELECTION = (
    ('Homme', 'Homme'),
    ('Femme', 'Femme'),
)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null= False)
    username = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_SELECTION)
    user_type=models.CharField(default="1", choices=USER, max_length=20)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    def __str__(self):
        return '%s - %s ' %(self.username, self.email,)

class TypeCustomPermission(models.Model):
    cid = ShortUUIDField(unique=True, length=6, prefix='pb-', alphabet="abcd1234", editable=False)
    categorie = models.CharField(max_length=100)
    def __str__(self):
        return self.categorie

class CustomPermission(models.Model):
    name = models.CharField(max_length=100)
    categorie = models.ForeignKey(TypeCustomPermission, on_delete=models.CASCADE,related_name='cat_permis')
    url = models.CharField(max_length=255)
    users = models.ManyToManyField(CustomUser, related_name='custom_permissions', blank=True)
    def __str__(self):
        return self.name

class Administ(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='administs')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=30)
    commune = models.CharField(max_length=255, null=True, blank=True)
    tel1 = models.CharField(max_length=255, null=True, blank=True)
    tel2 = models.CharField(max_length=255, null=True, blank=True)
    date_creation=models.DateField(auto_now_add=True)
    objects = models.Manager()
    def __str__(self):
        return '%s - %s' % (self.user.username, self.nom)
    
class Chefexploitation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='ads')
    create_by = models.ForeignKey(Administ, on_delete=models.CASCADE, related_name="adminchef")
    nom = models.CharField(max_length=255, null=True, blank=True)
    prenom = models.CharField(max_length=30)
    commune = models.CharField(max_length=255, null=True, blank=True)
    tel1 = models.CharField(max_length=255, null=True, blank=True)
    tel2 = models.CharField(max_length=255, null=True, blank=True)
    date_creation=models.DateField(auto_now_add=True)
    objects = models.Manager()
    def __str__(self):
        return '%s - %s - %s ' %(self.nom, self.user.user_type,  self.user.username)
    
class Comptable(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='cmpt')
    create_by = models.ForeignKey(Administ, on_delete=models.CASCADE, related_name="admincomptables")
    nom = models.CharField(max_length=255, null=True, blank=True)
    prenom = models.CharField(max_length=30)
    # date_naissance = models.DateField()
    commune = models.CharField(max_length=255, null=True, blank=True)
    tel1 = models.CharField(max_length=255, null=True, blank=True)
    tel2 = models.CharField(max_length=255, null=True, blank=True)
    date_creation=models.DateField(auto_now_add=True)
    objects = models.Manager()
    def __str__(self):
        return '%s - %s - %s '%(self.nom, self.user.user_type,  self.user.username)
    
class Gerant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='gerants')
    create_by = models.ForeignKey(Administ, on_delete=models.CASCADE, related_name="admingerants")
    gerant_voiture = models.CharField(max_length=20, choices=GERER_CAR_SELECTION)
    nom = models.CharField(max_length=255,)
    prenom = models.CharField(max_length=30,)
    commune = models.CharField(max_length=255, null=True, blank=True)
    tel1 = models.CharField(max_length=255, null=True, blank=True)
    tel2 = models.CharField(max_length=255, null=True, blank=True)
    date_creation=models.DateField(auto_now_add=True)
    objects = models.Manager()
    def __str__(self):
        return '%s - %s - %s ' %(self.nom, self.user.user_type, self.user.username)

class PWD_FORGET(models.Model):
    otp = models.IntegerField()
    status = models.CharField(max_length=1 ,default="0")
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    creat_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '%s - %s ' %(self.user_id.username, self.user_id.email)

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profession = models.CharField(max_length=50, null=True, blank="True")
    gender = models.CharField(max_length=20, choices=GENDER_SELECTION)
    commune = models.CharField(max_length=50, null=True, blank="True")
    def __str__(self):
        return f'{self.user.username}'
    