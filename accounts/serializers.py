from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    """Simple serializer for detail messages."""
    detail = serializers.CharField(help_text="Response message")
