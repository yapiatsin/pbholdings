import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def mark_existing_active_users_verified(apps, schema_editor):
    CustomUser = apps.get_model('userauths', 'CustomUser')
    CustomUser.objects.filter(is_active=True).update(email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0008_password_reset_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='adresse',
            field=models.CharField(blank=True, max_length=200, verbose_name='Adresse'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='date_naissance',
            field=models.DateField(blank=True, null=True, verbose_name='Date de naissance'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email_verified',
            field=models.BooleanField(default=False, verbose_name='Email vérifié'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Email vérifié le'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Dernière activité'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='nom',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nom'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='prenom',
            field=models.CharField(blank=True, max_length=100, verbose_name='Prénom'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='telephone',
            field=models.CharField(
                blank=True,
                help_text='Format international, ex. +2250712345678',
                max_length=20,
                validators=[django.core.validators.RegexValidator(
                    message='Le numéro doit être au format international, ex. +2250712345678 ou +33123456789',
                    regex='^\\+\\d{9,15}$',
                )],
                verbose_name='Téléphone',
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Modifié le'),
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Utilisateur',
                'verbose_name_plural': 'Utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True, verbose_name='Token')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('expires_at', models.DateTimeField(verbose_name='Expire le')),
                ('used', models.BooleanField(default=False, verbose_name='Utilisé')),
                ('used_at', models.DateTimeField(blank=True, null=True, verbose_name='Utilisé le')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='email_verification_tokens',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Token de vérification d\'email',
                'verbose_name_plural': 'Tokens de vérification d\'email',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Adresse IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Localisation')),
                ('login_successful', models.BooleanField(default=True, verbose_name='Connexion réussie')),
                ('failure_reason', models.CharField(blank=True, max_length=200, verbose_name='Raison de l\'échec')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de connexion')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='login_history',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Historique de connexion',
                'verbose_name_plural': 'Historiques de connexion',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PasswordHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_hash', models.CharField(max_length=255, verbose_name='Hash du mot de passe')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de changement')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='password_history',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Historique de mot de passe',
                'verbose_name_plural': 'Historiques de mots de passe',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['user', '-created_at'], name='userauths_l_user_id_6f0a8f_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['ip_address', '-created_at'], name='userauths_l_ip_addr_0d2f0a_idx'),
        ),
        migrations.AddIndex(
            model_name='passwordhistory',
            index=models.Index(fields=['user', '-created_at'], name='userauths_p_user_id_8b2c1a_idx'),
        ),
        migrations.RunPython(mark_existing_active_users_verified, migrations.RunPython.noop),
    ]
