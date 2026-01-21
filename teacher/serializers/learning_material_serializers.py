from rest_framework import serializers
from teacher.models import LearningMaterial
from school.models import Course, ClassRoom, AcademicYear

class LearningMaterialSerializer(serializers.ModelSerializer):
    """Serializer for Learning Material."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = LearningMaterial
        fields = [
            'id', 'material_code', 'course', 'classroom', 'academic_year',
            'uploaded_by', 'uploaded_by_name', 'title', 'description',
            'file_url', 'file_type', 'file_size', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'material_code']

    def create(self, validated_data):
        # Auto-generate material code? Or expect it? 
        # Model says unique. Let's auto-generate if not provided or just handle it.
        # Let's assume frontend doesn't send it and we generate it.
        import uuid
        validated_data['material_code'] = str(uuid.uuid4())[:8].upper()
        return super().create(validated_data)
