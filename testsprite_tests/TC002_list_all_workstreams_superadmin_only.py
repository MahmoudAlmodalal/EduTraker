import requests

BASE_URL = "http://localhost:8000/api/"
LOGIN_URL = BASE_URL + "auth/login/"
WORKSTREAM_LIST_URL = BASE_URL + "workstream/"
TIMEOUT = 30

SUPERADMIN_CREDENTIALS = {
    "username": "admin@test.com",
    "password": "test1234"
}

def test_list_all_workstreams_superadmin_only():
    # Helper to login and get access token
    def get_access_token(credentials):
        try:
            resp = requests.post(
                LOGIN_URL,
                json=credentials,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
            assert "tokens" in data and "access" in data["tokens"]
            return data["tokens"]["access"]
        except Exception as e:
            raise AssertionError(f"Login failed: {e}")

    headers_auth = {}
    # 1) Test unauthorized access - no auth header
    try:
        resp = requests.get(WORKSTREAM_LIST_URL, timeout=TIMEOUT)
        # Should return 401 Unauthorized
        assert resp.status_code == 401, f"Expected 401 for unauthorized, got {resp.status_code}"
    except Exception as e:
        raise AssertionError(f"Unauthorized access test failed: {e}")

    # 2) Test forbidden access - auth as non-SuperAdmin user (simulate with invalid token or different user)
    # Since we only have superadmin credentials here, attempt with an invalid token
    headers_invalid = {"Authorization": "Bearer invalidtoken12345"}
    try:
        resp = requests.get(WORKSTREAM_LIST_URL, headers=headers_invalid, timeout=TIMEOUT)
        # Should return 401 or 403 - depending on API implementation; 401 if token invalid, 403 if forbidden
        assert resp.status_code in (401, 403), f"Expected 401 or 403 for invalid token, got {resp.status_code}"
    except Exception as e:
        raise AssertionError(f"Invalid token access test failed: {e}")

    # 3) Test access with valid SuperAdmin token without filters
    access_token = get_access_token(SUPERADMIN_CREDENTIALS)
    headers_auth = {"Authorization": f"Bearer {access_token}"}
    try:
        resp = requests.get(WORKSTREAM_LIST_URL, headers=headers_auth, timeout=TIMEOUT)
        resp.raise_for_status()
        assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
        workstreams = resp.json()
        assert isinstance(workstreams, list), "Response should be a list"
        # Validate fields in first entry if exists
        if workstreams:
            ws = workstreams[0]
            expected_fields = {"id", "name", "description", "manager_id", "max_user", "is_active"}
            assert expected_fields.issubset(ws.keys()), f"Missing expected fields in workstream: {expected_fields - set(ws.keys())}"
    except Exception as e:
        raise AssertionError(f"SuperAdmin access without filters failed: {e}")

    # 4) Test filtering by search term (assumed search string 'test')
    try:
        params = {"search": "test"}
        resp = requests.get(WORKSTREAM_LIST_URL, headers=headers_auth, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        assert resp.status_code == 200, f"Expected 200 OK for search filter, got {resp.status_code}"
        workstreams = resp.json()
        assert isinstance(workstreams, list), "Response with search filter should be a list"
        # Optionally check that returned workstreams have 'test' in name or description (if any results)
        for ws in workstreams:
            name_desc = (ws.get("name", "") + ws.get("description", "")).lower()
            assert "test" in name_desc, f"Workstream does not match search term: {ws}"
    except Exception as e:
        raise AssertionError(f"SuperAdmin access with search filter failed: {e}")

    # 5) Test filtering by is_active status (True)
    try:
        params = {"is_active": "true"}
        resp = requests.get(WORKSTREAM_LIST_URL, headers=headers_auth, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        assert resp.status_code == 200, f"Expected 200 OK for is_active=True filter, got {resp.status_code}"
        workstreams = resp.json()
        assert isinstance(workstreams, list), "Response with is_active filter should be a list"
        for ws in workstreams:
            assert ws.get("is_active") is True, f"Workstream marked inactive when filtering active: {ws}"
    except Exception as e:
        raise AssertionError(f"SuperAdmin access with is_active=True filter failed: {e}")

    # 6) Test filtering by is_active status (False)
    try:
        params = {"is_active": "false"}
        resp = requests.get(WORKSTREAM_LIST_URL, headers=headers_auth, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        assert resp.status_code == 200, f"Expected 200 OK for is_active=False filter, got {resp.status_code}"
        workstreams = resp.json()
        assert isinstance(workstreams, list), "Response with is_active=False filter should be a list"
        for ws in workstreams:
            assert ws.get("is_active") is False, f"Workstream marked active when filtering inactive: {ws}"
    except Exception as e:
        raise AssertionError(f"SuperAdmin access with is_active=False filter failed: {e}")

test_list_all_workstreams_superadmin_only()
