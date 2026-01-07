from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManager
from manager.models import StaffEvaluation
from manager.selectors.staff_evaluation_selectors import staff_evaluation_list, staff_evaluation_get
from manager.services.staff_evaluation_services import (
    staff_evaluation_create,
    staff_evaluation_update,
    staff_evaluation_delete,
)


# =============================================================================
# StaffEvaluation Serializers
# =============================================================================

class StaffEvaluationInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating staff evaluations."""
    reviewee_id = serializers.IntegerField(required=False, help_text="User ID of person being reviewed")
    evaluation_date = serializers.DateField(required=False, help_text="Date of evaluation")
    rating_score = serializers.IntegerField(required=False, help_text="Rating score (1-5)")
    comments = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Comments")


class StaffEvaluationOutputSerializer(serializers.ModelSerializer):
    """Output serializer for staff evaluation responses."""
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.full_name', read_only=True)

    class Meta:
        model = StaffEvaluation
        fields = ['id', 'reviewer', 'reviewer_name', 'reviewee', 'reviewee_name', 'evaluation_date', 'rating_score', 'comments']
        read_only_fields = ['id', 'reviewer']


class StaffEvaluationFilterSerializer(serializers.Serializer):
    """Filter serializer for staff evaluation list endpoint."""
    reviewee_id = serializers.IntegerField(required=False, help_text="Filter by reviewee")
    reviewer_id = serializers.IntegerField(required=False, help_text="Filter by reviewer")
    start_date = serializers.DateField(required=False, help_text="Filter by start date")
    end_date = serializers.DateField(required=False, help_text="Filter by end date")


# =============================================================================
# StaffEvaluation Views
# =============================================================================

class StaffEvaluationListApi(APIView):
    """List all staff evaluations accessible to the current user."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Staff Evaluation'],
        summary='List staff evaluations',
        description='Get all staff evaluations filtered by permissions.',
        parameters=[
            OpenApiParameter(name='reviewee_id', type=int, description='Filter by reviewee'),
            OpenApiParameter(name='reviewer_id', type=int, description='Filter by reviewer'),
            OpenApiParameter(name='start_date', type=str, description='Filter by start date'),
            OpenApiParameter(name='end_date', type=str, description='Filter by end date'),
        ],
        responses={200: StaffEvaluationOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Evaluation List Response',
                value=[{
                    'id': 1,
                    'reviewer': 2,
                    'reviewer_name': 'Jane Manager',
                    'reviewee': 5,
                    'reviewee_name': 'John Teacher',
                    'evaluation_date': '2026-01-06',
                    'rating_score': 4,
                    'comments': 'Consistently high performance.'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = StaffEvaluationFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        evaluations = staff_evaluation_list(filters=filter_serializer.validated_data, user=request.user)
        return Response(StaffEvaluationOutputSerializer(evaluations, many=True).data)


class StaffEvaluationCreateApi(APIView):
    """Create a new staff evaluation."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Staff Evaluation'],
        summary='Create staff evaluation',
        description='Create a new staff evaluation.',
        request=StaffEvaluationInputSerializer,
        examples=[OpenApiExample('Create Request', value={'reviewee_id': 5, 'evaluation_date': '2026-01-06', 'rating_score': 4, 'comments': 'Good work'}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=StaffEvaluationOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Evaluation Created',
                        value={
                            'id': 10,
                            'reviewer': 2,
                            'reviewer_name': 'Jane Manager',
                            'reviewee': 5,
                            'reviewee_name': 'John Teacher',
                            'evaluation_date': '2026-01-06',
                            'rating_score': 5,
                            'comments': 'Excellent contributions this term.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = StaffEvaluationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        required = ['reviewee_id', 'evaluation_date', 'rating_score']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})
        evaluation = staff_evaluation_create(
            reviewer=request.user, reviewee_id=data['reviewee_id'],
            evaluation_date=data['evaluation_date'], rating_score=data['rating_score'], comments=data.get('comments'),
        )
        return Response(StaffEvaluationOutputSerializer(evaluation).data, status=status.HTTP_201_CREATED)


class StaffEvaluationDetailApi(APIView):
    """Retrieve, update, or delete a specific staff evaluation."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Staff Evaluation'],
        summary='Get evaluation details',
        description='Retrieve details of a specific staff evaluation.',
        parameters=[OpenApiParameter(name='evaluation_id', type=int, location=OpenApiParameter.PATH, description='Evaluation ID')],
        responses={
            200: OpenApiResponse(
                response=StaffEvaluationOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Evaluation Details',
                        value={
                            'id': 1,
                            'reviewer': 2,
                            'reviewer_name': 'Jane Manager',
                            'reviewee': 5,
                            'reviewee_name': 'John Teacher',
                            'evaluation_date': '2026-01-06',
                            'rating_score': 4,
                            'comments': 'Consistently high performance.'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, evaluation_id):
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)
        return Response(StaffEvaluationOutputSerializer(evaluation).data)

    @extend_schema(
        tags=['Staff Evaluation'],
        summary='Update evaluation',
        description='Update a staff evaluation with partial data.',
        parameters=[OpenApiParameter(name='evaluation_id', type=int, location=OpenApiParameter.PATH, description='Evaluation ID')],
        request=StaffEvaluationInputSerializer,
        examples=[OpenApiExample('Update Request', value={'rating_score': 5}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=StaffEvaluationOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Evaluation Updated',
                        value={
                            'id': 1,
                            'reviewer': 2,
                            'reviewer_name': 'Jane Manager',
                            'reviewee': 5,
                            'reviewee_name': 'John Teacher',
                            'evaluation_date': '2026-01-06',
                            'rating_score': 5,
                            'comments': 'Updated rating to reflect final results.'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, evaluation_id):
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)
        serializer = StaffEvaluationInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_evaluation = staff_evaluation_update(evaluation=evaluation, actor=request.user, data=serializer.validated_data)
        return Response(StaffEvaluationOutputSerializer(updated_evaluation).data)

    @extend_schema(
        tags=['Staff Evaluation'],
        summary='Delete evaluation',
        description='Delete a staff evaluation permanently.',
        parameters=[OpenApiParameter(name='evaluation_id', type=int, location=OpenApiParameter.PATH, description='Evaluation ID')],
        responses={204: OpenApiResponse(description='Deleted successfully')}
    )
    def delete(self, request, evaluation_id):
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)
        staff_evaluation_delete(evaluation=evaluation, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
