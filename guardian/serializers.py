from django.contrib.auth import get_user_model
from rest_framework import serializers

from guardian.models import Guardian, GuardianStudentLink
from student.models import Student

User = get_user_model()


class GuardianUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "is_active"]


class GuardianSerializer(serializers.ModelSerializer):
    user = GuardianUserSerializer(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Guardian
        fields = ["user_id", "user", "phone_number"]


class GuardianCreateSerializer(serializers.Serializer):
    """
    Create guardian profile for an EXISTING user.
    (If you want also to create the user here, tell me your CustomUser required fields.)
    """
    user_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value


class GuardianUpdateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)


class GuardianStudentLinkSerializer(serializers.ModelSerializer):
    guardian_user_id = serializers.IntegerField(source="guardian.user_id", read_only=True)
    student_id = serializers.IntegerField(source="student.id", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = GuardianStudentLink
        fields = ["guardian_user_id", "student_id", "student_name", "relationship_type"]


class GuardianStudentLinkCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    relationship_type = serializers.ChoiceField(choices=GuardianStudentLink.RELATIONSHIP_CHOICES)

    def validate_student_id(self, value):
        if not Student.objects.filter(id=value).exists():
            raise serializers.ValidationError("Student not found.")
        return value


class GuardianStudentLinkUpdateSerializer(serializers.Serializer):
    relationship_type = serializers.ChoiceField(choices=GuardianStudentLink.RELATIONSHIP_CHOICES)
