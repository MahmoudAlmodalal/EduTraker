from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsAdminOrManager
from manager.models import Course
from manager.selectors.school_selectors import school_get
from manager.selectors.course_selectors import course_list, course_get
from manager.services.course_services import course_create, course_update, course_delete


# =============================================================================
# Course Serializers
# =============================================================================

class CourseInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating courses."""
    grade_id = serializers.IntegerField(required=False)
    course_code = serializers.CharField(max_length=50, required=False)
    name = serializers.CharField(max_length=150, required=False)


class CourseOutputSerializer(serializers.ModelSerializer):
    """Output serializer for course responses."""
    grade_name = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'course_code', 'school', 'grade', 'grade_name', 'name']
        read_only_fields = ['id', 'school']


class CourseFilterSerializer(serializers.Serializer):
    """Filter serializer for course list endpoint."""
    name = serializers.CharField(required=False)
    grade_id = serializers.IntegerField(required=False)
    course_code = serializers.CharField(required=False)

# =============================================================================
# Course Views
# =============================================================================

class CourseListApi(APIView):
    """
    List courses for a specific school.
    
    GET: Returns courses for the given school.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id):
        """Return list of courses for a school."""
        # Verify user has access to the school
        school_get(school_id=school_id, actor=request.user)

        filter_serializer = CourseFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        courses = course_list(
            school_id=school_id,
            filters=filter_serializer.validated_data
        )

        return Response(CourseOutputSerializer(courses, many=True).data)


class CourseCreateApi(APIView):
    """
    Create a new course for a school.
    
    POST: Create course with provided data.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request, school_id):
        """Create a new course for the specified school."""
        serializer = CourseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = course_create(
            creator=request.user,
            school_id=school_id,
            grade_id=serializer.validated_data['grade_id'],
            course_code=serializer.validated_data['course_code'],
            name=serializer.validated_data['name'],
        )

        return Response(
            CourseOutputSerializer(course).data,
            status=status.HTTP_201_CREATED
        )


class CourseDetailApi(APIView):
    """
    Retrieve, update, or delete a specific course.
    
    GET: Retrieve course details.
    PATCH: Update course fields.
    DELETE: Delete course.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id, course_id):
        """Retrieve a single course by ID."""
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)
        return Response(CourseOutputSerializer(course).data)

    def patch(self, request, school_id, course_id):
        """Update a course with partial data."""
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)

        serializer = CourseInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_course = course_update(
            course=course,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(CourseOutputSerializer(updated_course).data)

    def delete(self, request, school_id, course_id):
        """Delete a course."""
        course = course_get(course_id=course_id, school_id=school_id, actor=request.user)
        course_delete(course=course, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)