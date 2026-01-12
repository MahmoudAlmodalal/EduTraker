import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30


def test_user_list_retrieval():
    # Step 1: Login as admin to get JWT access token
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
    access_token = login_response.json().get("tokens", {}).get("access")
    assert access_token, "Access token not found in login response"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Step 2: Get user list
    users_url = f"{BASE_URL}/api/users/"
    users_response = requests.get(users_url, headers=headers, timeout=TIMEOUT)

    # Assert the GET was successful
    assert users_response.status_code == 200, f"Failed to list users: {users_response.text}"

    users_data = users_response.json()
    assert isinstance(users_data, list), "User list response is not a list"

    # Step 3: Verify role-based access control by checking user roles exist and consistent
    # Since the test case doesn't specify particular users or roles to verify,
    # we will ensure at least one user exists and each user has a 'role' field.

    if users_data:
        for user in users_data:
            assert "id" in user, "User object missing 'id'"
            assert "email" in user, "User object missing 'email'"
            assert "role" in user, "User object missing 'role'"
            # roles should be string and not empty
            assert isinstance(user["role"], str) and user["role"], "User role invalid"
    else:
        # It's valid that users list could be empty if no users
        # But we expect admin user present so at least one user returned
        raise AssertionError("User list is empty; expected at least the admin user.")

    # Step 4: Try to perform user list retrieval without auth or with invalid token to verify RBAC
    unauthorized_response = requests.get(users_url, timeout=TIMEOUT)
    assert unauthorized_response.status_code in (401, 403), "Unauthorized access should be denied"

    invalid_headers = {
        "Authorization": "Bearer invalid.token.here"
    }
    invalid_token_response = requests.get(users_url, headers=invalid_headers, timeout=TIMEOUT)
    assert invalid_token_response.status_code in (401, 403), "Access with invalid token should be denied"


test_user_list_retrieval()