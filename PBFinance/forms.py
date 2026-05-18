from django import forms
from django.forms import DateInput, inlineformset_factory
from .models import *

# Widget commun pour toutes les dates
class DateInputFr(forms.DateInput):
    input_type = 'date'

# Mixin pour appliquer la classe Bootstrap à tous les champs
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            existing_class = widget.attrs.get('class', '')
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs['class'] = f'{existing_class} form-check-input'.strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = f'{existing_class} form-select'.strip()
            elif isinstance(widget, (forms.FileInput, forms.ClearableFileInput)):
                widget.attrs['class'] = f'{existing_class} form-control'.strip()
            else:
                widget.attrs['class'] = f'{existing_class} form-control'.strip()


def _build_form(model_cls, exclude=None, widgets=None):
    """Factory: génère dynamiquement un ModelForm avec le mixin Bootstrap."""
    meta_attrs = {'model': model_cls}
    if exclude:
        meta_attrs['exclude'] = exclude
    else:
        meta_attrs['fields'] = '__all__'
    if widgets:
        meta_attrs['widgets'] = widgets
    Meta = type('Meta', (), meta_attrs)
    return type(
        f"{model_cls.__name__}Form",
        (BootstrapFormMixin, forms.ModelForm),
        {'Meta': Meta},
    )


# =====================================================================
# FORMULAIRES DE GESTION — un par modèle
# =====================================================================

class SiteConfigForm(BootstrapFormMixin, forms.ModelForm):
    """Configuration globale du site (singleton)."""

    class Meta:
        model = SiteConfig
        exclude = ('date_modification',)
        widgets = {
            'date_creation_entreprise': DateInputFr(),
        }
        help_texts = {
            'date_creation_entreprise': (
                "Date de fondation de l'entreprise. Sert à afficher l'ancienneté sur le site "
                "(ex. page À propos : « 10 ans d'expérience »)."
            ),
        }
LangueForm = _build_form(Langue)
LienApplicationForm = _build_form(LienApplication)


class GainsChauffeurForm(BootstrapFormMixin, forms.ModelForm):
    """Formulaire gestion : ordre 0 = taux horaire Abidjan ; ordre ≥ 1 = paliers hebdomadaires."""

    class Meta:
        model = GainsChauffeur
        fields = '__all__'
        help_texts = {
            'montant': (
                'Montant en F CFA. Ordre 0 : taux horaire précis si pas de « montant de base », sinon valeur de secours / détail. '
                'Ordre ≥ 1 : montant hebdomadaire du bouton.'
            ),
            'montant_base': (
                'Réservé à l’entrée ordre = 0 : montant de base horaire (ex. 3214), affiché sur le site et utilisé pour le calcul du simulateur. '
                'Laisser vide pour n’utiliser que le champ « montant ».'
            ),
            'ordre': (
                '0 = taux horaire de référence à Abidjan (FCFA / heure), une seule entrée active recommandée. '
                '1, 2, 3… = montants des objectifs hebdomadaires affichés comme boutons sur la page Chauffeurs.'
            ),
            'actif': 'Décocher pour retirer cette valeur du simulateur public.',
        }


CategorieOngletForm = _build_form(CategorieOnglet)
SousCategorieOngletForm = _build_form(SousCategorieOnglet)

HeroSlideForm = _build_form(HeroSlide)
PromoSectionForm = _build_form(PromoSection)
PageAccueilForm = _build_form(PageAccueil)
CompteurForm = _build_form(Compteur)
CategorieGestionSectionForm = _build_form(CategorieGestionSection)
GestionSectionForm = _build_form(GestionSection)

# ---- Inline formset : sections rattachées à une catégorie de gestion ----
class _GestionSectionInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GestionSection
        fields = ['titre_section', 'active']

GestionSectionFormSet = inlineformset_factory(
    CategorieGestionSection,
    GestionSection,
    form=_GestionSectionInlineForm,
    fk_name='categorie',
    extra=1,
    can_delete=True,
)

# ---- Inline formset : piliers rattachés à un PageAccueil ----
class _PilierEntrepriseInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PilierEntreprise
        fields = ['titre']

PilierEntrepriseFormSet = inlineformset_factory(
    PageAccueil,
    PilierEntreprise,
    form=_PilierEntrepriseInlineForm,
    extra=1,
    can_delete=True,
)

NosServiceForm = _build_form(NosService)
CategorieServiceForm = _build_form(CategorieService)
CaracteristiqueServiceForm = _build_form(CaracteristiqueService)

# ---- Inline formset : caractéristiques rattachées à une CategorieService ----
class _CaracteristiqueServiceInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CaracteristiqueService
        fields = ['emoji', 'texte', 'ordre']

CaracteristiqueServiceFormSet = inlineformset_factory(
    CategorieService,
    CaracteristiqueService,
    form=_CaracteristiqueServiceInlineForm,
    extra=1,
    can_delete=True,
)

TypeVehiculeLocationForm = _build_form(TypeVehiculeLocation)
VehiculeLocationForm = _build_form(VehiculeLocation)
CaracteristiqueVehiculeLocationForm = _build_form(CaracteristiqueVehiculeLocation)

# ---- Inline formset : caractéristiques rattachées à un VehiculeLocation ----
class _CaracteristiqueVehiculeLocationInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CaracteristiqueVehiculeLocation
        fields = ['texte', 'ordre']

