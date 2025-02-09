from django.shortcuts import render
from todo.models import Profile, User, Todo  # Import Todo model
from todo.serializer import UserSerializer, MyTokenObtainPairSerializer, RegisterSerializer, TodoSerializer  # Import TodoSerializer
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework import viewsets

# Viewset for handling CRUD operations on Todo model
class TodoView(viewsets.ModelViewSet):       
    serializer_class = TodoSerializer          
    queryset = Todo.objects.all()   



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
        user = serializer.save()  # Save user with validated data
        
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
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
    ]
    return Response(routes)


# Dashboard View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    try:
        profile = user.profile  # Assuming a one-to-one relationship between User and Profile
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
