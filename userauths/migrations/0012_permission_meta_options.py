# Generated manually for Meta options on permission models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0011_notification_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custompermission',
            options={
                'ordering': ['categorie__categorie', 'name'],
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions',
            },
        ),
        migrations.AlterModelOptions(
            name='typecustompermission',
            options={
                'ordering': ['categorie'],
                'verbose_name': 'Catégorie de permission',
                'verbose_name_plural': 'Catégories de permissions',
            },
        ),
    ]
