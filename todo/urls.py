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
]
