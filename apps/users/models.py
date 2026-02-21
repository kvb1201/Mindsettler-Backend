# users/models.py
from django.db import models
from django.utils import timezone


class AppUser(models.Model):

    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_admin_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email