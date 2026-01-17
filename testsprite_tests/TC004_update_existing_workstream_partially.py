import requests

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NjQ3MTYzLCJpYXQiOjE3Njg2NDM1NjMsImp0aSI6ImI2OWMxNTRmYmE0NDQ0MzFiY2RlYTQxM2EzYTMxNjM2IiwidXNlcl9pZCI6IjUyIn0.vws_-oL8rF743FYpML0dykuPgXzUxaXMnLEAH4Grs2I"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
TIMEOUT = 30

def test_update_existing_workstream_partially():
    # Helper to create a workstream to update
    create_payload = {
        import uuid
        unique_name = f"Test Workstream Update {str(uuid.uuid4())[:8]}"
        "name": unique_name,
        "manager_id": 46,
        "max_user": 10,
        "description": "Initial description"
    }
    workstream_id = None
    try:
        # Create workstream
        create_resp = requests.post(f"{BASE_URL}/api/workstream/", json=create_payload, headers=HEADERS, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Workstream creation failed with status {create_resp.status_code}"
        workstream_id = create_resp.json().get("id")
        assert isinstance(workstream_id, int), "Created workstream ID is invalid"

        update_url = f"{BASE_URL}/api/workstreams/{workstream_id}/update/"

        # 1) Successful partial update with valid data
        update_payload = {
            "name": "Updated Name",
            "max_user": 20
        }
        update_resp = requests.put(update_url, json=update_payload, headers=HEADERS, timeout=TIMEOUT)
        assert update_resp.status_code == 200, f"Update failed with status {update_resp.status_code}"
        updated_data = update_resp.json()
        assert updated_data.get("name") == update_payload["name"], "Name was not updated correctly"
        assert updated_data.get("max_user") == update_payload["max_user"], "max_user was not updated correctly"

        # 2) Validation error handling: invalid max_user (below minimum)
        invalid_payload = {"max_user": 0}
        invalid_resp = requests.put(update_url, json=invalid_payload, headers=HEADERS, timeout=TIMEOUT)
        assert invalid_resp.status_code == 400, f"Expected 400 for invalid max_user but got {invalid_resp.status_code}"

        # 3) Unauthorized access: no token
        unauthorized_headers = {"Content-Type": "application/json"}
        unauthorized_resp = requests.put(update_url, json=update_payload, headers=unauthorized_headers, timeout=TIMEOUT)
        assert unauthorized_resp.status_code == 401, f"Expected 401 for unauthorized access but got {unauthorized_resp.status_code}"

        # 4) Forbidden access: token with insufficient permissions (simulate by a fake token)
        forbidden_headers = {"Authorization": "Bearer invalid_or_non_superadmin_token", "Content-Type": "application/json"}
        forbidden_resp = requests.put(update_url, json=update_payload, headers=forbidden_headers, timeout=TIMEOUT)
        assert forbidden_resp.status_code == 403, f"Expected 403 for forbidden access but got {forbidden_resp.status_code}"

        # 5) Update workstream not found (use large unlikely ID)
        not_found_url = f"{BASE_URL}/api/workstreams/99999999/update/"
        not_found_resp = requests.put(not_found_url, json=update_payload, headers=HEADERS, timeout=TIMEOUT)
        assert not_found_resp.status_code == 404, f"Expected 404 for not found workstream but got {not_found_resp.status_code}"

    finally:
        # Clean up created workstream if exists (deactivate then delete if supported)
        if workstream_id is not None:
            # Attempt deactivate (POST) endpoint
            try:
                requests.post(f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/", headers=HEADERS, timeout=TIMEOUT)
            except:
                pass
            # No delete endpoint specified in PRD, so no further cleanup

test_update_existing_workstream_partially()