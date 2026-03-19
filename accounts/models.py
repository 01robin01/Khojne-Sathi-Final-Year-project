from django.db import models

from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
# Create your models here.
ROLE_CHOICES = (
        ("user", "User"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    )
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True,help_text="Enter phone number with country code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()
    street_address = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True,help_text="Enter ZIP or postal code")
    secondary_contact = models.CharField(max_length=15, blank=True, null=True,help_text="Enter secondary contact number with country code")


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'phone']
    
    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        ordering = ['-created_at']
