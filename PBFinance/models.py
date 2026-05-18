from datetime import date
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# =====================================================================
# 1. CONFIGURATION GLOBALE DU SITE
# =====================================================================
class SiteConfig(models.Model):
    """Configuration globale du site (singleton recommandé)."""
    nom_site = models.CharField(max_length=150, default="P&BEntreprise")
    slogan = models.CharField(max_length=250, blank=True)
    logo_principal = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True)
    email_principal = models.EmailField(blank=True)
    bandeau_top = models.CharField(max_length=500, blank=True, help_text="Texte défilant en haut de page")
    date_creation_entreprise = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de création de l'entreprise",
        help_text="Utilisée pour afficher l'ancienneté sur le site (ex. page À propos).",
    )
    actif = models.BooleanField(default=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configuration du site"

    def __str__(self):
        return self.nom_site

    def annees_experience(self, reference=None):
        """Nombre d'années complètes depuis la date de création de l'entreprise."""
        if not self.date_creation_entreprise:
            return None
        ref = reference or date.today()
        creation = self.date_creation_entreprise
        annees = ref.year - creation.year
        if (ref.month, ref.day) < (creation.month, creation.day):
            annees -= 1
        return max(0, annees)

    def libelle_annees_experience(self, reference=None):
        """Libellé prêt à l'affichage : « X ans d'expérience »."""
        annees = self.annees_experience(reference=reference)
        if annees is None:
            return None
        if annees <= 1:
            return "1 an d'expérience"
        return f"{annees} ans d'expérience"

class Langue(models.Model):
    """Langue du site (fr, en, etc.)."""
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Langue"
        verbose_name_plural = "Langues"
        ordering = ['ordre']
    def __str__(self):
        return self.nom

class LienApplication(models.Model):
    """Lien de l'application (Google Play, App Store, Web)."""
    titre = models.CharField(max_length=100)
    image = models.ImageField(upload_to='apps/', blank=True, null=True)
    description = models.TextField(blank=True)
    lien_store = models.URLField(blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Lien application"
        verbose_name_plural = "Liens applications"  

class GainsChauffeur(models.Model):
    """Paramètres du simulateur chauffeur : taux horaire (ordre=0) et paliers hebdo (ordre≥1)."""
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="FCFA : si ordre = 0, taux horaire (précis) ou complément si « montant de base » est rempli ; sinon objectif hebdomadaire.",
    )
    montant_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant de base",
        help_text="Uniquement pour ordre = 0 : taux horaire « rond » affiché et utilisé pour le simulateur (ex. 3214). Vide = utiliser « montant » seul.",
    )
    ordre = models.PositiveIntegerField(
        default=0,
        help_text="0 = taux horaire (une ligne). ≥1 = montants des boutons « revenu souhaité » (semaine), triés.",
    )
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Gains chauffeur"
        verbose_name_plural = "Gains chauffeurs"
        ordering = ['ordre', 'pk']
    def __str__(self):
        if self.montant_base is not None:
            return f"{self.montant} F / base {self.montant_base} F (ordre {self.ordre})"
        return f"{self.montant} F (ordre {self.ordre})"

# =====================================================================
# 17. APPLICATION MOBILE (cartes démo de l'accueil)
# =====================================================================
class CategorieApplication(models.Model):
    """Catégorie d'une application (Client, Chauffeur, Admin, Babicar)."""
    sous_titre = models.CharField(max_length=100, blank=True)
    titre = models.CharField(max_length=100)
    image = models.ImageField(upload_to='apps/', blank=True, null=True)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Catégorie application"
        verbose_name_plural = "Catégories applications" 
        ordering = ['ordre']
    def __str__(self):
        return self.sous_titre

class ApplicationCarte(models.Model):
    """Carte de présentation d'une application (Client, Chauffeur, Admin, Babicar)."""
    categorie = models.ForeignKey(CategorieApplication, on_delete=models.CASCADE, related_name='applications')
    titre = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=100, blank=True, help_text="Classe Font Awesome")
    bouton_texte = models.CharField(max_length=60, default="Voir")
    bouton_lien = models.URLField(blank=True, null=True, help_text="Nom d'URL Django (ex: contact, a_propos), chemin (/contact/), URL absolue (https://...) ou ancre (#section).")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Carte Application"
        verbose_name_plural = "Cartes Applications"
        ordering = ['ordre']
    def __str__(self):
        return self.titre 

# =====================================================================
# 2. MENU / NAVIGATION
# =====================================================================
class CategorieOnglet(models.Model):
    """Catégorie principale du menu (ex: MEDIA, Carrières, À propos)."""
    libelle = models.CharField(max_length=100, verbose_name="Catégorie")
    lien = models.CharField(max_length=500, blank=True, null=True, verbose_name="Lien du contenu (optionnel)", help_text="Chemin interne (ex: /) ou URL complète")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Catégorie onglet"
        verbose_name_plural = "Catégories onglets"
        ordering = ['ordre', 'libelle']
    def __str__(self):
        return self.libelle

