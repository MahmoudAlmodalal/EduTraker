from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from workstream.models import WorkStream



class WorkstreamListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False, allow_null=True)

class WorkstreamCreateInputSerializer(serializers.Serializer):
    workstream_name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    capacity = serializers.IntegerField(min_value=1, default=100)
    location = serializers.CharField(required=False, allow_blank=True, max_length=255)


class WorkstreamOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    workstream_name = serializers.CharField(required=False)
    description = serializers.SerializerMethodField()
    manager_id = serializers.IntegerField(required=False)
    manager_name = serializers.SerializerMethodField()
    capacity = serializers.IntegerField(required=False, min_value=1)
    location = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    total_users = serializers.IntegerField(read_only=True)
    total_schools = serializers.IntegerField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)

    @extend_schema_field(serializers.CharField())
    def get_description(self, obj):
        return obj.description or ""

    @extend_schema_field(serializers.CharField())
    def get_manager_name(self, obj):
        return obj.manager.full_name if obj.manager else "Pending"
    
class WorkstreamUpdateInputSerializer(serializers.Serializer):
    workstream_name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.IntegerField(required=False)
    capacity = serializers.IntegerField(required=False, min_value=1)
    location = serializers.CharField(required=False, allow_blank=True, max_length=255)
    is_active = serializers.BooleanField(required=False)
