from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email address')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


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
        null=True,  
        blank=True, 
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
        auto_now_add=True,
        null=True, 
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
        ]

    def is_overdue(self):
        """Check if task is past due date and not completed"""
        return (
            self.due_date
            and self.status in ['O', 'P']  # Only open/in-progress tasks can be overdue
            and self.due_date < timezone.now().date()
        )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_completed(self):
        return self.status == 'D'