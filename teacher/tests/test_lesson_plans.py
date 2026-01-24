from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from teacher.models import Teacher, LessonPlan
from school.models import School, Course, ClassRoom, AcademicYear, Grade
from workstream.models import WorkStream
from accounts.models import Role
import datetime

User = get_user_model()

class LessonPlanTests(APITestCase):
    def setUp(self):
        # Setup infrastructure
        self.workstream = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(school_name="School 1", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(academic_year_code="2025/2026", school=self.school, start_date="2025-09-01", end_date="2026-06-30")
        self.grade = Grade.objects.create(name="Grade 10", numeric_level=10, min_age=15, max_age=16)
        
        # Setup Teacher
        self.teacher_user = User.objects.create_user(email='teacher@example.com', password='password123', full_name='Teacher One', role=Role.TEACHER, school=self.school)
        self.teacher = Teacher.objects.create(user=self.teacher_user, hire_date="2025-01-01", employment_status="full_time")
        
        # Setup Other Teacher
        self.other_teacher_user = User.objects.create_user(email='other_teacher@example.com', password='password123', full_name='Other Teacher', role=Role.TEACHER, school=self.school)
        self.other_teacher = Teacher.objects.create(user=self.other_teacher_user, hire_date="2025-01-01", employment_status="full_time")
        
        # Setup Course & Classroom
        self.course = Course.objects.create(name="Math", course_code="MATH101", school=self.school, grade=self.grade)
        self.classroom = ClassRoom.objects.create(classroom_name="10A", school=self.school, academic_year=self.academic_year, grade=self.grade)
        
        # URL
        self.url_list = reverse('teacher:lesson-plan-list-create')

    def test_create_lesson_plan(self):
        """Test creating a lesson plan as a teacher."""
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            'course': self.course.id,
            'classroom': self.classroom.id,
            'academic_year': self.academic_year.id,
            'title': 'Intro to Algebra',
            'content': 'Step 1: Variables, Step 2: Equations',
            'objectives': 'Students should understand variables',
            'date_planned': '2026-02-01',
            'is_published': True
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonPlan.objects.count(), 1)
        self.assertEqual(LessonPlan.objects.first().teacher, self.teacher)

    def test_list_lesson_plans(self):
        """Test listing lesson plans."""
        LessonPlan.objects.create(
            course=self.course, classroom=self.classroom, academic_year=self.academic_year,
            teacher=self.teacher, title="Lesson 1", content="Content 1", date_planned="2026-02-01", is_published=True
        )
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated or not
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)

    def test_student_limited_visibility(self):
        """Test that students only see published lesson plans."""
        # Published lesson plan
        LessonPlan.objects.create(
            course=self.course, classroom=self.classroom, academic_year=self.academic_year,
            teacher=self.teacher, title="Public Lesson", content="Content", date_planned="2026-02-01", is_published=True
        )
        # Unpublished lesson plan
        LessonPlan.objects.create(
            course=self.course, classroom=self.classroom, academic_year=self.academic_year,
            teacher=self.teacher, title="Secret Lesson", content="Content", date_planned="2026-02-02", is_published=False
        )
        
        student_user = User.objects.create_user(email='student@example.com', password='password123', full_name='Student', role=Role.STUDENT, school=self.school)
        self.client.force_authenticate(user=student_user)
        
        response = self.client.get(self.url_list)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], "Public Lesson")

    def test_update_lesson_plan_author_only(self):
        """Test that only the author (or admin) can update a lesson plan."""
        lp = LessonPlan.objects.create(
            course=self.course, classroom=self.classroom, academic_year=self.academic_year,
            teacher=self.teacher, title="Lesson 1", content="Content 1", date_planned="2026-02-01"
        )
        url_detail = reverse('teacher:lesson-plan-detail', args=[lp.id])
        
        # Try update as other teacher
        self.client.force_authenticate(user=self.other_teacher_user)
        data = {'title': 'Hacked Title'}
        response = self.client.patch(url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try update as author
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.patch(url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lp.refresh_from_db()
        self.assertEqual(lp.title, 'Hacked Title')

    def test_delete_lesson_plan(self):
        """Test deleting a lesson plan."""
        lp = LessonPlan.objects.create(
            course=self.course, classroom=self.classroom, academic_year=self.academic_year,
            teacher=self.teacher, title="Lesson to Delete", content="Content", date_planned="2026-02-01"
        )
        url_detail = reverse('teacher:lesson-plan-detail', args=[lp.id])
        
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LessonPlan.objects.filter(id=lp.id).exists())
