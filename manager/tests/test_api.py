from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, Role
from school.models import School
from workstream.models import WorkStream
from manager.models import StaffEvaluation

class StaffEvaluationApiTests(APITestCase):
    def setUp(self):
        # Create workstreams
        self.workstream = WorkStream.objects.create(workstream_name="WS 1", capacity=100)
        self.other_workstream = WorkStream.objects.create(workstream_name="WS 2", capacity=100)
        
        # Create schools
        self.school = School.objects.create(
            school_name="School 1", work_stream=self.workstream, 
            location="Loc 1", capacity=100, contact_email="s1@test.com"
        )
        self.other_school_same_ws = School.objects.create(
            school_name="School 2", work_stream=self.workstream, 
            location="Loc 2", capacity=100, contact_email="s2@test.com"
        )
        self.school_other_ws = School.objects.create(
            school_name="School 3", work_stream=self.other_workstream, 
            location="Loc 3", capacity=100, contact_email="s3@test.com"
        )

        # Users
        self.admin = CustomUser.objects.create_user(email="admin@test.com", password="pw", role=Role.ADMIN)
        
        self.ws_manager = CustomUser.objects.create_user(
            email="ws_mgr@test.com", password="pw", role=Role.MANAGER_WORKSTREAM, work_stream=self.workstream
        )
        
        self.school_manager = CustomUser.objects.create_user(
            email="sch_mgr@test.com", password="pw", role=Role.MANAGER_SCHOOL, school=self.school
        )
        
        self.other_school_manager = CustomUser.objects.create_user(
            email="other_sch_mgr@test.com", password="pw", role=Role.MANAGER_SCHOOL, school=self.other_school_same_ws
        )

        self.teacher = CustomUser.objects.create_user(
            email="teacher@test.com", password="pw", role=Role.TEACHER, school=self.school, full_name="John Teacher"
        )
        
        self.other_teacher_same_ws = CustomUser.objects.create_user(
            email="other_teacher@test.com", password="pw", role=Role.TEACHER, school=self.other_school_same_ws
        )
        
        self.teacher_other_ws = CustomUser.objects.create_user(
            email="other_ws_teacher@test.com", password="pw", role=Role.TEACHER, school=self.school_other_ws
        )

        self.list_url = reverse("manager:staff-evaluation-list")
        self.create_url = reverse("manager:staff-evaluation-create")

    # --- Permision & RBAC Tests ---

    def test_manager_school_create_in_school(self):
        self.client.force_authenticate(user=self.school_manager)
        data = {"reviewee_id": self.teacher.id, "evaluation_date": "2026-01-20", "rating_score": 5}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_school_create_out_of_school_denied(self):
        self.client.force_authenticate(user=self.school_manager)
        data = {"reviewee_id": self.other_teacher_same_ws.id, "evaluation_date": "2026-01-20", "rating_score": 5}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_workstream_create_in_ws(self):
        self.client.force_authenticate(user=self.ws_manager)
        data = {"reviewee_id": self.other_teacher_same_ws.id, "evaluation_date": "2026-01-20", "rating_score": 4}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_workstream_create_out_of_ws_denied(self):
        self.client.force_authenticate(user=self.ws_manager)
        data = {"reviewee_id": self.teacher_other_ws.id, "evaluation_date": "2026-01-20", "rating_score": 4}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_create_denied(self):
        self.client.force_authenticate(user=self.teacher)
        data = {"reviewee_id": self.teacher.id, "evaluation_date": "2026-01-20", "rating_score": 5}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Filtering & Listing Tests ---

    def test_list_evaluations_visibility_manager_school(self):
        # Evaluation in school
        StaffEvaluation.objects.create(reviewer=self.school_manager, reviewee=self.teacher, evaluation_date="2026-01-01", rating_score=5)
        # Evaluation outside school
        StaffEvaluation.objects.create(reviewer=self.other_school_manager, reviewee=self.other_teacher_same_ws, evaluation_date="2026-01-02", rating_score=4)
        
        self.client.force_authenticate(user=self.school_manager)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_evaluations_visibility_teacher(self):
        # Evaluation where teacher is reviewee
        StaffEvaluation.objects.create(reviewer=self.school_manager, reviewee=self.teacher, evaluation_date="2026-01-01", rating_score=5)
        # Evaluation where another teacher is reviewee
        StaffEvaluation.objects.create(reviewer=self.school_manager, reviewee=self.other_teacher_same_ws, evaluation_date="2026-01-02", rating_score=4)
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.list_url)
        # Handle both paginated and non-paginated responses
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['reviewee'], self.teacher.id)

    def test_filtering_by_date_range(self):
        StaffEvaluation.objects.create(reviewer=self.admin, reviewee=self.teacher, evaluation_date="2026-01-01", rating_score=5)
        StaffEvaluation.objects.create(reviewer=self.admin, reviewee=self.teacher, evaluation_date="2026-01-10", rating_score=5)
        StaffEvaluation.objects.create(reviewer=self.admin, reviewee=self.teacher, evaluation_date="2026-01-20", rating_score=5)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"start_date": "2026-01-05", "end_date": "2026-01-15"})
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['evaluation_date'], "2026-01-10")

    def test_pagination(self):
        # Create 12 evaluations
        for i in range(12):
            StaffEvaluation.objects.create(
                reviewer=self.admin, reviewee=self.teacher, 
                evaluation_date=f"2026-01-{i+1:02d}", rating_score=5
            )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10) # Default page size is 10
        self.assertIn('next', response.data)
        self.assertEqual(response.data['count'], 12)

    # --- Validation Tests ---

    def test_create_negative_rating_denied(self):
        self.client.force_authenticate(user=self.admin)
        data = {"reviewee_id": self.teacher.id, "evaluation_date": "2026-01-20", "rating_score": -1}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating_score", response.data)

    def test_create_invalid_reviewee_denied(self):
        self.client.force_authenticate(user=self.admin)
        data = {"reviewee_id": 9999, "evaluation_date": "2026-01-20", "rating_score": 5}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Update & Delete Tests ---

    def test_only_reviewer_or_admin_can_delete(self):
        evaluation = StaffEvaluation.objects.create(
            reviewer=self.school_manager, reviewee=self.teacher, evaluation_date="2026-01-01", rating_score=5
        )
        url = reverse("manager:staff-evaluation-detail", args=[evaluation.id])
        
        # Other manager tries to delete
        self.client.force_authenticate(user=self.other_school_manager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Reviewer deletes
        self.client.force_authenticate(user=self.school_manager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_patch_evaluation_as_higher_management(self):
        evaluation = StaffEvaluation.objects.create(
            reviewer=self.school_manager, reviewee=self.teacher, evaluation_date="2026-01-01", rating_score=5
        )
        url = reverse("manager:staff-evaluation-detail", args=[evaluation.id])
        
        # Workstream manager updates rating
        self.client.force_authenticate(user=self.ws_manager)
        data = {"rating_score": 3}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating_score'], 3)