CaracteristiqueVehiculeLocationFormSet = inlineformset_factory(
    VehiculeLocation,
    CaracteristiqueVehiculeLocation,
    form=_CaracteristiqueVehiculeLocationInlineForm,
    extra=1,
    can_delete=True,
)

CategoriePieceForm = _build_form(CategoriePiece)
PieceDetacheeForm = _build_form(PieceDetachee)

ProcessusEtapeForm = _build_form(ProcessusEtape)

PresentationForm = _build_form(Presentation)
PointFortForm = _build_form(PointFort)

AnnonceEvenementForm = _build_form(
    AnnonceEvenement,
    widgets={
        'date_debut': DateInputFr(),
        'date_fin': DateInputFr(),
    },
)
AnnonceInformationForm = _build_form(AnnonceInformation)
BanniereForm = _build_form(Banniere)

ReseauSocialForm = _build_form(ReseauSocial, exclude=('counter', 'date_dernier_clic'))
PartenSponsForm = _build_form(PartenSpons)

TemoignagePageForm = _build_form(TemoignagePage)
TemoignageForm = _build_form(Temoignage)

# ---- Inline formset : témoignages rattachés à une TemoignagePage ----
class _TemoignageInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Temoignage
        fields = ['nom_client', 'role', 'texte', 'photo', 'image_fond', 'badge', 'note', 'ordre', 'actif']

TemoignageFormSet = inlineformset_factory(
    TemoignagePage,
    Temoignage,
    form=_TemoignageInlineForm,
    extra=1,
    can_delete=True,
)

FAQForm = _build_form(FAQ)

EquipeForm = _build_form(Equipe)
AgenceForm = _build_form(Agence)

PageContactForm = _build_form(PageContact)
SujetContactForm = _build_form(SujetContact)
MessageContactForm = _build_form(MessageContact, exclude=['date_envoi', 'ip_address'])

FooterForm = _build_form(Footer)
LiencategoriefooterForm = _build_form(Liencategoriefooter)
LienFooterForm = _build_form(LienFooter)

# ---- Inline formset : liens rattachés à une Liencategoriefooter ----
class _LienFooterInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LienFooter
        fields = ['libelle', 'lien', 'ordre', 'actif']

LienFooterFormSet = inlineformset_factory(
    Liencategoriefooter,
    LienFooter,
    form=_LienFooterInlineForm,
    fk_name='categorie',
    extra=1,
    can_delete=True,
)

ApplicationCarteForm = _build_form(ApplicationCarte)
CategorieApplicationForm = _build_form(CategorieApplication)

# ---- Inline formset : cartes rattachées à une CategorieApplication ----
class _ApplicationCarteInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ApplicationCarte
        fields = ['titre', 'description', 'icone', 'bouton_texte', 'bouton_lien', 'ordre', 'actif']

ApplicationCarteFormSet = inlineformset_factory(
    CategorieApplication,
    ApplicationCarte,
    form=_ApplicationCarteInlineForm,
    fk_name='categorie',
    extra=1,
    can_delete=True,
)

CategorieBlogForm = _build_form(CategorieBlog)
TagBlogForm = _build_form(TagBlog)
ArticleForm = _build_form(
    Article,
    widgets={'date_publication': forms.DateTimeInput(attrs={'type': 'datetime-local'})},
)
CommentaireBlogForm = _build_form(CommentaireBlog)

PageSiteSearchForm = _build_form(PageSiteSearch)
SectionIntroPageForm = _build_form(SectionIntroPage)
# NB : Visite, Clic et StatistiqueAgregee n'ont pas de formulaire —
# ces tables sont alimentées automatiquement par le middleware TrackingMiddleware
# et l'endpoint /track-click/ (voir views.track_click).

# qrcode_image est généré automatiquement dans MonQrcode.save() — exclu du formulaire
MonQrcodeForm = _build_form(MonQrcode, exclude=('qrcode_image',))


# =====================================================================
# CATEGORIPAGE : formulaire principal + formsets imbriqués
# =====================================================================
CategoriPageForm = _build_form(CategoriPage)


class _CaracteristiqueProcedureInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CatacteristiqueProcedure
        fields = [ 'texte', 'ordre', 'actif']


CaracteristiqueProcedureFormSet = inlineformset_factory(
    CategoriPage,
    CatacteristiqueProcedure,
    form=_CaracteristiqueProcedureInlineForm,
    extra=1,
    can_delete=True,
)


class _StatistiqueProcedureInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = StatistiqueProcedure
        fields = ['icone', 'nombre', 'libelle', 'ordre', 'actif']


StatistiqueProcedureFormSet = inlineformset_factory(
    CategoriPage,
    StatistiqueProcedure,
    form=_StatistiqueProcedureInlineForm,
    extra=1,
    can_delete=True,
)


class _QuestionPageInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = QuestionPage
        fields = ['sous_titre', 'titre', 'ordre', 'actif']


QuestionPageFormSet = inlineformset_factory(
    CategoriPage,
    QuestionPage,
    form=_QuestionPageInlineForm,
    extra=1,
    can_delete=True,
)


class _QuestionInlineForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'reponse', 'ordre', 'actif']


# Formset imbriqué sous chaque QuestionPage (niveau 2)
QuestionFormSet = inlineformset_factory(
    QuestionPage,
    Question,
    form=_QuestionInlineForm,
    extra=1,
    can_delete=True,
)
