import requests

BASE_URL = "http://localhost:8000/api"
LOGIN_ENDPOINT = "/portal/auth/login/"
WORKSTREAM_CREATE_ENDPOINT = "/workstream/"
WORKSTREAM_UPDATE_ENDPOINT = "/workstreams/{workstream_id}/update/"
WORKSTREAM_DELETE_ENDPOINT = "/workstreams/{workstream_id}/deactivate/"

AUTH_CREDENTIALS = {"email": "admin@test.com", "password": "test1234"}
TIMEOUT = 30


def test_update_existing_workstream_by_id():
    session = requests.Session()
    token = None
    workstream_id = None

    def get_auth_token():
        url = BASE_URL + LOGIN_ENDPOINT
        resp = session.post(
            url, json={"email": AUTH_CREDENTIALS["email"], "password": AUTH_CREDENTIALS["password"]}, timeout=TIMEOUT
        )
        assert resp.status_code == 200, f"Authentication failed with status {resp.status_code}"
        json_resp = resp.json()
        assert "token" in json_resp and "access" in json_resp["token"], "Token not found in response"
        return json_resp["token"]["access"]

    def create_workstream(token, data):
        url = BASE_URL + WORKSTREAM_CREATE_ENDPOINT
        headers = {"Authorization": f"Bearer {token}"}
        resp = session.post(url, headers=headers, json=data, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Workstream creation failed with status {resp.status_code}, {resp.text}"
        json_resp = resp.json()
        assert "id" in json_resp, "Created workstream ID missing in response"
        return json_resp["id"]

    def delete_workstream(token, ws_id):
        url = BASE_URL + WORKSTREAM_DELETE_ENDPOINT.format(workstream_id=ws_id)
        headers = {"Authorization": f"Bearer {token}"}
        resp = session.post(url, headers=headers, timeout=TIMEOUT)
        # Allow 200 OK for successful deactivation or 404 if already deleted or non-existent
        assert resp.status_code in (200, 404), f"Workstream delete failed with status {resp.status_code}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new workstream to run update tests on
    create_payload = {"name": "Test Update WS", "manager_id": 1, "max_user": 5}
    workstream_id = None
    try:
        # Create workstream
        create_resp = session.post(
            BASE_URL + WORKSTREAM_CREATE_ENDPOINT, headers=headers, json=create_payload, timeout=TIMEOUT
        )
        assert create_resp.status_code == 201, f"Failed to create workstream, status={create_resp.status_code}"
        ws_data = create_resp.json()
        workstream_id = ws_data.get("id")
        assert isinstance(workstream_id, int), "Invalid workstream ID"

        update_url = BASE_URL + WORKSTREAM_UPDATE_ENDPOINT.format(workstream_id=workstream_id)

        # 1) Test valid update with optional fields
        update_payload_optional = {
            "description": "Updated description",
            "max_user": 10,
            "is_active": False,
        }
        resp = session.put(update_url, headers=headers, json=update_payload_optional, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Valid update failed with status {resp.status_code}"
        updated_data = resp.json()
        for key, value in update_payload_optional.items():
            assert key in updated_data and updated_data[key] == value, f"{key} not updated correctly"

        # 2) Test validation: max_user minimum constraint (should fail for zero or less)
        invalid_payload = {"max_user": 0}
        resp = session.put(update_url, headers=headers, json=invalid_payload, timeout=TIMEOUT)
        assert resp.status_code == 400, f"Validation did not fail for max_user=0, got {resp.status_code}"
        error_resp = resp.json()
        assert "max_user" in resp.text or ("max_user" in error_resp.get("errors", {}) or "max_user" in error_resp), "Validation error detail missing"

        # 3) Test update with non-existent workstream ID
        non_existent_id = 999999999
        non_exist_url = BASE_URL + WORKSTREAM_UPDATE_ENDPOINT.format(workstream_id=non_existent_id)
        resp = session.put(non_exist_url, headers=headers, json={"name": "Should Fail"}, timeout=TIMEOUT)
        assert resp.status_code == 404, f"Non-existent update did not return 404, got {resp.status_code}"

        # 4) Test authentication enforcement - no token
        resp = session.put(update_url, timeout=TIMEOUT, json={"name": "No Token"})
        assert resp.status_code == 401, f"Unauthorized update without token did not return 401, got {resp.status_code}"

        # 5) Test authorization enforcement - invalid token (simulate by altering token)
        invalid_headers = {"Authorization": "Bearer invalidtoken123"}
        resp = session.put(update_url, headers=invalid_headers, json={"name": "Invalid Token"}, timeout=TIMEOUT)
        assert resp.status_code in (401, 403), f"Forbidden update with invalid token did not return correct status, got {resp.status_code}"

    finally:
        if workstream_id:
            delete_workstream(token, workstream_id)


test_update_existing_workstream_by_id()
