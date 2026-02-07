
import os
import django
import sys
import time
import random

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from django.core.exceptions import ValidationError
from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from accounts.services.user_services import user_create, user_update

def run_test():
    print("Starting Verification: Single Manager per Workstream")
    
    # Generate unique suffix
    ts = int(time.time())
    suffix = f"{ts}_{random.randint(1000, 9999)}"
    
    # Clean up previous test data - SKIPPED to avoid django_admin_log error
    # CustomUser.objects.filter(email__startswith='test_mgr_').delete()
    # Workstream.objects.filter(workstream_name='Test Constraint WS').delete()

    # 1. Create a Test Workstream
    ws_name = f'Test Constraint WS {suffix}'
    ws = WorkStream.objects.create(
        workstream_name=ws_name,
        capacity=100
    )
    print(f"Created Workstream: {ws.workstream_name} (ID: {ws.id})")

    # 2. Create Admin (Creator)
    admin_email = f'test_admin_{suffix}@example.com'
    admin = CustomUser.objects.create(
        email=admin_email,
        full_name='Test Admin',
        role=Role.ADMIN
    )

    # 3. Create First Manager (Should Succeed)
    print("\n[TEST 1] Assigning First Manager...")
    try:
        mgr1 = user_create(
            creator=admin,
            email=f'test_mgr_1_{suffix}@example.com',
            full_name='Manager One',
            password='password123',
            role=Role.MANAGER_WORKSTREAM,
            work_stream_id=ws.id
        )
        print(f"✅ Success: Created Manager One (ID: {mgr1.id}) for Workstream.")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    # 4. Attempt to Create Second Manager for same WS (Should Fail)
    print("\n[TEST 2] Assigning Second Manager to SAME Workstream (Should Fail)...")
    try:
        mgr2 = user_create(
            creator=admin,
            email=f'test_mgr_2_{suffix}@example.com',
            full_name='Manager Two',
            password='password123',
            role=Role.MANAGER_WORKSTREAM,
            work_stream_id=ws.id
        )
        print(f"❌ FAILED: Manager Two was created but should have been blocked!")
    except ValidationError as e:
        print(f"✅ Success (Blocked): Caught ValidationError: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")

    # 5. Create Unassigned Manager then Update (Should Fail)
    print("\n[TEST 3] Updating Unassigned Manager to Occupied Workstream (Should Fail)...")
    try:
        # Create unassigned first
        mgr3 = CustomUser.objects.create(
            email=f'test_mgr_3_{suffix}@example.com',
            full_name='Manager Three',
            role=Role.GUEST # Start as guest then promote
        )
        
        # Update
        user_update(
            user=mgr3,
            data={
                'role': Role.MANAGER_WORKSTREAM,
                'work_stream_id': ws.id
            }
        )
        print(f"❌ FAILED: Manager Three updated but should have been blocked!")
    except ValidationError as e:
        print(f"✅ Success (Blocked): Caught ValidationError: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")

    # Cleanup - SKIPPED
    print("\nCleanup skipped to preserve DB integrity.")

if __name__ == '__main__':
    run_test()
