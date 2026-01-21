from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from school.models import School
from workstream.models import WorkStream
from secretary.models import Secretary
from datetime import date

class SecretaryApiTests(APITestCase):
    def setUp(self):
        # Create Workstream
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
        self.admin = CustomUser.objects.create_user(
            email="admin@school.com", password="password123", role="admin"
        )
        self.manager = CustomUser.objects.create_user(
            email="manager@school.com", password="password123", role="manager_school", school=self.school
        )

        # URLs
        self.list_url = reverse("secretary:secretary-list")
        self.create_url = reverse("secretary:secretary-create")

    def test_create_secretary_success(self):
        self.client.force_authenticate(user=self.manager)
        data = {
            "email": "janedoe@school.com",
            "full_name": "Jane Doe",
            "password": "SecurePass123!",
            "school_id": self.school.id,
            "department": "Administration",
            "hire_date": "2026-01-01",
            "office_number": "A-1"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Secretary.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get(email="janedoe@school.com").role, "secretary")

    def test_create_secretary_invalid_data(self):
        self.client.force_authenticate(user=self.manager)
        data = {
            "email": "invalid-email", 
            "full_name": ""
            # Missing required fields
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_secretaries(self):
        # Create a secretary first
        user = CustomUser.objects.create_user(
            email="existing@school.com", password="pw", role="secretary", school=self.school
        )
        Secretary.objects.create(
            user=user, department="HR", hire_date=date(2025, 1, 1)
        )
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], "existing@school.com")

    def test_get_secretary_detail(self):
        user = CustomUser.objects.create_user(
            email="detail@school.com", password="pw", role="secretary", school=self.school
        )
        secretary = Secretary.objects.create(
            user=user, department="IT", hire_date=date(2025, 1, 1)
        )
        url = reverse("secretary:secretary-detail", args=[user.id])
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department'], "IT")

    def test_update_secretary(self):
        user = CustomUser.objects.create_user(
            email="update@school.com", password="pw", role="secretary", school=self.school
        )
        secretary = Secretary.objects.create(
            user=user, department="Old Dept", hire_date=date(2025, 1, 1)
        )
        url = reverse("secretary:secretary-detail", args=[user.id])
        
        self.client.force_authenticate(user=self.manager)
        data = {"department": "New Dept"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department'], "New Dept")
        
        secretary.refresh_from_db()
        self.assertEqual(secretary.department, "New Dept")

    def test_deactivate_secretary(self):
        user = CustomUser.objects.create_user(
            email="deactivate@school.com", password="pw", role="secretary", school=self.school
        )
        secretary = Secretary.objects.create(
            user=user, department="HR", hire_date=date(2025, 1, 1)
        )
        url = reverse("secretary:secretary-deactivate", args=[user.id])
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        secretary.refresh_from_db()
        self.assertFalse(secretary.is_active)
        user.refresh_from_db()
        self.assertFalse(user.is_active)  # Assuming deactivate turns off user login too

    def test_delete_secretary_method_not_allowed(self):
        user = CustomUser.objects.create_user(
            email="del@school.com", password="pw", role="secretary", school=self.school
        )
        secretary = Secretary.objects.create(
            user=user, department="HR", hire_date=date(2025, 1, 1)
        )
        url = reverse("secretary:secretary-detail", args=[user.id])
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
