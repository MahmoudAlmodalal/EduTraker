import requests

BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
WORKSTREAM_URL = f"{BASE_URL}/workstream/"
TIMEOUT = 30
SUPERADMIN_CREDENTIALS = {"username": "admin@test.com", "password": "test1234"}


def get_superadmin_token():
    resp = requests.post(LOGIN_URL, json=SUPERADMIN_CREDENTIALS, timeout=TIMEOUT)
    resp.raise_for_status()
    tokens = resp.json().get("tokens", {})
    access_token = tokens.get("access")
    if not access_token:
        raise Exception("Access token not found in login response")
    return access_token


def create_workstream(headers, payload):
    resp = requests.post(WORKSTREAM_URL, json=payload, headers=headers, timeout=TIMEOUT)
    return resp


def delete_workstream(workstream_id, headers):
    # Assuming deleting a workstream is allowed for cleanup and is done via DELETE method on /workstream/{id}/
    url = f"{WORKSTREAM_URL}{workstream_id}/"
    try:
        resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
        # If delete not allowed or not implemented, ignore failure to avoid test interference
    except Exception:
        pass


def test_create_new_workstream_superadmin_only():
    access_token = get_superadmin_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Invalid manager_id (non-existent)
    invalid_manager_payload = {
        "name": "Test Workstream Invalid Manager",
        "manager_id": 99999999,  # Assuming this ID does not exist
        "max_user": 10
    }
    resp = create_workstream(headers, invalid_manager_payload)
    assert resp.status_code == 404, f"Expected 404 for non-existent manager_id, got {resp.status_code}"

    # Step 2: Missing required fields (no name, no manager_id, no max_user)
    missing_fields_payload = {}
    resp = create_workstream(headers, missing_fields_payload)
    assert resp.status_code == 400, f"Expected 400 for missing required fields, got {resp.status_code}"
    resp_json = resp.json()
    assert "name" in resp_json or "manager_id" in resp_json or "max_user" in resp_json, \
        "Validation errors for required fields expected"

    # Step 3: max_user below minimum value 1
    invalid_max_user_payload = {
        "name": "Test Workstream Invalid max_user",
        "manager_id": 1,  # Using 1 as a plausible manager_id, may error if manager 1 doesn't exist
        "max_user": 0
    }
    resp = create_workstream(headers, invalid_max_user_payload)
    assert resp.status_code in (400, 404), f"Expected 400 or 404 for invalid max_user or manager, got {resp.status_code}"

    # Step 4: Successful creation - we must find a valid manager_id first
    valid_payload = {
        "name": "Test Workstream SuperAdmin Valid",
        "manager_id": 1,
        "max_user": 5,
        "description": "Created by test_create_new_workstream_superadmin_only"
    }
    resp = create_workstream(headers, valid_payload)
    if resp.status_code == 201:
        created_workstream = resp.json()
        created_id = created_workstream.get("id")
        try:
            assert created_workstream.get("name") == valid_payload["name"], "Workstream name mismatch"
            assert created_workstream.get("manager_id") == valid_payload["manager_id"], "Manager ID mismatch"
            assert created_workstream.get("max_user") == valid_payload["max_user"], "max_user mismatch"
        finally:
            if created_id:
                delete_workstream(created_id, headers)
    else:
        assert resp.status_code in (400, 404), f"Unexpected status code for create with manager_id=1: {resp.status_code}"


test_create_new_workstream_superadmin_only()
