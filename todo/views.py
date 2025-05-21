from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.conf import settings
import logging

from .models import Profile, Todo
from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer
)
from .authentication import CookieJWTAuthentication  # Add this import

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
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
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

class MyTokenObtainPairView(APIView):
    """
    Custom token obtain view that sets JWT in HttpOnly cookies
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable default authentication

    def post(self, request):
        try:
            serializer = MyTokenObtainPairSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })

            # Set secure HttpOnly cookies
            response.set_cookie(
                key='access',
                value=access_token,
                httponly=True,
                secure=not DEBUG,
                samesite='None' if not DEBUG else 'Lax',
                max_age=24 * 3600  # 1 day
            )
            response.set_cookie(
                key='refresh',
                value=str(refresh),
                httponly=True,
                secure=not DEBUG,
                samesite='None' if not DEBUG else 'Lax',
                max_age=7 * 24 * 3600  # 7 days
            )

            return add_cors_headers(response)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {"detail": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Endpoint to log out by clearing JWT cookies"""
    response = Response({"message": "Successfully logged out"})
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return add_cors_headers(response)

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            Profile.objects.create(user=user)

            # Automatically log in the new user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
            
            # Set cookies
            response.set_cookie(
                'access', 
                access_token, 
                httponly=True, 
                secure=not DEBUG, 
                samesite='None' if not DEBUG else 'Lax',
                max_age=24 * 3600
            )
            response.set_cookie(
                'refresh', 
                str(refresh), 
                httponly=True, 
                secure=not DEBUG, 
                samesite='None' if not DEBUG else 'Lax',
                max_age=7 * 24 * 3600
            )
            
            return add_cors_headers(response)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# -----------------------
# TODO VIEWS
# -----------------------
class TodoViewSet(viewsets.ModelViewSet):
    """
    Viewset for Todo CRUD operations with cookie-based authentication
    """
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        """Return only the authenticated user's todos"""
        return Todo.objects.filter(user=self.request.user)\
                         .order_by('-due_date', 'priority')

    def perform_create(self, serializer):
        """Automatically set the current user when creating a todo"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Custom endpoint to update task status"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Todo.STATUS_CHOICES).keys():
            return Response(
                {'detail': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()
        return Response(self.get_serializer(task).data)

# -----------------------
# PROFILE VIEW
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Endpoint to get current user's profile"""
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response(
            {"detail": "Error fetching profile"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# -----------------------
# DEBUG VIEWS
# -----------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_routes(request):
    """Endpoint to list available API routes (for debugging)"""
    routes = [
        {'endpoint': '/api/token/', 'methods': 'POST', 'description': 'Login endpoint'},
        {'endpoint': '/api/logout/', 'methods': 'POST', 'description': 'Logout endpoint'},
        {'endpoint': '/api/register/', 'methods': 'POST', 'description': 'User registration'},
        {'endpoint': '/api/todos/', 'methods': 'GET,POST', 'description': 'List/create todos'},
        {'endpoint': '/api/todos/<id>/', 'methods': 'GET,PUT,PATCH,DELETE', 'description': 'Todo detail'},
        {'endpoint': '/api/profile/', 'methods': 'GET', 'description': 'User profile'},
        {'endpoint': '/api/csrf/', 'methods': 'GET', 'description': 'Get CSRF token'},
    ]
    return Response(routes)