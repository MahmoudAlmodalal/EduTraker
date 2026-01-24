from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManager
from accounts.pagination import PaginatedAPIMixin
from school.models import Course
from school.selectors.school_selectors import school_get
from school.selectors.course_selectors import course_list, course_get
from school.services.course_services import course_create, course_update, course_deactivate, course_activate


# =============================================================================
# Course Serializers
# =============================================================================

class CourseInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating courses."""
    grade_id = serializers.IntegerField(required=False, help_text="Grade ID")
    course_code = serializers.CharField(max_length=50, required=False, help_text="Course code")
    name = serializers.CharField(max_length=150, required=False, help_text="Course name")


class CourseOutputSerializer(serializers.ModelSerializer):
    """Output serializer for course responses."""
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'school', 'grade', 'grade_name', 'name',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'school', 'created_at', 'updated_at', 'deactivated_by_name']


class CourseFilterSerializer(serializers.Serializer):
    """Filter serializer for course list endpoint."""
    name = serializers.CharField(required=False, help_text="Filter by name")
    grade_id = serializers.IntegerField(required=False, help_text="Filter by grade")
    course_code = serializers.CharField(required=False, help_text="Filter by code")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


# =============================================================================
# Course Views
# =============================================================================

class CourseListApi(PaginatedAPIMixin, APIView):
    """List courses for a specific school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Course Management'],
        summary='List courses',
        description='Get all courses for a specific school.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='name', type=str, description='Filter by name'),
            OpenApiParameter(name='grade_id', type=int, description='Filter by grade'),
            OpenApiParameter(name='course_code', type=str, description='Filter by code'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: CourseOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Course List Response',
                value=[{
                    'id': 1,
                    'course_code': 'MATH101',
                    'school': 1,
                    'grade': 2,
                    'grade_name': 'Grade 1',
                    'name': 'Mathematics'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request, school_id):
        school_get(school_id=school_id, actor=request.user)
        filter_serializer = CourseFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        courses = course_list(
            school_id=school_id,
            actor=request.user,
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        page = self.paginate_queryset(courses)
        if page is not None:
            return self.get_paginated_response(CourseOutputSerializer(page, many=True).data)
        return Response(CourseOutputSerializer(courses, many=True).data)


class CourseCreateApi(APIView):
    """Create a new course for a school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Course Management'],
        summary='Create course',
        description='Create a new course for the specified school.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        request=CourseInputSerializer,
        examples=[OpenApiExample('Create Request', value={'grade_id': 1, 'course_code': 'MATH101', 'name': 'Mathematics'}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=CourseOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Course Created',
                        value={
                            'id': 10,
                            'course_code': 'SCI201',
                            'school': 1,
                            'grade': 3,
                            'grade_name': 'Grade 2',
                            'name': 'Science'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request, school_id):
        serializer = CourseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = course_create(
            creator=request.user, school_id=school_id,
            grade_id=serializer.validated_data['grade_id'],
            course_code=serializer.validated_data['course_code'],
            name=serializer.validated_data['name'],
        )
        return Response(CourseOutputSerializer(course).data, status=status.HTTP_201_CREATED)


class CourseDetailApi(APIView):
    """Retrieve, update, or deactivate a specific course."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Course Management'],
        summary='Get course details',
        description='Retrieve details of a specific course.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='course_id', type=int, location=OpenApiParameter.PATH, description='Course ID'),
        ],
        responses={
            200: OpenApiResponse(
                response=CourseOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Course Details',
                        value={
                            'id': 1,
                            'course_code': 'MATH101',
                            'school': 1,
                            'grade': 2,
                            'grade_name': 'Grade 1',
                            'name': 'Mathematics'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, school_id, course_id):
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)
        return Response(CourseOutputSerializer(course).data)

    @extend_schema(
        tags=['Course Management'],
        summary='Update course',
        description='Update a course with partial data.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='course_id', type=int, location=OpenApiParameter.PATH, description='Course ID'),
        ],
        request=CourseInputSerializer,
        examples=[OpenApiExample('Update Request', value={'name': 'Advanced Mathematics'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=CourseOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Course Updated',
                        value={
                            'id': 1,
                            'course_code': 'MATH101',
                            'school': 1,
                            'grade': 2,
                            'grade_name': 'Grade 1',
                            'name': 'Advanced Mathematics'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, school_id, course_id):
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)
        serializer = CourseInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_course = course_update(course=course, actor=request.user, data=serializer.validated_data)
        return Response(CourseOutputSerializer(updated_course).data)


class CourseDeactivateApi(APIView):
    """Deactivate a course."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Course Management'],
        summary='Deactivate course',
        description='Deactivate a course (soft delete).',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='course_id', type=int, location=OpenApiParameter.PATH, description='Course ID'),
        ],
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, school_id, course_id):
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)
        course_deactivate(course=course, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseActivateApi(APIView):
    """Activate a course."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Course Management'],
        summary='Activate course',
        description='Activate a previously deactivated course.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='course_id', type=int, location=OpenApiParameter.PATH, description='Course ID'),
        ],
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, school_id, course_id):
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user, include_inactive=True)
        course_activate(course=course, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)