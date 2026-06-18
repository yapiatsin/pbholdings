from django.db import migrations, models


def add_home_categorie(apps, schema_editor):
    CategorieOnglet = apps.get_model('PBFinance', 'CategorieOnglet')
    CategorieOnglet.objects.update_or_create(
        libelle="Accueil",
        defaults={'lien': '/', 'ordre': 1, 'actif': True},
    )


def remove_home_categorie(apps, schema_editor):
    CategorieOnglet = apps.get_model('PBFinance', 'CategorieOnglet')
    CategorieOnglet.objects.filter(libelle="Accueil", lien='/').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('PBFinance', '0003_agence_applicationcarte_article_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorieonglet',
            name='lien',
            field=models.CharField(
                blank=True,
                null=True,
                max_length=500,
                verbose_name="Lien du contenu (optionnel)",
                help_text="Chemin interne (ex: /) ou URL complète",
            ),
        ),
        migrations.RunPython(add_home_categorie, reverse_code=remove_home_categorie),
    ]
