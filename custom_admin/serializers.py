from rest_framework import serializers
from custom_admin.models import SupportTicket


class SupportTicketSerializer(serializers.ModelSerializer):
    """
    Serializer for SupportTicket model.
    """
    created_by_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    assigned_to_email = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_id', 'subject', 'description', 'priority', 'status',
            'created_by', 'created_by_name', 'created_by_email',
            'assigned_to', 'assigned_to_name', 'assigned_to_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ticket_id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else "Unknown"
    
    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else ""
    
    def get_assigned_to_name(self, obj):
        return obj.assigned_to.full_name if obj.assigned_to else "Unassigned"
    
    def get_assigned_to_email(self, obj):
        return obj.assigned_to.email if obj.assigned_to else ""


class SupportTicketStatsSerializer(serializers.Serializer):
    """
    Serializer for support ticket statistics.
    """
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    high_priority_tickets = serializers.IntegerField()
