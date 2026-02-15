"""
Test to verify that users can update their profile with their own email
without getting a duplicate email error.

This test validates the fix for the issue where users could not update
their profile with the same email they already had.
"""
from datetime import date
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from student.models import Student
from guardian.models import Guardian
from secretary.models import Secretary
from school.models import School, Grade
from workstream.models import WorkStream
from student.services.student_services import student_update
from guardian.services.guardian_services import guardian_update
from secretary.services.secretary_services import secretary_update


class EmailValidationFixTest(TestCase):
    """Test email validation during profile updates."""
    
    def setUp(self):
        """Set up test data."""
        self.workstream = WorkStream.objects.create(workstream_name="Test WS", capacity=50)
        self.school = School.objects.create(school_name="Test School", work_stream=self.workstream)
        self.grade = Grade.objects.create(name="Grade 1", numeric_level=1, min_age=6, max_age=7)
        
        # Create admin user
        self.admin = CustomUser.objects.create_user(
            email='admin@test.com',
            password='pass123',
            full_name='Admin User',
            role=Role.ADMIN
        )
    
    def test_student_can_update_with_same_email(self):
        """Test that a student can update their profile with their own email."""
        # Create a student
        student_user = CustomUser.objects.create_user(
            email='student@test.com',
            password='pass123',
            full_name='Student User',
            role=Role.STUDENT,
            school=self.school
        )
        student = Student.objects.create(
            user=student_user,
            grade=self.grade,
            date_of_birth=date(2010, 1, 1),
            admission_date=date(2023, 1, 1)
        )
        
        # Update student with the SAME email - should NOT raise an error
        updated_student = student_update(
            student=student,
            actor=self.admin,
            data={'email': 'student@test.com', 'full_name': 'Updated Student'}
        )
        
        # Verify the update was successful
        updated_student.user.refresh_from_db()
        self.assertEqual(updated_student.user.email, 'student@test.com')
        self.assertEqual(updated_student.user.full_name, 'Updated Student')
    
    def test_student_cannot_use_duplicate_email(self):
        """Test that a student cannot use another user's email."""
        # Create two students
        student1_user = CustomUser.objects.create_user(
            email='student1@test.com',
            password='pass123',
            full_name='Student 1',
            role=Role.STUDENT,
            school=self.school
        )
        student1 = Student.objects.create(
            user=student1_user,
            grade=self.grade,
            date_of_birth=date(2010, 1, 1),
            admission_date=date(2023, 1, 1)
        )
        
        student2_user = CustomUser.objects.create_user(
            email='student2@test.com',
            password='pass123',
            full_name='Student 2',
            role=Role.STUDENT,
            school=self.school
        )
        student2 = Student.objects.create(
            user=student2_user,
            grade=self.grade,
            date_of_birth=date(2010, 1, 1),
            admission_date=date(2023, 1, 1)
        )
        
        # Try to update student2 with student1's email - should raise an error
        with self.assertRaises(ValidationError) as cm:
            student_update(
                student=student2,
                actor=self.admin,
                data={'email': 'student1@test.com'}
            )
        
        # Verify the error message
        self.assertIn('email', cm.exception.detail)
        self.assertIn('already exists', str(cm.exception.detail['email']))
    
    def test_guardian_can_update_with_same_email(self):
        """Test that a guardian can update their profile with their own email."""
        # Create a guardian
        guardian_user = CustomUser.objects.create_user(
            email='guardian@test.com',
            password='pass123',
            full_name='Guardian User',
            role=Role.GUARDIAN,
            school=self.school
        )
        guardian = Guardian.objects.create(
            user=guardian_user,
            phone_number='1234567890'
        )
        
        # Update guardian with the SAME email - should NOT raise an error
        updated_guardian = guardian_update(
            guardian=guardian,
            actor=self.admin,
            data={'email': 'guardian@test.com', 'full_name': 'Updated Guardian'}
        )
        
        # Verify the update was successful
        updated_guardian.user.refresh_from_db()
        self.assertEqual(updated_guardian.user.email, 'guardian@test.com')
        self.assertEqual(updated_guardian.user.full_name, 'Updated Guardian')
    
    def test_guardian_cannot_use_duplicate_email(self):
        """Test that a guardian cannot use another user's email."""
        # Create two guardians
        guardian1_user = CustomUser.objects.create_user(
            email='guardian1@test.com',
            password='pass123',
            full_name='Guardian 1',
            role=Role.GUARDIAN,
            school=self.school
        )
        guardian1 = Guardian.objects.create(
            user=guardian1_user,
            phone_number='1234567890'
        )
        
        guardian2_user = CustomUser.objects.create_user(
            email='guardian2@test.com',
            password='pass123',
            full_name='Guardian 2',
            role=Role.GUARDIAN,
            school=self.school
        )
        guardian2 = Guardian.objects.create(
            user=guardian2_user,
            phone_number='0987654321'
        )
        
        # Try to update guardian2 with guardian1's email - should raise an error
        with self.assertRaises(ValidationError) as cm:
            guardian_update(
                guardian=guardian2,
                actor=self.admin,
                data={'email': 'guardian1@test.com'}
            )
        
        # Verify the error message
        self.assertIn('email', cm.exception.detail)
        self.assertIn('already exists', str(cm.exception.detail['email']))
    
    def test_secretary_can_update_with_same_email(self):
        """Test that a secretary can update their profile with their own email."""
        # Create a secretary
        secretary_user = CustomUser.objects.create_user(
            email='secretary@test.com',
            password='pass123',
            full_name='Secretary User',
            role=Role.SECRETARY,
            school=self.school
        )
        secretary = Secretary.objects.create(
            user=secretary_user,
            department='Administration',
            hire_date=date(2023, 1, 1)
        )
        
        # Update secretary with the SAME email - should NOT raise an error
        updated_secretary = secretary_update(
            secretary=secretary,
            actor=self.admin,
            data={'email': 'secretary@test.com', 'full_name': 'Updated Secretary'}
        )
        
        # Verify the update was successful
        updated_secretary.user.refresh_from_db()
        self.assertEqual(updated_secretary.user.email, 'secretary@test.com')
        self.assertEqual(updated_secretary.user.full_name, 'Updated Secretary')
    
    def test_secretary_cannot_use_duplicate_email(self):
        """Test that a secretary cannot use another user's email."""
        # Create two secretaries
        secretary1_user = CustomUser.objects.create_user(
            email='secretary1@test.com',
            password='pass123',
            full_name='Secretary 1',
            role=Role.SECRETARY,
            school=self.school
        )
        secretary1 = Secretary.objects.create(
            user=secretary1_user,
            department='Administration',
            hire_date=date(2023, 1, 1)
        )
        
        secretary2_user = CustomUser.objects.create_user(
            email='secretary2@test.com',
            password='pass123',
            full_name='Secretary 2',
            role=Role.SECRETARY,
            school=self.school
        )
        secretary2 = Secretary.objects.create(
            user=secretary2_user,
            department='HR',
            hire_date=date(2023, 1, 1)
        )
        
        # Try to update secretary2 with secretary1's email - should raise an error
        with self.assertRaises(ValidationError) as cm:
            secretary_update(
                secretary=secretary2,
                actor=self.admin,
                data={'email': 'secretary1@test.com'}
            )
        
        # Verify the error message
        self.assertIn('email', cm.exception.detail)
        self.assertIn('already exists', str(cm.exception.detail['email']))
    
    def test_email_case_insensitive_validation(self):
        """Test that email validation is case-insensitive."""
        # Create a student
        student_user = CustomUser.objects.create_user(
            email='student@test.com',
            password='pass123',
            full_name='Student User',
            role=Role.STUDENT,
            school=self.school
        )
        student = Student.objects.create(
            user=student_user,
            grade=self.grade,
            date_of_birth=date(2010, 1, 1),
            admission_date=date(2023, 1, 1)
        )
        
        # Update with different case of the same email - should NOT raise an error
        updated_student = student_update(
            student=student,
            actor=self.admin,
            data={'email': 'STUDENT@TEST.COM'}
        )
        
        # Email should be normalized to lowercase
        updated_student.user.refresh_from_db()
        self.assertEqual(updated_student.user.email, 'student@test.com')
