from todo.models import Profile, User, Todo
from todo.serializer import MyTokenObtainPairSerializer, RegisterSerializer, TodoSerializer
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404

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
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Ensure a Profile is created for the new User
        Profile.objects.get_or_create(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

# List all available API routes
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/tasks/',
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/tasks/add/',
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

# Add Task View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_task(request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
