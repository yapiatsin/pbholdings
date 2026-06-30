#context_processors.py
from userauths.models import TypeCustomPermission


def navbar_context(request):
    """Contexte navbar : profil et libellé de rôle."""
    if not request.user.is_authenticated:
        return {}
    from userauths.profile_helpers import (
        ensure_user_profile,
        refresh_user_profile_cache,
        user_initials,
        user_avatar_url,
    )
    refresh_user_profile_cache(request.user)
    profile = ensure_user_profile(request.user)
    if profile is not None:
        profile.refresh_from_db(fields=['avatar', 'prenom', 'nom'])
    role_labels = {
        '1': 'Admin',
        '2': 'Chef exploitation',
        '3': 'Comptable',
        '4': 'Gérant',
    }
    user_type = str(request.user.user_type)
    return {
        'navbar_profile': profile,
        'navbar_role_label': role_labels.get(user_type, request.user.username),
        'user_initials': user_initials(request.user, profile),
        'user_avatar_url': user_avatar_url(profile),
    }


def grouped_user_permissions(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    grouped_permissions = {}

    for category in TypeCustomPermission.objects.all():
        perms = category.cat_permis.filter(users=user)
        if perms.exists():
            grouped_permissions[category] = perms

    return {
        'grouped_permissions': grouped_permissions
    }


def _user_wants_site_notifications(user):
    try:
        return user.profile.notif_site
    except Exception:
        return True


def alertes_count(request):
    """Notifications navbar (alertes véhicules + compte) pour le rendu initial."""
    empty = {'total_alertes': 0, 'alertes_list': [], 'notifications_unread': 0}
    if not request.user.is_authenticated or not _user_wants_site_notifications(request.user):
        return empty
    try:
        from userauths.notification_utils import notifications_payload
        payload = notifications_payload(request.user, limit=15)
        alertes_list = []
        for item in payload['notifications']:
            label = item.get('label') or item.get('titre', '')
            vehicule = item.get('vehicule', '')
            jours = item.get('jours')
            alertes_list.append({
                'id': item['id'],
                'type': label,
                'vehicule': vehicule,
                'jours': jours if jours is not None else '',
                'lien': item.get('lien', ''),
                'lu': item.get('lu', False),
                'type_notif': item.get('type_notif', 'info'),
                'categorie': item.get('categorie', ''),
                'titre': item.get('titre', ''),
                'message': item.get('message', ''),
                'created_at': item.get('created_at', ''),
            })
        return {
            'total_alertes': payload['unread_count'],
            'notifications_unread': payload['unread_count'],
            'alertes_list': alertes_list,
        }
    except Exception:
        return empty
