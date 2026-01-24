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

    def test_list_secretaries_filtering_and_search(self):
        # Create multiple secretaries in different schools/departments
        school2 = School.objects.create(
            school_name="East Side Academy", work_stream=self.workstream, 
            location="East Side", capacity=500, contact_email="eastside@school.com"
        )
        # Secretary 1: HR, School 1
        u1 = CustomUser.objects.create_user(email="hr1@s1.com", password="pw", role="secretary", school=self.school, full_name="HR One")
        Secretary.objects.create(user=u1, department="HR", hire_date=date(2025, 1, 1))
        # Secretary 2: IT, School 1
        u2 = CustomUser.objects.create_user(email="it1@s1.com", password="pw", role="secretary", school=self.school, full_name="IT One")
        Secretary.objects.create(user=u2, department="IT", hire_date=date(2025, 1, 1))
        # Secretary 3: HR, School 2
        u3 = CustomUser.objects.create_user(email="hr2@s2.com", password="pw", role="secretary", school=school2, full_name="HR Two")
        Secretary.objects.create(user=u3, department="HR", hire_date=date(2025, 1, 1))

        self.client.force_authenticate(user=self.admin)
        
        # 1. Filter by school_id
        response = self.client.get(self.list_url, {"school_id": self.school.id})
        self.assertEqual(len(response.data['results']), 2)

        # 2. Filter by department
        response = self.client.get(self.list_url, {"department": "IT"})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], "it1@s1.com")

        # 3. Search by name
        response = self.client.get(self.list_url, {"search": "Two"})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], "HR Two")

        # 4. Search by email
        response = self.client.get(self.list_url, {"search": "hr1@s1.com"})
        self.assertEqual(len(response.data['results']), 1)

    def test_rbac_school_manager(self):
        # School Manager should ONLY see/manage secretaries in their school
        school2 = School.objects.create(
            school_name="Remote School", work_stream=self.workstream, 
            location="Remote", capacity=100, contact_email="remote@school.com"
        )
        u_other = CustomUser.objects.create_user(email="other@remote.com", password="pw", role="secretary", school=school2)
        Secretary.objects.create(user=u_other, department="HR", hire_date=date(2025, 1, 1))
        
        u_mine = CustomUser.objects.create_user(email="mine@school.com", password="pw", role="secretary", school=self.school)
        Secretary.objects.create(user=u_mine, department="IT", hire_date=date(2025, 1, 1))

        self.client.force_authenticate(user=self.manager)
        
        # List: only mine
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], "mine@school.com")

        # Detail: other (PermissionDenied expected in service/selector)
        url_other = reverse("secretary:secretary-detail", args=[u_other.id])
        response = self.client.get(url_other)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Create: for other school
        data = {
            "email": "failed@remote.com", "full_name": "Failed", "password": "pw",
            "school_id": school2.id, "department": "HR", "hire_date": "2026-01-01"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_secretary_self_management(self):
        user = CustomUser.objects.create_user(
            email="sec@school.com", password="password123", role="secretary", school=self.school, full_name="Old Name"
        )
        Secretary.objects.create(user=user, department="HR", hire_date=date(2025, 1, 1), office_number="101")
        
        self.client.force_authenticate(user=user)
        url = reverse("secretary:secretary-detail", args=[user.id])

        # Can view own detail
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can update allowed fields (full_name, office_number)
        data = {"full_name": "New Name", "office_number": "202", "department": "IT"} # department is NOT allowed for self-update
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertEqual(user.full_name, "New Name")
        self.assertEqual(user.secretary_profile.office_number, "202")
        self.assertEqual(user.secretary_profile.department, "HR") # should remain HR

    def test_deactivate_secretary_rbac(self):
        user = CustomUser.objects.create_user(
            email="sec_to_deactivate@school.com", password="pw", role="secretary", school=self.school
        )
        Secretary.objects.create(user=user, department="HR", hire_date=date(2025, 1, 1))
        url = reverse("secretary:secretary-deactivate", args=[user.id])
        
        # unauthorized user (another secretary)
        other_user = CustomUser.objects.create_user(email="other_sec@school.com", password="pw", role="secretary", school=self.school)
        self.client.force_authenticate(user=other_user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authorized manager
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertFalse(user.secretary_profile.is_active)

    def test_create_secretary_invalid_school(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "email": "invalid@school.com",
            "full_name": "Invalid",
            "password": "SecurePass123!",
            "school_id": 9999, # non-existent
            "department": "HR",
            "hire_date": "2026-01-01"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("school_id", response.data)

    def test_delete_secretary_method_not_allowed(self):
        user = CustomUser.objects.create_user(
            email="del@school.com", password="pw", role="secretary", school=self.school
        )
        Secretary.objects.create(user=user, department="HR", hire_date=date(2025, 1, 1))
        url = reverse("secretary:secretary-detail", args=[user.id])
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
