import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_to_unified_profile(apps, schema_editor):
    UserProfile = apps.get_model('PB_Entreprise', 'UserProfile')
    Administ = apps.get_model('userauths', 'Administ')
    Chefexploitation = apps.get_model('userauths', 'Chefexploitation')
    Comptable = apps.get_model('userauths', 'Comptable')
    OldUserProfile = apps.get_model('userauths', 'UserProfile')
    Gerant = apps.get_model('PB_Entreprise', 'Gerant')

    administ_user_map = {
        row['id']: row['user_id']
        for row in Administ.objects.values('id', 'user_id')
    }

    old_profile_map = {
        row['user_id']: row
        for row in OldUserProfile.objects.values('user_id', 'profession', 'commune')
    }

    def old_extra(user_id):
        return old_profile_map.get(user_id, {})

    for admin in Administ.objects.all():
        extra = old_extra(admin.user_id)
        UserProfile.objects.update_or_create(
            user_id=admin.user_id,
            defaults={
                'nom': admin.nom or '',
                'prenom': admin.prenom or '',
                'commune': admin.commune or extra.get('commune'),
                'tel1': admin.tel1,
                'tel2': admin.tel2,
                'profession': extra.get('profession'),
                'date_creation': admin.date_creation,
            },
        )

    for chef in Chefexploitation.objects.all():
        extra = old_extra(chef.user_id)
        UserProfile.objects.update_or_create(
            user_id=chef.user_id,
            defaults={
                'nom': chef.nom or '',
                'prenom': chef.prenom or '',
                'commune': chef.commune or extra.get('commune'),
                'tel1': chef.tel1,
                'tel2': chef.tel2,
                'profession': extra.get('profession'),
                'create_by_id': administ_user_map.get(chef.create_by_id),
                'date_creation': chef.date_creation,
            },
        )

    for comptable in Comptable.objects.all():
        extra = old_extra(comptable.user_id)
        UserProfile.objects.update_or_create(
            user_id=comptable.user_id,
            defaults={
                'nom': comptable.nom or '',
                'prenom': comptable.prenom or '',
                'commune': comptable.commune or extra.get('commune'),
                'tel1': comptable.tel1,
                'tel2': comptable.tel2,
                'profession': extra.get('profession'),
                'create_by_id': administ_user_map.get(comptable.create_by_id),
                'date_creation': comptable.date_creation,
            },
        )

    for gerant in Gerant.objects.all():
        extra = old_extra(gerant.user_id)
        profile, _ = UserProfile.objects.update_or_create(
            user_id=gerant.user_id,
            defaults={
                'nom': gerant.nom or '',
                'prenom': gerant.prenom or '',
                'commune': gerant.commune or extra.get('commune'),
                'tel1': gerant.tel1,
                'tel2': gerant.tel2,
                'profession': extra.get('profession'),
                'create_by_id': administ_user_map.get(gerant.create_by_id),
                'date_creation': gerant.date_creation,
            },
        )
        category_ids = list(gerant.gerant_voiture.values_list('pk', flat=True))
        if category_ids:
            profile.gerant_voiture.set(category_ids)

    for old in OldUserProfile.objects.all():
        if UserProfile.objects.filter(user_id=old.user_id).exists():
            continue
        UserProfile.objects.create(
            user_id=old.user_id,
            commune=old.commune,
            profession=old.profession,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0009_user_profile_and_verification'),
        ('PB_Entreprise', '0018_historicalbilletage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, verbose_name='Nom')),
                ('prenom', models.CharField(blank=True, max_length=100, verbose_name='Prénom')),
                ('commune', models.CharField(blank=True, max_length=255, null=True, verbose_name='Commune')),
                ('tel1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Téléphone 1')),
                ('tel2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Téléphone 2')),
                ('profession', models.CharField(blank=True, max_length=50, null=True, verbose_name='Profession')),
                ('date_creation', models.DateField(auto_now_add=True, verbose_name='Date de création')),
                (
                    'create_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='profiles_created',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Créé par',
                    ),
                ),
                (
                    'gerant_voiture',
                    models.ManyToManyField(
                        blank=True,
                        related_name='gerant_profiles',
                        to='PB_Entreprise.categovehi',
                        verbose_name='Catégories gérées (gérant)',
                    ),
                ),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='profile',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Utilisateur',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Profil utilisateur',
                'verbose_name_plural': 'Profils utilisateurs',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.RunPython(migrate_to_unified_profile, migrations.RunPython.noop),
        migrations.DeleteModel(
            name='Gerant',
        ),
    ]
