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
        
        for student in queryset.select_related('user', 'grade'):
            # Get grade representation
            grade_display = ""
            if student.grade:
                grade_display = student.grade.name
            elif student.grade_level:
                grade_display = f"Grade {student.grade_level}"
            else:
                grade_display = "N/A"
            
            # Get GPA, handle None case
            avg_percentage = gpa_map.get(student.user_id, 0.0)
            gpa_value = float(avg_percentage) / 25.0 if avg_percentage else 0.0
            
            data.append({
                "student": student.user.full_name,
                "grade": grade_display,
                "gpa": round(gpa_value, 2)
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

    @staticmethod
    def get_comprehensive_academic_data(school_id: int = None, actor = None) -> List[Dict[str, Any]]:
        """
        Generate comprehensive academic report data including students by workstream,
        schools overview, and academic performance metrics.
        """
        from reports.services.count_admin_services import (
            get_students_by_workstream,
            get_schools_overview
        )
        from accounts.models import CustomUser
        
        data = []
        
        # Get students by workstream
        students_data = get_students_by_workstream(actor=actor) if actor else {'by_workstream': []}
        if students_data and 'by_workstream' in students_data:
            for ws in students_data['by_workstream']:
                data.append({
                    'category': 'Students by Workstream',
                    'workstream': ws.get('workstream_name', 'N/A'),
                    'count': ws.get('student_count', 0),
                    'schools': ws.get('school_count', 0),
                    'metric': 'enrollment'
                })
        
        # Get schools overview
        schools_data = get_schools_overview(actor=actor) if actor else {'schools': []}
        if schools_data and 'schools' in schools_data:
            for school in schools_data['schools']:
                data.append({
                    'category': 'Schools Overview',
                    'school_name': school.get('school_name', 'N/A'),
                    'workstream': school.get('workstream_name', 'N/A'),
                    'students': school.get('student_count', 0),
                    'teachers': school.get('teacher_count', 0),
                    'metric': 'overview'
                })
        
        return data

    @staticmethod
    def get_teacher_evaluations_report(school_id: int = None, actor = None) -> List[Dict[str, Any]]:
        """
        Aggregates teacher evaluation data for reporting.
        """
        from manager.selectors.staff_evaluation_selectors import staff_evaluation_list
        
        # We pass empty filters to get all reachable evaluations
        evaluations = staff_evaluation_list(filters={}, user=actor)
        
        data = []
        for evaluation in evaluations:
            data.append({
                "reviewer": evaluation.reviewer.full_name,
                "reviewee": evaluation.reviewee.full_name,
                "date": evaluation.evaluation_date.isoformat(),
                "rating": evaluation.rating_score,
                "comments": evaluation.comments or ""
            })
        return data

    @staticmethod
    def get_comprehensive_system_usage_data(school_id: int = None, actor = None) -> List[Dict[str, Any]]:
        """
        Generate system usage report data including teachers by workstream,
        activity metrics, and platform usage statistics.
        """
        from reports.services.count_admin_services import (
            get_teachers_by_workstream,
            get_global_statistics
        )
        from accounts.models import CustomUser
        
        data = []
        
        # Get teachers by workstream
        teachers_data = get_teachers_by_workstream(actor=actor) if actor else {'by_workstream': []}
        if teachers_data and 'by_workstream' in teachers_data:
            for ws in teachers_data['by_workstream']:
                data.append({
                    'category': 'Teachers by Workstream',
                    'workstream': ws.get('workstream_name', 'N/A'),
                    'teacher_count': ws.get('teacher_count', 0),
                    'metric': 'staffing'
                })
        
        # Get global statistics for system metrics
        global_stats = get_global_statistics(actor=actor) if actor else {}
        if global_stats:
            # Add platform-wide metrics
            data.append({
                'category': 'Platform Statistics',
                'metric': 'total_users',
                'value': global_stats.get('total_users', 0),
                'description': 'Total Users'
            })
            data.append({
                'category': 'Platform Statistics',
                'metric': 'total_students',
                'value': global_stats.get('total_students', 0),
                'description': 'Total Students'
            })
            data.append({
                'category': 'Platform Statistics',
                'metric': 'total_teachers',
                'value': global_stats.get('total_teachers', 0),
                'description': 'Total Teachers'
            })
            data.append({
                'category': 'Platform Statistics',
                'metric': 'total_schools',
                'value': global_stats.get('total_schools', 0),
                'description': 'Total Schools'
            })
        
        return data

