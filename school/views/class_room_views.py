from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, extend_schema_field

from accounts.permissions import IsAdminOrManager
from school.models import ClassRoom
from school.selectors.school_selectors import school_get
from school.selectors.classroom_selectors import classroom_list, classroom_get
from school.services.classroom_services import classroom_create, classroom_update, classroom_deactivate, classroom_activate


# =============================================================================
# ClassRoom Serializers
# =============================================================================

class ClassRoomInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating classrooms."""
    grade_id = serializers.IntegerField(required=False, help_text="Grade ID")
    classroom_name = serializers.CharField(max_length=100, required=False, help_text="Classroom name")
    homeroom_teacher_id = serializers.IntegerField(required=False, allow_null=True, help_text="Teacher ID")


class ClassRoomOutputSerializer(serializers.ModelSerializer):
    """Output serializer for classroom responses."""
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    homeroom_teacher_name = serializers.SerializerMethodField()
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = ClassRoom
        fields = [
            'id', 'classroom_name', 'school', 'academic_year', 'grade', 'grade_name', 
            'homeroom_teacher', 'homeroom_teacher_name',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'school', 'academic_year', 'created_at', 'updated_at', 'deactivated_by_name']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_homeroom_teacher_name(self, obj):
        if obj.homeroom_teacher:
            return obj.homeroom_teacher.user.full_name
        return None


class ClassRoomFilterSerializer(serializers.Serializer):
    """Filter serializer for classroom list endpoint."""
    classroom_name = serializers.CharField(required=False, help_text="Filter by name")
    grade_id = serializers.IntegerField(required=False, help_text="Filter by grade")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


# =============================================================================
# ClassRoom Views
# =============================================================================

class ClassRoomListApi(APIView):
    """List classrooms for a specific school and academic year."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Classroom Management'],
        summary='List classrooms',
        description='Get all classrooms for a specific school and academic year.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
            OpenApiParameter(name='classroom_name', type=str, description='Filter by name'),
            OpenApiParameter(name='grade_id', type=int, description='Filter by grade'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
        ],
        responses={200: ClassRoomOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Classroom List Response',
                value=[{
                    'id': 1,
                    'classroom_name': 'Class 1A',
                    'school': 1,
                    'academic_year': 2,
                    'grade': 3,
                    'grade_name': 'Grade 1',
                    'homeroom_teacher': 5,
                    'homeroom_teacher_name': 'John Teacher'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request, school_id, academic_year_id):
        school_get(school_id=school_id, actor=request.user)
        filter_serializer = ClassRoomFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        classrooms = classroom_list(
            school_id=school_id, 
            academic_year_id=academic_year_id, 
            actor=request.user,
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        return Response(ClassRoomOutputSerializer(classrooms, many=True).data)


class ClassRoomCreateApi(APIView):
    """Create a new classroom for a school and academic year."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Classroom Management'],
        summary='Create classroom',
        description='Create a new classroom for the specified school and academic year.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
        ],
        request=ClassRoomInputSerializer,
        examples=[OpenApiExample('Create Request', value={'grade_id': 1, 'classroom_name': 'Class A', 'homeroom_teacher_id': 5}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=ClassRoomOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Classroom Created',
                        value={
                            'id': 10,
                            'classroom_name': 'Science Lab A',
                            'school': 1,
                            'academic_year': 2,
                            'grade': 3,
                            'grade_name': 'Grade 1',
                            'homeroom_teacher': 5,
                            'homeroom_teacher_name': 'John Teacher'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request, school_id, academic_year_id):
        serializer = ClassRoomInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        classroom = classroom_create(
            creator=request.user, school_id=school_id, academic_year_id=academic_year_id,
            grade_id=serializer.validated_data['grade_id'],
            classroom_name=serializer.validated_data['classroom_name'],
            homeroom_teacher_id=serializer.validated_data.get('homeroom_teacher_id'),
        )
        return Response(ClassRoomOutputSerializer(classroom).data, status=status.HTTP_201_CREATED)


class ClassRoomDetailApi(APIView):
    """Retrieve, update, or deactivate a specific classroom."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Classroom Management'],
        summary='Get classroom details',
        description='Retrieve details of a specific classroom.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
            OpenApiParameter(name='classroom_id', type=int, location=OpenApiParameter.PATH, description='Classroom ID'),
        ],
        responses={
            200: OpenApiResponse(
                response=ClassRoomOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Classroom Details',
                        value={
                            'id': 1,
                            'classroom_name': 'Class 1A',
                            'school': 1,
                            'academic_year': 2,
                            'grade': 3,
                            'grade_name': 'Grade 1',
                            'homeroom_teacher': 5,
                            'homeroom_teacher_name': 'John Teacher'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, school_id, academic_year_id, classroom_id):
        classroom = classroom_get(classroom_id=classroom_id, school_id=school_id, academic_year_id=academic_year_id, actor=request.user)
        return Response(ClassRoomOutputSerializer(classroom).data)

    @extend_schema(
        tags=['Classroom Management'],
        summary='Update classroom',
        description='Update a classroom with partial data.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
            OpenApiParameter(name='classroom_id', type=int, location=OpenApiParameter.PATH, description='Classroom ID'),
        ],
        request=ClassRoomInputSerializer,
        examples=[OpenApiExample('Update Request', value={'classroom_name': 'Class B'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=ClassRoomOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Classroom Updated',
                        value={
                            'id': 1,
                            'classroom_name': 'Class 1B',
                            'school': 1,
                            'academic_year': 2,
                            'grade': 3,
                            'grade_name': 'Grade 1',
                            'homeroom_teacher': 5,
                            'homeroom_teacher_name': 'John Teacher'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, school_id, academic_year_id, classroom_id):
        classroom = classroom_get(classroom_id=classroom_id, school_id=school_id, academic_year_id=academic_year_id, actor=request.user)
        serializer = ClassRoomInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_classroom = classroom_update(classroom=classroom, actor=request.user, data=serializer.validated_data)
        return Response(ClassRoomOutputSerializer(updated_classroom).data)


class ClassRoomDeactivateApi(APIView):
    """Deactivate a classroom."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Classroom Management'],
        summary='Deactivate classroom',
        description='Deactivate a classroom (soft delete).',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
            OpenApiParameter(name='classroom_id', type=int, location=OpenApiParameter.PATH, description='Classroom ID'),
        ],
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, school_id, academic_year_id, classroom_id):
        classroom = classroom_get(classroom_id=classroom_id, school_id=school_id, academic_year_id=academic_year_id, actor=request.user)
        classroom_deactivate(classroom=classroom, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassRoomActivateApi(APIView):
    """Activate a classroom."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Classroom Management'],
        summary='Activate classroom',
        description='Activate a previously deactivated classroom.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
            OpenApiParameter(name='classroom_id', type=int, location=OpenApiParameter.PATH, description='Classroom ID'),
        ],
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, school_id, academic_year_id, classroom_id):
        classroom = classroom_get(classroom_id=classroom_id, school_id=school_id, academic_year_id=academic_year_id, actor=request.user, include_inactive=True)
        classroom_activate(classroom=classroom, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
