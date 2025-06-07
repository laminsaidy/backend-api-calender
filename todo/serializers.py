from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Todo, Profile
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'image', 'verified']
        read_only_fields = ['verified']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']
        read_only_fields = ['email', 'username']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.id)
        token['email'] = user.email
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'token': data.pop('access'),
            'refresh': data.get('refresh'),
            'user': UserSerializer(self.user).data
        })
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
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

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already in use")
        return value

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password2": "Passwords do not match"
            })
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user

class TodoSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    overdue = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'category', 'due_date',
            'created_at', 'updated_at', 'overdue', 'user'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'overdue']

    def get_overdue(self, obj):
        return obj.is_overdue

    def validate_status(self, value):
        if value not in dict(Todo.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status value")
        return value

    def validate_priority(self, value):
        if value not in dict(Todo.PRIORITY_CHOICES).keys():
            raise serializers.ValidationError("Invalid priority value")
        return value