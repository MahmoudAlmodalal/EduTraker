import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30


def test_workstream_creation():
    session = requests.Session()
    try:
        # Step 1: Admin login to get access token
        login_resp = session.post(
            f"{BASE_URL}/api/portal/auth/login/",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        access_token = login_resp.json().get("tokens", {}).get("access")
        assert access_token, "No access token received on admin login"

        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Create a user with role 'manager_workstream' to use as manager for the workstream
        unique_email = f"manager_workstream_test_{uuid.uuid4().hex[:8]}@example.com"
        user_payload = {
            "email": unique_email,
            "full_name": "Manager Workstream Test",
            "password": "TestPass123!",
            "role": "manager_workstream",
        }

        user_create_resp = session.post(
            f"{BASE_URL}/api/users/create/",
            json=user_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert user_create_resp.status_code == 201, f"Manager user creation failed: {user_create_resp.text}"
        user_data = user_create_resp.json()
        manager_id = user_data.get("id")
        assert manager_id, "No user ID found for manager_workstream user"

        # Step 3: Create workstream with required fields name, manager_id, max_user
        workstream_payload = {
            "name": "Test Workstream TC008",
            "manager_id": manager_id,
            "max_user": 10,
        }
        workstream_create_resp = session.post(
            f"{BASE_URL}/api/workstream/",
            json=workstream_payload,
            headers=headers,
            timeout=TIMEOUT,
        )

        assert workstream_create_resp.status_code == 201, f"Workstream creation failed: {workstream_create_resp.text}"
        workstream_data = workstream_create_resp.json()
        assert workstream_data.get("name") == workstream_payload["name"], "Workstream name mismatch"
        assert workstream_data.get("manager_id") == manager_id, "Workstream manager_id mismatch"
        assert workstream_data.get("max_user") == 10, "Workstream max_user mismatch"
        assert "id" in workstream_data, "Workstream ID missing in response"

    finally:
        # Cleanup: delete created workstream and user
        # Delete workstream if created
        if 'workstream_data' in locals() and "id" in workstream_data:
            ws_id = workstream_data["id"]
            # No explicit delete endpoint provided for workstream in PRD;
            # Assuming delete by direct DELETE /api/workstreams/{workstream_id}/
            delete_ws_resp = session.delete(
                f"{BASE_URL}/api/workstreams/{ws_id}/",
                headers=headers,
                timeout=TIMEOUT,
            )

        # Delete user if created
        if 'manager_id' in locals():
            delete_user_resp = session.delete(
                f"{BASE_URL}/api/users/{manager_id}/",
                headers=headers,
                timeout=TIMEOUT,
            )


test_workstream_creation()
