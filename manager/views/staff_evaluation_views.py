from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

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
    reviewee_id = serializers.IntegerField(required=False)
    evaluation_date = serializers.DateField(required=False)
    rating_score = serializers.IntegerField(required=False)
    comments = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class StaffEvaluationOutputSerializer(serializers.ModelSerializer):
    """Output serializer for staff evaluation responses."""
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.full_name', read_only=True)

    class Meta:
        model = StaffEvaluation
        fields = [
            'id', 'reviewer', 'reviewer_name',
            'reviewee', 'reviewee_name',
            'evaluation_date', 'rating_score', 'comments'
        ]
        read_only_fields = ['id', 'reviewer']


class StaffEvaluationFilterSerializer(serializers.Serializer):
    """Filter serializer for staff evaluation list endpoint."""
    reviewee_id = serializers.IntegerField(required=False)
    reviewer_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


# =============================================================================
# StaffEvaluation Views
# =============================================================================

class StaffEvaluationListApi(APIView):
    """
    List all staff evaluations accessible to the current user.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        """Return list of staff evaluations filtered by user permissions."""
        filter_serializer = StaffEvaluationFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        evaluations = staff_evaluation_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )

        return Response(StaffEvaluationOutputSerializer(evaluations, many=True).data)


class StaffEvaluationCreateApi(APIView):
    """
    Create a new staff evaluation.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        """Create a new staff evaluation."""
        serializer = StaffEvaluationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Validate required fields
        required = ['reviewee_id', 'evaluation_date', 'rating_score']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})

        evaluation = staff_evaluation_create(
            reviewer=request.user,
            reviewee_id=data['reviewee_id'],
            evaluation_date=data['evaluation_date'],
            rating_score=data['rating_score'],
            comments=data.get('comments'),
        )

        return Response(
            StaffEvaluationOutputSerializer(evaluation).data,
            status=status.HTTP_201_CREATED
        )


class StaffEvaluationDetailApi(APIView):
    """
    Retrieve, update, or delete a specific staff evaluation.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, evaluation_id):
        """Retrieve a single staff evaluation by ID."""
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)
        return Response(StaffEvaluationOutputSerializer(evaluation).data)

    def patch(self, request, evaluation_id):
        """Update a staff evaluation with partial data."""
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)

        serializer = StaffEvaluationInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_evaluation = staff_evaluation_update(
            evaluation=evaluation,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(StaffEvaluationOutputSerializer(updated_evaluation).data)

    def delete(self, request, evaluation_id):
        """Delete a staff evaluation."""
        evaluation = staff_evaluation_get(evaluation_id=evaluation_id, actor=request.user)
        staff_evaluation_delete(evaluation=evaluation, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
