from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from todo import views
from django.http import HttpResponse

# Create a router and register views
router = routers.DefaultRouter()
router.register(r'tasks', views.TodoViewSet, basename='task')

# API URL patterns
api_patterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('', include('todo.urls')), 
]

def home(request):
    return HttpResponse("Welcome to the API!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((api_patterns, 'api'), namespace='api')),
    path('', home, name='home'),  
]
