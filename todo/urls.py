<<<<<<< HEAD
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('tasks/summary/', views.task_summary, name='task_summary'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/statistics/', views.view_statistics, name='view_statistics'),
    path('', views.getRoutes, name='get_routes'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test/', views.testEndPoint, name='test'),
=======
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from . import views

router = DefaultRouter()
router.register(r'todos', views.TodoViewSet, basename='todo')

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('csrf/', views.get_csrf_token, name='csrf'),

    path('', include(router.urls)),
    path('profile/', views.get_user_profile, name='profile'),
>>>>>>> main
]