class SousCategorieOnglet(models.Model):
    """Sous-catégorie d'un onglet (ex: Photo, Videos sous MEDIA)."""
    categorie = models.ForeignKey(CategorieOnglet, on_delete=models.CASCADE,
                                  related_name='sous_categories',
                                  verbose_name="Catégorie parente")
    libelle = models.CharField(max_length=100, verbose_name="Sous-catégorie")
    lien = models.CharField(max_length=500, blank=True, null=True,
                            verbose_name="Lien du contenu",
                            help_text="Chemin interne (ex: /) ou URL complète")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Sous-catégorie onglet"
        verbose_name_plural = "Sous-catégories onglets"
        ordering = ['categorie', 'ordre', 'libelle']
    def __str__(self):
        return f"{self.categorie.libelle} › {self.libelle}"

# =====================================================================
# 3. PAGE D'ACCUEIL — Hero slider, sections promo, compteurs
# =====================================================================
class HeroSlide(models.Model):
    """Slide du carrousel d'accueil (hero swiper)."""
    sous_titre = models.CharField(max_length=150, blank=True,
                                  help_text="Ex: Confort & Disponibilité")
    titre = models.CharField(max_length=200,
                             help_text="Titre principal (peut contenir <br>)")
    description = models.TextField()
    image_fond = models.ImageField(upload_to='hero/')
    bouton_texte = models.CharField(max_length=60, default="Découvrir")
    bouton_lien = models.CharField(max_length=500, default="#",
                                   help_text="URL ou nom d'URL Django")
    bouton_icone = models.CharField(max_length=80, blank=True,
                                    default="fa-regular fa-arrow-right")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Slide d'accueil (Hero)"
        verbose_name_plural = "Slides d'accueil (Hero)"
        ordering = ['ordre']
    def __str__(self):
        return self.titre

class PromoSection(models.Model):
    """Bloc promo de l'accueil (ex: Transport VTC, Livraison, Pièces)."""
    titre = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='promo/')
    bouton_texte = models.CharField(max_length=60, default="En savoir plus")
    bouton_lien = models.CharField(max_length=500, default="#", help_text="Nom d'URL Django (ex: contact, a_propos), chemin (/contact/), URL absolue (https://...) ou ancre (#section).")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Section promo accueil"
        verbose_name_plural = "Sections promo accueil"
        ordering = ['ordre']
    def __str__(self):
        return self.titre

