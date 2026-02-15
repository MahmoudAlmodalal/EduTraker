from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """Manager to filter for active records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft delete functionality.
    ALL educational models must inherit from this.
    """
    is_active = models.BooleanField(default=True, db_index=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deactivations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ActiveManager()  # Default: active records only
    all_objects = models.Manager()  # All records including inactive
    
    class Meta:
        abstract = True
    
    def deactivate(self, user=None):
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.deactivated_by = user
        self.save(update_fields=['is_active', 'deactivated_at', 'deactivated_by'])
    
    def activate(self):
        self.is_active = True
        self.deactivated_at = None
        self.deactivated_by = None
        self.save(update_fields=['is_active', 'deactivated_at', 'deactivated_by'])


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


class UserManager(BaseUserManager, ActiveManager):
    """Custom user manager for email-based authentication with soft delete support."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = str(email).strip()
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


class CustomUser(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
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
    # Audit fields
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
        help_text="User who created this account"
    )
    # Django auth specific fields
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True, help_text="Last login timestamp")
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text="Preferred timezone for this user"
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Whether email notifications are enabled"
    )
    in_app_alerts = models.BooleanField(
        default=True,
        help_text="Whether in-app alerts are enabled"
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text="Whether SMS notifications are enabled"
    )
    enable_2fa = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication preference is enabled"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]
    
    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["role"], name="idx_users_role"),
            models.Index(fields=["work_stream"], name="idx_users_work_stream"),
            models.Index(fields=["school"], name="idx_users_school"),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class SystemConfiguration(SoftDeleteModel):
    """
    System-wide or school-specific configuration settings.
    Schema: System_Configurations table
    """
    work_stream = models.ForeignKey(
        "workstream.WorkStream",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configurations",
        help_text="Workstream-specific config (null for global/school-specific)"
    )
    school = models.ForeignKey(
        "school.School",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configurations",
        help_text="School-specific config (null for global/workstream-specific)"
    )
    config_key = models.CharField(max_length=100, help_text="Configuration key")
    config_value = models.TextField(help_text="Configuration value")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "system_configurations"
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        constraints = [
            models.UniqueConstraint(
                fields=["work_stream", "config_key"],
                condition=models.Q(school__isnull=True),
                name="unique_workstream_config_key"
            ),
            models.UniqueConstraint(
                fields=["school", "config_key"],
                name="unique_school_config_key"
            ),
             models.UniqueConstraint(
                fields=["config_key"],
                condition=models.Q(school__isnull=True, work_stream__isnull=True),
                name="unique_global_config_key"
            )
        ]
        indexes = [
            models.Index(fields=["school", "config_key"], name="idx_sys_config_school"),
            models.Index(fields=["work_stream", "config_key"], name="idx_sys_config_workstream"),
        ]
    
    def __str__(self):
        scope = self.school.school_name if self.school else "Global"
        return f"{scope}: {self.config_key}"
