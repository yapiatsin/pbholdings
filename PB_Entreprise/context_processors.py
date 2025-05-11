#context_processors.py
from userauths.models import TypeCustomPermission

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
