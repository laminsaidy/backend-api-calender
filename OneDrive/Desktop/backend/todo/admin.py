from django.contrib import admin
from todo.models import User, Profile  

from .models import Todo 


class TodoAdmin(admin.ModelAdmin):  
    list_display = ('title', 'description', 'completed')  


# Register your models here.
admin.site.register(Todo, TodoAdmin)  




class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']  


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'verified']  
    list_editable = ['verified', ]  


admin.site.register(User, UserAdmin)  
admin.site.register(Profile, ProfileAdmin)  