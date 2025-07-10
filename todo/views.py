from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Profile, Todo
from .serializers import (
    ProfileSerializer,
    UserSerializer,
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer
)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

@api_view(['GET'])
def health_check(request):
    """Endpoint for service health verification"""
    return Response(
        {"status": "ok", "service": "todo-api", "version": "1.0.0"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_admin(request):
    """Development-only endpoint for admin creation"""
    if not settings.DEBUG:
        return Response(
            {"error": "This endpoint is only available in development mode"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        if User.objects.filter(email="admin@example.com").exists():
            return Response(
                {"message": "Superuser already exists"},
                status=status.HTTP_200_OK
            )

        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongAdminPass456"
        )
        return Response(
            {"message": "Superuser created successfully"},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MyTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with extended user data"""
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Endpoint to get CSRF token for forms"""
    return Response(
        {'message': 'CSRF cookie set'},
        status=status.HTTP_200_OK
    )

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            Profile.objects.create(user=user)

            return Response({
                "status": "success",
                "message": "User registered successfully",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username
                    }
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "errors": serializer.errors if hasattr(serializer, 'errors') else None
            }, status=status.HTTP_400_BAD_REQUEST)

class TodoViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for Todo items"""
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's todos"""
        return Todo.objects.filter(user=self.request.user).order_by('-due_date')

    def perform_create(self, serializer):
        """Automatically set the current user as todo owner"""
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get profile data for authenticated user"""
    try:
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    except ObjectDoesNotExist:
        return Response(
            {
                "status": "error",
                "message": "Profile does not exist",
                "data": None
            },
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def getRoutes(request):
    """API endpoint documentation"""
    routes = [
        {
            'endpoint': '/api/token/',
            'methods': 'POST',
            'description': 'Obtain JWT token pair',
            'authentication': False
        },
        {
            'endpoint': '/api/token/refresh/',
            'methods': 'POST',
            'description': 'Refresh JWT token',
            'authentication': False
        },
        {
            'endpoint': '/api/register/',
            'methods': 'POST',
            'description': 'Register new user',
            'authentication': False
        },
        {
            'endpoint': '/api/todos/',
            'methods': 'GET,POST',
            'description': 'List/create todos',
            'authentication': True
        },
        {
            'endpoint': '/api/todos/<id>/',
            'methods': 'GET,PUT,PATCH,DELETE',
            'description': 'Retrieve/update/delete todo',
            'authentication': True
        },
        {
            'endpoint': '/api/profile/',
            'methods': 'GET',
            'description': 'Get user profile',
            'authentication': True
        },
        {
            'endpoint': '/health/',
            'methods': 'GET',
            'description': 'Service health check',
            'authentication': False
        }
    ]
    return Response(
        {"status": "success", "data": routes},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_summary(request):
    """Get summary statistics for user's todos"""
    tasks = Todo.objects.filter(user=request.user)

    summary = {
        'total': tasks.count(),
        'open': tasks.filter(status='Open').count(),
        'in_progress': tasks.filter(status='In Progress').count(),
        'done': tasks.filter(status='Done').count(),
        'overdue': tasks.filter(due_date__lt=timezone.now(), status__in=['Open', 'In Progress']).count()
    }

    return Response(
        {"status": "success", "data": summary},
        status=status.HTTP_200_OK
    )
