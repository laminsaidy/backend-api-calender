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
from django.conf import settings
import logging

from .models import Profile, Todo
from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    TodoSerializer,
    UserProfileSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG

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
        try:
            serializer = MyTokenObtainPairSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = JsonResponse({
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "access": access_token,
                "refresh": str(refresh)
            })

            # Set secure HttpOnly cookies
            response.set_cookie(
                key='access',
                value=access_token,
                httponly=True,
                secure=not DEBUG,
                samesite='None' if not DEBUG else 'Lax',
                max_age=3600 * 24  # 1 day
            )
            response.set_cookie(
                key='refresh',
                value=str(refresh),
                httponly=True,
                secure=not DEBUG,
                samesite='None' if not DEBUG else 'Lax',
                max_age=3600 * 24 * 7  # 7 days
            )

            return response
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {"detail": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

# -----------------------
# LOGOUT VIEW (COOKIE CLEAR)
# -----------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    try:
        response = Response({"message": "Logged out successfully"})
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {"detail": "Logout failed"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# -----------------------
# REGISTER VIEW
# -----------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            Profile.objects.get_or_create(user=user)

            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'message': 'User registered successfully',
                'access': access_token,
                'refresh': str(refresh)
            }

            response = JsonResponse(response_data, status=status.HTTP_201_CREATED)
            
            # Set cookies for the new user
            response.set_cookie(
                'access', 
                access_token, 
                httponly=True, 
                secure=not DEBUG, 
                samesite='None' if not DEBUG else 'Lax',
                max_age=3600 * 24
            )
            response.set_cookie(
                'refresh', 
                str(refresh), 
                httponly=True, 
                secure=not DEBUG, 
                samesite='None' if not DEBUG else 'Lax',
                max_age=3600 * 24 * 7
            )
            
            return response
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# -----------------------
# TASK VIEWSET (IMPROVED)
# -----------------------
class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['due_date', 'created_at', 'priority']
    filterset_fields = ['status', 'priority', 'category']

    def get_queryset(self):
        try:
            queryset = Todo.objects.filter(user=self.request.user)
            
            # Dynamic filtering
            filters = {
                'status': self.request.query_params.get('status'),
                'priority': self.request.query_params.get('priority'),
                'category': self.request.query_params.get('category')
            }
            
            # Apply filters if provided
            for field, value in filters.items():
                if value:
                    queryset = queryset.filter(**{field: value})

            return queryset.order_by('-due_date')
        except Exception as e:
            logger.error(f"QuerySet error: {str(e)}")
            return Todo.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"Creating task with data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except Exception as e:
            logger.error(f"Task creation error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()  # Get the task by primary key
        status = request.data.get('status')  # Expecting status to be passed in the request data
        
        # Validate and update status
        if status not in ['O', 'P', 'D', 'C']:
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = status
        task.save()

        return Response(TodoSerializer(task).data, status=status.HTTP_200_OK)

# -----------------------
# USER PROFILE VIEW
# -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        profile = get_object_or_404(Profile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response(
            {"detail": "Error fetching profile"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# -----------------------
# ROUTES VIEW (FOR DEBUGGING)
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
        {'endpoint': '/api/profile/', 'methods': 'GET'},
    ]
    return Response(routes)
