from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Teacher, Assignment, CourseAllocation, Attendance
from school.models import School, Course, ClassRoom, AcademicYear, Grade
from workstream.models import WorkStream
from student.models import Student

User = get_user_model()

class TeacherApiTests(APITestCase):
    def setUp(self):
        # Setup infrastructure
        self.workstream = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(school_name="School 1", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(academic_year_code="2025/2026", school=self.school, start_date="2025-09-01", end_date="2026-06-30")
        self.grade_level = Grade.objects.create(name="Grade 10", numeric_level=10, min_age=15, max_age=16)
        
        # Setup Teacher
        self.teacher_user = User.objects.create_user(email='teacher@example.com', password='password123', full_name='Teacher One', role='teacher', school=self.school)
        self.teacher = Teacher.objects.create(user=self.teacher_user, hire_date="2025-01-01", employment_status="full_time")
        
        # Setup Student
        self.student_user = User.objects.create_user(email='student@example.com', password='password123', full_name='Student One', role='student', school=self.school)
        self.student = Student.objects.create(user=self.student_user, date_of_birth="2010-01-01", admission_date="2025-01-01")
        
        # Setup Course & Classroom
        self.course = Course.objects.create(name="Math", course_code="MATH101", school=self.school, grade=self.grade_level)
        self.classroom = ClassRoom.objects.create(classroom_name="10A", school=self.school, academic_year=self.academic_year, grade=self.grade_level)
        
        # Allocate Teacher
        self.allocation = CourseAllocation.objects.create(
            course=self.course, class_room=self.classroom, teacher=self.teacher, academic_year=self.academic_year
        )

    def test_create_assignment(self):
        """Test creating an assignment via the API."""
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('teacher:assignment-list-create')
        data = {
            'title': 'Math Quiz 1',
            'exam_type': 'quiz',
            'full_mark': '100.00',
            'description': 'A test quiz',
            'due_date': '2026-02-01'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_enter_grade(self):
        """Test entering a grade/mark for a student."""
        # Create assignment first
        assignment = Assignment.objects.create(
            course_allocation=self.allocation, created_by=self.teacher, 
            title="Quiz", full_mark=100, assignment_code="Q1"
        )
        
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('teacher:mark-record')
        data = {
            'student_id': self.student.user.id,
            'assignment_id': assignment.id,
            'score': 85
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_record_attendance(self):
        """Test recording student attendance."""
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('teacher:attendance-record')
        data = {
            'student_id': self.student.user.id,
            'course_allocation_id': self.allocation.id,
            'date': '2026-01-21',
            'status': 'present'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attendance.objects.count(), 1)
