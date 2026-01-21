from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from school.models import School
from workstream.models import WorkStream
from manager.models import StaffEvaluation

class StaffEvaluationApiTests(APITestCase):
    def setUp(self):
        # Create a workstream
        self.workstream = WorkStream.objects.create(
            workstream_name="Manager WS",
            capacity=100
        )
        # Create a school
        self.school = School.objects.create(
            school_name="Test School",
            work_stream=self.workstream,
            location="Test Location",
            capacity=500,
            contact_email="school@test.com"
        )
        
        # Create Users
        self.admin_user = CustomUser.objects.create_user(
            email="admin@test.com", password="password123", role="admin"
        )
        self.manager_user = CustomUser.objects.create_user(
            email="manager@test.com", password="password123", role="manager_school", school=self.school
        )
        self.teacher_user = CustomUser.objects.create_user(
            email="teacher@test.com", password="password123", role="teacher", school=self.school
        )
        self.other_user = CustomUser.objects.create_user(
            email="student@test.com", password="password123", role="student", school=self.school
        )

        # URL names from manager/urls.py
        self.list_url = reverse("manager:staff-evaluation-list")
        self.create_url = reverse("manager:staff-evaluation-create")

    def test_create_staff_evaluation_as_manager(self):
        self.client.force_authenticate(user=self.manager_user)
        data = {
            "reviewee_id": self.teacher_user.id,
            "evaluation_date": "2026-01-20",
            "rating_score": 5,
            "comments": "Great performance"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StaffEvaluation.objects.count(), 1)
        self.assertEqual(StaffEvaluation.objects.get().reviewer, self.manager_user)

    def test_create_staff_evaluation_permission_denied(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "reviewee_id": self.teacher_user.id,
            "evaluation_date": "2026-01-20",
            "rating_score": 5,
            "comments": "Self review"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_staff_evaluations(self):
        # Create an evaluation first
        StaffEvaluation.objects.create(
            reviewer=self.manager_user,
            reviewee=self.teacher_user,
            evaluation_date="2026-01-20",
            rating_score=4,
            comments="Good"
        )
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_staff_evaluation_detail(self):
        evaluation = StaffEvaluation.objects.create(
            reviewer=self.manager_user,
            reviewee=self.teacher_user,
            evaluation_date="2026-01-20",
            rating_score=4,
            comments="Good"
        )
        url = reverse("manager:staff-evaluation-detail", args=[evaluation.id])
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating_score'], 4)

    def test_update_staff_evaluation(self):
        evaluation = StaffEvaluation.objects.create(
            reviewer=self.manager_user,
            reviewee=self.teacher_user,
            evaluation_date="2026-01-20",
            rating_score=4,
            comments="Good"
        )
        url = reverse("manager:staff-evaluation-detail", args=[evaluation.id])
        
        self.client.force_authenticate(user=self.manager_user)
        data = {"rating_score": 5, "comments": "Improved"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating_score'], 5)
        
        evaluation.refresh_from_db()
        self.assertEqual(evaluation.rating_score, 5)

    def test_delete_staff_evaluation(self):
        evaluation = StaffEvaluation.objects.create(
            reviewer=self.manager_user,
            reviewee=self.teacher_user,
            evaluation_date="2026-01-20",
            rating_score=4,
            comments="Good"
        )
        url = reverse("manager:staff-evaluation-detail", args=[evaluation.id])
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StaffEvaluation.objects.count(), 0)
