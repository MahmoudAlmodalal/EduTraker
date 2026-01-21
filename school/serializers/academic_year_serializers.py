from rest_framework import serializers
from school.models import AcademicYear, School


class AcademicYearListQuerySerializer(serializers.Serializer):
    """Query serializer for academic year list endpoint."""
    school_id = serializers.IntegerField(required=False, help_text="Filter by school ID")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


class AcademicYearCreateInputSerializer(serializers.Serializer):
    """Input serializer for creating academic years."""
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), help_text="School ID")
    start_date = serializers.DateField(help_text="Start date of the academic year")
    end_date = serializers.DateField(help_text="End date of the academic year")


class AcademicYearUpdateInputSerializer(serializers.Serializer):
    """Input serializer for updating academic years."""
    start_date = serializers.DateField(required=False, help_text="Start date of the academic year")
    end_date = serializers.DateField(required=False, help_text="End date of the academic year")


class AcademicYearOutputSerializer(serializers.ModelSerializer):
    """Output serializer for academic year responses."""
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = AcademicYear
        fields = [
            'id', 'academic_year_code', 'school', 'school_name',
            'start_date', 'end_date', 'is_active',
            'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'academic_year_code', 'created_at', 'updated_at', 'deactivated_by_name']
