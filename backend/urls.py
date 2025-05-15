from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from todo import views
from django.contrib.auth import get_user_model  # Added for secure user model access

def home(request):
    return HttpResponse("Welcome to the API!")

# TEMPORARY ADMIN RESET FUNCTION (SECURE VERSION)
def secure_admin_reset(request):
    try:
        User = get_user_model()
        
        # Delete existing admin if exists
        User.objects.filter(username='your_new_admin').delete()
        
        # Create new superuser with secure credentials
        User.objects.create_superuser(
            username='admin',          
            email='nimalydias@gmail.com',  
            password='734862@Naasir'          
        )
        return HttpResponse("""
            Admin credentials reset successfully!<br><br>
            <strong>IMPORTANT:</strong><br>
            1. Log in at /admin/<br>
            2. Immediately remove this endpoint<br>
            3. Change password again in admin panel
        """)
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
    
    # TEMPORARY SECURE ENDPOINT - ADD THIS LAST
    path('emergency-admin-reset-9xY9/', secure_admin_reset, name='emergency_reset'),  # Obscure URL
]