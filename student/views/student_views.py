"""
Student management API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, extend_schema_field

from accounts.serializers import MessageSerializer

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
    school_id = serializers.IntegerField(required=False, help_text="Filter by school")
    grade_id = serializers.IntegerField(required=False, help_text="Filter by grade (via enrollments)")
    current_status = serializers.CharField(required=False, help_text="Filter by status")
    search = serializers.CharField(required=False, help_text="Search by name or email")


class StudentInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating students."""
    email = serializers.EmailField(required=False, help_text="Email address")
    full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
    password = serializers.CharField(write_only=True, required=False, help_text="Password")
    school_id = serializers.IntegerField(required=False, help_text="School ID")
    grade_id = serializers.IntegerField(required=False, help_text="Grade ID (for initial enrollment)")
    date_of_birth = serializers.DateField(required=False, help_text="Date of birth")
    admission_date = serializers.DateField(required=False, help_text="Admission date")
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Address")
    medical_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Medical notes")
    current_status = serializers.ChoiceField(choices=['active', 'inactive', 'graduated', 'transferred', 'suspended'], required=False, help_text="Status")


class StudentOutputSerializer(serializers.ModelSerializer):
    """Output serializer for student responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    # School info now from user
    school_id = serializers.IntegerField(source='user.school_id', read_only=True, allow_null=True)
    school_name = serializers.SerializerMethodField()
    work_stream_id = serializers.SerializerMethodField()
    # Grade from current enrollment
    current_grade = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'user_id', 'email', 'full_name', 'is_active',
            'school_id', 'school_name', 'work_stream_id',
            'current_grade', 'date_of_birth', 'admission_date',
            'current_status', 'address', 'medical_notes'
        ]
        read_only_fields = ['user_id']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_school_name(self, obj):
        if obj.user.school:
            return obj.user.school.school_name
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_work_stream_id(self, obj):
        if obj.user.school:
            return obj.user.school.work_stream_id
        return None

    @extend_schema_field(serializers.DictField(allow_null=True, child=serializers.CharField()))
    def get_current_grade(self, obj):
        """Get current grade from active enrollment."""
        active_enrollment = obj.enrollments.filter(status='active').select_related('class_room__grade').first()
        if active_enrollment and active_enrollment.class_room and active_enrollment.class_room.grade:
            return {
                'id': active_enrollment.class_room.grade.id,
                'name': active_enrollment.class_room.grade.name
            }
        return None


# =============================================================================
# Student Views
# =============================================================================

class StudentListApi(APIView):
    """List all students accessible to the current user."""
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Student Management'],
        summary='List students',
        description='Get all students filtered by permissions and filters.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, description='Filter by school'),
            OpenApiParameter(name='grade_id', type=int, description='Filter by grade (via enrollments)'),
            OpenApiParameter(name='current_status', type=str, description='Filter by status'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
        ],
        responses={200: StudentOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Student List Response',
                value=[{
                    'user_id': 20,
                    'email': 'student1@example.com',
                    'full_name': 'John Student',
                    'is_active': True,
                    'school_id': 1,
                    'school_name': 'Global Academy',
                    'work_stream_id': 5,
                    'current_grade': {'id': 2, 'name': 'Grade 10'},
                    'date_of_birth': '2010-05-15',
                    'admission_date': '2024-09-01',
                    'current_status': 'active',
                    'address': '123 Study Lane',
                    'medical_notes': 'None'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = StudentFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        students = student_list(filters=filter_serializer.validated_data, user=request.user)
        return Response(StudentOutputSerializer(students, many=True).data)


class StudentCreateApi(APIView):
    """Create a new student."""
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Student Management'],
        summary='Create student',
        description='Create a new student with user account.',
        request=StudentInputSerializer,
        examples=[OpenApiExample('Create Request', value={
            'email': 'student@school.com', 'full_name': 'John Student', 'password': 'SecurePass123!',
            'school_id': 1, 'grade_id': 1, 'date_of_birth': '2010-01-15', 'admission_date': '2026-01-01'
        }, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=StudentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Student Created',
                        value={
                            'user_id': 21,
                            'email': 'alice.young@example.com',
                            'full_name': 'Alice Young',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'work_stream_id': 5,
                            'current_grade': {'id': 2, 'name': 'Grade 10'},
                            'date_of_birth': '2011-03-20',
                            'admission_date': '2026-01-01',
                            'current_status': 'active',
                            'address': '456 Learn Blvd',
                            'medical_notes': 'Asthma'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = StudentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        required = ['email', 'full_name', 'password', 'school_id', 'grade_id', 'date_of_birth', 'admission_date']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})
        student = student_create(
            creator=request.user, email=data['email'], full_name=data['full_name'], password=data['password'],
            school_id=data['school_id'], grade_id=data['grade_id'], date_of_birth=data['date_of_birth'],
            admission_date=data['admission_date'], address=data.get('address'), medical_notes=data.get('medical_notes'),
            current_status=data.get('current_status', 'active'),
        )
        return Response(StudentOutputSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailApi(APIView):
    """Retrieve, update, or delete a specific student."""
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Student Management'],
        summary='Get student details',
        description='Retrieve details of a specific student.',
        parameters=[OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID')],
        responses={
            200: OpenApiResponse(
                response=StudentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Student Details',
                        value={
                            'user_id': 20,
                            'email': 'student1@example.com',
                            'full_name': 'John Student',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'work_stream_id': 5,
                            'current_grade': {'id': 2, 'name': 'Grade 10'},
                            'date_of_birth': '2010-05-15',
                            'admission_date': '2024-09-01',
                            'current_status': 'active',
                            'address': '123 Study Lane',
                            'medical_notes': 'None'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, student_id):
        student = student_get(student_id=student_id, actor=request.user)
        return Response(StudentOutputSerializer(student).data)

    @extend_schema(
        tags=['Student Management'],
        summary='Update student',
        description='Update a student with partial data.',
        parameters=[OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID')],
        request=StudentInputSerializer,
        examples=[OpenApiExample('Update Request', value={'current_status': 'graduated'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=StudentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Student Updated',
                        value={
                            'user_id': 20,
                            'email': 'student1@example.com',
                            'full_name': 'John Student',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'work_stream_id': 5,
                            'current_grade': {'id': 2, 'name': 'Grade 10'},
                            'date_of_birth': '2010-05-15',
                            'admission_date': '2024-09-01',
                            'current_status': 'graduated',
                            'address': '123 Study Lane',
                            'medical_notes': 'None'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, student_id):
        student = student_get(student_id=student_id, actor=request.user)
        serializer = StudentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_student = student_update(student=student, actor=request.user, data=serializer.validated_data)
        return Response(StudentOutputSerializer(updated_student).data)

    @extend_schema(
        tags=['Student Management'],
        summary='Delete student',
        description='Delete a student permanently.',
        parameters=[OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID')],
        responses={204: OpenApiResponse(description='Deleted successfully')}
    )
    def delete(self, request, student_id):
        student = student_get(student_id=student_id, actor=request.user)
        student_delete(student=student, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentDeactivateApi(APIView):
    """Deactivate a student account."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Student Management'],
        summary='Deactivate student',
        description='Deactivate a student account (soft delete).',
        parameters=[OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID')],
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description='Student deactivated successfully',
                examples=[
                    OpenApiExample(
                        'Student Deactivated',
                        value={'detail': 'Student deactivated successfully.'}
                    )
                ]
            )
        }
    )
    def post(self, request, student_id):
        student = student_get(student_id=student_id, actor=request.user)
        student_deactivate(student=student, actor=request.user)
        return Response({"detail": "Student deactivated successfully."}, status=status.HTTP_200_OK)
