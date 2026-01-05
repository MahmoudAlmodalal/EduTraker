from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsAdminOrManager
from manager.models import Grade
from manager.selectors.grade_selectors import grade_list, grade_get
from manager.services.grade_services import grade_create, grade_update, grade_delete


# =============================================================================
# Grade Serializers
# =============================================================================

class GradeInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating grades."""
    name = serializers.CharField(max_length=50, required=False)
    numeric_level = serializers.IntegerField(required=False)
    min_age = serializers.IntegerField(required=False)
    max_age = serializers.IntegerField(required=False)


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
# Grade Views
# =============================================================================

class GradeListApi(APIView):
    """
    List all grades.
    
    GET: Returns filtered list of grades.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        """Return list of grades."""
        filter_serializer = GradeFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        grades = grade_list(filters=filter_serializer.validated_data)

        return Response(GradeOutputSerializer(grades, many=True).data)


class GradeCreateApi(APIView):
    """
    Create a new grade.
    
    POST: Create grade with provided data.
    Authorization: admin only (enforced in service).
    """
    permission_classes = [IsAdminOrManager]

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


class GradeDetailApi(APIView):
    """
    Retrieve, update, or delete a specific grade.
    
    GET: Retrieve grade details.
    PATCH: Update grade fields.
    DELETE: Delete grade.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, grade_id):
        """Retrieve a single grade by ID."""
        grade = grade_get(grade_id=grade_id)
        return Response(GradeOutputSerializer(grade).data)

    def patch(self, request, grade_id):
        """Update a grade with partial data."""
        grade = grade_get(grade_id=grade_id)

        serializer = GradeInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_grade = grade_update(
            grade=grade,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(GradeOutputSerializer(updated_grade).data)

    def delete(self, request, grade_id):
        """Delete a grade."""
        grade = grade_get(grade_id=grade_id)
        grade_delete(grade=grade, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)