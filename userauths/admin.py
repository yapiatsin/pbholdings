from django.contrib import admin
from userauths.models import *


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email','gender','user_type']
    list_filter = ['username','email','gender','user_type']
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TypeCustomPermission)
admin.site.register(CustomPermission)
admin.site.register(Chefexploitation)
admin.site.register(Comptable)
admin.site.register(Administ)
admin.site.register(Gerant)

