from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, MessageReceipt

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

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient_ids', 'receipts', 
            'subject', 'body', 'attachments', 
            'thread_id', 'sent_at', 'is_draft'
        ]
        read_only_fields = ['sender', 'thread_id', 'sent_at', 'receipts']
        ref_name = 'UserMessageSerializer'

    def create(self, validated_data):
        recipients = validated_data.pop('recipients', [])
        # Assign sender from context if not present (handled in view usually, but good to ensure)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
            
        message = Message.objects.create(**validated_data)
        
        # Create receipts
        for user in recipients:
            MessageReceipt.objects.create(message=message, recipient=user)
            
        return message

class MessageDetailSerializer(MessageSerializer):
    """
    Same as MessageSerializer but could include more details if needed.
    """
    class Meta(MessageSerializer.Meta):
        ref_name = 'UserMessageDetailSerializer'

class MarkReadSerializer(serializers.Serializer):
    is_read = serializers.BooleanField(default=True)
