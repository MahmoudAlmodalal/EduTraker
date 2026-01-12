import requests

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/api/portal/auth/register/"
LOGIN_URL = f"{BASE_URL}/api/portal/auth/login/"

ADMIN_AUTH = ("admin@test.com", "test1234")
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}


def test_portal_user_registration():
    # Test data for registration with matching passwords (success case)
    user_data_success = {
        "email": "testuser_success@example.com",
        "full_name": "Test User Success",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "role": "student"
    }

    # Test data for registration with mismatched passwords (error case)
    user_data_error = {
        "email": "testuser_error@example.com",
        "full_name": "Test User Error",
        "password": "StrongPass123!",
        "password_confirm": "WrongPass123!",
        "role": "student"
    }

    # Helper to delete created user if registration succeeded
    def delete_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            requests.delete(url, headers=headers, timeout=TIMEOUT)
        except Exception:
            pass

    # 1. Register user with matching passwords - expect success and user object returned
    response_success = requests.post(REGISTER_URL, json=user_data_success, timeout=TIMEOUT)
    assert response_success.status_code == 201 or response_success.status_code == 200, f"Expected 201 or 200, got {response_success.status_code}"
    resp_json = response_success.json()
    assert "user" in resp_json, "Response JSON should contain 'user' object"
    user = resp_json["user"]
    assert user.get("full_name") == user_data_success["full_name"], "Registered user's full_name does not match"

    # Cleanup: Login as admin to get access token for deleting the created user
    admin_login_resp = requests.post(LOGIN_URL, json={"email": ADMIN_AUTH[0], "password": ADMIN_AUTH[1]}, timeout=TIMEOUT)
    assert admin_login_resp.status_code == 200, "Admin login failed"
    admin_access_token = admin_login_resp.json()['tokens']['access']

    user_id = user.get("id")
    assert user_id is not None, "Registered user ID is missing"
    try:
        # 2. Register user with mismatched password_confirm - expect validation error
        response_error = requests.post(REGISTER_URL, json=user_data_error, timeout=TIMEOUT)
        # Expect 400 Bad Request or similar client error
        assert response_error.status_code == 400 or response_error.status_code == 422, f"Expected 400 or 422 for mismatched passwords, got {response_error.status_code}"
        error_json = response_error.json()
        # Check error message refers to password mismatch
        error_msgs = str(error_json).lower()
        assert "password" in error_msgs and ("confirm" in error_msgs or "match" in error_msgs), "Error message should mention password confirmation mismatch"
    finally:
        # Delete the successfully created user to keep test environment clean
        delete_user(admin_access_token, user_id)


test_portal_user_registration()