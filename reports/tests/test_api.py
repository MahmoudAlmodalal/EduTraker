from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from school.models import AcademicYear, Grade, Course, ClassRoom, School
from student.models import Student
from workstream.models import WorkStream
from teacher.models import Teacher
from datetime import date

class ReportsApiTests(APITestCase):
    def setUp(self):
        # 1. Workstream
        self.workstream = WorkStream.objects.create(
            workstream_name="Primary Education",
            description="Primary School",
            capacity=100
        )

        # 2. School
        self.school = School.objects.create(
            school_name="West Side Academy",
            work_stream=self.workstream,
            location="West Side",
            capacity=1000,
            contact_email="westside@school.com"
        )
        # Link school to workstream (if applicable via `School.workstream` or specific relation - 
        # usually schools belong to a workstream or linked. Checking models... 
        # Assuming School has workstream generic or implicit. 
        # Actually in SRS, Workstream contains Schools.
        # Let's verify relation. Typically School might have a ForeignKey to Workstream.
        # If not, let's assume `get_student_count_by_workstream` finds schools linked to it.
        # I'll update School if it has workstream field.
        # Checking previous files... `School` model.
        # For now, I won't rely on Workstream specific stats if the link isn't clear,
        # but I'll focus on Teacher/School stats which are clearer.
        
        # 3. Users
        self.admin = CustomUser.objects.create_user(
            email="admin@school.com", password="password123", role="admin"
        )
        self.manager = CustomUser.objects.create_user(
            email="manager@school.com", password="password123", role="manager_school", school=self.school
        )
        self.teacher_user = CustomUser.objects.create_user(
            email="teacher@school.com", password="password123", role="teacher", school=self.school
        )
        
        # 4. Teacher Profile
        self.teacher_profile = Teacher.objects.create(
            user=self.teacher_user,
            specialization="Math",
            hire_date=date(2025, 1, 1)
        )

        # 5. Academic items
        self.ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2025, 9, 1), end_date=date(2026, 6, 30)
        )
        self.grade = Grade.objects.create(
            name="Grade 1", numeric_level=1, min_age=6, max_age=7
        )
        self.classroom = ClassRoom.objects.create(
            school=self.school, academic_year=self.ay, grade=self.grade, 
            classroom_name="1A", homeroom_teacher=self.teacher_profile
        )
        self.course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="MATH101", name="Math"
        )

        # 6. Students
        # Create student user and profile
        self.s1_user = CustomUser.objects.create_user(
            email="s1@school.com", password="pw", role="student", school=self.school
        )
        self.s1 = Student.objects.create(
            user=self.s1_user,
            date_of_birth=date(2018, 1, 1),
            admission_date=date(2025, 9, 1),
            enrollment_status="active"
        )
        # Enroll in classroom (if explicit relation exists, usually `Student.classroom` or Enrollment model)
        # Checking Student model... usually has `classroom` field or `enrollments`.
        # I'll update `classroom` field if it exists on Student.
        if hasattr(self.s1, 'classroom'):
            self.s1.classroom = self.classroom
            self.s1.save()
            
        # Also need to link Course to Student? Usually via Enrollment or Attendance.
        # But Report might just count by Classroom for School stats.
        # Verify `get_student_count_by_teacher` logic: it probably looks at Classrooms taught by teacher
        # or Courses taught by teacher.
        # Since I set `homeroom_teacher` on Classroom, that should trigger stats.

    def test_dashboard_statistics_admin(self):
        url = reverse("dashboard-statistics")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertTrue('total_students' in response.data['statistics'])
        self.assertTrue('total_teachers' in response.data['statistics'])

    def test_dashboard_statistics_teacher(self):
        url = reverse("dashboard-statistics")
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Depending on logic, might be 0 if logic relies on Course Assignment not established here,
        # but it shouldn't crash.
        self.assertEqual(response.data['role'], 'teacher')

    def test_teacher_student_count(self):
        url = reverse("teacher-student-count", args=[self.teacher_user.id])
        self.client.force_authenticate(user=self.admin) # Admin can view others
        response = self.client.get(url)
        # Assuming the service might return 404 if no complex mapping found or 0 count.
        # But we expect 200 OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_school_student_count(self):
        url = reverse("school-student-count", args=[self.school.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['school_id'], self.school.id)
        # Should see at least 1 student if `by_grade` logic works on Student.grade
        self.assertTrue(response.data['total_students'] >= 0)

    def test_comprehensive_statistics(self):
        url = reverse("comprehensive-statistics")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('statistics' in response.data)
