
import sys
import signal
import time
from django.contrib.auth import get_user_model
from reports.services.count_services import get_workstream_dashboard_statistics
from reports.services.count_managerWorkstream_services import (
    get_workstream_summary,
    get_schools_in_workstream,
    get_classrooms_in_workstream
)
from reports.services.activity_services import get_login_activity_chart

# Timeout handler
def handler(signum, frame):
    raise TimeoutError("Function timed out!")

signal.signal(signal.SIGALRM, handler)

User = get_user_model()
user_id = 90001 # Workstream Manager

try:
    user = User.objects.get(id=user_id)
    print(f"Testing for user: {user.full_name} ({user.role})")
    
    ws_id = user.work_stream_id
    
    # 1. get_workstream_summary
    print("\n--- Testing get_workstream_summary ---")
    sys.stdout.flush()
    signal.alarm(5) # Set 5 seconds timeout
    try:
        get_workstream_summary(workstream_id=ws_id, actor=user)
        print("PASS")
    except TimeoutError:
        print("TIMEOUT")
    except Exception as e:
        print(f"FAIL: {e}")
    signal.alarm(0)

    # 2. get_schools_in_workstream
    print("\n--- Testing get_schools_in_workstream ---")
    sys.stdout.flush()
    signal.alarm(5)
    try:
        get_schools_in_workstream(workstream_id=ws_id, actor=user)
        print("PASS")
    except TimeoutError:
        print("TIMEOUT")
    except Exception as e:
        print(f"FAIL: {e}")
    signal.alarm(0)

    # 3. get_classrooms_in_workstream
    print("\n--- Testing get_classrooms_in_workstream ---")
    sys.stdout.flush()
    signal.alarm(5)
    try:
        get_classrooms_in_workstream(workstream_id=ws_id, actor=user)
        print("PASS")
    except TimeoutError:
        print("TIMEOUT")
    except Exception as e:
        print(f"FAIL: {e}")
    signal.alarm(0)
    
    # 4. get_login_activity_chart
    print("\n--- Testing get_login_activity_chart ---")
    sys.stdout.flush()
    signal.alarm(5)
    try:
        get_login_activity_chart()
        print("PASS")
    except TimeoutError:
        print("TIMEOUT")
    except Exception as e:
        print(f"FAIL: {e}")
    signal.alarm(0)
    
except Exception as e:
    print(f"Top Level Error: {e}")
