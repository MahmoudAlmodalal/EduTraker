from django.db import models
from accounts.models import SoftDeleteModel


class Guardian(SoftDeleteModel):
    """
    Guardian profile linked to User.
    Schema: Guardians table
    """
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="guardian_profile",
        help_text="User account for this guardian"
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Guardian phone number"
    )
    
    class Meta:
        db_table = "guardians"
        verbose_name = "Guardian"
        verbose_name_plural = "Guardians"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class GuardianStudentLink(SoftDeleteModel):
    """
    Many-to-many relationship between guardians and students with relationship type.
    Schema: Guardian_Student_Link table
    """
    RELATIONSHIP_CHOICES = [
        ("parent", "Parent"),
        ("guardian", "Guardian"),
        ("sibling", "Sibling"),
        ("other", "Other"),
    ]
    
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="student_links",
        help_text="Guardian in this relationship"
    )
    student = models.ForeignKey(
        'student.Student',
        on_delete=models.CASCADE,
        related_name="guardian_links",
        help_text="Student in this relationship"
    )
    relationship_type = models.CharField(
        max_length=50,
        choices=RELATIONSHIP_CHOICES,
        help_text="Type of relationship"
    )
    
    class Meta:
        db_table = "guardian_student_link"
        verbose_name = "Guardian Student Link"
        verbose_name_plural = "Guardian Student Links"
        constraints = [
            models.UniqueConstraint(
                fields=["guardian", "student"],
                name="unique_guardian_student"
            )
        ]
        ordering = ["guardian", "student"]
        indexes = [
            models.Index(fields=["student"], name="idx_link_student"),
        ]
    
    def __str__(self):
        return f"{self.guardian.user.full_name} → {self.student.user.full_name} ({self.get_relationship_type_display()})"
