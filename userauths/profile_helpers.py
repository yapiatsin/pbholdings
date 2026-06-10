from PB_Entreprise.models import UserProfile, Vehicule


def get_user_profile(user):
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return None


def profiles_for_user_type(user_type):
    return UserProfile.objects.filter(user__user_type=str(user_type)).select_related('user')


def ensure_admin_profile(user):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'nom': user.username or '',
            'prenom': user.prenom or '',
            'commune': '',
        },
    )
    return profile, created


PROFILE_FORM_FIELDS = ('nom', 'prenom', 'commune', 'tel1', 'tel2', 'profession', 'gerant_voiture')

USER_TYPE_EMAIL_SUBJECTS = {
    '1': 'Création de Compte Administrateur',
    '2': "Création de Compte de chef d'exploitation",
    '3': 'Création de Compte Comptable',
    '4': 'Création de Compte de Gérant',
}


def save_user_profile(user, profile_form, *, create_by=None, sync_user_names=True):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    cleaned = profile_form.cleaned_data
    fields = getattr(getattr(profile_form, 'Meta', None), 'fields', PROFILE_FORM_FIELDS)
    for field in fields:
        if field == 'gerant_voiture':
            continue
        if field in cleaned:
            setattr(profile, field, cleaned[field])
    if create_by is not None:
        profile.create_by = create_by
    profile.save()
    if user.user_type == '4' and 'gerant_voiture' in cleaned:
        profile.gerant_voiture.set(cleaned.get('gerant_voiture', []))
    elif user.user_type != '4':
        profile.gerant_voiture.clear()
    if sync_user_names:
        user.nom = profile.nom or user.nom
        user.prenom = profile.prenom or user.prenom
        user.save(update_fields=['nom', 'prenom'])
    return profile


def gerant_categories_for_user(user):
    if user.user_type != "4":
        return None
    profile = get_user_profile(user)
    if not profile:
        return None
    return profile.gerant_voiture.all()


def apply_profile_edit_form(user, profile, form):
    user.username = form.cleaned_data['username']
    user.email = form.cleaned_data['email']
    user.gender = form.cleaned_data['gender']
    user.nom = form.cleaned_data.get('nom') or user.nom
    user.prenom = form.cleaned_data.get('prenom') or user.prenom
    user.save(update_fields=['username', 'email', 'gender', 'nom', 'prenom'])
    profile.nom = form.cleaned_data['nom']
    profile.prenom = form.cleaned_data['prenom']
    profile.commune = form.cleaned_data.get('commune')
    profile.tel1 = form.cleaned_data.get('tel1')
    profile.tel2 = form.cleaned_data.get('tel2')
    profile.save()
    if user.user_type == "4":
        profile.gerant_voiture.set(form.cleaned_data.get('gerant_voiture', []))
    return profile


def build_profile_page_context(user):
    from userauths.models import TypeCustomPermission

    user_profile = get_user_profile(user)
    grouped_permissions = {}
    for category in TypeCustomPermission.objects.all():
        perms = category.cat_permis.filter(users=user)
        if perms.exists():
            grouped_permissions[category] = perms
    return {
        'user': user,
        'user_profile': user_profile,
        'admin_profil': user_profile,
        'chefexploit_profil': user_profile,
        'comptable_profil': user_profile,
        'gerant_profil': user_profile,
        'grouped_permissions': grouped_permissions,
        'custom_permissions': user.custom_permissions.all(),
        'system_permissions': user.user_permissions.all(),
    }


def vehicules_for_user(user, queryset=None):
    if queryset is None:
        queryset = Vehicule.objects.filter(car_statut=True)
    if user.user_type != "4":
        return queryset
    categories = gerant_categories_for_user(user)
    if categories is not None and categories.exists():
        return queryset.filter(category__in=categories)
    return Vehicule.objects.none()
