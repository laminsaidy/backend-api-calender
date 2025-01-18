from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser



# class User(AbstractUser):
#     # Keep the username field but let email be the primary identifier
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=100, blank=True, null=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']  # You can optionally make 'username' required if necessary

#     def __str__(self):
#         return self.email

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Ensure the Profile is created when the User is saved
        if not self.pk:  # If the user is being created
            super().save(*args, **kwargs)  # Save the user first
            self.profile = Profile.objects.create(user=self)  # Create the Profile
        super().save(*args, **kwargs)  # Save again

    def __str__(self):
        return self.email



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
        Profile.objects.create(user=instance)

# Connect the signal to create a profile when a User is created
post_save.connect(create_user_profile, sender=User)

