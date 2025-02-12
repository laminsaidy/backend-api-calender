from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from todo import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # Add this import

# Create a router and register the TodoView
router = routers.DefaultRouter()
router.register(r'tasks', views.TodoView, 'task')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Include the router under 'api/'
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Add this
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Add this
]