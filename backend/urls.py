from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from todo import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  


# Create a router and register the TodoView
router = routers.DefaultRouter()
router.register(r'tasks', views.TodoView, 'task')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('api/routes/', views.getRoutes, name='api_routes'),  
]
