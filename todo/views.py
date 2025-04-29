from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Profile, Todo
from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer
)

User = get_user_model()

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        """Return tasks for the authenticated user with filtering support"""
        queryset = Todo.objects.filter(user=self.request.user)
        
        # Apply filters from query parameters
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        category_filter = self.request.query_params.get('category')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        return queryset.order_by('-due_date')

    def perform_create(self, serializer):
        """Automatically assign the current user to new tasks"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Handle creation of multiple tasks at once"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.get_or_create(user=user)
        
        # Return token along with user data
        token_serializer = MyTokenObtainPairSerializer()
        token = token_serializer.get_token(user)
        
        response_data = {
            'user': serializer.data,
            'access': str(token.access_token),
            'refresh': str(token)
        }
        
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

@api_view(['GET'])
def get_routes(request):
    """List all available API endpoints"""
    routes = [
        {'endpoint': '/api/tasks/', 'methods': 'GET,POST,PUT,PATCH,DELETE'},
        {'endpoint': '/api/token/', 'methods': 'POST'},
        {'endpoint': '/api/token/refresh/', 'methods': 'POST'},
        {'endpoint': '/api/register/', 'methods': 'POST'},
    ]
    return Response(routes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get authenticated user's profile"""
    profile = get_object_or_404(Profile, user=request.user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

class TaskAPIView(generics.CreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)