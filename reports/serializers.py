from rest_framework import serializers
from .models import ActivityLog

class TeacherStudentCountSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField(help_text="Teacher's User ID")
    teacher_name = serializers.CharField(help_text="Teacher's Full Name")
    total_students = serializers.IntegerField(help_text="Total students taught by this teacher")
    by_course = serializers.ListField(help_text="Student count per course")
    by_classroom = serializers.ListField(help_text="Student count per classroom")

class WorkstreamStudentCountSerializer(serializers.Serializer):
    workstream_id = serializers.IntegerField(help_text="Workstream ID")
    workstream_name = serializers.CharField(help_text="Workstream Name")
    total_students = serializers.IntegerField(help_text="Total students in workstream")
    school_count = serializers.IntegerField(help_text="Number of schools in workstream")
    by_school = serializers.ListField(help_text="Student count per school")

class SchoolStudentCountSerializer(serializers.Serializer):
    school_id = serializers.IntegerField(help_text="School ID")
    school_name = serializers.CharField(help_text="School Name")
    total_students = serializers.IntegerField(help_text="Total students in school")
    by_grade = serializers.ListField(help_text="Student count per grade")
    by_classroom = serializers.ListField(help_text="Student count per classroom")

class CourseStudentCountSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(help_text="Course ID")
    course_name = serializers.CharField(help_text="Course Name")
    total_students = serializers.IntegerField(help_text="Total students enrolled in course")
    by_classroom = serializers.ListField(help_text="Student count per classroom")

class ClassroomStudentCountSerializer(serializers.Serializer):
    classroom_id = serializers.IntegerField(help_text="Classroom ID")
    classroom_name = serializers.CharField(help_text="Classroom Name")
    total_students = serializers.IntegerField(help_text="Total students in classroom")

class ComprehensiveStatisticsSerializer(serializers.Serializer):
    role = serializers.CharField(help_text="User role")
    generated_at = serializers.DateTimeField(help_text="Time of generation")
    statistics = serializers.DictField(help_text="Key-value statistics")

class ActivityLogSerializer(serializers.ModelSerializer):
    created_at_human = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'action_type', 'entity_type', 'entity_id', 'description', 'created_at', 'created_at_human']
        
    def get_created_at_human(self, obj):
        from django.utils.timesince import timesince
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0 and diff.seconds < 60:
            return "Just now"
        return f"{timesince(obj.created_at)} ago"

class DashboardStatisticsSerializer(serializers.Serializer):
    role = serializers.CharField(help_text="User role")
    statistics = serializers.DictField(help_text="Dashboard-specific statistics")
    recent_activity = ActivityLogSerializer(many=True, required=False)
    activity_chart = serializers.ListField(required=False, help_text="Daily login counts")
