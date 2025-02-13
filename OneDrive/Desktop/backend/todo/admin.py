from django.contrib import admin
from todo.models import User, Profile  # Importing User and Profile models from the todo app

from .models import Todo  # Importing the Todo model


# Customizing the admin interface for Todo model
class TodoAdmin(admin.ModelAdmin):
    # Display fields in the list view of the Todo model
    list_display = ('title', 'description', 'status')  # Change 'completed' to 'status'
 


# Registering the Todo model with the customized TodoAdmin
admin.site.register(Todo, TodoAdmin)  


# Customizing the admin interface for User model
class UserAdmin(admin.ModelAdmin):
    # Display the username and email in the list view of the User model
    list_display = ['username', 'email']  


# Customizing the admin interface for Profile model
class ProfileAdmin(admin.ModelAdmin):
    # Display user, full name, and verified status in the list view of Profile model
    list_display = ['user', 'full_name', 'verified']  
    # Allow editing the verified status directly in the list view
    list_editable = ['verified', ]  


# Registering the User and Profile models with their customized admin interfaces
admin.site.register(User, UserAdmin)  
admin.site.register(Profile, ProfileAdmin)  
