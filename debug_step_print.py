
import sys
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics

User = get_user_model()
user_id = 90001 # Workstream Manager

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    user = User.objects.get(id=user_id)
    log(f"Testing for user: {user.full_name}")
    
    log("Calling get_comprehensive_statistics...")
    stats = get_comprehensive_statistics(actor=user)
    log("get_comprehensive_statistics returned.")
    
    log(f"Stats type: {type(stats)}")
    
    if isinstance(stats, dict):
        log(f"Keys: {list(stats.keys())}")
        
        if 'statistics' in stats:
            s = stats['statistics']
            log(f"Statistics type: {type(s)}")
            if isinstance(s, dict):
                log(f"Statistics Keys: {list(s.keys())}")
                
                for k in s.keys():
                    log(f"Accessing s['{k}']...")
                    val = s[k]
                    log(f"Val type: {type(val)}")
                    # str(val) might be huge or hang, so just print type/len
                    if isinstance(val, list):
                        log(f"List length: {len(val)}")
                    elif isinstance(val, dict):
                        log(f"Dict keys: {list(val.keys())}")
                    else:
                        log(f"Value: {str(val)[:50]}...")
                    log(f"Done with s['{k}']")
            else:
                log(f"Statistics value: {str(s)[:100]}")
    else:
        log("Stats is not a dict")

except Exception as e:
    log(f"Error: {e}")
