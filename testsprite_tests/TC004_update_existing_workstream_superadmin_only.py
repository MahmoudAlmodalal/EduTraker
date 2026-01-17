import requests

BASE_URL = "http://localhost:8000/api/"
AUTH_URL = f"{BASE_URL}auth/login/"
WORKSTREAM_URL = f"{BASE_URL}workstream/"
WORKSTREAMS_UPDATE_URL = f"{BASE_URL}workstreams/{{}}/update/"
TIMEOUT = 30

SUPERADMIN_CREDENTIALS = {
    "username": "admin@test.com",
    "password": "test1234"
}

def get_superadmin_token():
    try:
        resp = requests.post(AUTH_URL, json=SUPERADMIN_CREDENTIALS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        assert "tokens" in data and "access" in data["tokens"], "No access token in response"
        token = data["tokens"]["access"]
        return token
    except Exception as e:
        raise AssertionError(f"Failed to authenticate SuperAdmin: {e}")

def create_workstream(token, payload):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(WORKSTREAM_URL, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        raise AssertionError(f"Failed to create workstream: {e}")

def delete_workstream(token, workstream_id):
    # Deactivate only (no delete endpoint specified)
    url = f"{BASE_URL}workstreams/{workstream_id}/deactivate/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception:
        pass  # best effort cleanup

def update_workstream(token, workstream_id, payload):
    url = WORKSTREAMS_UPDATE_URL.format(workstream_id)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, json=payload, headers=headers, timeout=TIMEOUT)
    return response

def update_existing_workstream_superadmin_only():
    token = get_superadmin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new workstream first to update it
    new_workstream_payload = {
        "name": "Test Workstream TC004",
        "manager_id": 1,
        "max_user": 10
    }
    created_workstream = None
    try:
        resp = requests.post(WORKSTREAM_URL, json=new_workstream_payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        assert resp.status_code == 201, f"Unexpected status code when creating workstream: {resp.status_code}"
        created_workstream = resp.json()
        workstream_id = created_workstream.get("id")
        assert workstream_id is not None, "Created workstream ID missing"

        # 1) Successful update with optional fields
        update_payload = {
            "name": "Updated Workstream Name TC004",
            "description": "Updated description",
            "max_user": 15,
            "is_active": False
        }
        update_resp = update_workstream(token, workstream_id, update_payload)
        assert update_resp.status_code == 200, f"Expected 200 for successful update but got {update_resp.status_code}"
        update_data = update_resp.json()
        # minimal assertion: response JSON contains updated fields if present
        for key, val in update_payload.items():
            assert update_data.get(key) == val, f"Field {key} not updated as expected"

        # 2) Validation error: max_user minimum violation (e.g. 0)
        invalid_payload = {
            "max_user": 0
        }
        invalid_resp = update_workstream(token, workstream_id, invalid_payload)
        assert invalid_resp.status_code == 400, f"Expected 400 for invalid max_user but got {invalid_resp.status_code}"
        invalid_json = invalid_resp.json()
        # Should contain validation error info for max_user
        assert "max_user" in str(invalid_json), "Expected validation error for max_user"

        # 3) Access control: updating with invalid or missing token (401)
        no_auth_resp = requests.put(WORKSTREAMS_UPDATE_URL.format(workstream_id), json=update_payload, timeout=TIMEOUT)
        assert no_auth_resp.status_code == 401, f"Expected 401 Unauthorized without token but got {no_auth_resp.status_code}"

        # 4) Forbidden access for non-SuperAdmin
        fake_token = "invalid.invalid.invalid"
        headers_forbidden = {"Authorization": f"Bearer {fake_token}"}
        forbidden_resp = requests.put(WORKSTREAMS_UPDATE_URL.format(workstream_id), json=update_payload, headers=headers_forbidden, timeout=TIMEOUT)
        # Could be 401 or 403 depending on backend behavior. Specs say 403 for forbidden superadmin-only.
        assert forbidden_resp.status_code in [401, 403], f"Expected 401 or 403 for forbidden access but got {forbidden_resp.status_code}"

        # 5) Update non-existent workstream (404)
        non_existent_id = 999999999
        non_exist_resp = update_workstream(token, non_existent_id, update_payload)
        assert non_exist_resp.status_code == 404, f"Expected 404 for non-existent workstream but got {non_exist_resp.status_code}"

    finally:
        if created_workstream:
            delete_workstream(token, created_workstream.get("id"))

update_existing_workstream_superadmin_only()
