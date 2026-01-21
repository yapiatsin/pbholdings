# userauths/mixins.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

class CustomPermissionRequiredMixin:
    permission_url = None
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not self.permission_url:
            raise ValueError("permission_url must be defined in the view.")

        if not request.user.custom_permissions.filter(url=self.permission_url).exists():
            #raise PermissionDenied("Accès interdit.")
            return render(request, 'no_acces.html', status=403)
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('login')
