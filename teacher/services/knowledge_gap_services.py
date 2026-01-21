from typing import List, Dict, Any
from django.db.models import Avg, Count, Q
from teacher.models import Mark, CourseAllocation
from student.models import Student
from decimal import Decimal

def identify_knowledge_gaps(
    *, 
    course_allocation: CourseAllocation, 
    threshold: Decimal = Decimal("50.00")
) -> List[Dict[str, Any]]:
    """
    Identify students in a specific course allocation who are performing below 
     the defined threshold across their marks.
    Fulfills FR-APT-002: Knowledge Gap Identification.
    """
    # Get all students enrolled in this classroom (indirectly via marks or enrollment)
    # Here we analyze marks directly for gaps
    gaps = []
    
    # Aggregate student performance in this specific course allocation
    performance_data = Mark.objects.filter(
        assignment__course_allocation=course_allocation,
        is_active=True
    ).values(
        'student', 
        'student__user__full_name'
    ).annotate(
        average_score=Avg('percentage'),
        marks_count=Count('id')
    ).filter(
        average_score__lt=threshold
    )

    for item in performance_data:
        gaps.append({
            "student_id": item['student'],
            "student_name": item['student__user__full_name'],
            "average_percentage": item['average_score'],
            "total_assessments": item['marks_count'],
            "status": "at_risk"
        })
        
    return gaps

def get_student_weak_subjects(
    *, 
    student: Student, 
    threshold: Decimal = Decimal("50.00")
) -> List[Dict[str, Any]]:
    """
    Analyze all subjects for a specific student to identify where they are failing.
    """
    weak_subjects = Mark.objects.filter(
        student=student,
        is_active=True
    ).values(
        'assignment__course_allocation__course__name',
        'assignment__course_allocation__course_id'
    ).annotate(
        avg_percentage=Avg('percentage')
    ).filter(
        avg_percentage__lt=threshold
    )

    return [
        {
            "course_id": item['assignment__course_allocation__course_id'],
            "course_name": item['assignment__course_allocation__course__name'],
            "average": item['avg_percentage']
        } for item in weak_subjects
    ]
