import requests

BASE_URL = "http://localhost:8000"
ADMIN_AUTH = ("admin@test.com", "test1234")
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30


def test_workstream_user_login():
    # Helper function to handle admin auth and get token
    def admin_login():
        response = requests.post(
            f"{BASE_URL}/api/portal/auth/login/",
            json={"email": ADMIN_AUTH[0], "password": ADMIN_AUTH[1]},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        tokens = response.json().get("tokens")
        assert tokens and "access" in tokens and "refresh" in tokens
        return tokens["access"]

    # Helper to get admin user id
    def get_admin_user_id(admin_token):
        headers = dict(HEADERS)
        headers["Authorization"] = f"Bearer {admin_token}"
        response = requests.get(f"{BASE_URL}/api/users/", headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        users = response.json()
        admin_user = next((u for u in users if u.get("email") == ADMIN_AUTH[0]), None)
        assert admin_user and "id" in admin_user, "Admin user not found"
        return admin_user["id"]

    # Create a workstream user to login with
    def create_workstream_user(workstream_id, admin_token):
        user_data = {
            "email": "workstream_user_login_test@example.com",
            "full_name": "Workstream User Login Test",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "role": "teacher",
            "work_stream": workstream_id
        }
        headers = dict(HEADERS)
        headers["Authorization"] = f"Bearer {admin_token}"
        response = requests.post(
            f"{BASE_URL}/api/workstream/{workstream_id}/auth/register/",
            json=user_data,
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        user = response.json().get("user")
        assert user and "full_name" in user
        return user_data["email"], user_data["password"]

    admin_token = None
    admin_user_id = None
    workstream_id = None
    user_email = None
    user_password = None

    try:
        # Admin login to get token for further creations
        admin_token = admin_login()
        admin_user_id = get_admin_user_id(admin_token)

        # Create workstream with admin user as manager
        workstream_data = {
            "name": "Test Workstream TC004",
            "manager_id": admin_user_id,
            "max_user": 10,
        }
        headers = dict(HEADERS)
        headers["Authorization"] = f"Bearer {admin_token}"
        response = requests.post(
            f"{BASE_URL}/api/workstream/", json=workstream_data, headers=headers, timeout=TIMEOUT
        )
        response.raise_for_status()
        ws = response.json()
        assert ws and "id" in ws
        workstream_id = ws["id"]

        # Create a workstream user to login
        user_email, user_password = create_workstream_user(workstream_id, admin_token)

        # Now perform login via /api/workstream/{workstream_id}/auth/login/
        login_data = {"email": user_email, "password": user_password}
        response = requests.post(
            f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/",
            json=login_data,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        tokens = response.json().get("tokens")
        assert tokens is not None, "Response should contain 'tokens' object"
        assert "access" in tokens and "refresh" in tokens, "'tokens' must have 'access' and 'refresh'"
        access_token = tokens["access"]
        assert isinstance(access_token, str) and len(access_token) > 0, "Access token should be a non-empty string"

    finally:
        # Cleanup: delete the created workstream user and workstream if possible
        headers = {}
        if admin_token:
            headers["Authorization"] = f"Bearer {admin_token}"

        # Delete workstream user
        if user_email and admin_token:
            try:
                resp_users = requests.get(
                    f"{BASE_URL}/api/users/", headers=headers, timeout=TIMEOUT
                )
                resp_users.raise_for_status()
                users = resp_users.json()
                user_to_delete = next((u for u in users if u.get("email") == user_email), None)
                if user_to_delete and "id" in user_to_delete:
                    requests.delete(
                        f"{BASE_URL}/api/users/{user_to_delete['id']}/",
                        headers=headers,
                        timeout=TIMEOUT,
                    )
            except Exception:
                pass

        # Delete workstream
        if workstream_id and admin_token:
            try:
                requests.post(
                    f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/",
                    headers=headers,
                    timeout=TIMEOUT,
                )
                requests.delete(
                    f"{BASE_URL}/api/workstreams/{workstream_id}/",
                    headers=headers,
                    timeout=TIMEOUT,
                )
            except Exception:
                pass


test_workstream_user_login()
