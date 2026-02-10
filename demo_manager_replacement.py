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
from accounts.services.user_services import user_create, user_update

def demonstrate_manager_replacement():
    print("=" * 60)
    print("DEMONSTRATING SCHOOL MANAGER REPLACEMENT FEATURE")
    print("=" * 60)
    
    # Get a school with a manager
    school = School.objects.filter(manager__isnull=False).first()
    
    if not school:
        print("\nNo school with a manager found. Creating test data...")
        school = School.objects.filter(manager__isnull=True).first()
        if not school:
            print("No schools available!")
            return
    
    print(f"\n📚 School: {school.school_name}")
    print(f"   Current Manager: {school.manager.full_name if school.manager else 'None'}")
    
    # Get workstream manager
    ws_manager = CustomUser.objects.filter(
        role=Role.MANAGER_WORKSTREAM,
        work_stream=school.work_stream
    ).first()
    
    if not ws_manager:
        print("\n❌ No workstream manager found!")
        return
    
    print(f"\n👤 Acting as: {ws_manager.full_name} (Workstream Manager)")
    
    # Test Case 1: Create a new manager and assign to school with existing manager
    print("\n" + "-" * 60)
    print("TEST 1: Assign new manager to school (replacing existing)")
    print("-" * 60)
    
    old_manager = school.manager
    old_manager_name = old_manager.full_name if old_manager else "None"
    
    try:
        new_manager = user_create(
            creator=ws_manager,
            email=f"new_manager_{school.id}@test.com",
            full_name=f"New Manager for {school.school_name}",
            password="SecurePass123!",
            role=Role.MANAGER_SCHOOL,
            work_stream_id=school.work_stream_id,
            school_id=school.id
        )
        
        # Refresh from database
        school.refresh_from_db()
        
        print(f"\n✅ SUCCESS!")
        print(f"   Old Manager: {old_manager_name}")
        print(f"   New Manager: {new_manager.full_name}")
        print(f"   School's Current Manager: {school.manager.full_name}")
        
        if old_manager:
            old_manager.refresh_from_db()
            print(f"   Old Manager's School: {old_manager.school.school_name if old_manager.school else 'None (unassigned)'}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return
    
    # Test Case 2: Update existing manager to different school
    print("\n" + "-" * 60)
    print("TEST 2: Move manager to different school")
    print("-" * 60)
    
    another_school = School.objects.exclude(id=school.id).filter(
        work_stream=school.work_stream
    ).first()
    
    if another_school:
        print(f"\n📚 Target School: {another_school.school_name}")
        print(f"   Current Manager: {another_school.manager.full_name if another_school.manager else 'None'}")
        
        old_target_manager = another_school.manager
        
        try:
            # Move the new manager to another school
            user_update(
                user=new_manager,
                data={'school_id': another_school.id}
            )
            
            # Refresh from database
            new_manager.refresh_from_db()
            school.refresh_from_db()
            another_school.refresh_from_db()
            
            print(f"\n✅ SUCCESS!")
            print(f"   Manager {new_manager.full_name} moved from:")
            print(f"     {school.school_name} → {another_school.school_name}")
            print(f"\n   Original School ({school.school_name}):")
            print(f"     Manager: {school.manager.full_name if school.manager else 'None (unassigned)'}")
            print(f"\n   Target School ({another_school.school_name}):")
            print(f"     Manager: {another_school.manager.full_name}")
            
            if old_target_manager:
                old_target_manager.refresh_from_db()
                print(f"\n   Previous Target School Manager ({old_target_manager.full_name}):")
                print(f"     School: {old_target_manager.school.school_name if old_target_manager.school else 'None (unassigned)'}")
            
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
    else:
        print("\n⚠️  No other school available for testing manager move")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_manager_replacement()
