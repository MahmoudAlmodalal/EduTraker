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
        source='recipients',
        required=False,
        default=[]
    )
    # Input: Emails of recipients (alternative to recipient_ids)
    recipient_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False,
        default=[]
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
            'id', 'sender', 'recipient_ids', 'recipient_emails', 'receipts', 
            'subject', 'body', 'attachments', 
            'thread_id', 'parent_message', 'sent_at', 'is_draft'
        ]
        read_only_fields = ['sender', 'sent_at', 'receipts']
        ref_name = 'UserMessageSerializer'

    def validate(self, data):
        recipients_by_id = data.get('recipients', [])
        recipient_emails = data.get('recipient_emails', [])
        
        if not recipients_by_id and not recipient_emails:
            raise serializers.ValidationError(
                "You must provide at least one recipient via 'recipient_ids' or 'recipient_emails'."
            )
        return data

    def create(self, validated_data):
        from notifications.models import Notification

        recipients = list(validated_data.pop('recipients', []))
        recipient_emails = validated_data.pop('recipient_emails', [])
        
        # Resolve emails to users
        if recipient_emails:
            email_users = User.objects.filter(email__in=recipient_emails, is_active=True)
            found_emails = set(email_users.values_list('email', flat=True))
            not_found = [e for e in recipient_emails if e.lower() not in {f.lower() for f in found_emails}]
            if not_found:
                raise serializers.ValidationError(
                    {"recipient_emails": [f"No active user found with email: {e}" for e in not_found]}
                )
            # Merge, avoiding duplicates
            existing_ids = {u.id for u in recipients}
            for u in email_users:
                if u.id not in existing_ids:
                    recipients.append(u)
                    existing_ids.add(u.id)

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
