from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsTeacher, IsAdminOrManagerOrSecretary, IsStaffUser
from teacher.models import Mark, Assignment
from teacher.selectors.mark_selectors import mark_list, mark_get
from teacher.services.mark_services import (
    mark_record,
    mark_deactivate,
    mark_activate,
)
from student.selectors.student_selectors import student_get
from django.shortcuts import get_object_or_404


# =============================================================================
# Mark Serializers
# =============================================================================

class MarkFilterSerializer(serializers.Serializer):
    """Filter serializer for mark list."""
    student_id = serializers.IntegerField(required=False)
    assignment_id = serializers.IntegerField(required=False)
    include_inactive = serializers.BooleanField(default=False)


class MarkInputSerializer(serializers.Serializer):
    """Input serializer for recording marks."""
    student_id = serializers.IntegerField()
    assignment_id = serializers.IntegerField()
    score = serializers.DecimalField(max_digits=5, decimal_places=2)
    feedback = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class MarkOutputSerializer(serializers.ModelSerializer):
    """Output serializer for mark records."""
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.user.full_name', read_only=True)
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Mark
        fields = [
            'id', 'student_id', 'student_name', 'assignment', 'assignment_title',
            'score', 'feedback', 'graded_by', 'graded_by_name', 'graded_at',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'graded_by_name', 'graded_at', 'deactivated_by_name', 'created_at', 'updated_at']


# =============================================================================
# Mark Views
# =============================================================================

class MarkListApi(APIView):
    """List marks."""
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Teacher - Marks'],
        summary='List mark records',
        parameters=[
            OpenApiParameter(name='student_id', type=int),
            OpenApiParameter(name='assignment_id', type=int),
            OpenApiParameter(name='include_inactive', type=bool),
        ],
        responses={200: MarkOutputSerializer(many=True)}
    )
    def get(self, request):
        filter_serializer = MarkFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        records = mark_list(
            actor=request.user,
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        return Response(MarkOutputSerializer(records, many=True).data)


class MarkRecordApi(APIView):
    """Record mark."""
    permission_classes = [IsTeacher]

    @extend_schema(
        tags=['Teacher - Marks'],
        summary='Record mark',
        request=MarkInputSerializer,
        responses={201: MarkOutputSerializer}
    )
    def post(self, request):
        serializer = MarkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        student = student_get(student_id=data['student_id'], actor=request.user)
        assignment = get_object_or_404(Assignment, id=data['assignment_id'])
        
        mark = mark_record(
            teacher=request.user.teacher_profile,
            student=student,
            assignment=assignment,
            score=data['score'],
            feedback=data.get('feedback')
        )
        return Response(MarkOutputSerializer(mark).data, status=status.HTTP_201_CREATED)


class MarkDetailApi(APIView):
    """Mark Detail."""
    permission_classes = [IsStaffUser]

    @extend_schema(tags=['Teacher - Marks'], summary='Get mark record')
    def get(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user)
        return Response(MarkOutputSerializer(record).data)


class MarkDeactivateApi(APIView):
    """Deactivate."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(tags=['Teacher - Marks'], summary='Deactivate mark record')
    def post(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user)
        mark_deactivate(mark=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkActivateApi(APIView):
    """Activate."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(tags=['Teacher - Marks'], summary='Activate mark record')
    def post(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user, include_inactive=True)
        mark_activate(mark=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
