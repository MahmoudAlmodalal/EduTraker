from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Workstream, StaffEvaluation, DepartmentActivityReport

User = get_user_model()


class WorkstreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstream
        fields = [
            "id",
            "name",
            "capacity",
            "description",
            "manager",
            "created_by",
            "created_at",
        ]
        read_only_fields = ("created_by", "created_at")


class StaffEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffEvaluation
        fields = [
            "id",
            "manager",
            "teacher",
            "workstream",
            "period_start",
            "period_end",
            "score",
            "comments",
            "created_at",
        ]
        read_only_fields = ("manager", "created_at")


class DepartmentActivityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentActivityReport
        fields = [
            "id",
            "manager",
            "workstream",
            "date",
            "attendance_rate",
            "notes",
            "generated_at",
        ]
        read_only_fields = ("manager", "generated_at")


class CreateStaffAccountSerializer(serializers.ModelSerializer):
    """
    Manager creates Teacher / Secretary accounts (US-Manager-004).
    NOTE: Your User model must have a 'role' field or similar.
    """
    role = serializers.ChoiceField(choices=("teacher", "secretary"))

    class Meta:
        model = User
        fields = ["id", "username","first_name", "last_name", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
class WorkstreamStatsSerializer(serializers.Serializer):
    """Serializer for workstream statistics."""
    workstream_id = serializers.IntegerField()
    workstream_name = serializers.CharField()
    total_reports = serializers.IntegerField()
    avg_attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_evaluations = serializers.IntegerField()
    avg_evaluation_score = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)