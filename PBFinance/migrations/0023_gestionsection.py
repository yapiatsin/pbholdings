# Generated for GestionSection (visibilité des sections de la page d'accueil)

from django.db import migrations, models


SECTIONS_PAR_DEFAUT = [
    'promo',
    'nos_services',
    'compteur',
    'vehicule_location',
    'piece_detachee',
    'temoignage',
]


def seed_gestion_sections(apps, schema_editor):
    """Crée une ligne (active=True) pour chaque section pilotable."""
    GestionSection = apps.get_model('PBFinance', 'GestionSection')
    for code in SECTIONS_PAR_DEFAUT:
        GestionSection.objects.get_or_create(
            titre_section=code,
            defaults={'active': True},
        )


def remove_gestion_sections(apps, schema_editor):
    GestionSection = apps.get_model('PBFinance', 'GestionSection')
    GestionSection.objects.filter(titre_section__in=SECTIONS_PAR_DEFAUT).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('PBFinance', '0022_remove_monqrcode_image_monqrcode_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='GestionSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'titre_section',
                    models.CharField(
                        choices=[
                            ('promo', 'Sections promo (PromoSection)'),
                            ('nos_services', 'Nos services (NosService)'),
                            ('compteur', 'Chiffres clés / Compteurs'),
                            ('vehicule_location', 'Location de véhicules (VehiculeLocation)'),
                            ('piece_detachee', 'Pièces détachées (PieceDetachee)'),
                            ('temoignage', 'Témoignages (TemoignagePage)'),
                        ],
                        help_text="Section de la page d'accueil à activer ou masquer.",
                        max_length=50,
                        unique=True,
                        verbose_name='Section concernée',
                    ),
                ),
                (
                    'active',
                    models.BooleanField(
                        default=True,
                        help_text='Décochez pour masquer la section sur le site public.',
                        verbose_name='Section visible',
                    ),
                ),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Gestion de section (accueil)',
                'verbose_name_plural': 'Gestion des sections (accueil)',
                'ordering': ['titre_section'],
            },
        ),
        migrations.RunPython(seed_gestion_sections, remove_gestion_sections),
    ]
