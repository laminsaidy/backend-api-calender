from django.contrib import admin
from rest_framework import routers
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
router.register(r'tasks', views.TodoView, 'task')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/test/', views.testEndPoint, name='test'),
    path('api/tasks/summary/', views.task_summary, name='task_summary'),  
    path('', views.getRoutes),
]
