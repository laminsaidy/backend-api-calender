from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Todo, Profile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'image', 'verified']
        read_only_fields = ['verified']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']
        read_only_fields = ['email', 'username']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the default token response (access + refresh)
        data = super().validate(attrs)
        
        # Add user data to the response
        data['user'] = UserSerializer(self.user).data
        
        # Rename 'access' to 'token' for frontend compatibility
        data['token'] = data.pop('access')
        
        # Remove refresh token if not needed by frontend
        # data.pop('refresh', None)
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=128
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.get_or_create(user=user)  # Ensure profile is created
        return user

class TodoSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    overdue = serializers.BooleanField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'category', 'due_date',
            'created_at', 'updated_at', 'overdue', 'user'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'overdue']

    def validate_status(self, value):
        if value not in dict(Todo.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status value")
        return value

    def validate_priority(self, value):
        if value not in dict(Todo.PRIORITY_CHOICES).keys():
            raise serializers.ValidationError("Invalid priority value")
        return value