from django.urls import path
from . import views

urlpatterns = [
    path('routes/', views.get_routes, name='api_routes'),
    path('profile/', views.get_user_profile, name='user_profile'),
    path('tasks/add/', views.TaskAPIView.as_view(), name='add_task'),
    # Add any additional URL patterns specific to the `todo` app here
]
