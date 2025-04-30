from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from .models import Profile, Todo
from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer
)

User = get_user_model()

# -----------------------
# CSRF TOKEN VIEW
# -----------------------
@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    return Response({'message': 'CSRF cookie set'})

# -----------------------
# LOGIN VIEW (COOKIE BASED)
# -----------------------
class MyTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = JsonResponse({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
        })

        # Set secure HttpOnly cookies
        response.set_cookie(
            key='access',
            value=access_token,
            httponly=True,
            secure=not DEBUG,
            samesite='None' if not DEBUG else 'Lax'
        )
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            httponly=True,
            secure=not DEBUG,
            samesite='None' if not DEBUG else 'Lax'
        )

        return response

# -----------------------
# LOGOUT VIEW (COOKIE CLEAR)
# -----------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    response = Response({"message": "Logged out"})
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response

# -----------------------
# REGISTER VIEW
# -----------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.get_or_create(user=user)

        # Optionally: auto-login on registration (set cookies here too)

        token = RefreshToken.for_user(user)
        response = JsonResponse({
            'user': serializer.data,
            'access': str(token.access_token),
            'refresh': str(token)
        })
        response.set_cookie('access', str(token.access_token), httponly=True, secure=not DEBUG, samesite='None' if not DEBUG else 'Lax')
        response.set_cookie('refresh', str(token), httponly=True, secure=not DEBUG, samesite='None' if not DEBUG else 'Lax')
        return response

# -----------------------
# GET ROUTES (FOR DEBUGGING)
# -----------------------
@api_view(['GET'])
def get_routes(request):
    routes = [
        {'endpoint': '/api/tasks/', 'methods': 'GET,POST,PUT,PATCH,DELETE'},
        {'endpoint': '/api/token/', 'methods': 'POST'},
        {'endpoint': '/api/token/refresh/', 'methods': 'POST'},
        {'endpoint': '/api/register/', 'methods': 'POST'},
        {'endpoint': '/api/csrf/', 'methods': 'GET'},
        {'endpoint': '/api/logout/', 'methods': 'POST'},
    ]
    return Response(routes)

# -----------------------
# USER PROFILE
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

# -----------------------
# TASK VIEWSET
# -----------------------
class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
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
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# -----------------------
# OPTIONAL SINGLE CREATE API
# -----------------------
class TaskAPIView(generics.CreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
