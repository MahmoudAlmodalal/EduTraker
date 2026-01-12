import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30

def get_admin_token():
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()['tokens']['access']

def test_portal_user_registration():
    # Test that registration requires password_confirm and it must match password
    
    register_url = f"{BASE_URL}/api/portal/auth/register/"
    headers = {"Content-Type": "application/json"}
    
    # Case 1: Missing password_confirm field -> expect failure (400)
    payload_missing_confirm = {
        "username": "testuser_missing_confirm",
        "email": "testuser_missing_confirm@test.com",
        "password": "StrongPass123!"
    }
    resp = requests.post(register_url, json=payload_missing_confirm, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 400, f"Expected 400 when password_confirm missing, got {resp.status_code}"
    
    # Case 2: password_confirm does not match password -> expect failure (400)
    payload_mismatch_confirm = {
        "username": "testuser_mismatch_confirm",
        "email": "testuser_mismatch_confirm@test.com",
        "password": "StrongPass123!",
        "password_confirm": "WrongPass123!"
    }
    resp = requests.post(register_url, json=payload_mismatch_confirm, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 400, f"Expected 400 when password_confirm mismatches, got {resp.status_code}"
    
    # Case 3: Correct registration with matching password and password_confirm -> expect success (201 or 200)
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"testuser_success_{unique_suffix}"
    email = f"{username}@test.com"
    password = "StrongPass123!"
    payload_valid = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password
    }
    
    created_user_id = None
    try:
        resp = requests.post(register_url, json=payload_valid, headers=headers, timeout=TIMEOUT)
        assert resp.status_code in (200, 201), f"Expected 201 or 200 on successful registration, got {resp.status_code}"
        data = resp.json()
        
        # Check that response contains user info and possibly tokens if applicable
        assert "id" in data, "Response JSON should include 'id' for created user"
        created_user_id = data["id"]
        assert data.get("username") == username, "Returned username does not match"
        assert data.get("email") == email, "Returned email does not match"
        
    finally:
        # Cleanup: delete the created user if exists
        if created_user_id:
            # Admin token required for deletion
            admin_token = get_admin_token()
            delete_url = f"{BASE_URL}/api/users/{created_user_id}/"
            delete_headers = {
                "Authorization": f"Bearer {admin_token}"
            }
            try:
                del_resp = requests.delete(delete_url, headers=delete_headers, timeout=TIMEOUT)
                # Accept 204 (No content) or 200 as successful deletion
                assert del_resp.status_code in (200, 204), f"User deletion failed with status {del_resp.status_code}"
            except Exception:
                pass

test_portal_user_registration()
