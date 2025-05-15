from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from todo import views
from django.contrib.auth import get_user_model  # CHANGED: Use this instead

def home(request):
    return HttpResponse("Welcome to the API!")

# UPDATED SUPERUSER CREATION FUNCTION
def create_superuser(request):
    try:
        User = get_user_model()  # Gets your custom User model
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='temp@example.com',  # Change this
                password='TempPass123!'     # Change this
            )
            return HttpResponse("Superuser created successfully! Please remove this endpoint immediately.")
        return HttpResponse("Superuser already exists.")
        
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/', include('todo.urls')),
    path('', home, name='home'),
    path('temp-admin-create-123/', create_superuser),  # Keep this obscure
]