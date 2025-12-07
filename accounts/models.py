from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    """
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("guardian", "Guardian"),
        ("secretary", "Secretary"),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        help_text="User role for RBAC"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user can log in."
    )
    
    # Use email as the unique identifier instead of username
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # username still required but not used for login
    
    def __str__(self):
        return f"{self.email} ({self.role})"