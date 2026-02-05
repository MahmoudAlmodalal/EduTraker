from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, MessageReceipt
from notifications.services.notification_services import notification_create

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']
        ref_name = 'UserMessageUserMinimal'  # Avoid conflicts with other User serializers

class MessageReceiptSerializer(serializers.ModelSerializer):
    recipient = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = MessageReceipt
        fields = ['recipient', 'is_read', 'read_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)
    # Input: IDs of recipients
    recipient_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='recipients'
    )
    # Output: Receipt status for each recipient (or just list of recipients for simple view)
    receipts = MessageReceiptSerializer(many=True, read_only=True)
    
    parent_message = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient_ids', 'receipts', 
            'subject', 'body', 'attachments', 
            'thread_id', 'parent_message', 'sent_at', 'is_draft'
        ]
        read_only_fields = ['sender', 'sent_at', 'receipts']
        ref_name = 'UserMessageSerializer'

    def create(self, validated_data):
        from notifications.models import Notification

        recipients = validated_data.pop('recipients', [])
        # Assign sender from context if not present
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
            
        # IMPORTANT: Threading Logic
        # If this is a reply (has parent_message), it MUST share the same thread_id
        parent = validated_data.get('parent_message')
        if parent:
            validated_data['thread_id'] = parent.thread_id
            
        message = Message.objects.create(**validated_data)
        
        # Create receipts and notifications
        for user in recipients:
            MessageReceipt.objects.create(message=message, recipient=user)
            
            # Create a system notification for the recipient
            notification_create(
                recipient=user,
                sender=message.sender,
                title="New Message",
                message=f"You have received a new message from {message.sender.full_name}: {message.subject}",
                notification_type="message_received",
                action_url=f"/super-admin/communication" # Adjust based on role if needed
            )
            
        return message

class MessageDetailSerializer(MessageSerializer):
    """
    Same as MessageSerializer but could include more details if needed.
    """
    class Meta(MessageSerializer.Meta):
        ref_name = 'UserMessageDetailSerializer'

class MarkReadSerializer(serializers.Serializer):
    is_read = serializers.BooleanField(default=True)
