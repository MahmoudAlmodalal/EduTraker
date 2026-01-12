import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_school_creation_and_management():
    # Admin credentials for obtaining initial token
    admin_auth = ("admin@test.com", "test1234")
    headers = {"Content-Type": "application/json"}

    # Login as admin to get access token
    login_resp = requests.post(
        f"{BASE_URL}/api/portal/auth/login/", 
        json={"email": admin_auth[0], "password": admin_auth[1]},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    access_token = login_resp.json()["tokens"]["access"]
    auth_headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Helper to create a user and return user_id and email used
    def create_user(role):
        # Generate unique email to avoid conflicts
        unique_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
        user_data = {
            "email": unique_email,
            "full_name": f"Test {role.capitalize()} User",
            "password": "TestPass123!",
            "role": role,
        }
        resp = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=user_data,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 201, f"User creation failed for role {role}: {resp.text}"
        user_id = resp.json().get("id")
        assert user_id is not None, "User ID missing in creation response"
        return user_id, unique_email

    # Create a manager_workstream user (required to create a workstream)
    manager_workstream_id, _ = create_user("manager_workstream")

    # Create a manager_school user (optional manager for school)
    manager_school_id, _ = create_user("manager_school")

    # Create a workstream using the manager_workstream user
    workstream_data = {
        "name": f"WS_{uuid.uuid4().hex[:8]}",
        "manager_id": manager_workstream_id,
        "max_user": 10,
    }
    ws_resp = requests.post(
        f"{BASE_URL}/api/workstream/",
        json=workstream_data,
        headers=auth_headers,
        timeout=TIMEOUT,
    )
    assert ws_resp.status_code == 201, f"Workstream creation failed: {ws_resp.text}"
    workstream_id = ws_resp.json().get("id")
    assert workstream_id is not None, "Workstream ID missing in creation response"

    school_id = None
    try:
        # Create a school with required school_name and work_stream_id, plus optional manager_id
        school_create_payload = {
            "school_name": f"School_{uuid.uuid4().hex[:8]}",
            "work_stream_id": workstream_id,
            "manager_id": manager_school_id,
        }
        school_create_resp = requests.post(
            f"{BASE_URL}/api/manager/schools/create/",
            json=school_create_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert school_create_resp.status_code == 201, f"School creation failed: {school_create_resp.text}"
        school = school_create_resp.json()
        school_id = school.get("id")
        assert school_id is not None, "School ID missing in creation response"
        assert school.get("school_name") == school_create_payload["school_name"]
        assert school.get("work_stream_id") == workstream_id

        # GET the school details and verify
        get_resp = requests.get(
            f"{BASE_URL}/api/manager/schools/{school_id}/",
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert get_resp.status_code == 200, f"Get school failed: {get_resp.text}"
        school_get = get_resp.json()
        assert school_get.get("id") == school_id
        assert school_get.get("school_name") == school_create_payload["school_name"]
        assert school_get.get("work_stream_id") == workstream_id

        # PATCH update the school_name to a new value
        updated_name = f"UpdatedSchool_{uuid.uuid4().hex[:8]}"
        patch_resp = requests.patch(
            f"{BASE_URL}/api/manager/schools/{school_id}/",
            json={"school_name": updated_name},
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert patch_resp.status_code == 200, f"Patch school failed: {patch_resp.text}"
        patched_school = patch_resp.json()
        assert patched_school.get("school_name") == updated_name

        # GET again and verify the updated name
        get_resp2 = requests.get(
            f"{BASE_URL}/api/manager/schools/{school_id}/",
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert get_resp2.status_code == 200, f"Get school after patch failed: {get_resp2.text}"
        assert get_resp2.json().get("school_name") == updated_name

    finally:
        # Cleanup school
        if school_id:
            del_resp = requests.delete(
                f"{BASE_URL}/api/manager/schools/{school_id}/",
                headers=auth_headers,
                timeout=TIMEOUT,
            )
            assert del_resp.status_code in (204, 200), f"Delete school failed: {del_resp.text}"
        # Cleanup workstream
        if 'workstream_id' in locals():
            # Deleting workstream is not explicitly defined, skipping cleanup if no endpoint given
            pass
        # Cleanup created users by deactivating them instead of deleting
        for user_id in [manager_workstream_id, manager_school_id]:
            deactivate_resp = requests.post(
                f"{BASE_URL}/api/users/{user_id}/deactivate/",
                headers=auth_headers,
                timeout=TIMEOUT,
            )
            assert deactivate_resp.status_code in (200, 204), f"Deactivate user {user_id} failed: {deactivate_resp.text}"

test_school_creation_and_management()
