from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsTeacher, IsAdminOrManagerOrSecretary, IsStaffUser, IsStudent
from accounts.pagination import PaginatedAPIMixin
from teacher.models import Attendance
from teacher.selectors.attendance_selectors import attendance_list, attendance_get
from teacher.services.attendance_services import (
    attendance_record,
    attendance_deactivate,
    attendance_activate,
)
from student.selectors.student_selectors import student_get
from teacher.models import CourseAllocation
from django.shortcuts import get_object_or_404


# =============================================================================
# Attendance Serializers
# =============================================================================

class AttendanceFilterSerializer(serializers.Serializer):
    """Filter serializer for attendance list."""
    student_id = serializers.IntegerField(required=False)
    course_allocation_id = serializers.IntegerField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES, required=False)
    include_inactive = serializers.BooleanField(default=False)


class AttendanceInputSerializer(serializers.Serializer):
    """Input serializer for recording attendance."""
    student_id = serializers.IntegerField()
    course_allocation_id = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AttendanceOutputSerializer(serializers.ModelSerializer):
    """Output serializer for attendance records."""
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    course_name = serializers.CharField(source='course_allocation.course.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.user.full_name', read_only=True)
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'student_id', 'student_name', 'course_allocation', 'course_name',
            'date', 'status', 'note', 'recorded_by', 'recorded_by_name',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recorded_by_name', 'deactivated_by_name', 'created_at', 'updated_at']


# =============================================================================
# Attendance Views
# =============================================================================

class AttendanceListApi(PaginatedAPIMixin, APIView):
    """List attendance records."""
    permission_classes = [IsStaffUser | IsStudent]

    @extend_schema(
        tags=['Teacher - Attendance'],
        summary='List attendance records',
        parameters=[
            OpenApiParameter(name='student_id', type=int),
            OpenApiParameter(name='course_allocation_id', type=int),
            OpenApiParameter(name='date_from', type=str),
            OpenApiParameter(name='date_to', type=str),
            OpenApiParameter(name='status', type=str),
            OpenApiParameter(name='include_inactive', type=bool),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: AttendanceOutputSerializer(many=True)}
    )
    def get(self, request):
        filter_serializer = AttendanceFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        records = attendance_list(
            actor=request.user,
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        page = self.paginate_queryset(records)
        if page is not None:
            return self.get_paginated_response(AttendanceOutputSerializer(page, many=True).data)
        return Response(AttendanceOutputSerializer(records, many=True).data)


class AttendanceRecordApi(APIView):
    """Record attendance."""
    permission_classes = [IsTeacher]

    @extend_schema(
        tags=['Teacher - Attendance'],
        summary='Record attendance',
        request=AttendanceInputSerializer,
        responses={201: AttendanceOutputSerializer}
    )
    def post(self, request):
        serializer = AttendanceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        student = student_get(student_id=data['student_id'], actor=request.user)
        allocation = get_object_or_404(CourseAllocation, id=data['course_allocation_id'])
        
        attendance = attendance_record(
            teacher=request.user.teacher_profile,
            student=student,
            course_allocation=allocation,
            date=data['date'],
            status=data['status'],
            note=data.get('note')
        )
        return Response(AttendanceOutputSerializer(attendance).data, status=status.HTTP_201_CREATED)


class AttendanceDetailApi(APIView):
    """Attendance Detail."""
    permission_classes = [IsStaffUser | IsStudent]

    @extend_schema(
        tags=['Teacher - Attendance'], 
        summary='Get attendance record',
        responses={200: AttendanceOutputSerializer}
    )
    def get(self, request, attendance_id):
        record = attendance_get(attendance_id=attendance_id, actor=request.user)
        return Response(AttendanceOutputSerializer(record).data)


class AttendanceDeactivateApi(APIView):
    """Deactivate."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Attendance'], 
        summary='Deactivate attendance record',
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, attendance_id):
        record = attendance_get(attendance_id=attendance_id, actor=request.user)
        attendance_deactivate(attendance=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttendanceActivateApi(APIView):
    """Activate."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Attendance'], 
        summary='Activate attendance record',
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, attendance_id):
        record = attendance_get(attendance_id=attendance_id, actor=request.user, include_inactive=True)
        attendance_activate(attendance=record, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
