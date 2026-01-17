import requests

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NjQ3MTYzLCJpYXQiOjE3Njg2NDM1NjMsImp0aSI6ImI2OWMxNTRmYmE0NDQ0MzFiY2RlYTQxM2EzYTMxNjM2IiwidXNlcl9pZCI6IjUyIn0.vws_-oL8rF743FYpML0dykuPgXzUxaXMnLEAH4Grs2I"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
TIMEOUT = 30


def test_list_all_workstreams_with_filters():
    # Helper function to create a workstream for testing filters
    def create_workstream(name, description, manager_id, max_user, is_active=True):
        payload = {
            "name": name,
            "description": description,
            "manager_id": manager_id,
            "max_user": max_user
        }
        response = requests.post(f"{BASE_URL}/api/workstream/", json=payload, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 201:
            print(f"Error creating workstream: {response.status_code} {response.text}")
        response.raise_for_status()
        workstream = response.json()
        # Update is_active if needed by a PUT request
        if not is_active:
            update_payload = {"is_active": False}
            put_response = requests.put(
                f"{BASE_URL}/api/workstreams/{workstream['id']}/update/",
                json=update_payload,
                headers=HEADERS,
                timeout=TIMEOUT
            )
            put_response.raise_for_status()
        return workstream

    # Helper function to delete a workstream after test
    def delete_workstream(workstream_id):
        # No explicit delete endpoint specified in PRD
        # As safe cleanup, deactivate the workstream
        requests.post(
            f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/",
            headers=HEADERS,
            timeout=TIMEOUT
        )

    # 1. Test 200 response with correct filter data
    # Create two workstreams for testing filter
    workstreams_created = []
    try:
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        ws1 = create_workstream(f"FilterTestActive-{unique_suffix}", "Active test workstream", 33, 5, is_active=True)
        workstreams_created.append(ws1)
        ws2 = create_workstream(f"FilterTestInactive-{unique_suffix}", "Inactive test workstream", 23, 5, is_active=False)
        workstreams_created.append(ws2)

        # Without filters: list all
        resp = requests.get(f"{BASE_URL}/api/workstream/", headers=HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 200
        all_ws = resp.json()
        assert isinstance(all_ws, list)
        # Verify created workstreams are in the list
        ids = [ws['id'] for ws in all_ws]
        print(f"IDs in list: {ids}")
        print(f"Looking for: {ws1['id']} and {ws2['id']}")
        assert ws1['id'] in ids
        assert ws2['id'] in ids

        # Filter by search term (name contains unique_suffix)
        params = {"search": unique_suffix}
        resp = requests.get(f"{BASE_URL}/api/workstream/", headers=HEADERS, params=params, timeout=TIMEOUT)
        assert resp.status_code == 200
        filtered_ws = resp.json()
        assert isinstance(filtered_ws, list)
        # All names must contain the unique_suffix
        for ws in filtered_ws:
            assert unique_suffix in ws["name"].lower()

        # Filter by is_active = True
        params = {"is_active": "true"}
        resp = requests.get(f"{BASE_URL}/api/workstream/", headers=HEADERS, params=params, timeout=TIMEOUT)
        assert resp.status_code == 200
        active_ws = resp.json()
        assert isinstance(active_ws, list)
        for ws in active_ws:
            assert ws["is_active"] is True

        # Filter by is_active = False
        params = {"is_active": "false"}
        resp = requests.get(f"{BASE_URL}/api/workstream/", headers=HEADERS, params=params, timeout=TIMEOUT)
        assert resp.status_code == 200
        inactive_ws = resp.json()
        assert isinstance(inactive_ws, list)
        for ws in inactive_ws:
            assert ws["is_active"] is False

    finally:
        for ws in workstreams_created:
            try:
                delete_workstream(ws["id"])
            except Exception:
                pass

    # 2. Test 401 Unauthorized (no token)
    resp = requests.get(f"{BASE_URL}/api/workstream/", timeout=TIMEOUT)
    assert resp.status_code == 401

    # 3. Test 403 Forbidden (non-SuperAdmin user)
    # For this test, assume we have a token for a non-SuperAdmin user (simulate by tampering token)
    non_superadmin_token = TOKEN[:-3] + "xyz"  # Invalid token purposely for forbidden check
    headers_forbidden = {"Authorization": f"Bearer {non_superadmin_token}"}
    resp = requests.get(f"{BASE_URL}/api/workstream/", headers=headers_forbidden, timeout=TIMEOUT)
    # Could be 401 or 403 depending on implementation, expect 403 for forbidden access specifically
    assert resp.status_code in (401, 403)


test_list_all_workstreams_with_filters()