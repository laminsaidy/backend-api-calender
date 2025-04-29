from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="user_images/", default="default.jpg")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Automatically create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('O', 'Open'),
        ('P', 'In Progress'),
        ('D', 'Done'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    category = models.CharField(max_length=30, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def is_overdue(self):
        """Check if task is past due date and not completed"""
        return (
            self.due_date 
            and self.status != 'D' 
            and self.due_date < now().date()
        )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"