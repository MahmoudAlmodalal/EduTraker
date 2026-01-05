"""
School management API views.

Views are thin and only: parse request, validate with serializers,
call selectors/services, and return Response with correct status codes.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.models import CustomUser
from accounts.permissions import IsAdminOrManager, IsSuperAdmin
from manager.models import School, AcademicYear, Grade, Course, ClassRoom
from manager.selectors.school_selectors import (
    school_list,
    school_get,
    academic_year_list,
    grade_list,
    course_list,
    classroom_list,
)
from manager.services.school_services import (
    school_create,
    school_update,
    school_delete,
    academic_year_create,
    grade_create,
    course_create,
    classroom_create,
)


# =============================================================================
# School Serializers
# =============================================================================

class SchoolInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating schools."""
    school_name = serializers.CharField(max_length=255)
    work_stream_id = serializers.IntegerField()
    manager_id = serializers.IntegerField()


class SchoolOutputSerializer(serializers.ModelSerializer):
    """Output serializer for school responses."""
    work_stream_name = serializers.CharField(source='work_stream.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True, allow_null=True)

    class Meta:
        model = School
        fields = ['id', 'school_name', 'work_stream', 'work_stream_name', 'manager', 'manager_name']
        read_only_fields = ['id']


class SchoolFilterSerializer(serializers.Serializer):
    """Filter serializer for school list endpoint."""
    name = serializers.CharField(required=False)
    work_stream_id = serializers.IntegerField(required=False)
    manager_id = serializers.IntegerField(required=False)


# =============================================================================
# AcademicYear Serializers
# =============================================================================

class AcademicYearInputSerializer(serializers.Serializer):
    """Input serializer for creating academic years."""
    academic_year_code = serializers.CharField(max_length=20)
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class AcademicYearOutputSerializer(serializers.ModelSerializer):
    """Output serializer for academic year responses."""
    class Meta:
        model = AcademicYear
        fields = ['id', 'academic_year_code', 'school', 'start_date', 'end_date']
        read_only_fields = ['id', 'school']


class AcademicYearFilterSerializer(serializers.Serializer):
    """Filter serializer for academic year list endpoint."""
    academic_year_code = serializers.CharField(required=False)


# =============================================================================
# Grade Serializers
# =============================================================================

class GradeInputSerializer(serializers.Serializer):
    """Input serializer for creating grades."""
    name = serializers.CharField(max_length=50)
    numeric_level = serializers.IntegerField(min_value=1)
    min_age = serializers.IntegerField(min_value=0)
    max_age = serializers.IntegerField(min_value=0)


class GradeOutputSerializer(serializers.ModelSerializer):
    """Output serializer for grade responses."""
    class Meta:
        model = Grade
        fields = ['id', 'name', 'numeric_level', 'min_age', 'max_age']
        read_only_fields = ['id']


class GradeFilterSerializer(serializers.Serializer):
    """Filter serializer for grade list endpoint."""
    name = serializers.CharField(required=False)
    numeric_level = serializers.IntegerField(required=False)


# =============================================================================
# Course Serializers
# =============================================================================

class CourseInputSerializer(serializers.Serializer):
    """Input serializer for creating courses."""
    grade_id = serializers.IntegerField()
    course_code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=150)


class CourseOutputSerializer(serializers.ModelSerializer):
    """Output serializer for course responses."""
    grade_name = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'course_code', 'school', 'grade', 'grade_name', 'name']
        read_only_fields = ['id', 'school']


class CourseFilterSerializer(serializers.Serializer):
    """Filter serializer for course list endpoint."""
    course_code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    grade_id = serializers.IntegerField(required=False)


# =============================================================================
# ClassRoom Serializers
# =============================================================================

class ClassRoomInputSerializer(serializers.Serializer):
    """Input serializer for creating classrooms."""
    grade_id = serializers.IntegerField()
    classroom_name = serializers.CharField(max_length=100)
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
# School Views
# =============================================================================

class SchoolListApi(APIView):
    """
    List all schools accessible to the current user.
    
    GET: Returns filtered list of schools based on user role.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        """Return list of schools filtered by user permissions."""
        filter_serializer = SchoolFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        schools = school_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )

        return Response(SchoolOutputSerializer(schools, many=True).data)


class SchoolCreateApi(APIView):
    """
    Create a new school.
    
    POST: Create school with provided data.
    Authorization enforced in service layer.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        """Create a new school."""
        serializer = SchoolInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        school = school_create(
            creator=request.user,
            school_name=serializer.validated_data['school_name'],
            work_stream_id=serializer.validated_data['work_stream_id'],
            manager_id=serializer.validated_data['manager_id'],
        )

        return Response(
            SchoolOutputSerializer(school).data,
            status=status.HTTP_201_CREATED
        )


class SchoolDetailApi(APIView):
    """
    Retrieve, update, or delete a specific school.
    
    GET: Retrieve school details.
    PATCH: Update school fields.
    DELETE: Delete school.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id):
        """Retrieve a single school by ID."""
        school = school_get(school_id=school_id, actor=request.user)
        return Response(SchoolOutputSerializer(school).data)

    def patch(self, request, school_id):
        """Update a school with partial data."""
        school = school_get(school_id=school_id, actor=request.user)

        serializer = SchoolInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_school = school_update(
            school=school,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(SchoolOutputSerializer(updated_school).data)

    def delete(self, request, school_id):
        """Delete a school."""
        school = school_get(school_id=school_id, actor=request.user)
        school_delete(school=school, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# AcademicYear Views
# =============================================================================

class AcademicYearListApi(APIView):
    """
    List academic years for a specific school.
    
    GET: Returns academic years for the given school.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id):
        """Return list of academic years for a school."""
        # Verify user has access to the school
        school_get(school_id=school_id, actor=request.user)

        filter_serializer = AcademicYearFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        academic_years = academic_year_list(
            school_id=school_id,
            filters=filter_serializer.validated_data
        )

        return Response(AcademicYearOutputSerializer(academic_years, many=True).data)


class AcademicYearCreateApi(APIView):
    """
    Create a new academic year for a school.
    
    POST: Create academic year with provided data.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request, school_id):
        """Create a new academic year for the specified school."""
        serializer = AcademicYearInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        academic_year = academic_year_create(
            creator=request.user,
            school_id=school_id,
            academic_year_code=serializer.validated_data['academic_year_code'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )

        return Response(
            AcademicYearOutputSerializer(academic_year).data,
            status=status.HTTP_201_CREATED
        )


# =============================================================================
# Grade Views
# =============================================================================

class GradeListApi(APIView):
    """
    List all grades (global entities).
    
    GET: Returns all grades.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        """Return list of all grades."""
        filter_serializer = GradeFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        grades = grade_list(filters=filter_serializer.validated_data)

        return Response(GradeOutputSerializer(grades, many=True).data)


class GradeCreateApi(APIView):
    """
    Create a new grade (admin only).
    
    POST: Create grade with provided data.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        """Create a new grade."""
        serializer = GradeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grade = grade_create(
            creator=request.user,
            name=serializer.validated_data['name'],
            numeric_level=serializer.validated_data['numeric_level'],
            min_age=serializer.validated_data['min_age'],
            max_age=serializer.validated_data['max_age'],
        )

        return Response(
            GradeOutputSerializer(grade).data,
            status=status.HTTP_201_CREATED
        )


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
