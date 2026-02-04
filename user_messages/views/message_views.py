from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ..models import Message, MessageReceipt
from ..serializers import MessageSerializer, MessageDetailSerializer

@extend_schema(
    tags=['User Messages'],
    summary='List and create messages',
    description='List all messages for the current user (sent and received) or send a new one.',
    parameters=[
        OpenApiParameter(name='box', type=str, enum=['inbox', 'sent'], description='Filter by inbox or sent messages'),
    ],
    responses={200: MessageSerializer(many=True), 201: MessageSerializer}
)
class MessageListCreateView(generics.ListCreateAPIView):
    """
    GET: List all messages for the current user (sent and received).
    POST: Send a new message.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(
            models.Q(sender=user) | models.Q(receipts__recipient=user)
        ).distinct().select_related('sender').prefetch_related('receipts__recipient')
        
        # Optional: Filter by 'type' (inbox/sent) via query params if needed
        # Filter by peer_id (conversation with specific user)
        peer_id = self.request.query_params.get('peer_id')
        if peer_id:
            queryset = queryset.filter(
                models.Q(sender_id=peer_id) | models.Q(receipts__recipient_id=peer_id)
            )
            
        return queryset.order_by('sent_at' if peer_id else '-sent_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@extend_schema(
    tags=['User Messages'],
    summary='Retrieve or delete message',
    description='Retrieve message details or soft delete it.',
    responses={
        200: MessageDetailSerializer,
        204: OpenApiResponse(description='Deleted successfully')
    }
)
class MessageDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Retrieve a specific message details.
    DELETE: Soft delete a message (or just receipt for recipient).
    """
    serializer_class = MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(receipts__recipient=user)
        ).distinct()
        
    def perform_destroy(self, instance):
        user = self.request.user
        if instance.sender == user:
            # Sender deleting message -> Soft delete globally or just for them?
            # For now, let's say sender soft-deletes the message
            instance.deactivate(user=user)
        else:
            # Recipient deleting -> Mark receipt as deleted
            receipt = get_object_or_404(MessageReceipt, message=instance, recipient=user)
            receipt.is_deleted = True
            receipt.save()


@extend_schema(
    tags=['User Messages'],
    summary='List message thread',
    description='Retrieve all messages in a specific thread.',
    responses={200: MessageSerializer(many=True)}
)
class MessageThreadView(generics.ListAPIView):
    """
    GET: Retrieve all messages in a specific thread.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs.get('thread_id')
        user = self.request.user
        
        # Ensure user is part of the thread (sender or recipient in at least one message)
        # This is a basic check; real-world apps might need stricter thread membership models
        return Message.objects.filter(
            thread_id=thread_id
        ).filter(
            models.Q(sender=user) | models.Q(receipts__recipient=user)
        ).distinct().select_related('sender').prefetch_related('receipts__recipient').order_by('sent_at')


class MessageReadView(APIView):
    """
    POST/PATCH: Mark a message as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['User Messages'],
        summary='Mark message as read',
        description='Mark a specific message as read for the current user.',
        request=None,
        responses={
            200: OpenApiResponse(description='Marked as read successfully'),
            404: OpenApiResponse(description='Message receipt not found')
        }
    )
    def post(self, request, pk=None):
        return self.mark_read(request, pk)
        
    @extend_schema(
        tags=['User Messages'],
        summary='Mark message as read (partial)',
        description='Mark a specific message as read for the current user.',
        request=None,
        responses={
            200: OpenApiResponse(description='Marked as read successfully'),
            404: OpenApiResponse(description='Message receipt not found')
        }
    )
    def patch(self, request, pk=None):
        return self.mark_read(request, pk)
        
    def mark_read(self, request, pk):
        receipt = get_object_or_404(MessageReceipt, message_id=pk, recipient=request.user)
        if not receipt.is_read:
            receipt.is_read = True
            receipt.read_at = timezone.now()
            receipt.save()
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)
