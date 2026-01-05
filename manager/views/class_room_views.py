from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsAdminOrManager
from manager.models import ClassRoom
from manager.selectors.school_selectors import school_get
from manager.selectors.classroom_selectors import classroom_list, classroom_get
from manager.services.classroom_services import classroom_create, classroom_update, classroom_delete


# =============================================================================
# ClassRoom Serializers
# =============================================================================

class ClassRoomInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating classrooms."""
    grade_id = serializers.IntegerField(required=False)
    classroom_name = serializers.CharField(max_length=100, required=False)
    homeroom_teacher_id = serializers.IntegerField(required=False, allow_null=True)


class ClassRoomOutputSerializer(serializers.ModelSerializer):
    """Output serializer for classroom responses."""
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    homeroom_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassRoom
        fields = [
            'id', 'classroom_name', 'school', 'academic_year', 
            'grade', 'grade_name', 'homeroom_teacher', 'homeroom_teacher_name'
        ]
        read_only_fields = ['id', 'school', 'academic_year']

    def get_homeroom_teacher_name(self, obj):
        """Return teacher's full name if assigned."""
        if obj.homeroom_teacher:
            return obj.homeroom_teacher.user.full_name
        return None


class ClassRoomFilterSerializer(serializers.Serializer):
    """Filter serializer for classroom list endpoint."""
    classroom_name = serializers.CharField(required=False)
    grade_id = serializers.IntegerField(required=False)

# =============================================================================
# ClassRoom Views
# =============================================================================

class ClassRoomListApi(APIView):
    """
    List classrooms for a specific school and academic year.
    
    GET: Returns classrooms for the given school and academic year.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id, academic_year_id):
        """Return list of classrooms for a school and academic year."""
        # Verify user has access to the school
        school_get(school_id=school_id, actor=request.user)

        filter_serializer = ClassRoomFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        classrooms = classroom_list(
            school_id=school_id,
            academic_year_id=academic_year_id,
            filters=filter_serializer.validated_data
        )

        return Response(ClassRoomOutputSerializer(classrooms, many=True).data)


class ClassRoomCreateApi(APIView):
    """
    Create a new classroom for a school and academic year.
    
    POST: Create classroom with provided data.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request, school_id, academic_year_id):
        """Create a new classroom for the specified school and academic year."""
        serializer = ClassRoomInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        classroom = classroom_create(
            creator=request.user,
            school_id=school_id,
            academic_year_id=academic_year_id,
            grade_id=serializer.validated_data['grade_id'],
            classroom_name=serializer.validated_data['classroom_name'],
            homeroom_teacher_id=serializer.validated_data.get('homeroom_teacher_id'),
        )

        return Response(
            ClassRoomOutputSerializer(classroom).data,
            status=status.HTTP_201_CREATED
        )


class ClassRoomDetailApi(APIView):
    """
    Retrieve, update, or delete a specific classroom.
    
    GET: Retrieve classroom details.
    PATCH: Update classroom fields.
    DELETE: Delete classroom.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id, academic_year_id, classroom_id):
        """Retrieve a single classroom by ID."""
        classroom = classroom_get(
            classroom_id=classroom_id,
            school_id=school_id,
            academic_year_id=academic_year_id,
            actor=request.user
        )
        return Response(ClassRoomOutputSerializer(classroom).data)

    def patch(self, request, school_id, academic_year_id, classroom_id):
        """Update a classroom with partial data."""
        classroom = classroom_get(
            classroom_id=classroom_id,
            school_id=school_id,
            academic_year_id=academic_year_id,
            actor=request.user
        )

        serializer = ClassRoomInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_classroom = classroom_update(
            classroom=classroom,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(ClassRoomOutputSerializer(updated_classroom).data)

    def delete(self, request, school_id, academic_year_id, classroom_id):
        """Delete a classroom."""
        classroom = classroom_get(
            classroom_id=classroom_id,
            school_id=school_id,
            academic_year_id=academic_year_id,
            actor=request.user
        )
        classroom_delete(classroom=classroom, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
