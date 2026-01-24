from django.contrib.auth import get_user_model
from rest_framework import serializers

from guardian.models import Guardian, GuardianStudentLink

User = get_user_model()


# =============================================================================
# Guardian Serializers
# =============================================================================

class GuardianFilterSerializer(serializers.Serializer):
    """Filter serializer for guardian list endpoint."""
    school_id = serializers.IntegerField(required=False, help_text="Filter by school")
    search = serializers.CharField(required=False, help_text="Search by name or email")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


class GuardianInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating guardians."""
    email = serializers.EmailField(required=False, help_text="Email address")
    full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
    password = serializers.CharField(write_only=True, required=False, help_text="Password")
    school_id = serializers.IntegerField(required=False, help_text="School ID")

    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Phone number",
    )


class GuardianOutputSerializer(serializers.ModelSerializer):
    """Output serializer for guardian responses."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    school_id = serializers.IntegerField(source="user.school_id", read_only=True, allow_null=True)
    school_name = serializers.CharField(source="user.school.school_name", read_only=True, allow_null=True)

    deactivated_at = serializers.DateTimeField(source="user.deactivated_at", read_only=True)
    deactivated_by_name = serializers.CharField(source="user.deactivated_by.full_name", read_only=True, allow_null=True)

    class Meta:
        model = Guardian
        fields = [
            "user_id", "email", "full_name", "is_active",
            "school_id", "school_name", "phone_number",
            "deactivated_at", "deactivated_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at", "deactivated_by_name"]


class GuardianStudentLinkInputSerializer(serializers.Serializer):
    """Input serializer for linking student to guardian."""
    student_id = serializers.IntegerField(help_text="Student ID")
    relationship_type = serializers.ChoiceField(
        choices=GuardianStudentLink.RELATIONSHIP_CHOICES,
        help_text="Relationship type",
    )
    is_primary = serializers.BooleanField(required=False, help_text="Is primary guardian for this student")
    can_pickup = serializers.BooleanField(required=False, help_text="Can pick up student")


class GuardianStudentLinkOutputSerializer(serializers.ModelSerializer):
    """Output serializer for links."""
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    relationship_display = serializers.CharField(source="get_relationship_type_display", read_only=True)

    class Meta:
        model = GuardianStudentLink
        fields = [
            "id",
            "student_id",
            "student_name",
            "relationship_type",
            "relationship_display",
            "is_primary",
            "can_pickup",
            "is_active",
            "created_at",
            "updated_at",
        ]
