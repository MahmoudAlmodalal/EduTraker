from rest_framework import serializers
from ..models import LessonPlan

class LessonPlanSerializer(serializers.ModelSerializer):
    """Serializer for LessonPlan model."""
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.classroom_name', read_only=True)

    class Meta:
        model = LessonPlan
        fields = [
            'id', 'course', 'course_name', 'classroom', 'classroom_name',
            'academic_year', 'teacher', 'teacher_name', 'title',
            'content', 'objectives', 'resources_needed', 'date_planned',
            'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']
