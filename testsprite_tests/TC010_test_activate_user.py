import requests

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin@test.com"
AUTH_PASSWORD = "test1234"
TIMEOUT = 30


def test_activate_user():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    # Obtain JWT token from portal login
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    login_payload = {
        "email": AUTH_USERNAME,
        "password": AUTH_PASSWORD
    }
    login_resp = session.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    tokens = login_resp.json()
    access_token = tokens.get("access") or tokens.get("access_token") or tokens.get("accessToken")
    assert access_token, "Access token not found in login response"

    session.headers.update({"Authorization": f"Bearer {access_token}"})

    user_create_url = f"{BASE_URL}/api/users/create/"
    user_deactivate_url_template = f"{BASE_URL}/api/users/{{user_id}}/deactivate/"
    user_activate_url_template = f"{BASE_URL}/api/users/{{user_id}}/activate/"
    user_detail_url_template = f"{BASE_URL}/api/users/{{user_id}}/"

    # Step 1: Create a new user to test activation
    user_payload = {
        "email": "test_activate_user@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "ActivateUser",
        "role": "Student"
    }

    user_id = None
    try:
        create_resp = session.post(user_create_url, json=user_payload, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
        user_data = create_resp.json()
        user_id = user_data.get("id")
        assert user_id, "Created user ID not found in response"

        # Step 2: Deactivate the user
        deactivate_url = user_deactivate_url_template.format(user_id=user_id)
        deactivate_resp = session.post(deactivate_url, timeout=TIMEOUT)
        assert deactivate_resp.status_code == 200, f"User deactivation failed: {deactivate_resp.text}"

        # Step 3: Verify the user can access (admin checking user detail should work)
        get_user_resp = session.get(user_detail_url_template.format(user_id=user_id), timeout=TIMEOUT)
        assert get_user_resp.status_code == 200, "Failed to access user detail after deactivation (unexpected)"

        # Step 4: Activate the user
        activate_url = user_activate_url_template.format(user_id=user_id)
        activate_resp = session.post(activate_url, timeout=TIMEOUT)
        assert activate_resp.status_code == 200, f"User activation failed: {activate_resp.text}"

        # Step 5: Verify the user is active by checking user details again
        check_resp = session.get(user_detail_url_template.format(user_id=user_id), timeout=TIMEOUT)
        assert check_resp.status_code == 200, f"Failed to get user details after activation: {check_resp.text}"
        user_info = check_resp.json()
        is_active = user_info.get("is_active")
        assert is_active is True, "User is not active after activation"

    finally:
        # Cleanup: delete the created user
        if user_id:
            delete_url = f"{BASE_URL}/api/users/{user_id}/"
            session.delete(delete_url, timeout=TIMEOUT)


test_activate_user()
