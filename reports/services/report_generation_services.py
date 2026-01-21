from django.db.models import Avg, Count, F
from teacher.models import Mark, Attendance
from student.models import Student
from school.models import School
from typing import List, Dict, Any

class ReportGenerationService:
    @staticmethod
    def get_student_performance_data(school_id: int = None) -> List[Dict[str, Any]]:
        """
        Aggregates performance data for all students in a school.
        """
        queryset = Student.objects.all()
        if school_id:
            queryset = queryset.filter(user__school_id=school_id)
            
        data = []
        students_with_marks = Mark.objects.filter(
            is_active=True
        ).values('student').annotate(
            avg_gpa=Avg('percentage')
        )
        
        gpa_map = {item['student']: item['avg_gpa'] for item in students_with_marks}
        
        for student in queryset.select_related('user'):
            data.append({
                "student": student.user.full_name,
                "grade": student.grade_level,
                "gpa": float(gpa_map.get(student.user_id, 0.0)) / 25.0  # Simple conversion to 4.0 scale if %
            })
        return data

    @staticmethod
    def get_attendance_report(school_id: int = None) -> List[Dict[str, Any]]:
        """
        Aggregates attendance data.
        """
        queryset = Attendance.objects.filter(is_active=True)
        if school_id:
            queryset = queryset.filter(student__user__school_id=school_id)
            
        records = queryset.select_related('student__user', 'course_allocation__course').order_by('-date')
        
        data = []
        for record in records[:1000]: # Limit to last 1000 records for reporting
            data.append({
                "student": record.student.user.full_name,
                "date": record.date.isoformat(),
                "status": record.status,
                "course": record.course_allocation.course.name if record.course_allocation else "N/A"
            })
        return data

    @staticmethod
    def get_student_list(school_id: int = None) -> List[Dict[str, Any]]:
        """
        Basic student list for export.
        """
        queryset = Student.objects.all()
        if school_id:
            queryset = queryset.filter(user__school_id=school_id)
            
        data = []
        for student in queryset.select_related('user'):
            data.append({
                "name": student.user.full_name,
                "email": student.user.email,
                "id": student.student_id,
                "status": student.enrollment_status
            })
        return data
