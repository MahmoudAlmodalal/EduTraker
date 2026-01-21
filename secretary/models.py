from django.db import models
from accounts.models import SoftDeleteModel


class Secretary(SoftDeleteModel):
    """
    Secretary/Registrar profile linked to User.
    Schema: Secretaries table
    """
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="secretary_profile",
        help_text="User account for this secretary/registrar"
    )
    department = models.CharField(
        max_length=100,
        help_text="Department this secretary belongs to"
    )
    office_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Office number"
    )
    hire_date = models.DateField(help_text="Date of hire")
    
    class Meta:
        db_table = "secretaries"
        verbose_name = "Secretary/Registrar"
        verbose_name_plural = "Secretaries/Registrars"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email}) - {self.department}"
