from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Todo

# Customizing the admin interface for Todo model
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description', 'user__email')

# Registering the Todo model with the customized TodoAdmin
admin.site.register(Todo, TodoAdmin)

# Customizing the admin interface for User model
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)



# Customizing the admin interface for Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'verified')
    list_editable = ('verified',)
    search_fields = ('user__email', 'full_name')

# Registering the Profile model with the customized ProfileAdmin
admin.site.register(Profile, ProfileAdmin)