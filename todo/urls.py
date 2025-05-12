from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.TodoViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('routes/', views.get_routes, name='api_routes'),
    path('profile/', views.get_user_profile, name='user_profile'),
]
