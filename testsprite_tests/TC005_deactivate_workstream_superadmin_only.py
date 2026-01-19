import requests

BASE_URL = "http://localhost:8000/api/"
AUTH_URL = BASE_URL + "portal/auth/login/"
WORKSTREAM_URL = BASE_URL + "workstream/"
WORKSTREAM_UPDATE_URL = BASE_URL + "workstreams/{}/update/"
WORKSTREAM_DEACTIVATE_URL = BASE_URL + "workstreams/{}/deactivate/"

SUPERADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "test1234"
}

TIMEOUT = 30

def test_deactivate_workstream_superadmin_only():
    session = requests.Session()
    try:
        # Authenticate as SuperAdmin and get JWT token
        auth_resp = session.post(
            AUTH_URL,
            json=SUPERADMIN_CREDENTIALS,
            timeout=TIMEOUT
        )
        assert auth_resp.status_code == 200, f"Authentication failed: {auth_resp.text}"
        auth_json = auth_resp.json()
        access_token = auth_json.get("tokens", {}).get("access")
        assert access_token, "No access token found in auth response"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Create a new workstream to deactivate
        # Since manager_id is required, create minimal valid data
        # We assume manager_id=1 exists; if not, handling is limited here without manager creation endpoint.
        # Use max_user=1 as minimum valid
        create_payload = {
            "name": "Test Workstream Deactivate",
            "manager_id": 1,
            "max_user": 1
        }
        create_resp = session.post(
            WORKSTREAM_URL,
            json=create_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert create_resp.status_code == 201, f"Failed to create workstream: {create_resp.text}"
        created_ws = create_resp.json()
        workstream_id = created_ws.get("id")
        if not workstream_id:
            # Some APIs may just return Location header or no json - fallback parse from Location if available
            location = create_resp.headers.get("Location")
            if location:
                workstream_id = int(location.rstrip("/").split("/")[-1])
        assert workstream_id, "Created workstream ID not found"

        # Deactivate the workstream
        deactivate_resp = session.post(
            WORKSTREAM_DEACTIVATE_URL.format(workstream_id),
            headers=headers,
            timeout=TIMEOUT
        )
        assert deactivate_resp.status_code == 200, f"Failed to deactivate workstream: {deactivate_resp.text}"
        deactivate_json = deactivate_resp.json()
        assert "message" in deactivate_json, "Deactivate response missing 'message' field"

        # Verify the workstream is marked inactive by getting updated info via list with filter
        params = {"is_active": False, "search": "Test Workstream Deactivate"}
        list_resp = session.get(
            WORKSTREAM_URL,
            headers=headers,
            params=params,
            timeout=TIMEOUT
        )
        assert list_resp.status_code == 200, f"Failed to list workstreams: {list_resp.text}"
        ws_list = list_resp.json()
        # Expect the deactivated workstream to appear in inactive list
        found = False
        for ws in ws_list:
            if ws.get("id") == workstream_id:
                found = True
                assert ws.get("is_active") is False, "Workstream is_active flag not False after deactivation"
                break
        assert found, "Deactivated workstream not found in inactive filtered list"

        # Test access control: try to deactivate without auth returns 401 Unauthorized
        no_auth_resp = session.post(
            WORKSTREAM_DEACTIVATE_URL.format(workstream_id),
            timeout=TIMEOUT
        )
        assert no_auth_resp.status_code == 401, "Unauthenticated deactivate attempt did not return 401"

        # Test access control: try to deactivate with invalid token returns 401 Unauthorized
        bad_headers = {"Authorization": "Bearer invalidtoken123", "Content-Type": "application/json"}
        bad_auth_resp = session.post(
            WORKSTREAM_DEACTIVATE_URL.format(workstream_id),
            headers=bad_headers,
            timeout=TIMEOUT
        )
        assert bad_auth_resp.status_code == 401, "Invalid token deactivate attempt did not return 401"

    finally:
        # Cleanup: delete the created workstream by setting is_active to False and then delete if delete API existed
        # Since no delete endpoint described, revert activation to True or just leave inactive
        if 'workstream_id' in locals():
            try:
                # Reactivate before deleting if delete endpoint existed
                # For now, no delete endpoint given; skip
                pass
            except Exception:
                pass

test_deactivate_workstream_superadmin_only()
