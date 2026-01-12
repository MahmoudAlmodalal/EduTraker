import requests

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin@test.com"
AUTH_PASSWORD = "test1234"
TIMEOUT = 30


def get_jwt_token(username, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"email": username, "password": password}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    token = data.get("access") or data.get("token")
    assert token is not None, "Access token not found in login response"
    return token


def test_update_user_details():
    token = get_jwt_token(AUTH_USERNAME, AUTH_PASSWORD)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # Step 1: Create a new user to update
    create_payload = {
        "email": "tempuser@example.com",
        "password": "TempPass123!",
        "first_name": "Temp",
        "last_name": "User",
        "roles": []  # Assuming roles can be empty or default roles assigned
    }
    try:
        create_resp = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=create_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
        user_data = create_resp.json()
        user_id = user_data.get("id")
        assert user_id is not None, "Created user ID not returned"

        # Step 2: Partially update user details via PATCH
        update_payload = {
            "first_name": "UpdatedName",
            "last_name": "UpdatedLastName"
        }
        patch_resp = requests.patch(
            f"{BASE_URL}/api/users/{user_id}/",
            json=update_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert patch_resp.status_code == 200, f"User update failed: {patch_resp.text}"
        updated_data = patch_resp.json()
        for key, val in update_payload.items():
            assert updated_data.get(key) == val, f"Field {key} not updated correctly"

        # Step 3: Retrieve the user to verify persistence of changes
        get_resp = requests.get(
            f"{BASE_URL}/api/users/{user_id}/",
            headers=headers,
            timeout=TIMEOUT,
        )
        assert get_resp.status_code == 200, f"Fetching user failed: {get_resp.text}"
        fetched_user = get_resp.json()
        for key, val in update_payload.items():
            assert fetched_user.get(key) == val, f"Persisted field {key} mismatch"

    finally:
        # Cleanup: Delete the created user if exists
        if 'user_id' in locals():
            requests.delete(
                f"{BASE_URL}/api/users/{user_id}/",
                headers=headers,
                timeout=TIMEOUT,
            )


test_update_user_details()
