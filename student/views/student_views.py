"""
Student management API views.

Views are thin controllers: parse request, validate with serializers,
call selectors/services, and return Response with correct status codes.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.models import CustomUser
from accounts.permissions import IsStaffUser, IsAdminOrManagerOrSecretary
from student.models import Student
from student.selectors.student_selectors import (
    student_list,
    student_get,
)
from student.services.student_services import (
    student_create,
    student_update,
    student_delete,
    student_deactivate,
)


# =============================================================================
# Student Serializers
# =============================================================================

class StudentFilterSerializer(serializers.Serializer):
    """Filter serializer for student list endpoint."""
    school_id = serializers.IntegerField(required=False)
    grade_id = serializers.IntegerField(required=False)
    current_status = serializers.CharField(required=False)
    search = serializers.CharField(required=False)


class StudentInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating students."""
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, required=False)
    school_id = serializers.IntegerField(required=False)
    grade_id = serializers.IntegerField(required=False)
    date_of_birth = serializers.DateField(required=False)
    admission_date = serializers.DateField(required=False)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    medical_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    current_status = serializers.ChoiceField(
        choices=['active', 'inactive', 'graduated', 'transferred', 'suspended'],
        required=False
    )


class StudentOutputSerializer(serializers.ModelSerializer):
    """Output serializer for student responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True, allow_null=True)
    work_stream_id = serializers.IntegerField(source='school.work_stream_id', read_only=True)

    class Meta:
        model = Student
        fields = [
            'user_id', 'email', 'full_name', 'is_active',
            'school', 'school_name', 'work_stream_id',
            'grade', 'grade_name',
            'date_of_birth', 'admission_date',
            'current_status', 'address', 'medical_notes'
        ]
        read_only_fields = ['user_id']


# =============================================================================
# Student Views
# =============================================================================

class StudentListApi(APIView):
    """
    List all students accessible to the current user.

    GET: Returns filtered list of students based on user role and filters.
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        """Return list of students filtered by user permissions."""
        filter_serializer = StudentFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        students = student_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )

        return Response(StudentOutputSerializer(students, many=True).data)


class StudentCreateApi(APIView):
    """
    Create a new student.

    POST: Create student with provided data.
    Authorization enforced in service layer.
    """
    permission_classes = [IsStaffUser]

    def post(self, request):
        """Create a new student."""
        serializer = StudentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Validate required fields for creation
        required = ['email', 'full_name', 'password', 'school_id', 'grade_id', 'date_of_birth', 'admission_date']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})

        student = student_create(
            creator=request.user,
            email=data['email'],
            full_name=data['full_name'],
            password=data['password'],
            school_id=data['school_id'],
            grade_id=data['grade_id'],
            date_of_birth=data['date_of_birth'],
            admission_date=data['admission_date'],
            address=data.get('address'),
            medical_notes=data.get('medical_notes'),
            current_status=data.get('current_status', 'active'),
        )

        return Response(
            StudentOutputSerializer(student).data,
            status=status.HTTP_201_CREATED
        )


class StudentDetailApi(APIView):
    """
    Retrieve, update, or delete a specific student.

    GET: Retrieve student details.
    PATCH: Update student fields.
    DELETE: Raises error instructing to use deactivate.
    """
    permission_classes = [IsStaffUser]

    def get(self, request, student_id):
        """Retrieve a single student by ID."""
        student = student_get(student_id=student_id, actor=request.user)
        return Response(StudentOutputSerializer(student).data)

    def patch(self, request, student_id):
        """Update a student with partial data."""
        student = student_get(student_id=student_id, actor=request.user)

        serializer = StudentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_student = student_update(
            student=student,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(StudentOutputSerializer(updated_student).data)

    def delete(self, request, student_id):
        """Delete a student (raises error instructing to use deactivate)."""
        student = student_get(student_id=student_id, actor=request.user)
        student_delete(student=student, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentDeactivateApi(APIView):
    """
    Deactivate a student account.

    POST: Deactivates the student and their user account.
    """
    permission_classes = [IsAdminOrManagerOrSecretary]

    def post(self, request, student_id):
        """Deactivate a student."""
        student = student_get(student_id=student_id, actor=request.user)

        deactivated_student = student_deactivate(
            student=student,
            actor=request.user
        )

        return Response(
            StudentOutputSerializer(deactivated_student).data,
            status=status.HTTP_200_OK
        )
