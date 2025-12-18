from rest_framework import serializers
from .models import Guardian, GuardianStudentLink
from accounts.serializers import UserSerializer
from student.serializers import StudentSerializer

class GuardianSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Guardian
        fields = ['user', 'user_details', 'phone_number']

class GuardianStudentLinkSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = GuardianStudentLink
        fields = ['id', 'guardian', 'student', 'student_details', 'relationship_type']