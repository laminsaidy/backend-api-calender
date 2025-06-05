from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from todo.models import Profile, User, Todo
from todo.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer, TodoSerializer
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

# Updated create_admin view with error handling
def create_admin(request):
    try:
        User = get_user_model()
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                username="admin",  # Add username to avoid error if required
                email="admin@example.com",
                password="StrongAdminPass456"
            )
            return JsonResponse({"message": "✅ Superuser created with email 'admin@example.com'"})
        return JsonResponse({"message": "ℹ️ Superuser already exists."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Viewset for handling CRUD operations on Todo model
class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    queryset = Todo.objects.all().order_by('-due_date')

    def get_queryset(self):
        """Filter tasks based on query parameters (status, priority, category)."""
        queryset = Todo.objects.all().order_by('-due_date')

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

# Custom token view with MyTokenObtainPairSerializer
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Custom registration view
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

# List all available API routes
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/tasks/',
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/tasks/summary/',
        '/api/tasks/add/',
        '/api/tasks/statistics/',
    ]
    return Response(routes)

# Task Manager View
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

# Test Endpoint
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task(request, task_id):
    """Retrieve a single task by ID"""
    task = get_object_or_404(Todo, id=task_id)
    serializer = TodoSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Task Summary View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_summary(request):
    tasks = Todo.objects.all()
    summary = {
        'open': tasks.filter(status='Open').count(),
        'inProgress': tasks.filter(status='In Progress').count(),
        'done': tasks.filter(status='Done').count(),
    }
    recent_tasks = tasks.order_by('-created_at')[:5]
    recent_tasks_serializer = TodoSerializer(recent_tasks, many=True)
    return Response({'summary': summary, 'recentTasks': recent_tasks_serializer.data})

# Add Task View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_task(request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View Statistics View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_statistics(request):
    tasks = Todo.objects.all()
    statistics = {
        'total_tasks': tasks.count(),
        'open_tasks': tasks.filter(status='Open').count(),
        'in_progress_tasks': tasks.filter(status='In Progress').count(),
        'done_tasks': tasks.filter(status='Done').count(),
    }
    return Response(statistics, status=status.HTTP_200_OK)
