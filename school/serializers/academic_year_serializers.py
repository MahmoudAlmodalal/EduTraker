from rest_framework import serializers
from school.models import AcademicYear, School


class AcademicYearCreateInputSerializer(serializers.Serializer):
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class AcademicYearUpdateInputSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


class AcademicYearOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    academic_year_code = serializers.CharField()
    school = serializers.IntegerField(source="school_id")
    start_date = serializers.DateField()
    end_date = serializers.DateField()
