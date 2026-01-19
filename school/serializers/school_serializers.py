from rest_framework import serializers
from workstream.models import WorkStream


class SchoolListQuerySerializer(serializers.Serializer):
    work_stream_id = serializers.IntegerField(required=False)
    include_inactive = serializers.BooleanField(default=False)


class SchoolCreateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255)
    work_stream = serializers.PrimaryKeyRelatedField(queryset=WorkStream.objects.all())


class SchoolUpdateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255, required=False)


class SchoolOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    school_name = serializers.CharField()
    work_stream = serializers.IntegerField(source="work_stream_id")
    manager = serializers.IntegerField(source="manager_id", allow_null=True)
    is_active = serializers.BooleanField()
    deactivated_at = serializers.DateTimeField(allow_null=True)
    deactivated_by = serializers.IntegerField(source="deactivated_by_id", allow_null=True)
    deactivated_by_name = serializers.CharField(source="deactivated_by.full_name", allow_null=True, read_only=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
