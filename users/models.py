from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    time_of_birth = models.TimeField(null=True, blank=True)
    Country_of_Birth = models.CharField(max_length=50, blank=True, null=True)
    Place_of_Birth = models.CharField(max_length=255, blank=True , null=True)
    country_code = models.CharField(max_length=4, blank=True , null=True)
    whatsapp = models.CharField(max_length=10, blank=True , null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update

    def __str__(self):
        return f"{self.user.username}'s Profile"

