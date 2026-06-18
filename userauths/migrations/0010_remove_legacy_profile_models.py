from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0009_user_profile_and_verification'),
        ('PB_Entreprise', '0019_userprofile_merge'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='Comptable',
        ),
        migrations.DeleteModel(
            name='Chefexploitation',
        ),
        migrations.DeleteModel(
            name='Administ',
        ),
    ]
