# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
# from api import views

# urlpatterns = [
#     path('token/', views.MyTokenObtainPairView.as_view()),
#     path('token/refresh/', TokenRefreshView.as_view()), 
#     path('register/', views.RegisterView.as_view()),
#     path("dashboard/", views.dashboard), 
#     path("routes/", views.getRoutes),    
#     path("test-endpoint/", views.testEndPoint),  

# ]


from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    path('', views.getRoutes),
]