#!/usr/bin/env python3
"""
Test script to diagnose secretary creation issue.
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser, Role
from secretary.services.secretary_services import secretary_create

# Find a school manager user
try:
    school_manager = CustomUser.objects.filter(role=Role.MANAGER_SCHOOL).first()
    
    if not school_manager:
        print("❌ No School Manager found in database")
    else:
        print(f"✅ Found School Manager: {school_manager.email} (ID: {school_manager.id})")
        print(f"   School ID: {school_manager.school_id}")
        
        # Try to create a secretary
        print("\n🔄 Attempting to create a test secretary...")
        try:
            secretary = secretary_create(
                creator=school_manager,
                email="test_secretary_999@test.com",
                full_name="Test Secretary 999",
                password="testpass123",
                school_id=school_manager.school_id,
                department="Administration",
                hire_date=date.today(),
                office_number="Room 101"
            )
            print(f"✅ SUCCESS! Secretary created: {secretary.user.full_name} (ID: {secretary.id})")
        except Exception as e:
            print(f"❌ FAILED with error: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            import traceback
            print("\n📋 Full traceback:")
            traceback.print_exc()

except Exception as e:
    print(f"❌ Script error: {e}")
    import traceback
    traceback.print_exc()
