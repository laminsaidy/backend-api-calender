from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
import logging
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
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

User = get_user_model()
logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG

def add_cors_headers(response):
    response["Access-Control-Allow-Origin"] = settings.FRONTEND_URL
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken"
    response["Access-Control-Allow-Credentials"] = "true"
    return response

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
                {"message": "✅ Superuser created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "ℹ️ Superuser already exists"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Superuser creation error: {str(e)}", exc_info=True)
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
    response = Response({'message': 'CSRF cookie set'})
    return add_cors_headers(response)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if password != password2:
            return Response(
                {"error": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            Profile.objects.get_or_create(user=user)

            return Response(
                {
                    "message": "User registered successfully",
                    "user": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).order_by('-due_date')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Task creation error: {str(e)}", exc_info=True)
            raise

    @action(detail=False, methods=['post'])
    def add_task(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def taskManager(request):
    user = request.user
    try:
        profile = user.profile
        data = {
            "username": user.username,
            "email": user.email,
            "full_name": profile.full_name,
            "bio": profile.bio,
            "image": str(profile.image),
            "verified": profile.verified,
        }
        return Response(data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response(
            {"error": "Profile does not exist for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task(request, task_id):
    task = get_object_or_404(Todo, id=task_id, user=request.user)
    serializer = TodoSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_summary(request):
    tasks = Todo.objects.filter(user=request.user)
    summary = {
        'open': tasks.filter(status='Open').count(),
        'inProgress': tasks.filter(status='In Progress').count(),
        'done': tasks.filter(status='Done').count(),
    }
    recent_tasks = tasks.order_by('-created_at')[:5]
    recent_tasks_serializer = TodoSerializer(recent_tasks, many=True)
    return Response(
        {'summary': summary, 'recentTasks': recent_tasks_serializer.data},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'endpoint': '/api/tasks/', 'methods': 'GET,POST', 'description': 'List/create todos'},
        {'endpoint': '/api/token/', 'methods': 'POST', 'description': 'JWT token obtain'},
        {'endpoint': '/api/register/', 'methods': 'POST', 'description': 'User registration'},
        {'endpoint': '/api/token/refresh/', 'methods': 'POST', 'description': 'JWT token refresh'},
        {'endpoint': '/api/tasks/summary/', 'methods': 'GET', 'description': 'Tasks summary'},
        {'endpoint': '/api/tasks/add/', 'methods': 'POST', 'description': 'Add new task'},
        {'endpoint': '/api/tasks/statistics/', 'methods': 'GET', 'description': 'Tasks statistics'},
        {'endpoint': '/api/csrf/', 'methods': 'GET', 'description': 'Get CSRF token'},
        {'endpoint': '/api/profile/', 'methods': 'GET', 'description': 'User profile'},
        {'endpoint': '/api/create-admin/', 'methods': 'POST', 'description': 'Create admin (dev only)'},
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulations {request.user}, your API just responded to a GET request!"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = "Hello buddy"
        data = f"Congratulations, your API just responded to a POST request with text: {text}"
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)
