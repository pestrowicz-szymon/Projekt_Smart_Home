from django.db import models
from django.contrib.auth.models import User

# We're using Django's built-in User model
# You can extend it here if needed in the future

# Example future extension:
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=15, blank=True)
#     address = models.TextField(blank=True)
