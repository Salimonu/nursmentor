from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    SUBSCRIPTION_CHOICES = [
        ('freemium', 'Freemium'),
        ('premium', 'Premium'),
    ]

    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('pro', 'Pro'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='freemium')
    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
