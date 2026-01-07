from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class Role:
    """Role constants for user roles."""
    STUDENT = "student"
    TEACHER = "teacher"
    SECRETARY = "secretary"
    MANAGER_SCHOOL = "manager_school"
    MANAGER_WORKSTREAM = "manager_workstream"
    GUARDIAN = "guardian"
    ADMIN = "admin"
    GUEST = "guest"


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email-based authentication and role-based access control.
    Schema: Users table
    """
    ROLE_CHOICES = [
        (Role.STUDENT, "Student"),
        (Role.TEACHER, "Teacher"),
        (Role.SECRETARY, "Secretary"),
        (Role.MANAGER_SCHOOL, "School Manager"),
        (Role.MANAGER_WORKSTREAM, "Workstream Manager"),
        (Role.GUARDIAN, "Guardian"),
        (Role.ADMIN, "Admin"),
        (Role.GUEST, "Guest"),
    ]
    
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="Email address used for login"
    )
    full_name = models.CharField(
        max_length=150,
        help_text="Full name of the user"
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        db_index=True,
        default=Role.GUEST,
        help_text="User role"
    )
    work_stream = models.ForeignKey(
        'workstream.WorkStream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="Workstream this user belongs to"
    )
    school = models.ForeignKey(
        'school.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="School this user belongs to"
    )
    # Django auth fields
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user can log in."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]
    
    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class SystemConfiguration(models.Model):
    """
    System-wide or school-specific configuration settings.
    Schema: System_Configurations table
    """
    school = models.ForeignKey(
        "school.School",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configurations",
        help_text="School-specific config (null for global)"
    )
    config_key = models.CharField(max_length=100, help_text="Configuration key")
    config_value = models.TextField(help_text="Configuration value")
    
    class Meta:
        db_table = "system_configurations"
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        constraints = [
            models.UniqueConstraint(
                fields=["school", "config_key"],
                name="unique_school_config_key"
            )
        ]
        indexes = [
            models.Index(fields=["school", "config_key"]),
        ]
    
    def __str__(self):
        scope = self.school.school_name if self.school else "Global"
        return f"{scope}: {self.config_key}"
