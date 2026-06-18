from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PBFinance', '0041_rename_lien_appstore_lienapplication_lien_store_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='date_creation_entreprise',
            field=models.DateField(
                blank=True,
                help_text="Utilisée pour afficher l'ancienneté sur le site (ex. page À propos).",
                null=True,
                verbose_name="Date de création de l'entreprise",
            ),
        ),
    ]