class PageAccueil(models.Model):
    """Bloc de présentation de la page d'accueil (avec piliers d'entreprise)."""
    sous_titre = models.CharField(max_length=200, blank=True, verbose_name="Sous-titre")
    titre = models.CharField(max_length=250, default='', verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='accueil/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Bloc page d'accueil"
        verbose_name_plural = "Page d'accueil"
        ordering = ['ordre']
    def __str__(self):
        return self.titre

class PilierEntreprise(models.Model):
    """Pilier d'entreprise rattaché à un bloc PageAccueil."""
    pilier = models.ForeignKey(PageAccueil, on_delete=models.CASCADE, related_name='piliers')
    titre = models.CharField(max_length=100, blank=True)
    class Meta:
        verbose_name = "Pilier d'entreprise"
        verbose_name_plural = "Piliers d'entreprise"
    def __str__(self):
        return self.titre or f"Pilier #{self.pk}"

class Compteur(models.Model):
    """Bloc de chiffres clés (chauffeurs, satisfaction, pièces)."""
    sous_titre = models.CharField(max_length=200, blank=True, verbose_name="Sous-titre")
    titre = models.CharField(max_length=250, blank=True, verbose_name="Titre")
    nombre_chauffeur = models.PositiveIntegerField(default=0, verbose_name="Nombre de chauffeurs")
    nombre_satisfaction = models.PositiveIntegerField(default=0, verbose_name="Taux de satisfaction (%)")
    nombre_piece = models.PositiveIntegerField(default=0, verbose_name="Nombre de pièces")
    image = models.ImageField(upload_to='compteurs/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Compteur / Chiffre clé"
        verbose_name_plural = "Compteurs / Chiffres clés"
        ordering = ['ordre']
    def __str__(self):
        return self.titre or f"Compteur #{self.pk}"

# =====================================================================
# 4. SERVICES & CATÉGORIES DE MOBILITÉ
# =====================================================================
class NosService(models.Model):
    """Section Nos Services : libellé, image, description, lien détail."""
    libelle = models.CharField(max_length=200)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    description = models.TextField(blank=True)
    lien_detail = models.CharField(max_length=500, blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Nos Services"
        ordering = ['ordre', 'libelle']
    def __str__(self):
        return self.libelle

class CategorieService(models.Model):
    """Catégorie de service mobilité (Économique, Confort, Confort+, Confort X)."""
    nom = models.CharField(max_length=80, help_text="Ex: Économique, Confort")
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True, help_text="Ex: POUR LES PETITS TRAJETS")
    modeles_vehicules = models.CharField(max_length=300, blank=True, help_text="Ex: Suzuki Alto, Toyota Starlet")
    image = models.ImageField(upload_to='services/categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    bouton_texte = models.CharField(max_length=60, default="Ouvrir dans le navigateur")
    bouton_lien = models.CharField(max_length=500, default="#", help_text="Nom d'URL Django (ex: contact, a_propos), chemin (/contact/), URL absolue (https://...) ou ancre (#section).")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Catégorie de service mobilité"
        verbose_name_plural = "Catégories de services mobilité"
        ordering = ['ordre', 'nom']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom

class CaracteristiqueService(models.Model):
    """Caractéristique d'une catégorie de service (ligne de liste)."""
    categorie = models.ForeignKey(CategorieService, on_delete=models.CASCADE, related_name='caracteristiques')
    emoji = models.CharField(max_length=10, blank=True, help_text="Ex: ⚡ 💰 🟢")
    texte = models.CharField(max_length=250)
    ordre = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name = "Caractéristique de service"
        verbose_name_plural = "Caractéristiques de services"
        ordering = ['categorie', 'ordre']

    def __str__(self):
        return f"{self.categorie.nom} — {self.texte[:40]}"

# =====================================================================
# 5. LOCATION DE VÉHICULES
# =====================================================================
class TypeVehiculeLocation(models.Model):
    """Onglet de type de véhicule (Convertible, Audi, Mercedes, Limousine, Camry)."""
    nom = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    icone_image = models.ImageField(upload_to='location/types/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type de véhicule (location)"
        verbose_name_plural = "Types de véhicules (location)"
        ordering = ['ordre', 'nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom

class VehiculeLocation(models.Model):
    """Véhicule disponible à la location avec ses spécifications."""
    type_vehicule = models.ForeignKey(TypeVehiculeLocation, on_delete=models.CASCADE, related_name='vehicules')
    titre = models.CharField(max_length=100, help_text="Ex: Convertible")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='location/vehicules/')
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unite_prix = models.CharField(max_length=30, default="Par Jour")
    bouton_texte = models.CharField(max_length=60, default="Réserver Maintenant")
    bouton_lien = models.CharField(max_length=500, default="#", help_text="Nom d'URL Django (ex: contact, a_propos), chemin (/contact/), URL absolue (https://...) ou ancre (#section).")
    # Spécifications rapides
    modele = models.CharField(max_length=100, blank=True)
    nb_portes = models.PositiveIntegerField(null=True, blank=True)
    nb_sieges = models.PositiveIntegerField(null=True, blank=True)
    bagages = models.CharField(max_length=80, blank=True)
    transmission_auto = models.BooleanField(default=True)
    climatisation = models.BooleanField(default=True)
    age_minimum = models.PositiveIntegerField(null=True, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Véhicule de location"
        verbose_name_plural = "Véhicules de location"
        ordering = ['ordre', 'titre']
    def __str__(self):
        return f"{self.titre} ({self.type_vehicule.nom})"

class CaracteristiqueVehiculeLocation(models.Model):
    """Caractéristique texte du panneau de location."""
    vehicule = models.ForeignKey(VehiculeLocation, on_delete=models.CASCADE, related_name='features')
    texte = models.CharField(max_length=200)
    ordre = models.PositiveIntegerField(default=0) 
    class Meta:
        ordering = ['ordre']
        verbose_name = "Caractéristique véhicule location"
        verbose_name_plural = "Caractéristiques véhicules location"

    def __str__(self):
        return self.texte

# =====================================================================
# 6. PIÈCES DÉTACHÉES SUZUKI
# =====================================================================
class CategoriePiece(models.Model):
    """Catégorie de pièce Suzuki (Pneus, Freins, Phares, etc.)."""
    nom = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Catégorie de pièce"
        verbose_name_plural = "Catégories de pièces"
        ordering = ['ordre', 'nom']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom

class PieceDetachee(models.Model):
    """Pièce détachée Suzuki mise en avant."""
    categorie = models.ForeignKey(CategoriePiece, on_delete=models.SET_NULL, null=True, blank=True, related_name='pieces')
    titre = models.CharField(max_length=150, help_text="Ex: Pneus Suzuki")
    meta = models.CharField(max_length=100, blank=True, default="Pièces d'origine")
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unite_prix = models.CharField(max_length=30, default="Par Pièce", help_text="Ex: Par Pièce, Par Kg, Par Litre, etc.")
    description = models.TextField()
    image = models.ImageField(upload_to='pieces/')
    lien_detail = models.CharField(max_length=500, default="#")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Pièce détachée"
        verbose_name_plural = "Pièces détachées"
        ordering = ['ordre', 'titre']

    def __str__(self):
        return self.titre

# =====================================================================
# 7. PROCESSUS (étapes : télécharger app, créer compte, validation, etc.)
# =====================================================================
class ProcessusEtape(models.Model):
    """Étape d'un processus (inscription chauffeur, livreur, client)."""
    CIBLE_CHOIX = [
        ('client', 'Client / Passager'),
        ('chauffeur', 'Chauffeur'),
        ('livreur', 'Livreur'),
        ('general', 'Général'),
    ]
    cible = models.CharField(max_length=20, choices=CIBLE_CHOIX, default='general')
    numero = models.PositiveIntegerField(default=1)
    titre = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=100, blank=True, help_text="Classe Font Awesome")
    image = models.ImageField(upload_to='processus/', blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Étape de processus"
        verbose_name_plural = "Étapes de processus"
        ordering = ['cible', 'numero']
    def __str__(self):
        return f"{self.get_cible_display()} - Étape {self.numero}: {self.titre}"

# =====================================================================
# 8. PRÉSENTATION / À PROPOS / POINTS FORTS
# =====================================================================
class Presentation(models.Model):
    """Section Présentation / About de l'accueil."""
    libelle = models.CharField(max_length=200)
    sous_titre = models.CharField(max_length=200, blank=True,
                                  help_text="Ex: Qui Sommes-Nous")
    description = models.TextField()
    image = models.ImageField(upload_to='presentation/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Présentation"
        verbose_name_plural = "Présentations"
        ordering = ['ordre']
    def __str__(self):
        return self.libelle

class PointFort(models.Model):
    """Point fort listé dans la section À propos (numéroté)."""
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE,
                                     related_name='points_forts',
                                     null=True, blank=True)
    numero = models.CharField(max_length=5, default="01",
                              help_text="Ex: 01, 02, 03")
    texte = models.TextField()
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Point fort"
        verbose_name_plural = "Points forts"
        ordering = ['ordre']
    def __str__(self):
        return f"{self.numero} - {self.texte[:50]}"

# =====================================================================
# 9. ANNONCES & BANNIÈRES
# =====================================================================
class AnnonceEvenement(models.Model):
    """Annonce / bandeau évènement (image)."""
    image = models.ImageField(upload_to='annonces/evenements/')
    libelle = models.CharField(max_length=150, blank=True)
    lien = models.URLField(max_length=500, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Annonce évènement"
        verbose_name_plural = "Annonces évènements"
        ordering = ['-date_creation']
    def __str__(self):
        return self.libelle or f"Annonce #{self.pk}"

class AnnonceInformation(models.Model):
    """Annonces et informations (actualités, alertes)."""
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='annonces/infos/', blank=True, null=True)
    date_publication = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Annonce / Information"
        verbose_name_plural = "Annonces & Informations"
        ordering = ['-date_publication']
    def __str__(self):
        return self.titre

class Banniere(models.Model):
    """Bannière : texte + contact."""
    texte = models.TextField()
    contact = models.CharField(max_length=200, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Bannière"
        verbose_name_plural = "Bannières"
    def __str__(self):
        return (self.texte[:50] + "...") if len(self.texte) > 50 else self.texte

# =====================================================================
# 10. RÉSEAUX SOCIAUX, PARTENAIRES, SPONSORS
# =====================================================================
class ReseauSocial(models.Model):
    """Réseaux sociaux : icône + lien + compteur de clics."""
    nom = models.CharField(max_length=50)
    icon = models.CharField(max_length=100, blank=True, help_text="Classe CSS (ex: fa-brands fa-facebook-f)")
    lien = models.URLField(max_length=500)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    counter = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de clics",
        help_text="Nombre total de clics sur l'icône de ce réseau social",
    )
    date_dernier_clic = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date du dernier clic",
        help_text="Date/heure du dernier clic enregistré sur l'icône",
    )
    class Meta:
        verbose_name = "Réseau social"
        verbose_name_plural = "Réseaux sociaux"
        ordering = ['ordre']
    def __str__(self):
        return self.nom

class PartenSpons(models.Model):
    """Partenaire ou sponsor."""
    TYPE_CHOIX = [
        ('partenaire', 'Partenaire'),
        ('sponsor', 'Sponsor'),
    ]
    type_entite = models.CharField(max_length=20, choices=TYPE_CHOIX, default='partenaire')
    nom = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='partenaires_sponsors/', blank=True, null=True)
    lien = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Partenaire / Sponsor"
        verbose_name_plural = "Partenaires & Sponsors"
        ordering = ['type_entite', 'ordre', 'nom']
    def __str__(self):
        return f"{self.get_type_entite_display()} - {self.nom}"

# =====================================================================
# 11. TÉMOIGNAGES CLIENTS
# =====================================================================
class TemoignagePage(models.Model):
    """Slide du carrousel d'accueil (hero swiper)."""
    sous_titre = models.CharField(max_length=150, blank=True,
                                  help_text="Ex: Confort & Disponibilité")
    titre = models.CharField(max_length=200,
                             help_text="Titre principal (peut contenir <br>)")
    description = models.TextField()
    bouton_texte = models.CharField(max_length=60, default="Découvrir")
    bouton_lien = models.CharField(max_length=500, default="#",
                                   help_text="URL ou nom d'URL Django")
    bouton_icone = models.CharField(max_length=80, blank=True,
                                    default="fa-regular fa-arrow-right")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Slide d'accueil (Hero)"
        verbose_name_plural = "Slides d'accueil (Hero)"
        ordering = ['ordre']
    def __str__(self):
        return self.titre

class Temoignage(models.Model):
    """Avis client affiché sur la home et autres pages."""
    temoignage_page = models.ForeignKey(TemoignagePage, on_delete=models.CASCADE, related_name='temoignages')
    BADGE_CHOIX = [
        ('vtc', 'VTC & entreprises'),
        ('pieces', 'Pièces détachées Suzuki'),
        ('taxi', 'Taxi & transferts'),
        ('location', 'Location de véhicules'),
        ('autre', 'Autre'),
    ]
    nom_client = models.CharField(max_length=100)
    role = models.CharField(max_length=150, blank=True, help_text="Ex: Directeur Commercial, Abidjan")
    texte = models.TextField()
    photo = models.ImageField(upload_to='temoignages/', blank=True, null=True)
    image_fond = models.ImageField(upload_to='temoignages/fonds/', blank=True, null=True)
    badge = models.CharField(max_length=20, choices=BADGE_CHOIX, default='vtc')
    note = models.PositiveSmallIntegerField(default=5, help_text="Note sur 5")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Témoignage client"
        verbose_name_plural = "Témoignages clients"
        ordering = ['ordre', '-date_creation'] 
    def __str__(self):
        return f"{self.nom_client} ({self.note}/5)"

# =====================================================================
# 12. FAQ
# =====================================================================
class FAQ(models.Model):
    """Question fréquente (utilisée sur a_propos, clients, chauffeurs)."""
    CIBLE_CHOIX = [
        ('general', 'Général'),
        ('client', 'Passagers / Clients'),
        ('chauffeur', 'Chauffeurs'),
        ('livreur', 'Livreurs'),
        ('pieces', 'Pièces détachées'),
        ('location', 'Location'),
    ]
    cible = models.CharField(max_length=20, choices=CIBLE_CHOIX, default='general', help_text="Page sur laquelle la FAQ apparaît")
    question = models.CharField(max_length=300)
    reponse = models.TextField()
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ['cible', 'ordre']

    def __str__(self):
        return f"[{self.get_cible_display()}] {self.question[:60]}"

# =====================================================================
# 13. ÉQUIPE / CHAUFFEURS
# =====================================================================
class Equipe(models.Model):
    """Membre de l'équipe (direction, staff)."""
    nom = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='equipe/', blank=True, null=True)
    facebook = models.CharField(max_length=500, blank=True, null=True)
    instagram = models.CharField(max_length=500, blank=True, null=True)
    linkedin = models.CharField(max_length=500, blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Membre équipe"
        verbose_name_plural = "Equipes"
        ordering = ['ordre', 'nom']
    def __str__(self):
        return f"{self.nom} - {self.role}"

# =====================================================================
# 14. AGENCES (Koumassi, Bingerville) — carte Leaflet
# =====================================================================
class Agence(models.Model):
    """Agence P&BEntreprise avec géolocalisation pour la carte."""
    nom = models.CharField(max_length=150, help_text="Ex: P&B Entreprise — Bingerville")
    adresse = models.CharField(max_length=300, help_text="Ex: Non loin de AB Center, Bingerville")
    telephone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, help_text="Ex: 5.3617")
    longitude = models.DecimalField(max_digits=9, decimal_places=7, help_text="Ex: -3.8866")
    horaires = models.TextField(blank=True)
    image = models.ImageField(upload_to='agences/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ['ordre', 'nom']
    def __str__(self):
        return self.nom

# =====================================================================
# 15. CONTACT
# =====================================================================
class PageContact(models.Model):
    """Configuration de la page Contact."""
    titre = models.CharField(max_length=200, default="Contactez-nous")
    introduction = models.TextField(blank=True)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    horaires = models.TextField(blank=True)
    carte_embed = models.TextField(blank=True, help_text="Code iframe Google Maps ou autre")
    actif_formulaire = models.BooleanField(default=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Page Contact"
        verbose_name_plural = "Page Contact"
    def __str__(self):
        return self.titre

class SujetContact(models.Model):
    """Sujet disponible dans le formulaire de contact."""
    libelle = models.CharField(max_length=100)
    valeur = models.SlugField(max_length=100, unique=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Sujet de contact"
        verbose_name_plural = "Sujets de contact"
        ordering = ['ordre']
    def __str__(self):
        return self.libelle

class MessageContact(models.Model):
    """Messages envoyés depuis le formulaire de contact."""
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    traite = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    class Meta:
        verbose_name = "Message contact"
        verbose_name_plural = "Messages contact"
        ordering = ['-date_envoi']
    def __str__(self):
        return f"{self.nom} - {self.sujet or self.message[:30]}"

# =====================================================================
# 16. FOOTER
# =====================================================================
class Footer(models.Model):
    """Pied de page (singleton)."""
    localisation_bp = models.CharField(max_length=300, blank=True,verbose_name="Localisation / B.P.")
    contact_1 = models.CharField(max_length=100, blank=True)
    contact_2 = models.CharField(max_length=100, blank=True)
    contact_3 = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    logo = models.CharField(max_length=200, blank=True, help_text="Texte ou nom du logo affiché dans le footer")
    copyright_texte = models.CharField(max_length=300, blank=True,default="Tous droits réservés.")
    ordre = models.PositiveIntegerField(default=1)
    actif = models.BooleanField(default=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footer"
    def __str__(self):
        return "Configuration du footer"

class Liencategoriefooter(models.Model):
    """Lien de la colonne footer (Quick Links, etc.)."""
    libelle = models.CharField(max_length=100)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Lien categorie footer"
        verbose_name_plural = "Liens categorie footer"
        ordering = ['ordre']
    def __str__(self):
        return f"{self.libelle}"

class LienFooter(models.Model):
    """Lien de la colonne footer (Quick Links, etc.)."""
    categorie = models.ForeignKey(Liencategoriefooter, on_delete=models.CASCADE, related_name='liens_categorie_footer')
    libelle = models.CharField(max_length=100)
    lien = models.CharField(max_length=500)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Lien footer"
        verbose_name_plural = "Liens footer"
        ordering = ['categorie', 'ordre']
    def __str__(self):
        return f"{self.categorie} - {self.libelle}"

# =====================================================================
# 18. BLOG — Articles, Catégories, Tags, Commentaires
# =====================================================================
class CategorieBlog(models.Model):
    """Catégorie d'article de blog."""
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Catégorie blog"
        verbose_name_plural = "Catégories blog"
        ordering = ['ordre', 'nom']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom

class TagBlog(models.Model):
    """Tag pour un article de blog."""
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    class Meta:
        verbose_name = "Tag blog"
        verbose_name_plural = "Tags blog"
        ordering = ['nom']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom

class Article(models.Model):
    """Article de blog."""
    titre = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    auteur_nom = models.CharField(max_length=100, blank=True, default="P&BEntreprise", help_text="Nom d'auteur affiché si pas d'utilisateur lié")
    categorie = models.ForeignKey(CategorieBlog, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(TagBlog, blank=True, related_name='articles')
    image_principale = models.ImageField(upload_to='blog/')
    extrait = models.TextField(blank=True, max_length=500, help_text="Résumé affiché dans la liste")
    contenu = models.TextField()
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)
    date_publication = models.DateTimeField(default=timezone.now)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    nb_vues = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    a_la_une = models.BooleanField(default=False, help_text="Afficher en page d'accueil")
    ordre = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles (Blog)"
        ordering = ['ordre', '-date_publication']
        indexes = [models.Index(fields=['slug']), models.Index(fields=['-date_publication'])]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)[:250]
        super().save(*args, **kwargs) 
    def __str__(self):
        return self.titre

class CommentaireBlog(models.Model):
    """Commentaire posté sur un article de blog."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reponses')
    class Meta:
        verbose_name = "Commentaire blog"
        verbose_name_plural = "Commentaires blog"
        ordering = ['-date_creation']
    def __str__(self):
        return f"{self.nom} sur {self.article.titre[:40]}"

# =====================================================================
# 20. STATISTIQUES (visites, clics, pages visitées)
# =====================================================================
class PageSiteSearch(models.Model):
    """Référentiel de pages pour stats."""
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    url_path = models.CharField(max_length=300, blank=True, help_text="Chemin ou pattern d'URL")
    class Meta:
        verbose_name = "Page (référentiel)"
        verbose_name_plural = "Pages (référentiel)"
    def __str__(self):
        return self.nom

class Visite(models.Model):
    """Enregistrement d'une visite."""
    page = models.ForeignKey(PageSiteSearch, on_delete=models.SET_NULL, null=True, blank=True, related_name='visites')
    url_visitee = models.CharField(max_length=500)
    titre_page = models.CharField(max_length=200, blank=True)
    date_visite = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    class Meta:
        verbose_name = "Visite"
        verbose_name_plural = "Visites"
        ordering = ['-date_visite']
        indexes = [
            models.Index(fields=['date_visite']),
            models.Index(fields=['url_visitee']),
        ] 
    def __str__(self):
        return f"{self.url_visitee} - {self.date_visite}"

class Clic(models.Model):
    """Enregistrement d'un clic (bouton, lien, CTA)."""
    element = models.CharField(max_length=200, verbose_name="Élément cliqué (id, texte, lien)")
    url_page = models.CharField(max_length=500, blank=True)
    date_clic = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    class Meta:
        verbose_name = "Clic"
        verbose_name_plural = "Clics"
        ordering = ['-date_clic']
        indexes = [
            models.Index(fields=['date_clic']),
            models.Index(fields=['element']),
        ]
    def __str__(self):
        return f"{self.element} - {self.date_clic}"

class StatistiqueAgregee(models.Model):
    """Statistiques pré-agrégées (optionnel, perf)."""
    PERIODE_CHOIX = [
        ('jour', 'Journalier'),
        ('mois', 'Mensuel'),
        ('annee', 'Annuel'),
    ]
    periode = models.CharField(max_length=10, choices=PERIODE_CHOIX)
    date_debut = models.DateField()
    date_fin = models.DateField()
    url_visitee = models.CharField(max_length=500, blank=True)
    nombre_visites = models.PositiveIntegerField(default=0)
    nombre_clics = models.PositiveIntegerField(default=0)
    date_maj = models.DateTimeField(auto_now=True) 
    class Meta:
        verbose_name = "Statistique agrégée"
        verbose_name_plural = "Statistiques agrégées"
        unique_together = [['periode', 'date_debut', 'url_visitee']]
        indexes = [models.Index(fields=['periode', 'date_debut'])]
    def __str__(self):
        return f"{self.get_periode_display()} {self.date_debut} - {self.url_visitee or 'global'}"

##########################################################################################################################
################################################## Gestion des pages autres pages ########################################
##########################################################################################################################
#Comment devenir chauffeur clients, autres
class CategoriPage(models.Model):
    """Catégorie de demande (location, pièces, service, etc.)."""
    sous_titre = models.CharField(max_length=200)
    titre = models.CharField(max_length=250)
    page = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Catégorie de procédure"
        verbose_name_plural = "Catégories de procédures"
        ordering = ['ordre', 'page']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.page)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.page

class CatacteristiqueProcedure(models.Model):
    page = models.ForeignKey(CategoriPage, on_delete=models.CASCADE, related_name='caracteristiques')
    texte = models.CharField(max_length=200)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Caractéristique de procédure"
        verbose_name_plural = "Caractéristiques de procédures"
        ordering = ['page', 'ordre']
    def __str__(self):
        return self.texte

#### les valeurs clées par page
class StatistiqueProcedure(models.Model):
    page = models.ForeignKey(CategoriPage, on_delete=models.CASCADE, related_name='statistiques')
    icone = models.CharField(max_length=100, blank=True, null=True, help_text="Classe Font Awesome (ex: fa-solid fa-location-dot)")
    nombre = models.CharField(max_length=200)
    libelle = models.CharField(max_length=200)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Statistique de procédure"
        verbose_name_plural = "Statistiques de procédures"
        ordering = ['ordre']
    def __str__(self):
        return f"{self.page.page} - {self.libelle}"

class QuestionPage(models.Model):
    page = models.ForeignKey(CategoriPage, on_delete=models.CASCADE, related_name='question')
    sous_titre = models.CharField(max_length=200)
    titre = models.CharField(max_length=250)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Page de question"
        verbose_name_plural = "Pages de questions"
        ordering = ['ordre']
    def __str__(self):
        return f"{self.page.page} - {self.titre}"

class Question(models.Model):
    section = models.ForeignKey(QuestionPage, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=200)
    reponse = models.TextField()
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['ordre']
    def __str__(self):
        return f"{self.section.page} - {self.question}"

# PAGE_CHAUFFEURS = 'chauffeurs'
    # PAGE_LIVREUR = 'livreur'
    # PAGE_CLIENTS = 'clients'
    # PAGE_ASSISTANCE = 'assistance'
    # PAGE_SERVICES = 'services'
    # PAGE_CHOICES = [
    #     (PAGE_CHAUFFEURS, "Chauffeurs"),
    #     (PAGE_LIVREUR, "Livreur"),
    #     (PAGE_CLIENTS, "Clients"),
    #     (PAGE_ASSISTANCE, "Assistance"),
    #     (PAGE_SERVICES, "Services"),
    # ]
class SectionIntroPage(models.Model):
    """Blocs texte + image en haut des pages Chauffeurs, Livreur, Clients (ordre, position)."""
    POS_GAUCHE = 'gauche'
    POS_DROITE = 'droite'
    POSITION_CHOICES = [
        (POS_GAUCHE, "Image à gauche, texte à droite"),
        (POS_DROITE, "Image à droite, texte à gauche"),
    ]
    page = models.ForeignKey(CategoriPage, on_delete=models.CASCADE, related_name='sections_intro')
    ordre = models.PositiveIntegerField(default=0)
    sous_titre = models.CharField(max_length=200)
    titre = models.CharField(max_length=250)
    texte = models.TextField()
    image = models.ImageField(upload_to='pages_intro/', blank=True, null=True)
    position_image = models.CharField(max_length=10, choices=POSITION_CHOICES, default=POS_DROITE, help_text="Côté de l'image (le texte se place de l'autre côté).",)
    classes_section = models.CharField(max_length=200, blank=True, help_text="Classes CSS supplémentaires sur la balise <section> (ex. : pb-120).",)
    actif = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Section d'intro (page contenu)"
        verbose_name_plural = "Sections d'intro (pages contenu)"
        ordering = ['page', 'ordre', 'pk']
    def __str__(self):
        return f"{self.page} — {self.sous_titre} (ordre {self.ordre})"

# =====================================================================
# QR CODES — génération à la volée d'un QR code à partir d'un lien
# =====================================================================
class MonQrcode(models.Model):
    """QR code généré automatiquement à partir d'un lien.
    L'utilisateur saisit :
      - un titre (libellé du QR code)
      - un lien (URL ou texte à encoder)
      - une description optionnelle
    Le champ ``qrcode_image`` est généré/régénéré automatiquement à
    chaque sauvegarde à partir de ``lien``.
    """
    titre = models.CharField(max_length=150, help_text="Nom interne du QR code (ex: 'Lien Google Play')")
    lien = models.CharField(max_length=500, help_text="URL ou texte à encoder dans le QR code")
    description = models.TextField(blank=True, null=True,
                                   help_text="Description ou note interne (optionnel)")
    qrcode_image = models.ImageField(upload_to='qrcodes/generes/', blank=True, null=True,
                                     editable=False, help_text="QR code généré automatiquement")
    couleur = models.CharField(max_length=20, default="#000000",
                               help_text="Couleur du QR code (hex, ex: #000000)")
    couleur_fond = models.CharField(max_length=20, default="#FFFFFF",
                                    help_text="Couleur du fond (hex, ex: #FFFFFF)")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        ordering = ['ordre', '-date_creation']

    def __str__(self):
        return self.titre

    def _generer_qrcode(self):
        """Construit l'image PNG du QR code à partir de self.lien.
        Retourne un ContentFile prêt à être assigné à qrcode_image.
        """
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(self.lien or '')
        qr.make(fit=True)

        couleur = self.couleur or '#000000'
        couleur_fond = self.couleur_fond or '#FFFFFF'
        img = qr.make_image(fill_color=couleur, back_color=couleur_fond).convert('RGB')

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        nom_fichier = f"qrcode_{slugify(self.titre) or 'sans-titre'}.png"
        return nom_fichier, ContentFile(buffer.getvalue())

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            kwargs.pop('force_insert', None)
        nom_fichier, contenu = self._generer_qrcode()
        self.qrcode_image.save(nom_fichier, contenu, save=False)
        super().save(*args, **kwargs)

# =====================================================================
# 21. GESTION DE LA VISIBILITÉ DES SECTIONS (toutes pages)
# =====================================================================
class CategorieGestionSection(models.Model):
    """Regroupe les sections par zone/page (home, chauffeurs, clients, etc.)."""
    code = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Identifiant technique unique (ex: home, chauffeurs, livreur, clients)",
    )
    libelle = models.CharField(max_length=120, help_text="Nom affiché en administration")
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Catégorie gestion section"
        verbose_name_plural = "Catégories gestion sections"
        ordering = ['ordre', 'libelle']
    def __str__(self):
        return f"{self.libelle} ({self.code})"

class GestionSection(models.Model):
    """Pilote la visibilité d'une section donnée sur une page donnée."""
    categorie = models.ForeignKey(
        CategorieGestionSection,
        on_delete=models.PROTECT,
        related_name='sections',
        null=True,
        blank=True,
        verbose_name="Catégorie de page",
    )
    titre_section = models.CharField(
        max_length=80,
        verbose_name="Section concernée",
        help_text="Clé technique de section (ex: promo, nos_services, hero, faq, etc.)",
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Section visible",
        help_text="Décochez pour masquer la section sur le site public.",
    )
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gestion de section (accueil)"
        verbose_name_plural = "Gestion des sections (accueil)"
        ordering = ['categorie__ordre', 'titre_section']
        unique_together = [['categorie', 'titre_section']]

    def __str__(self):
        etat = "visible" if self.active else "masquée"
        if self.categorie:
            return f"{self.categorie.libelle} / {self.titre_section} — {etat}"
        return f"{self.titre_section} — {etat}"
