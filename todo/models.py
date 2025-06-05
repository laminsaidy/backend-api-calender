from django.db import models
<<<<<<< HEAD
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

from django.utils.timezone import now

# Custom User model
class User(AbstractUser):
    email = models.EmailField(unique=True)
=======
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email address')
>>>>>>> main
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

<<<<<<< HEAD

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    bio = models.CharField(max_length=500)  # Increased max_length for more flexibility
    image = models.ImageField(upload_to="user_images", default="default.jpg")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


# Signal to automatically create a Profile for new Users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)  # Ensure no duplicate Profiles are created


# Todo model
class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    category = models.CharField(max_length=20, blank=True, null=True)  # Allow any category
    due_date = models.DateField(null=True, blank=True)

    def is_overdue(self):
        """Check if the task is overdue"""
        if self.due_date and self.status != 'Done' and self.due_date < now().date():
            return True
        return False

    def __str__(self):
        return self.title
=======
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(
        upload_to="user_images/",
        default="default.jpg",
        verbose_name='profile image'
    )
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to automatically create profile when user is created"""
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
        ('C', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='todos',
        help_text="The user this todo item belongs to"
    )
    title = models.CharField(
        max_length=200,
        verbose_name='task title'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='detailed description'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='O',
        verbose_name='task status'
    )
    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default='M',
        verbose_name='task priority'
    )
    category = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='task category'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='due date'
    )
    created_at = models.DateTimeField(
        default=timezone.now,  # Updated to include a default value
        verbose_name='creation date'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='last update'
    )

    class Meta:
        ordering = ['-due_date', 'priority']
        verbose_name = 'Todo Item'
        verbose_name_plural = 'Todo Items'
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['user']),
        ]

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def priority_display(self):
        return self.get_priority_display()

    @property
    def overdue(self):
        """Check if task is past due date and not completed"""
        return (
            self.due_date and
            self.due_date < timezone.now().date() and
            self.status in ['O', 'P']  # Only open/in-progress tasks can be overdue
        )

    @property
    def is_completed(self):
        return self.status == 'D'

    def __str__(self):
        return f"{self.title} ({self.status_display})"
>>>>>>> main
