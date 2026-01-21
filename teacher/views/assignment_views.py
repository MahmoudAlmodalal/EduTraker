from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsTeacher, IsAdminOrManagerOrSecretary
from teacher.serializers.assignment_serializers import (
    AssignmentInputSerializer,
    AssignmentUpdateSerializer,
    AssignmentOutputSerializer,
    AssignmentFilterSerializer,
)
from teacher.selectors.assignment_selectors import assignment_list, assignment_get
from teacher.services.assignment_services import (
    assignment_create,
    assignment_update,
    assignment_deactivate,
    assignment_activate,
)


# =============================================================================
# Assignment Views
# =============================================================================

class AssignmentListCreateApi(APIView):
    """List and create assignments."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(
        operation_id='teacher_assignments_list',
        tags=['Teacher - Assignments'],
        summary='List assignments',
        description='Get assignments with optional filtering and RBAC.',
        parameters=[
            OpenApiParameter(name='exam_type', type=str, description='Filter by exam type'),
            OpenApiParameter(name='due_date_from', type=str, description='Filter by due date from'),
            OpenApiParameter(name='due_date_to', type=str, description='Filter by due date to'),
            OpenApiParameter(name='title', type=str, description='Filter by title'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
        ],
        responses={200: AssignmentOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Assignment List Response',
                value=[{
                    'id': 1,
                    'assignment_code': 'ASN-A1B2C3D4',
                    'created_by': 1,
                    'created_by_name': 'John Smith',
                    'title': 'Mathematics Quiz 1',
                    'description': 'Basic algebra quiz',
                    'due_date': '2026-02-15',
                    'exam_type': 'quiz',
                    'exam_type_display': 'Quiz',
                    'full_mark': '100.00'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = AssignmentFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        assignments = assignment_list(
            actor=request.user, 
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        
        return Response(AssignmentOutputSerializer(assignments, many=True).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Create assignment',
        description='Create a new assignment. Must be a teacher.',
        request=AssignmentInputSerializer,
        examples=[
            OpenApiExample(
                'Create Assignment Request',
                value={
                    'title': 'Mathematics Quiz 1',
                    'description': 'Basic algebra quiz covering chapters 1-3',
                    'due_date': '2026-02-15',
                    'exam_type': 'quiz',
                    'full_mark': '100.00'
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(response=AssignmentOutputSerializer),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied - not a teacher')
        }
    )
    def post(self, request):
        serializer = AssignmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        assignment = assignment_create(
            creator=request.user,
            title=serializer.validated_data['title'],
            exam_type=serializer.validated_data['exam_type'],
            full_mark=serializer.validated_data['full_mark'],
            assignment_code=serializer.validated_data.get('assignment_code'),
            description=serializer.validated_data.get('description'),
            due_date=serializer.validated_data.get('due_date'),
        )
        
        return Response(
            AssignmentOutputSerializer(assignment).data,
            status=status.HTTP_201_CREATED
        )


class AssignmentDetailApi(APIView):
    """Retrieve, update, or deactivate a specific assignment."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(
        operation_id='teacher_assignment_retrieve',
        tags=['Teacher - Assignments'],
        summary='Get assignment details',
        description='Retrieve details of a specific assignment.',
        parameters=[OpenApiParameter(name='assignment_id', type=int, location=OpenApiParameter.PATH, description='Assignment ID')],
        responses={200: OpenApiResponse(response=AssignmentOutputSerializer)}
    )
    def get(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        return Response(AssignmentOutputSerializer(assignment).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Update assignment',
        description='Update an existing assignment with partial data.',
        parameters=[OpenApiParameter(name='assignment_id', type=int, location=OpenApiParameter.PATH, description='Assignment ID')],
        request=AssignmentUpdateSerializer,
        responses={200: OpenApiResponse(response=AssignmentOutputSerializer)}
    )
    def patch(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        serializer = AssignmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_assignment = assignment_update(assignment=assignment, actor=request.user, data=serializer.validated_data)
        return Response(AssignmentOutputSerializer(updated_assignment).data)


class AssignmentDeactivateApi(APIView):
    """Deactivate an assignment."""
    permission_classes = [IsTeacher | IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Deactivate assignment',
        description='Deactivate an assignment (soft delete).',
        parameters=[OpenApiParameter(name='assignment_id', type=int, location=OpenApiParameter.PATH, description='Assignment ID')],
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        assignment_deactivate(assignment=assignment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentActivateApi(APIView):
    """Activate an assignment."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Activate assignment',
        description='Activate a previously deactivated assignment.',
        parameters=[OpenApiParameter(name='assignment_id', type=int, location=OpenApiParameter.PATH, description='Assignment ID')],
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user, include_inactive=True)
        assignment_activate(assignment=assignment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
