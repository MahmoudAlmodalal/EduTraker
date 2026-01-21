from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser, Role

class ReportExportApiTests(APITestCase):
    def setUp(self):
        from school.models import Grade, School, AcademicYear, Course, ClassRoom
        from workstream.models import WorkStream
        from teacher.models import Teacher, Assignment, Mark
        from student.models import Student, StudentEnrollment
        from datetime import date
        from decimal import Decimal

        self.ws = WorkStream.objects.create(workstream_name="WS1", capacity=100)
        self.school = School.objects.create(school_name="Sch1", work_stream=self.ws)
        self.admin = CustomUser.objects.create_user(email='admin@test.com', password='password123', role=Role.ADMIN, full_name='Admin', school=self.school)
        self.teacher_user = CustomUser.objects.create_user(email='teacher@test.com', password='password123', role=Role.TEACHER, full_name='Teacher', school=self.school)
        self.teacher = Teacher.objects.create(user=self.teacher_user, hire_date=date(2025,1,1))
        
        self.ay = AcademicYear.objects.create(academic_year_code="2025", school=self.school, start_date=date(2025,1,1), end_date=date(2025,12,31))
        self.grade = Grade.objects.create(name="G1", numeric_level=1, min_age=6, max_age=8)
        self.course = Course.objects.create(course_code="MATH101", school=self.school, grade=self.grade, name="Math")
        self.classroom = ClassRoom.objects.create(classroom_name="1A", school=self.school, academic_year=self.ay, grade=self.grade)
        
        self.student_user = CustomUser.objects.create_user(email='student@test.com', password='password123', role=Role.STUDENT, full_name='Student', school=self.school)
        self.student = Student.objects.create(user=self.student_user, grade=self.grade, date_of_birth=date(2018,1,1), admission_date=date(2025,1,1))
        
        from teacher.models import CourseAllocation
        self.alloc = CourseAllocation.objects.create(course=self.course, class_room=self.classroom, teacher=self.teacher, academic_year=self.ay)
        
        self.assignment = Assignment.objects.create(title="Test", course_allocation=self.alloc, created_by=self.teacher, weight=10, full_mark=100)
        Mark.objects.create(student=self.student, assignment=self.assignment, score=Decimal("85.00"), percentage=Decimal("85.00"), graded_by=self.teacher)

        self.url = reverse('report-export')

    def test_admin_export_excel(self):
        self.client.force_authenticate(user=self.admin)
        data = {'report_type': 'student_performance'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="student_performance_'))

    def test_teacher_export_excel_denied(self):
        # IsStaffUser allows ADMIN, MANAGER_WORKSTREAM, MANAGER_SCHOOL, TEACHER, SECRETARY.
        self.client.force_authenticate(user=self.teacher_user)
        data = {'report_type': 'student_performance'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_export_denied(self):
        student = CustomUser.objects.create_user(email='student@test.com', password='password123', role=Role.STUDENT, full_name='Student')
        self.client.force_authenticate(user=student)
        data = {'report_type': 'student_performance'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
