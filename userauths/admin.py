from django.contrib import admin
from userauths.models import *

class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'gender', 'user_type', 'email_verified',
        'failed_login_attempts', 'is_active', 'date_blocage',
    ]
    list_filter = [
        'username', 'email', 'gender', 'user_type', 'email_verified',
        'failed_login_attempts', 'is_active', 'date_blocage',
    ]

class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'categorie', 'url']
    list_filter = ['name', 'categorie', 'url']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TypeCustomPermission)
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
