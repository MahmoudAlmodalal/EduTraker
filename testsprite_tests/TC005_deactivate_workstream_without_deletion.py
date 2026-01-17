import requests
import uuid

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NjQ3MTYzLCJpYXQiOjE3Njg2NDM1NjMsImp0aSI6ImI2OWMxNTRmYmE0NDQ0MzFiY2RlYTQxM2EzYTMxNjM2IiwidXNlcl9pZCI6IjUyIn0.vws_-oL8rF743FYpML0dykuPgXzUxaXMnLEAH4Grs2I"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
TIMEOUT = 30

def test_deactivate_workstream_without_deletion():
    create_url = f"{BASE_URL}/api/workstream/"
    deactivate_url_template = f"{BASE_URL}/api/workstreams/{{}}/deactivate/"
    update_url_template = f"{BASE_URL}/api/workstreams/{{}}/update/"
    get_url_template = f"{BASE_URL}/api/workstreams/{{}}/info/"

    new_workstream_id = None
    try:
        # Step 1: Create a new workstream to deactivate
        # Use a unique name to avoid conflicts
        unique_name = f"TestWorkstream-{uuid.uuid4()}"
        # Use a valid manager_id which has MANAGER_WORKSTREAM role. Assuming 1 is valid.
        create_payload = {
            "name": unique_name,
            "manager_id": 49,
            "max_user": 1
        }

        resp = requests.post(create_url, json=create_payload, headers=HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Failed to create workstream for test setup: {resp.status_code} {resp.text}"
        created_data = resp.json()
        # The API docs don't specify response payload on create, so get the id by listing or subsequent calls
        # We'll list all workstreams filtering by name to find the created workstream id
        list_resp = requests.get(f"{BASE_URL}/api/workstream/?search={unique_name}", headers=HEADERS, timeout=TIMEOUT)
        assert list_resp.status_code == 200, f"Failed to list workstreams for test setup: {list_resp.status_code} {list_resp.text}"
        list_data = list_resp.json()
        assert isinstance(list_data, list) and len(list_data) == 1, "Created workstream not found in list"
        new_workstream_id = list_data[0]["id"]

        # Step 2: Deactivate the workstream
        deactivate_url = deactivate_url_template.format(new_workstream_id)
        deactivate_resp = requests.post(deactivate_url, headers=HEADERS, timeout=TIMEOUT)
        assert deactivate_resp.status_code == 200, f"Deactivate request failed: {deactivate_resp.status_code} {deactivate_resp.text}"
        deactivate_data = deactivate_resp.json()
        assert "message" in deactivate_data and isinstance(deactivate_data["message"], str) and deactivate_data["message"], "Deactivate message missing or empty"

        # Step 3: Verify the workstream is marked inactive without deletion
        # Use update endpoint to get the current state since info endpoint is public and limited, use listing endpoint again
        list_resp2 = requests.get(f"{BASE_URL}/api/workstream/?search={unique_name}", headers=HEADERS, timeout=TIMEOUT)
        assert list_resp2.status_code == 200, f"Failed to list workstream after deactivate: {list_resp2.status_code} {list_resp2.text}"
        list_data2 = list_resp2.json()
        assert len(list_data2) == 1, "Workstream disappeared after deactivate - likely deleted"
        updated_ws = list_data2[0]
        assert updated_ws["is_active"] is False, f"Workstream is_active flag not false after deactivate: {updated_ws['is_active']}"

        # Step 4: Test Unauthorized (no token)
        deactivate_resp_unauth = requests.post(deactivate_url, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        assert deactivate_resp_unauth.status_code == 401, f"Unauthorized request did not return 401: {deactivate_resp_unauth.status_code}"

        # Step 5: Test Forbidden (invalid / non-SuperAdmin token)
        # For the test, modify token (simulate non-SuperAdmin by altering token)
        fake_token = "Bearer invalid.token.forbiddencase"
        headers_forbidden = {"Authorization": fake_token, "Content-Type": "application/json"}
        deactivate_resp_forbidden = requests.post(deactivate_url, headers=headers_forbidden, timeout=TIMEOUT)
        assert deactivate_resp_forbidden.status_code == 403, f"Forbidden request did not return 403: {deactivate_resp_forbidden.status_code}"

        # Step 6: Test Not Found (nonexistent workstream id)
        fake_workstream_id = 99999999
        deactivate_url_notfound = deactivate_url_template.format(fake_workstream_id)
        deactivate_resp_notfound = requests.post(deactivate_url_notfound, headers=HEADERS, timeout=TIMEOUT)
        assert deactivate_resp_notfound.status_code == 404, f"Not found request did not return 404: {deactivate_resp_notfound.status_code}"

    finally:
        if new_workstream_id:
            # Cleanup: Reactivate or delete the test workstream to keep environment clean
            # Since no delete endpoint described, reactivate by updating is_active to True
            try:
                update_url = update_url_template.format(new_workstream_id)
                reactivate_payload = {"is_active": True}
                requests.put(update_url, headers=HEADERS, json=reactivate_payload, timeout=TIMEOUT)
            except Exception:
                pass


test_deactivate_workstream_without_deletion()