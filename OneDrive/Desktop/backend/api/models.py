from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __Str__(self):
        return self.username