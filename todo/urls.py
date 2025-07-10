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
    path('todos/summary/', views.task_summary, name='task_summary'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('routes/', views.getRoutes, name='api_routes'),
    path('', include(router.urls)),
]
