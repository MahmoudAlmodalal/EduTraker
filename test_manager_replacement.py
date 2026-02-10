import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from school.models import School
from accounts.models import CustomUser, Role
from workstream.models import WorkStream

def test_manager_replacement():
    print("=== Testing School Manager Replacement ===\n")
    
    # Get a workstream
    ws = WorkStream.objects.first()
    if not ws:
        print("No workstream found!")
        return
    
    print(f"Using workstream: {ws.workstream_name}\n")
    
    # Get a school
    school = School.objects.filter(work_stream=ws).first()
    if not school:
        print("No school found!")
        return
    
    print(f"Testing with school: {school.school_name}")
    print(f"Current manager: {school.manager.full_name if school.manager else 'None'}\n")
    
    # Get or create a workstream manager to perform the operations
    ws_manager = CustomUser.objects.filter(
        role=Role.MANAGER_WORKSTREAM,
        work_stream=ws
    ).first()
    
    if not ws_manager:
        print("No workstream manager found!")
        return
    
    print(f"Acting as workstream manager: {ws_manager.full_name}\n")
    
    # Test 1: Assign a new manager to a school that already has one
    print("--- Test 1: Replace existing manager ---")
    
    from accounts.services.user_services import user_create, user_update
    
    try:
        # Create a new school manager
        new_manager = user_create(
            creator=ws_manager,
            email=f"test_manager_{school.id}@example.com",
            full_name="Test New Manager",
            password="TestPass123!",
            role=Role.MANAGER_SCHOOL,
            work_stream_id=ws.id,
            school_id=school.id
        )
        
        print(f"✓ Successfully created new manager: {new_manager.full_name}")
        
        # Refresh school from database
        school.refresh_from_db()
        print(f"✓ School manager updated to: {school.manager.full_name if school.manager else 'None'}")
        print(f"✓ New manager's school: {new_manager.school.school_name if new_manager.school else 'None'}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n--- Test 2: Update existing manager to different school ---")
    
    # Get another school
    another_school = School.objects.filter(work_stream=ws).exclude(id=school.id).first()
    
    if another_school:
        print(f"Target school: {another_school.school_name}")
        print(f"Current manager: {another_school.manager.full_name if another_school.manager else 'None'}")
        
        try:
            # Update the manager to a different school
            if school.manager:
                manager_to_update = school.manager
                user_update(
                    user=manager_to_update,
                    data={'school_id': another_school.id}
                )
                
                # Refresh from database
                manager_to_update.refresh_from_db()
                school.refresh_from_db()
                another_school.refresh_from_db()
                
                print(f"✓ Manager {manager_to_update.full_name} moved to {another_school.school_name}")
                print(f"✓ Original school manager: {school.manager.full_name if school.manager else 'None'}")
                print(f"✓ New school manager: {another_school.manager.full_name if another_school.manager else 'None'}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("No other school available for testing")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_manager_replacement()
