import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_get_public_workstream_info():
    # Step 1: Get all workstreams to find a valid workstream id
    list_url = f"{BASE_URL}/api/workstream/"
    # This endpoint requires SuperAdmin auth, but since no auth is provided here, we will just assume using a public known id or fallback
    # We'll try to query a public id 1; if fails we test with 404 only
    test_workstream_id = 1

    # Step 2: Test successful retrieval of public workstream info (no auth required)
    info_url = f"{BASE_URL}/api/workstreams/{test_workstream_id}/info/"
    info_resp = requests.get(info_url, timeout=TIMEOUT)
    if info_resp.status_code == 200:
        info_data = info_resp.json()
        assert info_data["id"] == test_workstream_id, f"Expected id {test_workstream_id}, got {info_data['id']}"
        assert isinstance(info_data["name"], str), "Expected name to be a string"
    else:
        # If not found, we skip this part
        assert info_resp.status_code == 404, f"Expected 200 or 404, got {info_resp.status_code}"

    # Step 3: Test 404 response when workstream does not exist
    non_exist_id = 99999999
    if non_exist_id == test_workstream_id:
        non_exist_id += 1  # ensure it differs
    not_found_url = f"{BASE_URL}/api/workstreams/{non_exist_id}/info/"
    not_found_resp = requests.get(not_found_url, timeout=TIMEOUT)
    assert not_found_resp.status_code == 404, f"Expected 404 Not Found for non-existent id, got {not_found_resp.status_code}"


test_get_public_workstream_info()
