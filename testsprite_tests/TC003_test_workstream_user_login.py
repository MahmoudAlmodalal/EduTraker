import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASSWORD = 'test1234'


def get_admin_token():
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    resp = requests.post(login_url, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    data = resp.json()
    tokens = data.get('tokens')
    assert tokens is not None and 'access' in tokens, "Admin tokens missing after login"
    return tokens['access']


def test_workstream_user_login():
    admin_access_token = get_admin_token()
    headers_admin = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {admin_access_token}'
    }

    user_manager_workstream = None
    workstream = None

    try:
        # 1. Create a user with role 'manager_workstream'
        user_data = {
            "email": "manager_workstream_test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "role": "manager_workstream",
            "first_name": "Manager",
            "last_name": "Workstream",
            "full_name": "Manager Workstream"
        }
        resp_user = requests.post(f"{BASE_URL}/api/users/create/", json=user_data, headers=headers_admin, timeout=TIMEOUT)
        assert resp_user.status_code == 201, f"User creation failed: {resp_user.text}"
        user_manager_workstream = resp_user.json()
        manager_id = user_manager_workstream.get("id")
        assert manager_id is not None, "Manager ID not found in user creation response"

        # 2. Create a Workstream using this manager_id
        workstream_data = {
            "name": "Test Workstream",
            "manager_id": manager_id,
            "description": "Workstream for testing user login"
        }
        resp_ws = requests.post(f"{BASE_URL}/api/workstream/", json=workstream_data, headers=headers_admin, timeout=TIMEOUT)
        assert resp_ws.status_code == 201, f"Workstream creation failed: {resp_ws.text}"
        workstream = resp_ws.json()
        workstream_id = workstream.get("id")
        assert workstream_id is not None, "Workstream ID not found in creation response"

        # 3. Attempt login to workstream auth endpoint
        login_url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
        login_payload = {
            "email": user_manager_workstream["email"],
            "password": user_data["password"]  # use original password
        }
        resp_login = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert resp_login.status_code == 200, f"Workstream login failed: {resp_login.text}"

        login_response_json = resp_login.json()
        assert "tokens" in login_response_json, "'tokens' not found in login response"
        tokens = login_response_json["tokens"]
        assert isinstance(tokens, dict), "'tokens' is not an object"
        assert "access" in tokens and "refresh" in tokens, "'access' or 'refresh' token missing in 'tokens'"
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        assert isinstance(access_token, str) and len(access_token) > 0, "Invalid access token"
        assert isinstance(refresh_token, str) and len(refresh_token) > 0, "Invalid refresh token"

    finally:
        # Cleanup: Delete workstream and user if created
        if workstream:
            _ = requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=headers_admin, timeout=TIMEOUT)
        if user_manager_workstream:
            user_id = user_manager_workstream.get("id")
            if user_id:
                _ = requests.delete(f"{BASE_URL}/api/users/{user_id}/", headers=headers_admin, timeout=TIMEOUT)


test_workstream_user_login()