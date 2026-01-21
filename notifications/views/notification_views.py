from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
from django.utils import timezone

from notifications.models import Notification


# =============================================================================
# Notification Serializers
# =============================================================================

class NotificationOutputSerializer(serializers.ModelSerializer):
    """Output serializer for notifications."""
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'recipient', 'recipient_email', 'sender', 'sender_name',
            'action_url', 'related_object_type', 'related_object_id',
            'is_read', 'read_at', 'email_sent', 'push_sent',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationFilterSerializer(serializers.Serializer):
    """Filter serializer for notification list."""
    is_read = serializers.BooleanField(required=False)
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPE_CHOICES,
        required=False
    )


# =============================================================================
# Notification Views
# =============================================================================

class NotificationListApi(APIView):
    """List notifications for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='List user notifications',
        parameters=[
            OpenApiParameter(name='is_read', type=bool),
            OpenApiParameter(name='notification_type', type=str),
        ],
        responses={200: NotificationOutputSerializer(many=True)}
    )
    def get(self, request):
        filter_serializer = NotificationFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_active=True
        )
        
        if 'is_read' in filters:
            notifications = notifications.filter(is_read=filters['is_read'])
        if 'notification_type' in filters:
            notifications = notifications.filter(notification_type=filters['notification_type'])
        
        notifications = notifications.order_by('-created_at')
        return Response(NotificationOutputSerializer(notifications, many=True).data)


class NotificationMarkReadApi(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='Mark notification as read',
        request=None,
        responses={200: NotificationOutputSerializer}
    )
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user,
            is_active=True
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
        return Response(NotificationOutputSerializer(notification).data)


class NotificationDetailApi(APIView):
    """Get notification details."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='Get notification details',
        responses={200: NotificationOutputSerializer}
    )
    def get(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user,
            is_active=True
        )
        return Response(NotificationOutputSerializer(notification).data)
