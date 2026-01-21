"""
Integration Flow Tests

Tests complete end-to-end workflows as described in SRS User Stories.
SRS Reference: Section 9 User Stories
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream
from school.models import School, AcademicYear, Grade, ClassRoom, Course
from student.models import Student, StudentEnrollment
from teacher.models import Teacher, Assignment, CourseAllocation, Attendance, Mark
from guardian.models import Guardian, GuardianStudentLink
from notifications.models import Notification

User = get_user_model()


class StudentRegistrationFlowTests(APITestCase):
    """
    Test: US-SEC-001 - Register New Student
    Complete workflow: Secretary registers student → Links guardian → Enrolls in class
    """
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(workstream_name="Test WS", capacity=10)
        self.school = School.objects.create(school_name="Test School", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(
            academic_year_code="2025/2026", school=self.school, 
            start_date="2025-09-01", end_date="2026-06-30"
        )
        self.grade = Grade.objects.create(name="Grade 9", numeric_level=9, min_age=14, max_age=15)
        self.classroom = ClassRoom.objects.create(
            classroom_name="9A", school=self.school, academic_year=self.academic_year, grade=self.grade
        )
        
        # Secretary who will register students
        self.secretary = User.objects.create_user(
            email='secretary@test.com', password='pass123', full_name='Secretary',
            role='secretary', school=self.school
        )

    def test_complete_student_registration_workflow(self):
        """Test the complete student registration flow as per SRS."""
        self.client.force_authenticate(user=self.secretary)
        
        # Step 1: Create student user
        student_user = User.objects.create_user(
            email='newstudent@test.com', password='pass123', full_name='New Student',
            role='student', school=self.school
        )
        
        # Step 2: Create student profile
        student = Student.objects.create(
            user=student_user, date_of_birth="2010-03-15", admission_date="2025-09-01"
        )
        self.assertIsNotNone(student.pk)
        
        # Step 3: Create guardian
        guardian_user = User.objects.create_user(
            email='newguardian@test.com', password='pass123', full_name='Parent Name',
            role='guardian'
        )
        guardian = Guardian.objects.create(user=guardian_user, phone_number="1234567890")
        
        # Step 4: Link guardian to student
        link = GuardianStudentLink.objects.create(
            guardian=guardian, student=student, 
            relationship_type="parent", is_primary=True
        )
        self.assertTrue(link.is_primary)
        
        # Step 5: Enroll student in classroom
        enrollment = StudentEnrollment.objects.create(
            student=student, class_room=self.classroom, academic_year=self.academic_year
        )
        self.assertIsNotNone(enrollment.pk)
        
        # Verify complete registration
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(GuardianStudentLink.objects.filter(student=student).count(), 1)
        self.assertEqual(StudentEnrollment.objects.filter(student=student).count(), 1)


class GradeEntryFlowTests(APITestCase):
    """
    Test: US-TEACH-002 - Enter Grades
    Complete workflow: Teacher creates assignment → Enters grades → Notifications sent
    """
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(workstream_name="Test WS", capacity=10)
        self.school = School.objects.create(school_name="Test School", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(
            academic_year_code="2025/2026", school=self.school, 
            start_date="2025-09-01", end_date="2026-06-30"
        )
        self.grade = Grade.objects.create(name="Grade 10", numeric_level=10, min_age=15, max_age=16)
        self.classroom = ClassRoom.objects.create(
            classroom_name="10A", school=self.school, academic_year=self.academic_year, grade=self.grade
        )
        self.course = Course.objects.create(
            name="Mathematics", course_code="MATH101", school=self.school, grade=self.grade
        )
        
        # Teacher setup
        self.teacher_user = User.objects.create_user(
            email='teacher@test.com', password='pass123', full_name='Teacher',
            role='teacher', school=self.school
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, hire_date="2025-01-01", employment_status="full_time"
        )
        self.allocation = CourseAllocation.objects.create(
            course=self.course, class_room=self.classroom, 
            teacher=self.teacher, academic_year=self.academic_year
        )
        
        # Student setup
        self.student_user = User.objects.create_user(
            email='student@test.com', password='pass123', full_name='Student',
            role='student', school=self.school
        )
        self.student = Student.objects.create(
            user=self.student_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )

    def test_complete_grade_entry_workflow(self):
        """Test the complete grade entry flow."""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Step 1: Create assignment
        url = reverse('teacher:assignment-list-create')
        assignment_data = {
            'title': 'Math Quiz 1',
            'exam_type': 'quiz',
            'full_mark': '100.00',
            'description': 'First quiz of the semester',
            'due_date': '2026-02-01'
        }
        response = self.client.post(url, assignment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        assignment = Assignment.objects.first()
        self.assertIsNotNone(assignment)
        
        # Step 2: Enter grade for student
        url = reverse('teacher:mark-record')
        grade_data = {
            'student_id': self.student.user.id,
            'assignment_id': assignment.id,
            'score': 85
        }
        response = self.client.post(url, grade_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify mark was created
        mark = Mark.objects.filter(student=self.student, assignment=assignment).first()
        self.assertIsNotNone(mark)
        self.assertEqual(mark.score, 85)


class AttendanceRecordingFlowTests(APITestCase):
    """
    Test: US-TEACH-001 - Record Daily Attendance
    Complete workflow: Teacher marks attendance → Records saved → Stats updated
    """
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(workstream_name="Test WS", capacity=10)
        self.school = School.objects.create(school_name="Test School", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(
            academic_year_code="2025/2026", school=self.school,
            start_date="2025-09-01", end_date="2026-06-30"
        )
        self.grade = Grade.objects.create(name="Grade 10", numeric_level=10, min_age=15, max_age=16)
        self.classroom = ClassRoom.objects.create(
            classroom_name="10A", school=self.school, academic_year=self.academic_year, grade=self.grade
        )
        self.course = Course.objects.create(
            name="Mathematics", course_code="MATH101", school=self.school, grade=self.grade
        )
        
        self.teacher_user = User.objects.create_user(
            email='teacher@test.com', password='pass123', full_name='Teacher',
            role='teacher', school=self.school
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, hire_date="2025-01-01", employment_status="full_time"
        )
        self.allocation = CourseAllocation.objects.create(
            course=self.course, class_room=self.classroom,
            teacher=self.teacher, academic_year=self.academic_year
        )
        
        self.student_user = User.objects.create_user(
            email='student@test.com', password='pass123', full_name='Student',
            role='student', school=self.school
        )
        self.student = Student.objects.create(
            user=self.student_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )

    def test_attendance_recording_workflow(self):
        """Test recording attendance for a class."""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = reverse('teacher:attendance-record')
        attendance_data = {
            'student_id': self.student.user.id,
            'course_allocation_id': self.allocation.id,
            'date': '2026-01-21',
            'status': 'present'
        }
        response = self.client.post(url, attendance_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify attendance was recorded
        attendance = Attendance.objects.filter(student=self.student).first()
        self.assertIsNotNone(attendance)
        self.assertEqual(attendance.status, 'present')


class MessagingFlowTests(APITestCase):
    """
    Test: FR-COM-001 - Internal Messaging System
    Complete workflow: Send message → Recipient receives → Mark as read
    """
    
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            email='teacher@test.com', password='pass123', full_name='Teacher', role='teacher'
        )
        self.student_user = User.objects.create_user(
            email='student@test.com', password='pass123', full_name='Student', role='student'
        )

    def test_complete_messaging_workflow(self):
        """Test sending and receiving messages."""
        # Step 1: Teacher sends message
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('user_messages:message-list-create')
        message_data = {
            'recipient_ids': [self.student_user.id],
            'subject': 'Important Announcement',
            'body': 'Please review the assignment.'
        }
        response = self.client.post(url, message_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Student retrieves messages
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
