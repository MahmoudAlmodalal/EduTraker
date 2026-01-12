import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30

def test_user_activation():
    session = requests.Session()

    # Step 1: Admin login to get access token
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_resp = session.post(f"{BASE_URL}/api/portal/auth/login/", json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    access_token = login_resp.json()['tokens']['access']
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Create a new user (inactive by default)
    user_payload = {
        "email": "activatetestuser@example.com",
        "full_name": "Activate Test User",
        "password": "TestUserPass123!",
        "role": "student"
    }
    create_resp = session.post(f"{BASE_URL}/api/users/create/", json=user_payload, headers=headers, timeout=TIMEOUT)
    assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
    user = create_resp.json()
    user_id = user['id']

    try:
        # Step 3: Activate the user via /api/users/{user_id}/activate/
        activate_resp = session.post(f"{BASE_URL}/api/users/{user_id}/activate/", headers=headers, timeout=TIMEOUT)
        assert activate_resp.status_code == 200, f"User activation failed: {activate_resp.text}"

        # Step 4: Verify response content for success indication
        activate_json = activate_resp.json()
        assert 'detail' in activate_json or 'message' in activate_json, "Activation success message missing"
        # Optionally check that user is now active via GET user
        get_resp = session.get(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"User retrieval failed after activation: {get_resp.text}"
        user_details = get_resp.json()
        assert user_details.get('is_active') is True or user_details.get('active') is True, "User not active after activation"
    finally:
        # Cleanup: Delete the created user
        delete_resp = session.delete(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
        assert delete_resp.status_code in (200, 204), f"User deletion failed: {delete_resp.text}"

test_user_activation()
