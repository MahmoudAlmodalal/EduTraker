
import sys
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics
from reports.services.activity_services import get_login_activity_chart

User = get_user_model()
user_id = 90001 # Workstream Manager

def safe_print(obj, indent=0, max_depth=5):
    prefix = "  " * indent
    if indent > max_depth:
        print(f"{prefix}...")
        return

    if isinstance(obj, dict):
        print(f"{prefix}{{")
        for k, v in obj.items():
            print(f"{prefix}  {k}: ", end="")
            if isinstance(v, (dict, list)):
                print("")
                safe_print(v, indent + 1, max_depth)
            else:
                print(f"{type(v).__name__}: {v}")
        print(f"{prefix}}}")
    elif isinstance(obj, list):
        print(f"{prefix}[ (len={len(obj)})")
        for i, v in enumerate(obj[:3]): # Print first 3
            safe_print(v, indent + 1, max_depth)
        if len(obj) > 3:
            print(f"{prefix}  ... ({len(obj)-3} more)")
        print(f"{prefix}]")
    else:
        print(f"{prefix}{type(obj).__name__}: {obj}")

try:
    user = User.objects.get(id=user_id)
    print(f"Testing for user: {user.full_name} ({user.role})")
    
    stats = get_comprehensive_statistics(actor=user)
    stats['activity_chart'] = get_login_activity_chart()
    
    print("\n--- INSECTING DATA STRUCTURE ---")
    safe_print(stats)
    
except Exception as e:
    print(f"Error: {e}")
