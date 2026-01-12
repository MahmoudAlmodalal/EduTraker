import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30


def get_admin_token():
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    resp = requests.post(login_url, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    data = resp.json()
    token = data.get("access")
    assert token, "Admin access token missing"
    return token


def test_deactivate_user():
    token = get_admin_token()
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    # Step 1: Create a new user to deactivate
    create_user_url = f"{BASE_URL}/api/users/create/"
    create_payload = {
        "email": "tempuser@example.com",
        "password": "TempPass123!",
        "first_name": "Temp",
        "last_name": "User",
        "role": "Teacher"
    }
    user_id = None

    try:
        create_resp = requests.post(create_user_url, json=create_payload, headers=headers, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
        user_data = create_resp.json()
        user_id = user_data.get("id")
        assert user_id is not None, "Created user ID missing"

        # Step 2: Deactivate the created user
        deactivate_url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
        deactivate_resp = requests.post(deactivate_url, headers=headers, timeout=TIMEOUT)
        assert deactivate_resp.status_code == 200, f"User deactivation failed: {deactivate_resp.text}"

        # Step 3: Try to access a protected resource as the deactivated user (login attempt)
        login_url = f"{BASE_URL}/api/portal/auth/login/"
        login_payload = {"email": create_payload["email"], "password": create_payload["password"]}
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        # Expect login failure due to deactivated status
        assert login_resp.status_code in (401, 403), \
            f"Deactivated user should not be able to login, but got: {login_resp.status_code}"

    finally:
        # Cleanup - delete the user if it was created
        if user_id:
            delete_url = f"{BASE_URL}/api/users/{user_id}/"
            delete_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
            assert delete_resp.status_code in (200, 204), f"User cleanup failed: {delete_resp.status_code} {delete_resp.text}"


test_deactivate_user()
