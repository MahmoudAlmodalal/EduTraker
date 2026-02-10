import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from school.models import School
from accounts.models import CustomUser, Role

def fix_incorrect_assignments():
    print("--- Starting School Manager Correction ---")
    
    # 1. Find all schools where the manager is NOT a Role.MANAGER_SCHOOL
    schools = School.objects.exclude(manager=None)
    fixed_count = 0
    
    for school in schools:
        manager = school.manager
        if manager.role != Role.MANAGER_SCHOOL:
            print(f"Fixing School '{school.school_name}': Manager '{manager.full_name}' has incorrect role '{manager.role}'. Unassigning...")
            school.manager = None
            school.save(update_fields=['manager'])
            fixed_count += 1
            
    print(f"--- Correction Complete. Fixed {fixed_count} schools. ---")

if __name__ == "__main__":
    fix_incorrect_assignments()
