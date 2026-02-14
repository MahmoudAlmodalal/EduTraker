from rest_framework import serializers
from workstream.models import WorkStream


class SchoolListQuerySerializer(serializers.Serializer):
    work_stream_id = serializers.IntegerField(required=False)
    include_inactive = serializers.BooleanField(default=False)


class SchoolCreateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=300, required=False, allow_blank=True, allow_null=True)
    capacity = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    # Make work_stream optional; when omitted, views can fall back to the
    # authenticated user's work_stream (for manager_workstream roles).
    work_stream = serializers.PrimaryKeyRelatedField(
        queryset=WorkStream.objects.all(),
        required=False,
        allow_null=True,
    )


class SchoolUpdateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=300, required=False, allow_blank=True, allow_null=True)
    capacity = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class SchoolOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    school_name = serializers.CharField()
    location = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    capacity = serializers.IntegerField(allow_null=True, required=False)
    work_stream = serializers.IntegerField(source="work_stream_id")
    manager = serializers.IntegerField(source="manager_id", allow_null=True)
    is_active = serializers.BooleanField()
    deactivated_at = serializers.DateTimeField(allow_null=True)
    deactivated_by = serializers.IntegerField(source="deactivated_by_id", allow_null=True)
    deactivated_by_name = serializers.CharField(source="deactivated_by.full_name", allow_null=True, read_only=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
