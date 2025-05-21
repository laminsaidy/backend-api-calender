from django.contrib import admin
from django.urls import path, include
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