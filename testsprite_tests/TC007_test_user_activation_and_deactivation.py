import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30

def test_user_activation_and_deactivation():
    # Authenticate as admin to get JWT access token
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    access_token = login_resp.json()['tokens']['access']
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Create a new user (to activate/deactivate)
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    user_create_url = f"{BASE_URL}/api/users/create/"
    user_payload = {
        "email": unique_email,
        "full_name": "Test User Activation",
        "password": "TestPass123!",
        "role": "student"
    }
    user_create_resp = requests.post(user_create_url, json=user_payload, headers=headers, timeout=TIMEOUT)
    assert user_create_resp.status_code == 201, f"User creation failed: {user_create_resp.text}"
    user_id = user_create_resp.json().get("id")
    assert user_id is not None, "User ID not returned on creation"

    try:
        activate_url = f"{BASE_URL}/api/users/{user_id}/activate/"
        deactivate_url = f"{BASE_URL}/api/users/{user_id}/deactivate/"

        # Deactivate user first to ensure known state
        deactivate_resp = requests.post(deactivate_url, headers=headers, timeout=TIMEOUT)
        assert deactivate_resp.status_code == 200, f"User deactivation failed: {deactivate_resp.text}"
        # Confirm user is inactive
        user_get_resp = requests.get(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
        assert user_get_resp.status_code == 200, f"Fetching user failed: {user_get_resp.text}"
        user_data = user_get_resp.json()
        assert user_data.get("is_active") is False, "User should be inactive after deactivation"

        # Activate user
        activate_resp = requests.post(activate_url, headers=headers, timeout=TIMEOUT)
        assert activate_resp.status_code == 200, f"User activation failed: {activate_resp.text}"
        # Confirm user is active
        user_get_resp = requests.get(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
        assert user_get_resp.status_code == 200, f"Fetching user failed: {user_get_resp.text}"
        user_data = user_get_resp.json()
        assert user_data.get("is_active") is True, "User should be active after activation"

        # Deactivate again to verify toggle works both ways
        deactivate_resp = requests.post(deactivate_url, headers=headers, timeout=TIMEOUT)
        assert deactivate_resp.status_code == 200, f"User deactivation failed: {deactivate_resp.text}"
        # Confirm user is inactive again
        user_get_resp = requests.get(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
        assert user_get_resp.status_code == 200, f"Fetching user failed: {user_get_resp.text}"
        user_data = user_get_resp.json()
        assert user_data.get("is_active") is False, "User should be inactive after second deactivation"

    finally:
        # Cleanup: deactivate the created user instead of delete
        deactivate_url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
        del_resp = requests.post(deactivate_url, headers=headers, timeout=TIMEOUT)
        assert del_resp.status_code == 200, f"User deactivation (cleanup) failed: {del_resp.text}"

test_user_activation_and_deactivation()
