from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from todo import views
from django.contrib.auth.models import User 

def home(request):
    return HttpResponse("Welcome to the API!")

# NEW: temporary superuser creation function
def create_superuser(request):
    # Check if a superuser already exists
    if not User.objects.filter(is_superuser=True).exists():
        # CREATE YOUR SUPERUSER 
        User.objects.create_superuser(
            username='admin',              
            email='nimalydias@gmail.com',      
            password='734862@Naasir'         
        )
        return HttpResponse("Superuser created successfully! Please remove this endpoint immediately.")
    return HttpResponse("Superuser already exists. No action taken.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/', include('todo.urls')),
    path('', home, name='home'),
    path('temp-admin-create-123/', create_superuser, name='temp_admin_create'),
]