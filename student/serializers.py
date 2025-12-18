from rest_framework import serializers
from .models import Student, StudentEnrollment
from accounts.serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    # Nested serializer to show full user details when fetching a student
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Student
        fields = ['user', 'user_details', 'school', 'grade', 'date_of_birth', 'admission_date', 'current_status', 'address', 'medical_notes']

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        fields = '__all__'