from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManagerOrSecretary, IsStaffUser, IsTeacher
from guardian.models import Guardian, GuardianStudentLink
from guardian.selectors.guardian_selectors import guardian_list, guardian_get, guardian_student_list
from guardian.services.guardian_services import (
    guardian_create,
    guardian_update,
    guardian_deactivate,
    guardian_activate,
    guardian_student_link_create,
    guardian_student_link_deactivate,
)
from student.selectors.student_selectors import student_get


# =============================================================================
# Guardian Serializers
# =============================================================================

class GuardianFilterSerializer(serializers.Serializer):
    """Filter serializer for guardian list endpoint."""
    school_id = serializers.IntegerField(required=False, help_text="Filter by school")
    search = serializers.CharField(required=False, help_text="Search by name or email")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


class GuardianInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating guardians."""
    email = serializers.EmailField(required=False, help_text="Email address")
    full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
    password = serializers.CharField(write_only=True, required=False, help_text="Password")
    school_id = serializers.IntegerField(required=False, help_text="School ID")
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True, help_text="Phone number")


class GuardianOutputSerializer(serializers.ModelSerializer):
    """Output serializer for guardian responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    school_id = serializers.IntegerField(source='user.school_id', read_only=True, allow_null=True)
    school_name = serializers.CharField(source='user.school.school_name', read_only=True, allow_null=True)
    
    deactivated_at = serializers.DateTimeField(source='user.deactivated_at', read_only=True)
    deactivated_by_name = serializers.CharField(source='user.deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Guardian
        fields = [
            'user_id', 'email', 'full_name', 'is_active',
            'school_id', 'school_name', 'phone_number',
            'deactivated_at', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'deactivated_by_name']


class GuardianStudentLinkInputSerializer(serializers.Serializer):
    """Input serializer for linking student to guardian."""
    student_id = serializers.IntegerField(help_text="Student ID")
    relationship_type = serializers.ChoiceField(choices=GuardianStudentLink.RELATIONSHIP_CHOICES, help_text="Relationship type")


class GuardianStudentLinkOutputSerializer(serializers.ModelSerializer):
    """Output serializer for links."""
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    relationship_display = serializers.CharField(source='get_relationship_type_display', read_only=True)

    class Meta:
        model = GuardianStudentLink
        fields = ['id', 'student_id', 'student_name', 'relationship_type', 'relationship_display', 'is_active']


# =============================================================================
# Guardian Views
# =============================================================================

class GuardianListApi(APIView):
    """List guardians."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Guardian Management'],
        summary='List guardians',
        parameters=[
            OpenApiParameter(name='school_id', type=int, description='Filter by school'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
        ],
        responses={200: GuardianOutputSerializer(many=True)}
    )
    def get(self, request):
        filter_serializer = GuardianFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        guardians = guardian_list(
            filters=filter_serializer.validated_data, 
            user=request.user,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        return Response(GuardianOutputSerializer(guardians, many=True).data)


class GuardianCreateApi(APIView):
    """Create guardian."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Guardian Management'],
        summary='Create guardian',
        request=GuardianInputSerializer,
        responses={201: GuardianOutputSerializer}
    )
    def post(self, request):
        serializer = GuardianInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        guardian = guardian_create(
            creator=request.user, email=data['email'], full_name=data['full_name'], password=data['password'],
            school_id=data['school_id'], phone_number=data.get('phone_number')
        )
        return Response(GuardianOutputSerializer(guardian).data, status=status.HTTP_201_CREATED)


class GuardianDetailApi(APIView):
    """Detail API."""
    permission_classes = [IsAdminOrManagerOrSecretary | IsTeacher | IsStaffUser]

    @extend_schema(
        tags=['Guardian Management'],
        summary='Get guardian details',
        responses={200: GuardianOutputSerializer}
    )
    def get(self, request, guardian_id):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        return Response(GuardianOutputSerializer(guardian).data)

    @extend_schema(
        tags=['Guardian Management'],
        summary='Update guardian',
        request=GuardianInputSerializer,
        responses={200: GuardianOutputSerializer}
    )
    def patch(self, request, guardian_id):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        serializer = GuardianInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = guardian_update(guardian=guardian, actor=request.user, data=serializer.validated_data)
        return Response(GuardianOutputSerializer(updated).data)


class GuardianDeactivateApi(APIView):
    """Deactivate."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(tags=['Guardian Management'], summary='Deactivate guardian')
    def post(self, request, guardian_id):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        guardian_deactivate(guardian=guardian, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GuardianActivateApi(APIView):
    """Activate."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(tags=['Guardian Management'], summary='Activate guardian')
    def post(self, request, guardian_id):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user, include_inactive=True)
        guardian_activate(guardian=guardian, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GuardianStudentLinkApi(APIView):
    """Link student to guardian."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Guardian Management'],
        summary='List linked students',
        responses={200: GuardianStudentLinkOutputSerializer(many=True)}
    )
    def get(self, request, guardian_id):
        links = guardian_student_list(guardian_id=guardian_id, actor=request.user)
        return Response(GuardianStudentLinkOutputSerializer(links, many=True).data)

    @extend_schema(
        tags=['Guardian Management'],
        summary='Link student to guardian',
        request=GuardianStudentLinkInputSerializer,
        responses={201: GuardianStudentLinkOutputSerializer}
    )
    def post(self, request, guardian_id):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        serializer = GuardianStudentLinkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = student_get(student_id=serializer.validated_data['student_id'], actor=request.user)
        link = guardian_student_link_create(
            actor=request.user, guardian=guardian, student=student,
            relationship_type=serializer.validated_data['relationship_type']
        )
        return Response(GuardianStudentLinkOutputSerializer(link).data, status=status.HTTP_201_CREATED)
