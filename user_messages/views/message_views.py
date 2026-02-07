from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ..models import Message, MessageReceipt
from ..serializers import MessageSerializer, MessageDetailSerializer
from ..serializers import UserMinimalSerializer
from accounts.selectors.user_selectors import user_list
from accounts.models import CustomUser, Role

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
            
        return queryset.order_by('-sent_at')

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
@extend_schema(
    tags=['User Messages'],
    summary='Search users for messaging',
    description='Search for users to send messages to. Returns minimal info (name, email) and is filtered by school visibility.',
    parameters=[
        OpenApiParameter(name='search', type=str, description='Search by name or email'),
    ],
    responses={200: UserMinimalSerializer(many=True)}
)
class CommunicationUserSearchApi(generics.ListAPIView):
    """
    GET: Search for users for messaging. 
    Broader search than user_list — allows messaging across schools in the same workstream.
    ADMIN can search all users. 
    MANAGER_WORKSTREAM can search all users in their workstream.
    MANAGER_SCHOOL, TEACHER, SECRETARY can search all users in their workstream (cross-school messaging).
    STUDENT, GUARDIAN can search staff in their school.
    """

    def get_serializer_class(self):
        return UserMinimalSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search', '')
        if not search_term or len(search_term) < 2:
            return CustomUser.objects.none()

        user = self.request.user
        qs = CustomUser.objects.filter(is_active=True)

        if user.role == Role.ADMIN:
            # Admin can message anyone
            pass
        elif user.role == Role.MANAGER_WORKSTREAM:
            # Workstream manager can message anyone in their workstream
            qs = qs.filter(work_stream=user.work_stream)
        elif user.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
            # School staff can message anyone in their workstream (cross-school)
            work_stream = user.work_stream or (user.school.work_stream if user.school else None)
            if work_stream:
                qs = qs.filter(
                    models.Q(work_stream=work_stream) |
                    models.Q(school__work_stream=work_stream)
                )
            elif user.school:
                qs = qs.filter(school=user.school)
        elif user.role in [Role.STUDENT, Role.GUARDIAN]:
            # Students/Guardians can message staff in their school
            qs = qs.filter(
                school=user.school,
                role__in=[Role.TEACHER, Role.SECRETARY, Role.MANAGER_SCHOOL]
            )
        else:
            return CustomUser.objects.none()

        # Exclude self from results
        qs = qs.exclude(id=user.id)

        # Apply search filter
        from django.db.models import Q
        from django.db.models.functions import Lower
        qs = qs.annotate(
            low_full_name=Lower('full_name'),
            low_email=Lower('email')
        ).filter(
            Q(low_full_name__icontains=search_term.lower()) |
            Q(low_email__icontains=search_term.lower())
        )

        return qs[:20]  # Limit results
