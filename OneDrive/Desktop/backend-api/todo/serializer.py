from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Todo
from rest_framework import serializers

# Get the custom User model
User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']

# Custom Token Serializer for JWT
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email  
        return token

# Register Serializer for User Sign Up
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Todo Serializer

class TodoSerializer(serializers.ModelSerializer):
    overdue = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = ('id', 'title', 'description', 'status', 'priority', 'category', 'due_date', 'overdue')

    def get_overdue(self, obj):
        return obj.is_overdue()

    def validate_category(self, value):
        # Allow any category as long as it's a string
        if isinstance(value, list):
            return value[0]  # Convert array to string (if needed)
        return value