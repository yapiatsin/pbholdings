# userauths/mixins.py
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

class CustomPermissionRequiredMixin:
    permission_url = None
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not self.permission_url:
            raise ValueError("permission_url must be defined in the view.")

        if not request.user.custom_permissions.filter(url=self.permission_url).exists():
            #raise PermissionDenied("Accès interdit.")
            return HttpResponse("""
                            <!DOCTYPE html>
                            <html lang="fr">
                            <head>
                                <meta charset="UTF-8">
                                <title>Accès interdit</title>
                                <style>
                                    body {
                                        margin: 0;
                                        padding: 0;
                                        background-color: #f5f5f5;
                                        font-family: Arial, sans-serif;
                                        height: 100vh;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                    }
                                    .card {
                                        background-color: #fff;
                                        padding: 40px;
                                        border-radius: 10px;
                                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                                        text-align: center;
                                        max-width: 400px;
                                        width: 100%;
                                    }
                                    h1 {
                                        color: #c00;
                                        margin-bottom: 15px;
                                    }
                                    p {
                                        margin-bottom: 25px;
                                        font-size: 16px;
                                        color: #555;
                                    }
                                    .btn {
                                        display: inline-block;
                                        padding: 12px 20px;
                                        background-color: #c00;
                                        color: #fff;
                                        text-decoration: none;
                                        border-radius: 6px;
                                        transition: background-color 0.3s ease;
                                    }
                                    .btn:hover {
                                        background-color: #a00;
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="card">
                                    <h1>Accès interdit</h1>
                                    <p>Vous n'avez pas la permission d'accéder à cette page.</p>
                                    <a href="/auths/deconnexion" class="btn">Se déconnecter</a>
                                    <p>P&BEntreprise</p>
                                </div>
                            </body>
                            </html>
                            """)
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('login')
