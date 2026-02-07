from django.utils import timezone
from accounts.models import CustomUser, Role
from school.models import School, ClassRoom, Grade
from workstream.models import WorkStream
from teacher.models import Teacher, Attendance
from student.models import Student, StudentEnrollment
from reports.services.count_managerWorkstream_services import get_workstream_summary


def verify_attendance_stats():
    print("Setting up test data...")
    
    # Create Workstream
    ws, _ = WorkStream.objects.get_or_create(
        workstream_name="Test WS",
        defaults={"capacity": 1000}
    )
    
    # Create Manager
    manager_user, _ = CustomUser.objects.get_or_create(
        email="manager@test.com",
        defaults={
            "full_name": "Test Manager",
            "role": Role.MANAGER_WORKSTREAM,
            "work_stream_id": ws.id
        }
    )
    if manager_user.work_stream_id != ws.id:
        manager_user.work_stream_id = ws.id
        manager_user.save()
        
    # Create School
    school, _ = School.objects.get_or_create(
        school_name="Test School",
        defaults={"work_stream": ws}
    )
    
    # Create Student
    student_user, _ = CustomUser.objects.get_or_create(
        email="student@test.com",
        defaults={
            "full_name": "Test Student",
            "role": Role.STUDENT,
            "school_id": school.id
        }
    )
    student, _ = Student.objects.get_or_create(
        user=student_user,
        defaults={"enrollment_status": "active"}
    )
    
    # Clear existing attendance for this student
    Attendance.objects.filter(student=student).delete()
    
    # Create Attendance Records
    # 3 Present, 1 Absent, 1 Late = 5 Total
    # Present count = 3 + 1 (Late) = 4
    # Absent count = 1
    # Attendance % = 4/5 = 80%
    # Absent % = 1/5 = 20%
    
    today = timezone.now().date()
    Attendance.objects.create(student=student, date=today, status="present")
    Attendance.objects.create(student=student, date=today, status="present")
    Attendance.objects.create(student=student, date=today, status="present")
    Attendance.objects.create(student=student, date=today, status="absent")
    Attendance.objects.create(student=student, date=today, status="late")
    
    print("Calling get_workstream_summary...")
    stats = get_workstream_summary(workstream_id=ws.id, actor=manager_user)
    
    school_stat = next((s for s in stats['by_school'] if s['school_id'] == school.id), None)
    
    if not school_stat:
        print("Error: School stats not found!")
        return

    print(f"School Stats: {school_stat}")
    
    expected_attendance = 80.0
    expected_absent = 20.0
    
    if school_stat['attendance_percentage'] == expected_attendance and \
       school_stat['absent_percentage'] == expected_absent:
        print("SUCCESS: Attendance stats match expected values.")
    else:
        print(f"FAILURE: Expected Attendance {expected_attendance}%, Got {school_stat['attendance_percentage']}%")
        print(f"FAILURE: Expected Absent {expected_absent}%, Got {school_stat['absent_percentage']}%")

try:
    verify_attendance_stats()
except Exception as e:
    print(f"Error during verification: {e}")
    import traceback
    traceback.print_exc()
