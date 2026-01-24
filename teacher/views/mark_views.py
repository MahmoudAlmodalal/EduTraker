from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsTeacher, IsAdminOrManagerOrSecretary, IsStaffUser, IsStudent
from accounts.pagination import PaginatedAPIMixin
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

class MarkListApi(PaginatedAPIMixin, APIView):
    """List marks."""
    permission_classes = [IsStaffUser | IsStudent]

    @extend_schema(
        tags=['Teacher - Marks'],
        summary='List mark records',
        parameters=[
            OpenApiParameter(name='student_id', type=int),
            OpenApiParameter(name='assignment_id', type=int),
            OpenApiParameter(name='include_inactive', type=bool),
            OpenApiParameter(name='page', type=int, description='Page number'),
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
        page = self.paginate_queryset(records)
        if page is not None:
            return self.get_paginated_response(MarkOutputSerializer(page, many=True).data)
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
    permission_classes = [IsStaffUser | IsStudent]

    @extend_schema(
        tags=['Teacher - Marks'], 
        summary='Get mark record',
        responses={200: MarkOutputSerializer}
    )
    def get(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user)
        return Response(MarkOutputSerializer(record).data)


class MarkDeactivateApi(APIView):
    """Deactivate."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Marks'], 
        summary='Deactivate mark record',
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user)
        mark_deactivate(mark=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkActivateApi(APIView):
    """Activate."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Marks'], 
        summary='Activate mark record',
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, mark_id):
        record = mark_get(mark_id=mark_id, actor=request.user, include_inactive=True)
        mark_activate(mark=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
from teacher.services.mark_services import mark_bulk_import
from teacher.services.knowledge_gap_services import identify_knowledge_gaps
from teacher.models import CourseAllocation

class BulkMarkImportApi(APIView):
    """
    Bulk import marks from CSV.
    """
    permission_classes = [IsTeacher]

    @extend_schema(
        tags=['Teacher - Marks'],
        summary='Bulk import marks from CSV',
        description='Upload a CSV file with "student_email,score,feedback" to bulk record marks for an assignment.',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'assignment_id': {'type': 'integer'},
                    'file': {'type': 'string', 'format': 'binary'}
                },
                'required': ['assignment_id', 'file']
            }
        },
        responses={200: OpenApiResponse(description='Import results')}
    )
    def post(self, request):
        assignment_id = request.data.get('assignment_id')
        csv_file = request.FILES.get('file')
        
        if not assignment_id or not csv_file:
            return Response({"detail": "assignment_id and file are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        results = mark_bulk_import(
            teacher=request.user.teacher_profile,
            assignment=assignment,
            csv_file=csv_file
        )
        return Response(results, status=status.HTTP_200_OK)


class KnowledgeGapListApi(APIView):
    """
    Identify student knowledge gaps for a course allocation.
    """
    permission_classes = [IsTeacher]

    @extend_schema(
        tags=['Teacher - Analytics'],
        summary='Identify knowledge gaps',
        description='Identify students performing below a threshold in a specific course allocation.',
        parameters=[
            OpenApiParameter(name='course_allocation_id', type=int, required=True),
            OpenApiParameter(name='threshold', type=float, default=50.0),
        ],
        responses={200: OpenApiResponse(description='List of at-risk students')}
    )
    def get(self, request):
        allocation_id = request.query_params.get('course_allocation_id')
        threshold = request.query_params.get('threshold', 50.0)
        
        if not allocation_id:
             return Response({"detail": "course_allocation_id is required."}, status=status.HTTP_400_BAD_REQUEST)
             
        allocation = get_object_or_404(CourseAllocation, id=allocation_id)
        
        # Security check: Teacher should own this allocation
        if allocation.teacher != request.user.teacher_profile:
             return Response({"detail": "You don't have access to this allocation."}, status=status.HTTP_403_FORBIDDEN)

        gaps = identify_knowledge_gaps(
            course_allocation=allocation,
            threshold=Decimal(str(threshold))
        )
        return Response(gaps, status=status.HTTP_200_OK)
