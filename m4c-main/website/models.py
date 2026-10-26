from django.conf import settings
from django.db import models


class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_profile")
    full_name = models.CharField(max_length=150, blank=True, default="")
    phone_number = models.CharField(max_length=16, unique=True)
    county = models.CharField(max_length=80, blank=True, default="")
    interest = models.CharField(max_length=80, blank=True, default="")

    def __str__(self):
        return self.user.get_username()


class VolunteerRegistration(models.Model):
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=32)
    county = models.CharField(max_length=80)
    interest = models.CharField(max_length=80)
    email = models.EmailField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.county})"