import random
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from shortuuid.django_fields import ShortUUIDField

USER = (
    ("1", "Administrateur"),
    ("2", "ChefExploitation"),
    ("3", "Comptable"),
    ("4", "Gerant"),
)

GENDER_SELECTION = (
    ('Homme', 'Homme'),
    ('Femme', 'Femme'),
)

PHONE_INVALID_MESSAGE = (
    "Le numéro doit être au format international, ex. +2250712345678 ou +33123456789"
)

class CustomUser(AbstractUser):
    nom = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    prenom = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    adresse = models.CharField(max_length=200, blank=True, verbose_name="Adresse")
    email = models.EmailField(unique=True, null=False, verbose_name="Email")
    username = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_SELECTION)
    user_type = models.CharField(default="1", choices=USER, max_length=20)
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    telephone = models.CharField(
        max_length=20, blank=True, verbose_name="Téléphone",
        validators=[RegexValidator(regex=r'^\+\d{9,15}$', message=PHONE_INVALID_MESSAGE,),],
        help_text="Format international, ex. +2250712345678",
    )
    email_verified = models.BooleanField(default=False, verbose_name="Email vérifié")
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Email vérifié le")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="Dernière activité")
    is_active = models.BooleanField(default=False, verbose_name="Actif/Inactif")
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Nombre d'échecs de connexion consécutifs. Le compte est désactivé automatiquement après 3 tentatives.",
    )
    date_blocage = models.DateTimeField(
        null=True, blank=True,
        help_text="Date à laquelle le compte a été bloqué automatiquement.",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name='customuser_permissions',blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']
    def __str__(self):
        return self.email
    @property
    def nom_complet(self):
        if self.nom or self.prenom:
            return f"{self.prenom} {self.nom}".strip()
        return self.username or self.email
    @property
    def age(self):
        if not self.date_naissance:
            return None
        today = timezone.localdate()
        years = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            years -= 1
        return max(years, 0)

class TypeCustomPermission(models.Model):
    cid = ShortUUIDField(unique=True, length=6, prefix='pb-', alphabet="abcd1234", editable=False)
    categorie = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Catégorie de permission'
        verbose_name_plural = 'Catégories de permissions'
        ordering = ['categorie']

    def __str__(self):
        return self.categorie


class CustomPermission(models.Model):
    name = models.CharField(max_length=100)
    categorie = models.ForeignKey(TypeCustomPermission, on_delete=models.CASCADE, related_name='cat_permis')
    url = models.CharField(max_length=255)
    users = models.ManyToManyField(CustomUser, related_name='custom_permissions', blank=True)
    def __str__(self):
        return self.name

class PasswordResetOTP(models.Model):
    """OTP de 6 chiffres pour la réinitialisation de mot de passe (valide 5 minutes)."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='password_reset_otps',
        verbose_name="Utilisateur",
    )
    otp = models.CharField(max_length=6, verbose_name="OTP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    expires_at = models.DateTimeField(verbose_name="Expire le")
    used = models.BooleanField(default=False, verbose_name="Utilisé")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Utilisé le")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    attempts = models.IntegerField(default=0, verbose_name="Tentatives de vérification")
    class Meta:
        verbose_name = "OTP de réinitialisation"
        verbose_name_plural = "OTPs de réinitialisation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['otp', 'expires_at']),
        ]
    def __str__(self):
        return f"OTP pour {self.user.email} - {self.otp}"
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)
    def is_valid(self):
        return (
            not self.used
            and timezone.now() < self.expires_at
            and self.attempts < 5
        )
    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])

class EmailVerificationToken(models.Model):
    """Token pour la vérification d'email à la création de compte."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        verbose_name="Utilisateur",
    )
    token = models.CharField(max_length=64, unique=True, verbose_name="Token")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    expires_at = models.DateTimeField(verbose_name="Expire le")
    used = models.BooleanField(default=False, verbose_name="Utilisé")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Utilisé le")
    class Meta:
        verbose_name = "Token de vérification d'email"
        verbose_name_plural = "Tokens de vérification d'email"
        ordering = ['-created_at']
    def __str__(self):
        return f"Token vérification pour {self.user.email} - {self.token[:10]}..."

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

class LoginHistory(models.Model):
    """Historique des connexions des utilisateurs."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='login_history',
        verbose_name="Utilisateur",
    )
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    location = models.CharField(max_length=200, blank=True, verbose_name="Localisation")
    login_successful = models.BooleanField(default=True, verbose_name="Connexion réussie")
    failure_reason = models.CharField(max_length=200, blank=True, verbose_name="Raison de l'échec")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de connexion")
    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    def __str__(self):
        status = "Réussi" if self.login_successful else "Échoué"
        return f"{self.user.email} - {status} - {self.created_at}"

class PasswordHistory(models.Model):
    """Historique des mots de passe pour empêcher la réutilisation."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='password_history',
        verbose_name="Utilisateur",
    )
    password_hash = models.CharField(max_length=255, verbose_name="Hash du mot de passe")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de changement")
    class Meta:
        verbose_name = "Historique de mot de passe"
        verbose_name_plural = "Historiques de mots de passe"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    def __str__(self):
        return f"Mot de passe de {self.user.email} - {self.created_at}"


class Notification(models.Model):
    """Notification in-app pour un utilisateur (hors superadmin)."""

    TYPE_CHOICES = (
        ('info', 'Information'),
        ('alert', 'Alerte véhicule'),
        ('compte', 'Compte'),
        ('system', 'Système'),
    )

    CATEGORIE_CHOICES = (
        ('visite', 'Visite technique'),
        ('entretien', 'Entretien'),
        ('assurance', 'Assurance'),
        ('vignette', 'Vignette'),
        ('patente', 'Patente'),
        ('stationnement', 'Stationnement'),
        ('compte_bloque', 'Compte bloqué'),
        ('compte_reset', 'Réinitialisation compte'),
        ('compte_actif', 'Compte activé'),
        ('autre', 'Autre'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire',
    )
    titre = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    lien = models.CharField(max_length=500, blank=True, verbose_name='Lien')
    type_notif = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name='Type',
    )
    categorie = models.CharField(
        max_length=30,
        choices=CATEGORIE_CHOICES,
        default='autre',
        blank=True,
        verbose_name='Catégorie',
    )
    dedupe_key = models.CharField(max_length=120, blank=True, verbose_name='Clé unique')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Métadonnées')
    lu = models.BooleanField(default=False, verbose_name='Lu')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'lu', '-created_at']),
            models.Index(fields=['user', 'dedupe_key']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'dedupe_key'],
                condition=models.Q(dedupe_key__gt=''),
                name='unique_user_notification_dedupe',
            ),
        ]

    def __str__(self):
        return f'{self.titre} → {self.user.email}'

    @property
    def jours_label(self):
        jours = (self.metadata or {}).get('jours')
        if jours is None:
            return ''
        return f'{jours} j'

