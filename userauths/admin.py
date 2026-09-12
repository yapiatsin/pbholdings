from django.contrib import admin
from userauths.models import *


class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'gender', 'user_type', 'email_verified',
        'failed_login_attempts', 'is_active', 'date_blocage',
    ]
    list_filter = [
        'user_type', 'email_verified', 'is_active', 'gender',
    ]
    search_fields = ['username', 'email', 'nom', 'prenom']


class TypeCustomPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'categorie', 'cid']
    search_fields = ['categorie', 'cid']


class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'categorie', 'url']
    list_filter = ['categorie']
    search_fields = ['name', 'url']
    # Évite le widget M2M massif (users) qui peut faire planter l'add en prod
    fields = ['name', 'categorie', 'url']
    filter_horizontal = ()
    autocomplete_fields = ['categorie']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TypeCustomPermission, TypeCustomPermissionAdmin)
admin.site.register(CustomPermission, CustomPermissionAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(LoginHistory)
admin.site.register(PasswordHistory)
admin.site.register(PasswordResetOTP)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'user', 'type_notif', 'categorie', 'lu', 'created_at']
    list_filter = ['type_notif', 'categorie', 'lu', 'created_at']
    search_fields = ['titre', 'message', 'user__email']
    readonly_fields = ['created_at']
