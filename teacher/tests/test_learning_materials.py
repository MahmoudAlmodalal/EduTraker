from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser, Role
from teacher.models import Teacher, LearningMaterial
from workstream.models import WorkStream
from school.models import School, AcademicYear, Course, Grade, ClassRoom
from student.models import Student, StudentEnrollment
from datetime import date

class LearningMaterialApiTests(APITestCase):
    def setUp(self):
        # Setup
        self.ws = WorkStream.objects.create(workstream_name="WS1", capacity=100)
        self.school = School.objects.create(school_name="Sch1", work_stream=self.ws)
        self.ay = AcademicYear.objects.create(academic_year_code="2025", school=self.school, start_date=date(2025,1,1), end_date=date(2025,12,31))
        self.grade = Grade.objects.create(name="G1", numeric_level=1, min_age=6, max_age=8)
        self.course = Course.objects.create(course_code="MATH101", school=self.school, grade=self.grade, name="Math")
        
        self.teacher_user = CustomUser.objects.create_user(email='teacher@test.com', password='password123', role=Role.TEACHER, full_name='Teacher')
        self.teacher_profile = Teacher.objects.create(user=self.teacher_user, hire_date=date(2020,1,1), employment_status='full_time')
        
        self.classroom = ClassRoom.objects.create(classroom_name="1A", school=self.school, academic_year=self.ay, grade=self.grade, homeroom_teacher=self.teacher_profile)
        
        self.student_user = CustomUser.objects.create_user(email='student@test.com', password='password123', role=Role.STUDENT, full_name='Student')
        self.student_profile = Student.objects.create(user=self.student_user, student_id="STU001", admission_date=date(2025,1,1), date_of_birth=date(2018,1,1), grade=self.grade)
        # Enrollment moved to specific test

        self.url_list = reverse('teacher:learning-material-list-create')

    def test_teacher_create_material(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            'course': self.course.id,
            'classroom': self.classroom.id,
            'academic_year': self.ay.id,
            'title': 'Algebra Notes',
            'file_url': 'http://example.com/notes.pdf', # Mocking file upload by sending URL directly as per model
            'file_type': 'pdf'
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['uploaded_by'], self.teacher_user.id)
        self.assertIsNotNone(response.data['material_code'])

    def test_student_cannot_create_material(self):
        self.client.force_authenticate(user=self.student_user)
        data = {
            'course': self.course.id,
            'classroom': self.classroom.id,
            'academic_year': self.ay.id,
            'title': 'Hacked Notes',
            'file_url': 'http://example.com/hack.pdf',
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_read_material(self):
        # Create unique classroom for this test to avoid leakage
        cr = ClassRoom.objects.create(classroom_name="Unique", school=self.school, academic_year=self.ay, grade=self.grade)
        StudentEnrollment.objects.create(student=self.student_profile, class_room=cr, academic_year=self.ay, status='active')
        
        # Create material in this classroom
        lm = LearningMaterial.objects.create(
            material_code='MAT_UNIQ', course=self.course, classroom=cr, academic_year=self.ay,
            uploaded_by=self.teacher_user, title='Read Me', file_url='http://x.com/f.pdf'
        )
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify our material is present in the list
        titles = [item['title'] for item in response.data]
        self.assertIn('Read Me', titles)

    def test_teacher_delete_own_material(self):
         lm = LearningMaterial.objects.create(
            material_code='MAT002', course=self.course, classroom=self.classroom, academic_year=self.ay,
            uploaded_by=self.teacher_user, title='Delete Me', file_url='http://x.com/d.pdf'
        )
         url_detail = reverse('teacher:learning-material-detail', args=[lm.id])
         self.client.force_authenticate(user=self.teacher_user)
         response = self.client.delete(url_detail)
         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_teacher_cannot_delete_others_material(self):
         other_teacher = CustomUser.objects.create_user(email='other@test.com', password='password123', role=Role.TEACHER, full_name='Other')
         lm = LearningMaterial.objects.create(
            material_code='MAT003', course=self.course, classroom=self.classroom, academic_year=self.ay,
            uploaded_by=other_teacher, title='Protected', file_url='http://x.com/p.pdf'
        )
         url_detail = reverse('teacher:learning-material-detail', args=[lm.id])
         self.client.force_authenticate(user=self.teacher_user)
         response = self.client.delete(url_detail)
         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
