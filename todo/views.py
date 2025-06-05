from django.http import JsonResponse
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

from .models import Profile, Todo, User
from .serializer import (
    UserSerializer,
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer
)

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

# Updated create_admin view with error handling
def create_admin(request):
    try:
        User = get_user_model()
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                username="admin",  # Added username as required by AbstractUser
                email="admin@example.com",
                password="StrongAdminPass456"
            )
            return JsonResponse({"message": "✅ Superuser created with email 'admin@example.com'"})
        return JsonResponse({"message": "ℹ️ Superuser already exists."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Endpoint to get CSRF token"""
    response = Response({'message': 'CSRF cookie set'})
    return add_cors_headers(response)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Manually validate password confirmation
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

            # Ensure a Profile is created for the new User
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

# -----------------------
# TODO VIEWS
# -----------------------
class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        """Filter tasks based on query parameters (status, priority, category)."""
        queryset = Todo.objects.filter(user=self.request.user).order_by('-due_date')

        status_filter = self.request.query_params.get('status', None)
        priority_filter = self.request.query_params.get('priority', None)
        category_filter = self.request.query_params.get('category', None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        return queryset

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
# PROFILE & UTILITY VIEWS
# -----------------------
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
    """Retrieve a single task by ID"""
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
    return Response({'summary': summary, 'recentTasks': recent_tasks_serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_task(request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_statistics(request):
    tasks = Todo.objects.filter(user=request.user)
    statistics = {
        'total_tasks': tasks.count(),
        'open_tasks': tasks.filter(status='Open').count(),
        'in_progress_tasks': tasks.filter(status='In Progress').count(),
        'done_tasks': tasks.filter(status='Done').count(),
    }
    return Response(statistics, status=status.HTTP_200_OK)

# -----------------------
# DEBUG & TEST ROUTES
# -----------------------
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