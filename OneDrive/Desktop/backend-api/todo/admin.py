from django.contrib import admin
from todo.models import User, Profile  

from .models import Todo  


# Customizing the admin interface for Todo model
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'status')  
 


# Registering the Todo model with the customized TodoAdmin
admin.site.register(Todo, TodoAdmin)  


# Customizing the admin interface for User model
class UserAdmin(admin.ModelAdmin):
    # Display the username and email in the list view of the User model
    list_display = ['username', 'email']  


# Customizing the admin interface for Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'verified']  
    list_editable = ['verified', ]  


# Registering the User and Profile models with their customized admin interfaces
admin.site.register(User, UserAdmin)  
admin.site.register(Profile, ProfileAdmin)  
