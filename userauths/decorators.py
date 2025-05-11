#decorators.py
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from userauths.models import CustomPermission

def custom_permission_required(permission_url):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')  # ou ta page d’erreur personnalisée

            # Vérifie si l'utilisateur a la permission avec cette URL
            has_permission = user.custom_permissions.filter(url=permission_url).exists()
            if not has_permission:
                raise PermissionDenied("Vous n'avez pas la permission d'accéder à cette ressource.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
