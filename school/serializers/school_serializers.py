from rest_framework import serializers
from workstream.models import WorkStream


class SchoolListQuerySerializer(serializers.Serializer):
    work_stream_id = serializers.IntegerField(required=False)


class SchoolCreateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255)
    work_stream = serializers.PrimaryKeyRelatedField(queryset=WorkStream.objects.all())


class SchoolUpdateInputSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255, required=False)


class SchoolOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source="school_name")
    work_stream = serializers.IntegerField(source="work_stream_id")
    manager = serializers.IntegerField(source="manager_id", allow_null=True)
