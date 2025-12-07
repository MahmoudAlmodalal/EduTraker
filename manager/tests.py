from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Workstream, StaffEvaluation, DepartmentActivityReport

User = get_user_model()


class ManagerWorkstreamTests(APITestCase):
    """Tests for Workstream management."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="teacherpass123",
            role="teacher",
        )
        self.client = APIClient()
    
    def test_admin_can_create_workstream(self):
        """Test admin can create a workstream."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("workstream-list")
        data = {
            "name": "Mathematics Department",
            "capacity": 500,
            "description": "Math department workstream",
            "manager": self.manager.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workstream.objects.count(), 1)
        self.assertEqual(Workstream.objects.first().name, "Mathematics Department")
        self.assertEqual(Workstream.objects.first().manager, self.manager)
    
    def test_manager_can_view_own_workstream(self):
        """Test manager can view their assigned workstream."""
        workstream = Workstream.objects.create(
            name="Math Dept",
            capacity=300,
            manager=self.manager,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("workstream-detail", kwargs={"pk": workstream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Math Dept")
    
    def test_manager_cannot_view_other_workstreams(self):
        """Test manager cannot view workstreams they don't manage."""
        other_manager = User.objects.create_user(
            username="manager2",
            email="manager2@example.com",
            password="pass123",
            role="manager",
        )
        workstream = Workstream.objects.create(
            name="Other Dept",
            capacity=200,
            manager=other_manager,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("workstream-detail", kwargs={"pk": workstream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_view_all_workstreams(self):
        """Test admin can view all workstreams."""
        Workstream.objects.create(
            name="Dept 1",
            capacity=100,
            manager=self.manager,
            created_by=self.admin,
        )
        Workstream.objects.create(
            name="Dept 2",
            capacity=200,
            created_by=self.admin,
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("workstream-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_workstream_statistics_endpoint(self):
        """Test workstream statistics endpoint."""
        workstream = Workstream.objects.create(
            name="Test Dept",
            capacity=100,
            manager=self.manager,
            created_by=self.admin,
        )
        # Create some reports and evaluations
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=workstream,
            date=date.today(),
            attendance_rate=Decimal("85.5"),
        )
        StaffEvaluation.objects.create(
            manager=self.manager,
            teacher=self.teacher,
            workstream=workstream,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            score=Decimal("8.5"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("workstream-statistics", kwargs={"pk": workstream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["workstream_name"], "Test Dept")
        self.assertEqual(response.data["total_reports"], 1)
        self.assertEqual(response.data["total_evaluations"], 1)


class ManagerStaffEvaluationTests(APITestCase):
    """Tests for Staff Evaluation functionality."""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="teacherpass123",
            role="teacher",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.workstream = Workstream.objects.create(
            name="Math Dept",
            capacity=300,
            manager=self.manager,
            created_by=self.admin,
        )
        self.client = APIClient()
    
    def test_manager_can_create_staff_evaluation(self):
        """Test manager can create staff evaluation (US-Manager-003)."""
        self.client.force_authenticate(user=self.manager)
        url = reverse("staff-evaluation-list")
        data = {
            "teacher": self.teacher.id,
            "workstream": self.workstream.id,
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "score": "8.5",
            "comments": "Excellent performance",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StaffEvaluation.objects.count(), 1)
        evaluation = StaffEvaluation.objects.first()
        self.assertEqual(evaluation.manager, self.manager)
        self.assertEqual(evaluation.teacher, self.teacher)
        self.assertEqual(evaluation.score, Decimal("8.5"))
    
    def test_manager_can_view_own_evaluations(self):
        """Test manager can view their evaluations."""
        evaluation = StaffEvaluation.objects.create(
            manager=self.manager,
            teacher=self.teacher,
            workstream=self.workstream,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            score=Decimal("9.0"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("staff-evaluation-detail", kwargs={"pk": evaluation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["score"]), 9.0)
    
    def test_non_manager_cannot_create_evaluation(self):
        """Test non-manager cannot create evaluation."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("staff-evaluation-list")
        data = {
            "teacher": self.teacher.id,
            "workstream": self.workstream.id,
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "score": "8.5",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_evaluation_summary_endpoint(self):
        """Test evaluation summary endpoint."""
        StaffEvaluation.objects.create(
            manager=self.manager,
            teacher=self.teacher,
            workstream=self.workstream,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            score=Decimal("8.5"),
        )
        StaffEvaluation.objects.create(
            manager=self.manager,
            teacher=self.teacher,
            workstream=self.workstream,
            period_start=date.today() - timedelta(days=60),
            period_end=date.today() - timedelta(days=30),
            score=Decimal("9.0"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("staff-evaluation-summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_evaluations"], 2)
        self.assertEqual(float(response.data["avg_score"]), 8.75)


class ManagerDepartmentReportTests(APITestCase):
    """Tests for Department Activity Reports."""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.workstream = Workstream.objects.create(
            name="Math Dept",
            capacity=300,
            manager=self.manager,
            created_by=self.admin,
        )
        self.client = APIClient()
    
    def test_manager_can_create_department_report(self):
        """Test manager can create department activity report (US-Manager-001/002)."""
        self.client.force_authenticate(user=self.manager)
        url = reverse("department-report-list")
        data = {
            "workstream": self.workstream.id,
            "date": "2024-01-15",
            "attendance_rate": "85.5",
            "notes": "Good attendance today",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DepartmentActivityReport.objects.count(), 1)
        report = DepartmentActivityReport.objects.first()
        self.assertEqual(report.manager, self.manager)
        self.assertEqual(report.attendance_rate, Decimal("85.5"))
    
    def test_daily_analysis_endpoint(self):
        """Test daily analysis endpoint (US-Manager-001)."""
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=self.workstream,
            date=date.today(),
            attendance_rate=Decimal("85.5"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("department-report-daily-analysis")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reports"], 1)
        self.assertEqual(float(response.data["avg_attendance_rate"]), 85.5)
    
    def test_department_statistics_endpoint(self):
        """Test department statistics endpoint."""
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=self.workstream,
            date=date.today(),
            attendance_rate=Decimal("85.5"),
        )
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=self.workstream,
            date=date.today() - timedelta(days=1),
            attendance_rate=Decimal("90.0"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("department-report-statistics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reports"], 2)
        self.assertEqual(float(response.data["avg_attendance_rate"]), 87.75)
    
    def test_manager_cannot_create_duplicate_report_same_date(self):
        """Test that duplicate reports for same workstream and date are prevented."""
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=self.workstream,
            date=date.today(),
            attendance_rate=Decimal("85.5"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("department-report-list")
        data = {
            "workstream": self.workstream.id,
            "date": date.today().isoformat(),
            "attendance_rate": "90.0",
        }
        # This should fail due to unique_together constraint
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ManagerStaffAccountTests(APITestCase):
    """Tests for creating staff accounts (US-Manager-004)."""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="teacherpass123",
            role="teacher",
        )
        self.client = APIClient()
    
    def test_manager_can_create_teacher_account(self):
        """Test manager can create teacher account."""
        self.client.force_authenticate(user=self.manager)
        url = reverse("create-staff-account")
        data = {
            "username": "newteacher",
            "first_name": "John",
            "last_name": "Doe",
            "email": "newteacher@example.com",
            "password": "newteacherpass123",
            "role": "teacher",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(role="teacher").count(), 2)
        new_teacher = User.objects.get(email="newteacher@example.com")
        self.assertEqual(new_teacher.role, "teacher")
        self.assertTrue(new_teacher.check_password("newteacherpass123"))
    
    def test_manager_can_create_secretary_account(self):
        """Test manager can create secretary account."""
        self.client.force_authenticate(user=self.manager)
        url = reverse("create-staff-account")
        data = {
            "username": "newsecretary",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "newsecretary@example.com",
            "password": "newsecretarypass123",
            "role": "secretary",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_secretary = User.objects.get(email="newsecretary@example.com")
        self.assertEqual(new_secretary.role, "secretary")
    
    def test_manager_cannot_create_admin_account(self):
        """Test manager cannot create admin account (only teacher/secretary)."""
        self.client.force_authenticate(user=self.manager)
        url = reverse("create-staff-account")
        data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "newadminpass123",
            "role": "admin",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_non_manager_cannot_create_staff_account(self):
        """Test non-manager cannot create staff accounts."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("create-staff-account")
        data = {
            "username": "newteacher",
            "email": "newteacher@example.com",
            "password": "pass123",
            "role": "teacher",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ManagerDashboardTests(APITestCase):
    """Tests for Manager Dashboard."""
    
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="teacherpass123",
            role="teacher",
        )
        self.workstream = Workstream.objects.create(
            name="Math Dept",
            capacity=300,
            manager=self.manager,
            created_by=self.admin,
        )
        self.client = APIClient()
    
    def test_manager_dashboard_endpoint(self):
        """Test manager dashboard returns correct data."""
        # Create some data
        DepartmentActivityReport.objects.create(
            manager=self.manager,
            workstream=self.workstream,
            date=date.today(),
            attendance_rate=Decimal("85.5"),
        )
        StaffEvaluation.objects.create(
            manager=self.manager,
            teacher=self.teacher,
            workstream=self.workstream,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            score=Decimal("8.5"),
        )
        self.client.force_authenticate(user=self.manager)
        url = reverse("manager-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("manager", response.data)
        self.assertIn("workstream", response.data)
        self.assertIn("statistics", response.data)
        self.assertEqual(response.data["statistics"]["total_reports"], 1)
        self.assertEqual(response.data["statistics"]["total_evaluations"], 1)
    
    def test_non_manager_cannot_access_dashboard(self):
        """Test non-manager cannot access manager dashboard."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("manager-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ManagerPermissionTests(APITestCase):
    """Tests for role-based permissions."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="managerpass123",
            role="manager",
        )
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="teacherpass123",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student1",
            email="student@example.com",
            password="studentpass123",
            role="student",
        )
        self.client = APIClient()
    
    def test_unauthenticated_user_cannot_access_manager_endpoints(self):
        """Test unauthenticated users cannot access manager endpoints."""
        url = reverse("manager-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_student_cannot_access_manager_endpoints(self):
        """Test students cannot access manager endpoints."""
        self.client.force_authenticate(user=self.student)
        url = reverse("manager-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_teacher_cannot_access_manager_endpoints(self):
        """Test teachers cannot access manager endpoints."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("create-staff-account")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)