from rest_framework import serializers
from decimal import Decimal

from teacher.models import Assignment


# =============================================================================
# Assignment Serializers
# =============================================================================

class AssignmentInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating assignments."""
    assignment_code = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Assignment code (auto-generated if not provided)"
    )
    title = serializers.CharField(
        max_length=150,
        help_text="Assignment title"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Assignment description"
    )
    due_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Due date for the assignment"
    )
    exam_type = serializers.ChoiceField(
        choices=Assignment.EXAM_TYPE_CHOICES,
        help_text="Type of assignment/exam"
    )
    full_mark = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Full marks for this assignment"
    )


class AssignmentUpdateSerializer(serializers.Serializer):
    """Input serializer for updating assignments (all fields optional)."""
    assignment_code = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Assignment code"
    )
    title = serializers.CharField(
        max_length=150,
        required=False,
        help_text="Assignment title"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Assignment description"
    )
    due_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Due date for the assignment"
    )
    exam_type = serializers.ChoiceField(
        choices=Assignment.EXAM_TYPE_CHOICES,
        required=False,
        help_text="Type of assignment/exam"
    )
    full_mark = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=False,
        help_text="Full marks for this assignment"
    )


class AssignmentOutputSerializer(serializers.ModelSerializer):
    """Output serializer for assignment responses."""
    created_by_name = serializers.CharField(
        source='created_by.user.full_name',
        read_only=True
    )
    exam_type_display = serializers.CharField(
        source='get_exam_type_display',
        read_only=True
    )
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Assignment
        fields = [
            'id',
            'assignment_code',
            'created_by',
            'created_by_name',
            'title',
            'description',
            'due_date',
            'exam_type',
            'exam_type_display',
            'full_mark',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'exam_type_display', 'deactivated_by_name', 'created_at', 'updated_at']


class AssignmentFilterSerializer(serializers.Serializer):
    """Filter serializer for assignment list endpoint."""
    exam_type = serializers.ChoiceField(
        choices=Assignment.EXAM_TYPE_CHOICES,
        required=False,
        help_text="Filter by exam/assignment type"
    )
    due_date_from = serializers.DateField(
        required=False,
        help_text="Filter assignments due on or after this date"
    )
    due_date_to = serializers.DateField(
        required=False,
        help_text="Filter assignments due on or before this date"
    )
    title = serializers.CharField(
        required=False,
        help_text="Filter by title (partial match)"
    )
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")
