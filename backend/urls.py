from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from rest_framework import routers
from todo import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import the create_admin view
from todo.views import create_admin, MyTokenObtainPairView

router = routers.DefaultRouter()
router.register(r'tasks', views.TodoView, 'task')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Updated to use custom token view
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/routes/', views.getRoutes, name='api_routes'),
    path('create-admin/', create_admin),  # Moved into main urlpatterns
]
=======
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    """Simple health check endpoint"""
    return HttpResponse("Welcome to the API!")

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Include todo app URLs
    path('api/', include('todo.urls')),  # This will include all todo app URLs
    
    # Health check/root endpoint
    path('', home, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> main
