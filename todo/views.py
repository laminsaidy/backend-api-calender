from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse
from django.conf import settings
import logging

from .models import Profile, Todo
from .serializers import (
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer,
    UserSerializer
)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email  # add custom claim if you want
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


User = get_user_model()
logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def add_cors_headers(response):
    """Add CORS headers to responses"""
    response["Access-Control-Allow-Origin"] = settings.FRONTEND_URL
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken"
    response["Access-Control-Allow-Credentials"] = "true"
    return response

# -----------------------
# AUTHENTICATION VIEWS
# -----------------------

@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Endpoint to get CSRF token"""
    response = Response({'message': 'CSRF cookie set'})
    return add_cors_headers(response)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Session-based login"""
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)

    if user:
        login(request, user)  # Django session login
        logger.info("User logged in: %s", user.email)
        return add_cors_headers(Response({
            "message": "Logged in successfully",
            "user": UserSerializer(user).data
        }))
    else:
        logger.warning("Failed login attempt for email: %s", email)
        return add_cors_headers(Response({
            "detail": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Session-based logout"""
    logout(request)
    logger.info("User logged out: %s", request.user)
    response = Response({"message": "Successfully logged out"})
    response.delete_cookie('csrftoken')
    return add_cors_headers(response)

class RegisterView(generics.CreateAPIView):
    """
    User registration with session login
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.create(user=user)
        login(request, user)  # auto-login using session
        logger.info("User registered and logged in: %s", user.email)
        return add_cors_headers(Response({
            'user': UserSerializer(user).data,
            'message': 'Registered and logged in'
        }, status=status.HTTP_201_CREATED))

# -----------------------
# TODO VIEWS (session-based auth)
# -----------------------
class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).order_by('-due_date', 'priority')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Todo.STATUS_CHOICES).keys():
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status
        task.save()
        return Response(self.get_serializer(task).data)

# -----------------------
# PROFILE VIEW
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}", exc_info=True)
        return Response(
            {"detail": "Error fetching profile"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# -----------------------
# DEBUG ROUTES
# -----------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_routes(request):
    routes = [
        {'endpoint': '/api/csrf/', 'methods': 'GET', 'description': 'Get CSRF token'},
        {'endpoint': '/api/login/', 'methods': 'POST', 'description': 'Login endpoint'},
        {'endpoint': '/api/logout/', 'methods': 'POST', 'description': 'Logout endpoint'},
        {'endpoint': '/api/register/', 'methods': 'POST', 'description': 'User registration'},
        {'endpoint': '/api/todos/', 'methods': 'GET,POST', 'description': 'List/create todos'},
        {'endpoint': '/api/todos/<id>/', 'methods': 'GET,PUT,PATCH,DELETE', 'description': 'Todo detail'},
        {'endpoint': '/api/profile/', 'methods': 'GET', 'description': 'User profile'},
    ]
    return Response(routes)
