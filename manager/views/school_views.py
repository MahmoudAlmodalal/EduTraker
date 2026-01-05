from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.models import CustomUser
from accounts.permissions import IsAdminOrManager
from manager.models import School
from manager.selectors.school_selectors import school_list, school_get
from manager.services.school_services import school_create, school_update, school_delete


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