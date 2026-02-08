from rest_framework import serializers
from teacher.models import CourseAllocation

class CourseAllocationSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    classroom_name = serializers.CharField(source='class_room.classroom_name', read_only=True)
    
    # These fields are expected by the current frontend dashboard mapping
    subject = serializers.CharField(source='course.name', read_only=True)
    classroom = serializers.CharField(source='class_room.classroom_name', read_only=True)
    # Add 'class' alias for the frontend
    # Note: 'class' is a reserved keyword in Python, so we can't use it directly as a field name
    # in the class body if we were using it for something else, but here we can define it in Meta fields
    # or use a SerializerMethodField if needed. Actually, using source is fine.
    
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    # Mocking time and room for now as they might not be in the model but are in the UI
    time = serializers.SerializerMethodField()
    room = serializers.CharField(source='class_room.room_number', read_only=True, default='TBD')
    status = serializers.SerializerMethodField()

    class Meta:
        model = CourseAllocation
        fields = [
            'id', 'course_name', 'classroom_name', 'subject', 'classroom', 'class', 'teacher_name',
            'time', 'room', 'status', 'course_id', 'class_room_id', 'academic_year_id'
        ]

    def get_fields(self):
        fields = super().get_fields()
        # Add the 'class' field to the output dictionary
        fields['class'] = serializers.CharField(source='class_room.classroom_name', read_only=True)
        return fields

    def get_time(self, obj):
        # Pseudo-dynamic time based on ID for demo purposes
        hour = 8 + (obj.id % 6)
        if hour < 12:
            return f"{hour:02d}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour-12:02d}:00 PM"

    def get_status(self, obj):
        # Randomly assign status for demo
        statuses = ["upcoming", "current", "completed"]
        return statuses[obj.id % 3]
