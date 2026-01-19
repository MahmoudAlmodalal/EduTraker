import requests

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NjQ3MTYzLCJpYXQiOjE3Njg2NDM1NjMsImp0aSI6ImI2OWMxNTRmYmE0NDQ0MzFiY2RlYTQxM2EzYTMxNjM2IiwidXNlcl9pZCI6IjUyIn0.vws_-oL8rF743FYpML0dykuPgXzUxaXMnLEAH4Grs2I",
    "Content-Type": "application/json",
}
TIMEOUT = 30


def test_create_new_workstream_with_validation():
    # Use a known free manager ID (manager_workstream_test_2ca9e5ee@example.com)
    valid_manager_id = 36

    # Helper function to create a valid workstream payload
    def valid_payload():
        import uuid
        unique_name = f"Test Workstream {str(uuid.uuid4())[:8]}"
        return {
            "name": unique_name,
            "manager_id": valid_manager_id,
            "max_user": 10,
            "description": "A test workstream"
        }

    # Helper function to delete a workstream by ID
    def delete_workstream(workstream_id):
        url = f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/"
        resp = requests.post(url, headers=HEADERS, timeout=TIMEOUT)
        return resp.status_code == 200

    created_workstream_id = None

    try:
        # 1. Success case: create a valid workstream
        resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=valid_payload(),
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 201, f"Unexpected status code {resp.status_code} for valid create"
        # Response body may be empty or contain created resource info
        data = resp.json() if resp.content else {}
        # Try to get the id from response if available
        if "id" in data:
            created_workstream_id = data["id"]
        else:
            # Fallback: get id by listing workstreams with filter by name
            list_resp = requests.get(
                f"{BASE_URL}/api/workstream/?search={unique_name}",
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            assert list_resp.status_code == 200
            items = list_resp.json()
            found = next((item for item in items if item["name"] == unique_name), None)
            assert found is not None, "Created workstream not found in list"
            created_workstream_id = found["id"]

        # 2. Validation errors - Missing required fields
        for missing_field in ["name", "manager_id", "max_user"]:
            payload = valid_payload()
            payload.pop(missing_field)
            resp = requests.post(
                f"{BASE_URL}/api/workstream/",
                json=payload,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            assert resp.status_code == 400, f"Expected 400 for missing {missing_field}, got {resp.status_code}"
            error_json = resp.json()
            assert missing_field in error_json or any(missing_field in str(v).lower() for v in error_json.values()), "Missing field error not in response"

        # 3. Validation error - max_user minimum value (should be >= 1)
        payload = valid_payload()
        payload["max_user"] = 0
        resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=payload,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 400, f"Expected 400 for max_user=0, got {resp.status_code}"
        error_json = resp.json()
        assert "max_user" in error_json or any("max_user" in str(v).lower() for v in error_json.values())

        # 4. Unauthorized access - no token
        resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=valid_payload(),
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 401

        # 5. Forbidden access - token of non-SuperAdmin (simulate with invalid token)
        resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=valid_payload(),
            headers={"Authorization": "Bearer invalid_or_non_superadmin_token", "Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 403

        # 6. Manager not found (use a manager_id that likely does not exist)
        payload = valid_payload()
        payload["manager_id"] = 9999999
        resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=payload,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 404

    finally:
        # Cleanup created resource if any
        if created_workstream_id is not None:
            try:
                delete_workstream(created_workstream_id)
            except Exception:
                pass


test_create_new_workstream_with_validation()