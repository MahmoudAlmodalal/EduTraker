
import sys
import json
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics
from rest_framework.renderers import JSONRenderer

User = get_user_model()
user_id = 90001
renderer = JSONRenderer()

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    user = User.objects.get(id=user_id)
    log(f"Testing for user: {user.full_name}")
    
    stats = get_comprehensive_statistics(actor=user)
    log("Got stats.")
    
    # 1. Serialize Role
    log("Serializing role...")
    renderer.render({'role': stats.get('role', 'N/A')})
    log("Role OK")
    
    # 2. Serialize Statistics Keys (Top Level)
    s = stats.get('statistics', {})
    log(f"Statistics keys: {list(s.keys())}")
    
    # 3. Serialize each key in statistics
    for k, v in s.items():
        log(f"Serializing statistics['{k}']...")
        try:
            renderer.render({k: v})
            log(f"statistics['{k}'] OK")
        except Exception as e:
            log(f"statistics['{k}'] FAILED: {e}")
            
    # 4. Drill down into 'summary' if it exists
    if 'summary' in s:
        summ = s['summary']
        log("Drilling down into summary...")
        for k, v in summ.items():
            log(f"Serializing summary['{k}']...")
            try:
                # If it's the schools list, iterate it
                if k == 'by_school' and isinstance(v, list):
                    log(f"Serializing by_school list (len={len(v)})...")
                    for i, school in enumerate(v):
                        log(f"  School {i} keys: {list(school.keys())}")
                        renderer.render(school)
                        log(f"  School {i} OK")
                else:
                    renderer.render({k: v})
                    log(f"summary['{k}'] OK")
            except Exception as e:
                log(f"summary['{k}'] FAILED: {e}")

    # 5. Drill down into 'schools' (list) if it exists
    if 'schools' in s and isinstance(s['schools'], dict):
        # wait, get_schools_in_workstream returns a dict with 'schools' key inside it?
        # No, look at count_managerWorkstream_services.py:
        # get_workstream_dashboard_statistics returns:
        # { 'summary': ..., 'schools': ..., 'classrooms': ... }
        # And get_schools_in_workstream returns dict:
        # { 'workstream_id': ..., 'schools': [...] }
        
        schools_data = s['schools']
        log("Drilling down into schools data...")
        for k, v in schools_data.items():
            log(f"Serializing schools_data['{k}']...")
            if k == 'schools' and isinstance(v, list):
                 for i, item in enumerate(v):
                     log(f"  Item {i} keys: {list(item.keys())}")
                     renderer.render(item)
                     log(f"  Item {i} OK")
            else:
                renderer.render({k: v})
            log(f"schools_data['{k}'] OK")

except Exception as e:
    log(f"Error: {e}")
