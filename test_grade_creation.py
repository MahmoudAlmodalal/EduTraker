#!/usr/bin/env python3
"""
Test script to diagnose grade creation issue.
This will attempt to create a grade and show the exact error.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser, Role
from school.services.grade_services import grade_create

# Find a school manager user
try:
    school_manager = CustomUser.objects.filter(role=Role.MANAGER_SCHOOL).first()
    
    if not school_manager:
        print("❌ No School Manager found in database")
        print("Available roles in database:")
        for role_value, role_name in Role.choices:
            count = CustomUser.objects.filter(role=role_value).count()
            print(f"  - {role_name}: {count} users")
    else:
        print(f"✅ Found School Manager: {school_manager.email} (ID: {school_manager.id})")
        print(f"   Role: {school_manager.role}")
        print(f"   School: {school_manager.school}")
        
        # Try to create a grade
        print("\n🔄 Attempting to create a test grade...")
        try:
            grade = grade_create(
                creator=school_manager,
                name="Test Grade 999",
                numeric_level=999,
                min_age=10,
                max_age=11
            )
            print(f"✅ SUCCESS! Grade created: {grade.name} (ID: {grade.id})")
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
