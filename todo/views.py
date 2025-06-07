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
    UserProfileSerializer,
    UserSerializer,
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer
)
from django.conf import settings

User = get_user_model()

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_admin(request):
    if not settings.DEBUG:
        return Response(
            {"error": "This endpoint is only available in development mode"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="StrongAdminPass456"
            )
            return Response(
                {"message": "Superuser created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Superuser already exists"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    return Response({'message': 'CSRF cookie set'})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
            Profile.objects.create(user=user)
            return Response({
                "success": "User registered successfully",
                "user": {
                    "email": user.email,
                    "username": user.username
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).order_by('-due_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response(
            {"detail": "Profile does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'endpoint': '/api/tasks/', 'methods': 'GET,POST', 'description': 'List/create todos'},
        {'endpoint': '/api/token/', 'methods': 'POST', 'description': 'JWT token obtain'},
        {'endpoint': '/api/register/', 'methods': 'POST', 'description': 'User registration'},
        {'endpoint': '/api/token/refresh/', 'methods': 'POST', 'description': 'JWT token refresh'},
        {'endpoint': '/api/profile/', 'methods': 'GET', 'description': 'User profile'},
        {'endpoint': '/health/', 'methods': 'GET', 'description': 'Health check'},
    ]
    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_summary(request):
    tasks = Todo.objects.filter(user=request.user)
    summary = {
        'open': tasks.filter(status='Open').count(),
        'in_progress': tasks.filter(status='In Progress').count(),
        'done': tasks.filter(status='Done').count(),
    }
    return Response(summary, status=status.HTTP_200_OK)