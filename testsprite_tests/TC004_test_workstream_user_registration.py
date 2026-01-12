import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_admin_token():
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    response = requests.post(url, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()['tokens']['access']

def create_user(admin_token, role):
    url = f"{BASE_URL}/api/users/create/"
    unique_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "email": unique_email,
        "username": unique_email,
        "password": "ManagerPass123!",
        "role": role,
        "first_name": "Test",
        "last_name": "User"
    }
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()  # Expect user object with 'id'

def create_workstream(admin_token, manager_id):
    url = f"{BASE_URL}/api/workstream/"
    payload = {
        "name": f"WS-{uuid.uuid4().hex[:8]}",
        "manager_id": manager_id
    }
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()  # Expect workstream object with 'id'

def delete_workstream(admin_token, workstream_id):
    url = f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    # Deactivate before delete if required
    requests.post(url, headers=headers, timeout=TIMEOUT)
    url_del = f"{BASE_URL}/api/workstreams/{workstream_id}/"
    requests.delete(url_del, headers=headers, timeout=TIMEOUT)

def delete_user(admin_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    requests.delete(url, headers=headers, timeout=TIMEOUT)

def test_workstream_user_registration():
    admin_token = get_admin_token()

    # Create a workstream manager user
    manager_user = create_user(admin_token, "manager_workstream")
    manager_id = manager_user["id"]

    # Create a workstream using the manager_id
    workstream = create_workstream(admin_token, manager_id)
    workstream_id = workstream["id"]

    # URL for workstream user registration
    register_url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/register/"

    # Test with mismatched password_confirm - expect error
    bad_registration_payload = {
        "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password": "StrongPass123!",
        "password_confirm": "WrongConfirm123!",
        "first_name": "Workstream",
        "last_name": "User"
    }
    try:
        bad_resp = requests.post(register_url, json=bad_registration_payload, timeout=TIMEOUT)
        # Expect 400 Bad Request due to password_confirm mismatch
        assert bad_resp.status_code == 400, f"Expected 400 for bad password_confirm but got {bad_resp.status_code}"
        bad_resp_json = bad_resp.json()
        # The error should mention password_confirm or passwords mismatch
        errors_str = str(bad_resp_json).lower()
        assert "password_confirm" in errors_str or "password" in errors_str or "mismatch" in errors_str
    except requests.RequestException as e:
        assert False, f"Bad registration request failed unexpectedly: {e}"

    # Test successful registration
    new_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    reg_payload = {
        "email": new_email,
        "username": new_email,
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "first_name": "Workstream",
        "last_name": "User"
    }

    # Register the user and capture user_id for cleanup
    created_user_id = None
    try:
        reg_resp = requests.post(register_url, json=reg_payload, timeout=TIMEOUT)
        assert reg_resp.status_code == 201, f"Expected 201 Created but got {reg_resp.status_code}"
        reg_resp_json = reg_resp.json()
        # Expect fields indicating user created, e.g., id or username returned
        assert "id" in reg_resp_json, "Response missing user id"
        created_user_id = reg_resp_json["id"]
        assert reg_resp_json.get("email") == new_email
    except requests.RequestException as e:
        assert False, f"Registration request failed unexpectedly: {e}"
    finally:
        # Cleanup: Delete created workstream user if possible (requires admin)
        if created_user_id:
            try:
                delete_user(admin_token, created_user_id)
            except Exception:
                pass

        # Cleanup created workstream and manager user
        try:
            delete_workstream(admin_token, workstream_id)
        except Exception:
            pass
        try:
            delete_user(admin_token, manager_id)
        except Exception:
            pass

test_workstream_user_registration()
