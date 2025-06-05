from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from todo import views
from todo.views import create_admin, MyTokenObtainPairView

# Router for API endpoints
router = routers.DefaultRouter()
router.register(r'tasks', views.TodoView, 'task')

def home(request):
    """Simple health check endpoint"""
    return HttpResponse("Welcome to the API!")

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/routes/', views.getRoutes, name='api_routes'),
    
    # Admin creation endpoint
    path('create-admin/', create_admin),
    
    # Health check/root endpoint
    path('', home, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)