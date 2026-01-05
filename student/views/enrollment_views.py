from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsStaffUser, IsAdminOrManagerOrSecretary
from student.models import StudentEnrollment
from student.selectors.enrollment_selectors import (
    student_enrollment_list,
    enrollment_get,
)
from student.services.enrollment_services import (
    enrollment_create,
    enrollment_update,
    enrollment_delete,
)


# =============================================================================
# Enrollment Serializers
# =============================================================================

class EnrollmentFilterSerializer(serializers.Serializer):
    """Filter serializer for enrollment list endpoint."""
    status = serializers.CharField(required=False)


class EnrollmentInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating enrollments."""
    student_id = serializers.IntegerField(required=False)
    class_room_id = serializers.IntegerField(required=False)
    academic_year_id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(
        choices=['enrolled', 'completed', 'withdrawn', 'transferred'],
        required=False
    )


class EnrollmentOutputSerializer(serializers.ModelSerializer):
    """Output serializer for enrollment responses."""
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    classroom_name = serializers.CharField(source='class_room.classroom_name', read_only=True)
    academic_year_code = serializers.CharField(source='academic_year.academic_year_code', read_only=True)
    grade_name = serializers.CharField(source='class_room.grade.name', read_only=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            'id', 'student_id', 'student_name',
            'class_room', 'classroom_name',
            'academic_year', 'academic_year_code',
            'grade_name', 'status'
        ]
        read_only_fields = ['id']


# =============================================================================
# Enrollment Views
# =============================================================================

class StudentEnrollmentListApi(APIView):
    """
    List enrollments for a specific student.

    GET: Returns enrollments for the given student.
    """
    permission_classes = [IsStaffUser]

    def get(self, request, student_id):
        """Return list of enrollments for a student."""
        enrollments = student_enrollment_list(
            student_id=student_id,
            actor=request.user
        )

        return Response(EnrollmentOutputSerializer(enrollments, many=True).data)


class EnrollmentCreateApi(APIView):
    """
    Create a new enrollment.

    POST: Create enrollment with provided data.
    """
    permission_classes = [IsAdminOrManagerOrSecretary]

    def post(self, request):
        """Create a new enrollment."""
        serializer = EnrollmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Validate required fields for creation
        required = ['student_id', 'class_room_id', 'academic_year_id']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})

        enrollment = enrollment_create(
            creator=request.user,
            student_id=data['student_id'],
            class_room_id=data['class_room_id'],
            academic_year_id=data['academic_year_id'],
            status=data.get('status', 'enrolled'),
        )

        return Response(
            EnrollmentOutputSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )


class EnrollmentDetailApi(APIView):
    """
    Retrieve, update, or delete a specific enrollment.

    GET: Retrieve enrollment details.
    PATCH: Update enrollment status.
    DELETE: Delete enrollment.
    """
    permission_classes = [IsAdminOrManagerOrSecretary]

    def get(self, request, enrollment_id):
        """Retrieve a single enrollment by ID."""
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)
        return Response(EnrollmentOutputSerializer(enrollment).data)

    def patch(self, request, enrollment_id):
        """Update an enrollment with partial data."""
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)

        serializer = EnrollmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_enrollment = enrollment_update(
            enrollment=enrollment,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(EnrollmentOutputSerializer(updated_enrollment).data)

    def delete(self, request, enrollment_id):
        """Delete an enrollment."""
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)
        enrollment_delete(enrollment=enrollment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
