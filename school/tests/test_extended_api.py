from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from school.models import AcademicYear, Grade, Course, ClassRoom, School
from workstream.models import WorkStream
from datetime import date

class SchoolExtendedApiTests(APITestCase):
    def setUp(self):
        # Create WorkStream
        self.workstream = WorkStream.objects.create(
            workstream_name="Global Workstream",
            capacity=100
        )
        # Create School
        self.school = School.objects.create(
            school_name="West Side Academy",
            work_stream=self.workstream,
            location="West Side",
            capacity=1000,
            contact_email="westside@school.com"
        )
        
        # Create Users
        self.manager = CustomUser.objects.create_user(
            email="manager@school.com", password="password123", role="manager_school", school=self.school
        )
        # Workstream Manager usually has broader access, but we test with School Manager if allowed or Admin
        self.admin = CustomUser.objects.create_user(
            email="admin@school.com", password="password123", role="admin"
        )

        # Create basic Grade
        self.grade = Grade.objects.create(
            name="Grade 1", numeric_level=1, min_age=6, max_age=7
        )

    # --- Academic Year Tests ---

    def test_create_academic_year(self):
        # URLs for Academic Year often use WorkStreamManager permission, let's verify if SchoolManager is allowed
        # The view says: permission_classes = [IsWorkStreamManager] which inherits from IsAdminOrManager usually?
        # Let's check permissions. If it requires WorkStream Manager, we need one.
        # Assuming IsWorkStreamManager allows School Manager for their own school or we use Admin.
        # The view source says: permission_classes = [IsWorkStreamManager]
        # Let's use a Workstream Manager to be safe if that's the requirement, or Admin.
        # Ideally check definition of IsWorkStreamManager. Assuming Admin fails if it's strictly WS Manager.
        # Let's create a WS Manager.
        
        ws_manager = CustomUser.objects.create_user(
            email="ws_manager@test.com", password="password123", role="manager_workstream", work_stream=self.workstream
        )

        url = reverse("school:academic-year-create")
        self.client.force_authenticate(user=ws_manager)
        data = {
            "school": self.school.id,
            "start_date": "2026-09-01",
            "end_date": "2027-06-30"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AcademicYear.objects.count(), 1)

    def test_list_academic_years(self):
        ws_manager = CustomUser.objects.create_user(
            email="ws_manager2@test.com", password="password123", role="manager_workstream", work_stream=self.workstream
        )
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        url = reverse("school:academic-year-list")
        self.client.force_authenticate(user=ws_manager)
        response = self.client.get(url, {"school_id": self.school.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_academic_year(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        url = reverse("school:academic-year-detail", args=[ay.id])
        ws_manager = CustomUser.objects.create_user(
            email="ws_manager_ay@test.com", password="password123", role="manager_workstream", work_stream=self.workstream
        )
        self.client.force_authenticate(user=ws_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['academic_year_code'], "2026/27")

    def test_update_academic_year(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2027, 9, 1), end_date=date(2028, 6, 30), academic_year_code="2027/28"
        )
        url = reverse("school:academic-year-update", args=[ay.id])
        ws_manager = CustomUser.objects.create_user(
            email="ws_manager_ayu@test.com", password="password123", role="manager_workstream", work_stream=self.workstream
        )
        self.client.force_authenticate(user=ws_manager)
        data = {"start_date": "2027-10-01"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ay.refresh_from_db()
        self.assertEqual(str(ay.start_date), "2027-10-01")

    def test_deactivate_academic_year(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        url = reverse("school:academic-year-deactivate", args=[ay.id])
        ws_manager = CustomUser.objects.create_user(
            email="ws_manager_ayd@test.com", password="password123", role="manager_workstream", work_stream=self.workstream
        )
        self.client.force_authenticate(user=ws_manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        ay.refresh_from_db()
        self.assertFalse(ay.is_active)

    # --- Grade Tests ---
    
    def test_create_grade(self):
        url = reverse("school:grade-create")
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Grade 2", "numeric_level": 2, "min_age": 7, "max_age": 8
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.filter(name="Grade 2").count(), 1)

    def test_list_grades(self):
        url = reverse("school:grade-list")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # Including setup grade

    def test_manager_can_list_inactive_grades_with_include_inactive(self):
        extra_grade = Grade.objects.create(
            name="Grade 2", numeric_level=2, min_age=7, max_age=8
        )
        self.grade.is_active = False
        self.grade.save(update_fields=["is_active"])

        url = reverse("school:grade-list")
        self.client.force_authenticate(user=self.manager)

        active_only_response = self.client.get(url)
        self.assertEqual(active_only_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(active_only_response.data['results']), 1)
        self.assertEqual(active_only_response.data['results'][0]['id'], extra_grade.id)

        include_inactive_response = self.client.get(url, {"include_inactive": "true"})
        self.assertEqual(include_inactive_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(include_inactive_response.data['results']), 2)

    def test_retrieve_grade(self):
        url = reverse("school:grade-detail", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.grade.name)

    def test_update_grade(self):
        url = reverse("school:grade-detail", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Updated Grade"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.name, "Updated Grade")

    def test_update_inactive_grade_returns_validation_error(self):
        self.grade.is_active = False
        self.grade.save(update_fields=["is_active"])
        url = reverse("school:grade-detail", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {"name": "Should Fail"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot update an inactive grade", str(response.data))

    def test_deactivate_grade(self):
        url = reverse("school:grade-deactivate", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.grade.refresh_from_db()
        self.assertFalse(self.grade.is_active)

    def test_activate_grade(self):
        self.grade.is_active = False
        self.grade.save()
        url = reverse("school:grade-activate", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.grade.refresh_from_db()
        self.assertTrue(self.grade.is_active)

    def test_toggle_grade_status_returns_json(self):
        url = reverse("school:grade-toggle-status", args=[self.grade.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_active'])
        self.assertIn('message', response.data)

    # --- Course Actions ---

    def test_create_course(self):
        # IsAdminOrManager
        url = reverse("school:course-create", args=[self.school.id])
        self.client.force_authenticate(user=self.manager)
        data = {
            "grade_id": self.grade.id,
            "course_code": "MATH101",
            "name": "Mathematics"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_list_courses(self):
        Course.objects.create(
            school=self.school, grade=self.grade, course_code="SCI101", name="Science"
        )
        url = reverse("school:course-list", args=[self.school.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_course(self):
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C1", name="Course 1"
        )
        url = reverse("school:course-detail", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Course 1")

    def test_update_course(self):
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C1", name="Course 1"
        )
        url = reverse("school:course-detail", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        data = {"name": "Course 1 Updated"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, "Course 1 Updated")

    def test_update_inactive_course_returns_validation_error(self):
        course = Course.all_objects.create(
            school=self.school, grade=self.grade, course_code="C4", name="Course 4", is_active=False
        )
        url = reverse("school:course-detail", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(url, {"name": "Should Fail"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot update an inactive subject", str(response.data))

    def test_manager_can_list_inactive_courses_with_include_inactive(self):
        inactive_course = Course.all_objects.create(
            school=self.school, grade=self.grade, course_code="C2", name="Course 2", is_active=False
        )
        active_course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C3", name="Course 3"
        )
        url = reverse("school:course-list", args=[self.school.id])
        self.client.force_authenticate(user=self.manager)

        active_only_response = self.client.get(url)
        self.assertEqual(active_only_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(active_only_response.data['results']), 1)
        self.assertEqual(active_only_response.data['results'][0]['id'], active_course.id)

        include_inactive_response = self.client.get(url, {"include_inactive": "true"})
        self.assertEqual(include_inactive_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(include_inactive_response.data['results']), 2)
        returned_ids = {row['id'] for row in include_inactive_response.data['results']}
        self.assertIn(inactive_course.id, returned_ids)
        self.assertIn(active_course.id, returned_ids)

    def test_deactivate_course(self):
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C1", name="Course 1"
        )
        url = reverse("school:course-deactivate", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        course.refresh_from_db()
        self.assertFalse(course.is_active)

    def test_activate_course(self):
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C1", name="Course 1", is_active=False
        )
        url = reverse("school:course-activate", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        course.refresh_from_db()
        self.assertTrue(course.is_active)

    def test_toggle_course_status_returns_json(self):
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C5", name="Course 5"
        )
        url = reverse("school:course-toggle-status", args=[self.school.id, course.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_active'])
        self.assertIn('message', response.data)

    # --- ClassRoom Actions ---

    def test_create_classroom(self):
        # Needs Academic Year
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        url = reverse("school:classroom-create", args=[self.school.id, ay.id])
        self.client.force_authenticate(user=self.manager)
        
        # Teacher for homeroom
        teacher_user = CustomUser.objects.create_user(
            email="teacher@school.com", password="pw", role="teacher", school=self.school
        )
        from teacher.models import Teacher
        teacher_profile = Teacher.objects.create(user=teacher_user, hire_date=date(2025,1,1))

        data = {
            "grade_id": self.grade.id,
            "classroom_name": "Class 1A",
            "homeroom_teacher_id": teacher_user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassRoom.objects.count(), 1)

    def test_list_classrooms(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        url = reverse("school:classroom-list", args=[self.school.id, ay.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_classroom(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        cr = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        url = reverse("school:classroom-detail", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['classroom_name'], "Class 1A")

    def test_update_classroom(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        cr = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        url = reverse("school:classroom-detail", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        data = {"classroom_name": "Class 1B"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cr.refresh_from_db()
        self.assertEqual(cr.classroom_name, "Class 1B")

    def test_update_inactive_classroom_returns_validation_error(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        cr = ClassRoom.all_objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A", is_active=False
        )
        url = reverse("school:classroom-detail", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(url, {"classroom_name": "Should Fail"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot update an inactive classroom", str(response.data))

    def test_manager_can_list_inactive_classrooms_with_include_inactive(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30), academic_year_code="2026/27"
        )
        active_classroom = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        inactive_classroom = ClassRoom.all_objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1B", is_active=False
        )
        url = reverse("school:classroom-list", args=[self.school.id, ay.id])
        self.client.force_authenticate(user=self.manager)

        active_only_response = self.client.get(url)
        self.assertEqual(active_only_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(active_only_response.data['results']), 1)
        self.assertEqual(active_only_response.data['results'][0]['id'], active_classroom.id)

        include_inactive_response = self.client.get(url, {"include_inactive": "true"})
        self.assertEqual(include_inactive_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(include_inactive_response.data['results']), 2)
        returned_ids = {row['id'] for row in include_inactive_response.data['results']}
        self.assertIn(active_classroom.id, returned_ids)
        self.assertIn(inactive_classroom.id, returned_ids)

    def test_deactivate_classroom(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        cr = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        url = reverse("school:classroom-deactivate", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cr.refresh_from_db()
        self.assertFalse(cr.is_active)

    def test_activate_classroom(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        cr = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A", is_active=False
        )
        url = reverse("school:classroom-activate", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cr.refresh_from_db()
        self.assertTrue(cr.is_active)

    def test_toggle_classroom_status_returns_json(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        cr = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        url = reverse("school:classroom-toggle-status", args=[self.school.id, ay.id, cr.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_active'])
        self.assertIn('message', response.data)

    def test_toggle_course_allocation_status_returns_json(self):
        ay = AcademicYear.objects.create(
            school=self.school, start_date=date(2026, 9, 1), end_date=date(2027, 6, 30)
        )
        classroom = ClassRoom.objects.create(
            school=self.school, academic_year=ay, grade=self.grade, classroom_name="Class 1A"
        )
        course = Course.objects.create(
            school=self.school, grade=self.grade, course_code="C6", name="Course 6"
        )

        teacher_user = CustomUser.objects.create_user(
            email="teacher_toggle@school.com", password="pw", role="teacher", school=self.school
        )
        from teacher.models import Teacher, CourseAllocation
        teacher_profile = Teacher.objects.create(user=teacher_user, hire_date=date(2025, 1, 1))
        allocation = CourseAllocation.objects.create(
            course=course, class_room=classroom, teacher=teacher_profile, academic_year=ay
        )

        url = reverse("school:course-allocation-toggle-status", args=[self.school.id, allocation.id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_active'])
        self.assertIn('message', response.data)
