from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

router = DefaultRouter()
router.register(r'tasks', views.TodoViewSet, basename='task')

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('user/', views.get_authenticated_user, name='get_authenticated_user'),
    path('profile/', views.get_user_profile, name='get_user_profile'),
    path('todos/summary/', views.task_summary, name='task_summary'),
    path('', include(router.urls)),
    path('routes/', views.getRoutes, name='api_routes'),
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
]
