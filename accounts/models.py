from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True
    )

    location = models.CharField(max_length=100, blank=True)

    department = models.ForeignKey(
        'tickets.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )