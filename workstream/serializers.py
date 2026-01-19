from rest_framework import serializers
from workstream.models import WorkStream



class WorkstreamListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

class WorkstreamCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    max_user = serializers.IntegerField(min_value=1, default=100)


class WorkstreamOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False)
    description = serializers.SerializerMethodField()
    manager_id = serializers.IntegerField(required=False)
    max_user = serializers.IntegerField(required=False, min_value=1)
    is_active = serializers.BooleanField(required=False)

    def get_description(self, obj):
        return obj.description or ""
    
class WorkstreamUpdateInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.IntegerField(required=False)
    max_user = serializers.IntegerField(required=False, min_value=1)
    is_active = serializers.BooleanField(required=False)
