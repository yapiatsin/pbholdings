# Migration : compteur de tentatives de connexion + date de blocage automatique

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0006_alter_customuser_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='failed_login_attempts',
            field=models.PositiveIntegerField(
                default=0,
                help_text="Nombre d'échecs de connexion consécutifs. Le compte est désactivé automatiquement après 3 tentatives.",
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='date_blocage',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="Date à laquelle le compte a été bloqué automatiquement.",
            ),
        ),
    ]
