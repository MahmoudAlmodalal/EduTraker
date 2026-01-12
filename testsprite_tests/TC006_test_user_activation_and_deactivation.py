import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_user_activation_and_deactivation():
    session = requests.Session()

    def login(username, password):
        url = f"{BASE_URL}/api/portal/auth/login/"
        payload = {"username": username, "password": password}
        resp = session.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()['tokens']['access']

    def create_user(access_token, role):
        url = f"{BASE_URL}/api/users/create/"
        user_data = {
            "email": f"temp_{role}_user@test.com",
            "password": "Password123!",
            "password_confirm": "Password123!",
            "role": role,
            "first_name": "Temp",
            "last_name": f"{role.capitalize()}User",
            "is_active": True
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = session.post(url, json=user_data, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def get_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = session.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def activate_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/activate/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = session.post(url, headers=headers, timeout=TIMEOUT)
        return resp

    def deactivate_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = session.post(url, headers=headers, timeout=TIMEOUT)
        return resp

    def delete_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = session.delete(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code not in [204, 200]:
            resp.raise_for_status()

    admin_access_token = login("admin@test.com", "test1234")

    # Create a test user with role "teacher" who will be activated/deactivated
    test_user = create_user(admin_access_token, "teacher")
    test_user_id = test_user["id"]

    try:
        # Confirm the user is active by default
        user_info = get_user(admin_access_token, test_user_id)
        assert user_info["is_active"] is True

        # Deactivate user
        resp_deactivate = deactivate_user(admin_access_token, test_user_id)
        assert resp_deactivate.status_code == 200 or resp_deactivate.status_code == 204

        # Check user is inactive
        user_info = get_user(admin_access_token, test_user_id)
        assert user_info["is_active"] is False

        # Activate user
        resp_activate = activate_user(admin_access_token, test_user_id)
        assert resp_activate.status_code == 200 or resp_activate.status_code == 204

        # Check user is active again
        user_info = get_user(admin_access_token, test_user_id)
        assert user_info["is_active"] is True

        # Role-based access control check:
        # Create a user with limited role (e.g. "teacher") and attempt to deactivate another user
        limited_user = create_user(admin_access_token, "teacher")
        limited_user_id = limited_user["id"]
        limited_token = login(limited_user["email"], "Password123!")

        # Limited user tries to deactivate test_user, expect forbidden or unauthorized
        resp_forbidden = deactivate_user(limited_token, test_user_id)
        assert resp_forbidden.status_code in [401, 403]

    finally:
        # Clean up users
        delete_user(admin_access_token, test_user_id)
        if 'limited_user_id' in locals():
            delete_user(admin_access_token, limited_user_id)

test_user_activation_and_deactivation()