from rest_framework import serializers

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

class DashboardStatisticsSerializer(serializers.Serializer):
    role = serializers.CharField(help_text="User role")
    statistics = serializers.DictField(help_text="Dashboard-specific statistics")
