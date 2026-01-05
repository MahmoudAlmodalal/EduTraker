from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsAdminOrManager
from manager.models import AcademicYear
from manager.selectors.school_selectors import school_get
from manager.selectors.academic_year_selectors import academic_year_list, academic_year_get
from manager.services.academic_year_services import academic_year_create, academic_year_update, academic_year_delete


# =============================================================================
# AcademicYear Serializers
# =============================================================================

class AcademicYearInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating academic years."""
    academic_year_code = serializers.CharField(max_length=20, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


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


class AcademicYearDetailApi(APIView):
    """
    Retrieve, update, or delete a specific academic year.
    
    GET: Retrieve academic year details.
    PATCH: Update academic year fields.
    DELETE: Delete academic year.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, school_id, academic_year_id):
        """Retrieve a single academic year by ID."""
        academic_year = academic_year_get(
            academic_year_id=academic_year_id,
            school_id=school_id,
            actor=request.user
        )
        return Response(AcademicYearOutputSerializer(academic_year).data)

    def patch(self, request, school_id, academic_year_id):
        """Update an academic year with partial data."""
        academic_year = academic_year_get(
            academic_year_id=academic_year_id,
            school_id=school_id,
            actor=request.user
        )

        serializer = AcademicYearInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_year = academic_year_update(
            academic_year=academic_year,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(AcademicYearOutputSerializer(updated_year).data)

    def delete(self, request, school_id, academic_year_id):
        """Delete an academic year."""
        academic_year = academic_year_get(
            academic_year_id=academic_year_id,
            school_id=school_id,
            actor=request.user
        )
        academic_year_delete(academic_year=academic_year, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)