import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser, Role
from school.models import School
from workstream.models import WorkStream
from rest_framework.exceptions import ValidationError

def reproduce_issue():
    print("--- Starting Reproduction Script ---")
    
    # 1. Setup: Create a Workstream and a School
    print("Creating test Workstream and School...")
    ws, _ = WorkStream.objects.get_or_create(workstream_name="Repro WS")
    school, _ = School.objects.get_or_create(school_name="Repro School", work_stream=ws, defaults={"capacity": 100})
    
    # Clean up existing managers for this school if any
    CustomUser.objects.filter(school=school, role=Role.MANAGER_SCHOOL).delete()
    school.manager = None
    school.save()

    # 2. Create First Manager
    print("Creating Manager 1...")
    try:
        manager1 = CustomUser.objects.create_user(
            email="manager1@example.com",
            password="password123",
            full_name="Manager One",
            role=Role.MANAGER_SCHOOL,
            school=school,
            work_stream=ws
        )
        print("Manager 1 created successfully.")
    except Exception as e:
        print(f"Failed to create Manager 1: {e}")
        return

    # 3. Attempt to Create Second Manager for SAME School
    print("Attempting to create Manager 2 for the SAME school...")
    try:
        # We need to use the service because that's where the validation logic lives (or should live)
        from accounts.services.user_services import user_create
        
        # Mock a creator (can be admin)
        admin, _ = CustomUser.objects.get_or_create(email="admin@repro.com", role=Role.ADMIN, defaults={"full_name": "Admin"})

        manager2 = user_create(
            creator=admin,
            email="manager2@example.com",
            password="password123",
            full_name="Manager Two",
            role=Role.MANAGER_SCHOOL,
            school_id=school.id,
            work_stream_id=ws.id
        )
        print("Manager 2 created successfully (UNEXPECTED - Issue Reproduced!)")
        
        # Validate if School.manager is set (it might be overwritten)
        school.refresh_from_db()
        print(f"Current School Manager: {school.manager}")

    except ValidationError as e:
        print(f"Caught expected ValidationError: {e}")
        print("SUCCESS: Validation prevented multiple managers.")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")

    # Cleanup
    print("Cleaning up...")
    try:
        if 'manager1' in locals(): manager1.delete()
        if 'manager2' in locals(): manager2.delete()
        school.delete()
        ws.delete()
    except:
        pass
    print("--- End Reproduction Script ---")

if __name__ == '__main__':
    reproduce_issue()
