"""
Notification management API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from notifications.models import Notification
from notifications.selectors.notification_selectors import (
    notification_list,
    notification_get,
)
from notifications.services.notification_services import (
    notification_mark_read,
)


# =============================================================================
# Notification Serializers
# =============================================================================

from accounts.pagination import PaginatedAPIMixin

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
    is_read = serializers.BooleanField(required=False, allow_null=True)
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPE_CHOICES,
        required=False
    )


# =============================================================================
# Notification Views
# =============================================================================

class NotificationListApi(PaginatedAPIMixin, APIView):
    """List notifications for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='List user notifications',
        parameters=[
            OpenApiParameter(name='is_read', type=bool),
            OpenApiParameter(name='notification_type', type=str),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: NotificationOutputSerializer(many=True)}
    )
    def get(self, request):
        filter_serializer = NotificationFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        notifications = notification_list(
            user=request.user,
            filters=filter_serializer.validated_data
        )
        
        page = self.paginate_queryset(notifications)
        if page is not None:
            return self.get_paginated_response(NotificationOutputSerializer(page, many=True).data)
        
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
        notification = notification_mark_read(
            notification_id=pk,
            user=request.user
        )
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
        notification = notification_get(
            notification_id=pk,
            user=request.user
        )
        return Response(NotificationOutputSerializer(notification).data)


class NotificationUnreadCountApi(APIView):
    """Get unread notification count for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='Get unread notification count',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'unread_count': {'type': 'integer'}
                }
            }
        }
    )
    def get(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': unread_count})


class NotificationMarkAllReadApi(APIView):
    """Mark all notifications as read for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='Mark all notifications as read',
        request=None,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'count': {'type': 'integer'}
                }
            }
        }
    )
    def post(self, request):
        from django.utils import timezone
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })
