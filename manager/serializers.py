from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import WorkStream, School, Grade, AcademicYear, SystemConfiguration, StaffEvaluation

User = get_user_model()

class WorkStreamSerializer(serializers.ModelSerializer):
    # Serializer for the WorkStream model
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)

    class Meta:
        model = WorkStream
        fields = ['id', 'name', 'description', 'manager', 'manager_name', 'max_user', 'is_active']
        read_only_fields = ['id']

class SchoolSerializer(serializers.ModelSerializer):
    # Serializer for the School model
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    work_stream_name = serializers.CharField(source='work_stream.name', read_only=True)

    class Meta:
        model = School
        fields = ['id', 'school_name', 'work_stream', 'work_stream_name', 'manager', 'manager_name']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = '__all__'

class StaffEvaluationSerializer(serializers.ModelSerializer):
    # Corrected fields to match manager/models.py
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.full_name', read_only=True)

    class Meta:
        model = StaffEvaluation
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewee', 'reviewee_name', 
            'evaluation_date', 'rating_score', 'comments'
        ]
        read_only_fields = ['reviewer']

class CreateStaffAccountSerializer(serializers.ModelSerializer):
    """
    Manager creates Teacher / Secretary accounts.
    Corrected to use 'email' and 'full_name' instead of username/first/last.
    """
    role = serializers.ChoiceField(choices=[('teacher', 'Teacher'), ('register', 'Secretary')])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "password", "role", "school", "work_stream"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Create user using the custom manager method
        user = User.objects.create_user(password=password, **validated_data)
        return user

class WorkstreamStatsSerializer(serializers.Serializer):
    """
    Serializer for workstream analytics (Custom non-model serializer).
    """
    workstream_id = serializers.IntegerField()
    workstream_name = serializers.CharField()
    total_schools = serializers.IntegerField()
    total_users = serializers.IntegerField()
    active_status = serializers.BooleanField()