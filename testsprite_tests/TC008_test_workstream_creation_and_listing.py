import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"


def test_workstream_creation_and_listing():
    # Login as admin to get access token
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        login_resp.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Admin login request failed: {e}"
    login_json = login_resp.json()
    assert "tokens" in login_json and "access" in login_json["tokens"], "Login response missing tokens.access"
    admin_access_token = login_json["tokens"]["access"]

    headers_admin = {"Authorization": f"Bearer {admin_access_token}"}

    # Create user with role 'manager_workstream'
    user_create_url = f"{BASE_URL}/api/users/create/"
    unique_email = f"mgrws_{uuid.uuid4().hex[:8]}@test.com"
    user_payload = {
        "email": unique_email,
        "full_name": "Manager Workstream Test",
        "password": "TestPass123!",
        "role": "manager_workstream",
    }
    user_id = None
    workstream_id = None
    try:
        user_resp = requests.post(user_create_url, json=user_payload, headers=headers_admin, timeout=TIMEOUT)
        user_resp.raise_for_status()
        user_json = user_resp.json()
        user_id = user_json.get("id")
        assert user_id is not None, "Created user response missing 'id'"

        # Create workstream using the created manager_workstream user_id
        workstream_create_url = f"{BASE_URL}/api/workstream/"
        workstream_name = f"Test Workstream {uuid.uuid4().hex[:6]}"
        workstream_payload = {
            "name": workstream_name,
            "manager_id": user_id,
            "max_user": 10
        }
        ws_resp = requests.post(workstream_create_url, json=workstream_payload, headers=headers_admin, timeout=TIMEOUT)
        ws_resp.raise_for_status()
        ws_json = ws_resp.json()
        workstream_id = ws_json.get("id")
        assert ws_resp.status_code == 201 or ws_resp.status_code == 200, "Workstream creation status code not success"
        assert workstream_id is not None, "Created workstream response missing 'id'"
        assert ws_json.get("name") == workstream_name, "Workstream name mismatch"
        assert ws_json.get("manager_id") == user_id, "Workstream manager_id mismatch"
        assert ws_json.get("max_user") == 10, "Workstream max_user mismatch"

        # List workstreams and verify created workstream is present
        workstream_list_url = f"{BASE_URL}/api/workstream/"
        list_resp = requests.get(workstream_list_url, headers=headers_admin, timeout=TIMEOUT)
        list_resp.raise_for_status()
        list_json = list_resp.json()
        assert isinstance(list_json, list), "Workstream list response is not a list"
        # Confirm that our created workstream appears in the list by id
        found = any(ws.get("id") == workstream_id and ws.get("name") == workstream_name for ws in list_json)
        assert found, "Created workstream not found in workstream list"
    finally:
        # Cleanup: delete created workstream
        if workstream_id is not None:
            try:
                del_ws_url = f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/"
                del_resp = requests.post(del_ws_url, headers=headers_admin, timeout=TIMEOUT)
                del_resp.raise_for_status()
            except Exception:
                pass
        # Cleanup: delete created user
        if user_id is not None:
            try:
                del_user_url = f"{BASE_URL}/api/users/{user_id}/"
                del_resp = requests.delete(del_user_url, headers=headers_admin, timeout=TIMEOUT)
                del_resp.raise_for_status()
            except Exception:
                pass


test_workstream_creation_and_listing()