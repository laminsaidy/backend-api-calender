from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Todo, Profile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'image', 'verified']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']
        read_only_fields = ['email', 'username']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Store user on serializer for views to access
        self.user = self.user

        # Only include user data in response (not tokens)
        data.clear()
        data.update({
            'user': UserSerializer(self.user).data
        })
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class TodoSerializer(serializers.ModelSerializer):
    overdue = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'status',
            'priority', 'category', 'due_date',
            'overdue', 'user', 'created_at'
        ]
        read_only_fields = ['created_at', 'user']

    def get_overdue(self, obj):
        return obj.is_overdue()

    def validate_category(self, value):
        if isinstance(value, list):
            return value[0]
        return value

    def validate_priority(self, value):
        if value not in dict(Todo.PRIORITY_CHOICES).keys():
            raise serializers.ValidationError("Invalid priority value")
        return value
