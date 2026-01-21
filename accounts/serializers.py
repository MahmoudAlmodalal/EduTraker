from rest_framework import serializers
from .models import SystemConfiguration

class MessageSerializer(serializers.Serializer):
    """Simple serializer for detail messages."""
    detail = serializers.CharField(help_text="Response message")

class SystemConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for SystemConfiguration."""
    class Meta:
        model = SystemConfiguration
        fields = ['id', 'work_stream', 'school', 'config_key', 'config_value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that only one scope (work_stream or school) is set, or neither (global).
        """
        school = data.get('school')
        work_stream = data.get('work_stream')

        if school and work_stream:
            raise serializers.ValidationError("Configuration cannot be both School-specific and Workstream-specific simultaneously. Choose one scope.")
        
        return data
