from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsTeacher
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
    assignment_delete,
)


# =============================================================================
# Assignment Views
# =============================================================================

class AssignmentListCreateApi(APIView):
    """List and create assignments for the authenticated teacher."""
    permission_classes = [IsTeacher]

    @extend_schema(
        operation_id='teacher_assignments_list',
        tags=['Teacher - Assignments'],
        summary='List assignments',
        description='Get all assignments created by the authenticated teacher with optional filtering.',
        parameters=[
            OpenApiParameter(
                name='exam_type',
                type=str,
                description='Filter by exam type (assignment, quiz, midterm, final, project)'
            ),
            OpenApiParameter(
                name='due_date_from',
                type=str,
                description='Filter assignments due on or after this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='due_date_to',
                type=str,
                description='Filter assignments due on or before this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='title',
                type=str,
                description='Filter by title (partial match)'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AssignmentOutputSerializer(many=True),
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
        }
    )
    def get(self, request):
        filter_serializer = AssignmentFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        teacher = request.user.teacher_profile
        assignments = assignment_list(teacher=teacher, filters=filter_serializer.validated_data)
        
        return Response(AssignmentOutputSerializer(assignments, many=True).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Create assignment',
        description='Create a new assignment for the authenticated teacher.',
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
            201: OpenApiResponse(
                response=AssignmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Assignment Created',
                        value={
                            'id': 10,
                            'assignment_code': 'ASN-E5F6G7H8',
                            'created_by': 1,
                            'created_by_name': 'John Smith',
                            'title': 'Mathematics Quiz 1',
                            'description': 'Basic algebra quiz covering chapters 1-3',
                            'due_date': '2026-02-15',
                            'exam_type': 'quiz',
                            'exam_type_display': 'Quiz',
                            'full_mark': '100.00'
                        }
                    )
                ]
            ),
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
    """Retrieve, update, or delete a specific assignment."""
    permission_classes = [IsTeacher]

    @extend_schema(
        operation_id='teacher_assignment_retrieve',
        tags=['Teacher - Assignments'],
        summary='Get assignment details',
        description='Retrieve details of a specific assignment.',
        parameters=[
            OpenApiParameter(
                name='assignment_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Assignment ID'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AssignmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Assignment Details',
                        value={
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
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Assignment not found')
        }
    )
    def get(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        return Response(AssignmentOutputSerializer(assignment).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Update assignment',
        description='Update an existing assignment with partial data.',
        parameters=[
            OpenApiParameter(
                name='assignment_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Assignment ID'
            ),
        ],
        request=AssignmentUpdateSerializer,
        examples=[
            OpenApiExample(
                'Update Assignment Request',
                value={
                    'title': 'Updated Mathematics Quiz',
                    'full_mark': '150.00'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=AssignmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Assignment Updated',
                        value={
                            'id': 1,
                            'assignment_code': 'ASN-A1B2C3D4',
                            'created_by': 1,
                            'created_by_name': 'John Smith',
                            'title': 'Updated Mathematics Quiz',
                            'description': 'Basic algebra quiz',
                            'due_date': '2026-02-15',
                            'exam_type': 'quiz',
                            'exam_type_display': 'Quiz',
                            'full_mark': '150.00'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Assignment not found')
        }
    )
    def patch(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        
        serializer = AssignmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_assignment = assignment_update(
            assignment=assignment,
            actor=request.user,
            data=serializer.validated_data
        )
        
        return Response(AssignmentOutputSerializer(updated_assignment).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Update assignment (full)',
        description='Update an existing assignment with full data.',
        parameters=[
            OpenApiParameter(
                name='assignment_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Assignment ID'
            ),
        ],
        request=AssignmentInputSerializer,
        responses={
            200: OpenApiResponse(response=AssignmentOutputSerializer),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Assignment not found')
        }
    )
    def put(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        
        serializer = AssignmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_assignment = assignment_update(
            assignment=assignment,
            actor=request.user,
            data=serializer.validated_data
        )
        
        return Response(AssignmentOutputSerializer(updated_assignment).data)

    @extend_schema(
        tags=['Teacher - Assignments'],
        summary='Delete assignment',
        description='Delete an assignment permanently.',
        parameters=[
            OpenApiParameter(
                name='assignment_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Assignment ID'
            ),
        ],
        responses={
            204: OpenApiResponse(description='Deleted successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Assignment not found')
        }
    )
    def delete(self, request, assignment_id):
        assignment = assignment_get(assignment_id=assignment_id, actor=request.user)
        assignment_delete(assignment=assignment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
