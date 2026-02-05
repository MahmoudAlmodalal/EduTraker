from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from typing import Optional
from decimal import Decimal

from teacher.models import Mark, Teacher, Assignment
from student.models import Student
from accounts.models import CustomUser, Role
from notifications.services.notification_services import notification_create


@transaction.atomic
def mark_record(
    *,
    teacher: Teacher,
    student: Student,
    assignment: Assignment,
    score: Decimal,
    feedback: Optional[str] = None
) -> Mark:
    """
    Record or update a mark for a student.
    """
    # Permission check: Teacher must be the owner of the assignment
    if assignment.created_by != teacher:
        raise PermissionDenied("You can only grade assignments you created.")

    if score > assignment.full_mark:
        raise ValidationError({"score": f"Score cannot exceed full mark ({assignment.full_mark})."})

    mark, created = Mark.objects.get_or_create(
        student=student,
        assignment=assignment,
        defaults={'score': score, 'feedback': feedback, 'graded_by': teacher, 'graded_at': timezone.now()}
    )

    if not created:
        mark.score = score
        mark.feedback = feedback
        mark.graded_by = teacher
        mark.graded_at = timezone.now()
        mark.is_active = True
        mark.save()
        
    # Create notification for the student
    notification_create(
        recipient=student.user,
        sender=teacher.user,
        title="Grade Posted",
        message=f"A new grade has been posted for {assignment.title}. Score: {score}/{assignment.full_mark}",
        notification_type="grade_posted",
        action_url=f"/student/results"
    )

    return mark


@transaction.atomic
def mark_deactivate(*, mark: Mark, actor: CustomUser) -> None:
    """
    Deactivate a mark.
    """
    is_owner = hasattr(actor, 'teacher_profile') and mark.graded_by == actor.teacher_profile
    if not (is_owner or actor.role == Role.ADMIN):
        raise PermissionDenied("You don't have permission to deactivate this mark.")

    if not mark.is_active:
        raise ValidationError("Mark already deactivated.")

    mark.deactivate(user=actor)


@transaction.atomic
def mark_activate(*, mark: Mark, actor: CustomUser) -> None:
    """
    Activate a mark.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate marks.")

    if mark.is_active:
        raise ValidationError("Mark is already active.")

    mark.activate()
@transaction.atomic
def mark_bulk_import(
    *,
    teacher: Teacher,
    assignment: Assignment,
    csv_file
) -> dict:
    """
    Import marks from a CSV file.
    CSV Format: student_email,score,feedback
    """
    import csv
    import io
    
    if assignment.created_by != teacher:
        raise PermissionDenied("You can only grade assignments you created.")

    results = {"success": 0, "errors": []}
    
    # Read CSV
    file_data = csv_file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(file_data))
    
    for row in reader:
        email = row.get('student_email')
        score_val = row.get('score')
        feedback = row.get('feedback', '')
        
        if not email or not score_val:
            results["errors"].append(f"Missing email or score in row: {row}")
            continue
            
        try:
            student = Student.objects.get(user__email=email)
            score = Decimal(score_val)
            
            mark_record(
                teacher=teacher,
                student=student,
                assignment=assignment,
                score=score,
                feedback=feedback
            )
            results["success"] += 1
        except Student.DoesNotExist:
            results["errors"].append(f"Student with email {email} not found.")
        except Exception as e:
            results["errors"].append(f"Error processing {email}: {str(e)}")
            
    return results
