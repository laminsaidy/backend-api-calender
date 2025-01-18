from django.contrib import admin
from api.models import User, Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']  # Columns shown in the user admin list


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'verified']  # Columns shown in the profile admin list
    list_editable = ['verified', ]  # Fields editable in the admin list view


admin.site.register(User, UserAdmin)  # Register the User model
admin.site.register(Profile, ProfileAdmin)  # Register the Profile model
