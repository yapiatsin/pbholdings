from django.db import migrations


def use_url_name(apps, schema_editor):
    """Fait pointer l'entrée Accueil sur le nom d'URL Django 'home'
    (résolu dynamiquement via reverse() / le filter pb_link)."""
    CategorieOnglet = apps.get_model('PBFinance', 'CategorieOnglet')
    CategorieOnglet.objects.filter(libelle="Accueil", lien='/').update(lien='home')


def revert_url_name(apps, schema_editor):
    CategorieOnglet = apps.get_model('PBFinance', 'CategorieOnglet')
    CategorieOnglet.objects.filter(libelle="Accueil", lien='home').update(lien='/')


class Migration(migrations.Migration):

    dependencies = [
        ('PBFinance', '0006_alter_annonceevenement_lien_alter_partenspons_lien_and_more'),
    ]

    operations = [
        migrations.RunPython(use_url_name, reverse_code=revert_url_name),
    ]
