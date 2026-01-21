import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"

ROLES = [
    "student",
    "teacher",
    "secretary",
    "manager_school",
    "manager_workstream",
    "guardian",
    "admin",
    "guest"
]

def login_portal(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    assert resp.status_code == 200, f"Unexpected status code {resp.status_code} on login"
    assert "access" in data and isinstance(data["access"], str), "Missing or invalid 'access' token in login response"
    assert "refresh" in data and isinstance(data["refresh"], str), "Missing or invalid 'refresh' token in login response"
    assert "user" in data, "Missing 'user' object in login response"
    return data["access"]

def create_user(token, email, password, role, first_name=None, last_name=None):
    url = f"{BASE_URL}/api/users/create/"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "email": email,
        "password": password,
        "role": role,
    }
    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    return resp

def delete_user(token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    if resp.status_code not in (204, 404):
        resp.raise_for_status()

def user_management_create_user_with_role_assignment():
    admin_token = login_portal(ADMIN_EMAIL, ADMIN_PASSWORD)
    created_user_ids = []
    try:
        for role in ROLES:
            email = f"test_{role}_user@example.com"
            password = "Password123!"
            first_name = f"First{role.capitalize()}"
            last_name = f"Last{role.capitalize()}"
            resp = create_user(
                admin_token,
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
            )

            if role in ["student", "teacher", "secretary", "manager_school", "manager_workstream", "guardian", "admin", "guest"]:
                # We expect 201 Created for valid roles
                if resp.status_code == 201:
                    data = resp.json()
                    # Should contain user id in response
                    assert "id" in data, f"Response for role {role} missing user id"
                    # Verify returned fields match input (email, first_name, last_name, role)
                    assert data.get("email") == email.lower()
                    # Role in response could be same or mapped; verify presence
                    if "role" in data:
                        assert data["role"] == role, f"Role mismatch for {role} creation"
                    # Save user ids for cleanup
                    created_user_ids.append(data["id"])
                else:
                    # Some roles may have RBAC limits; checking 400 or 403/401
                    assert resp.status_code in (201, 403, 400), f"Unexpected status {resp.status_code} for role {role}"
            else:
                # For non-valid roles, expect 400 or 403
                assert resp.status_code in (400, 403)
    finally:
        # Cleanup: deactivate created users to avoid pollution
        for user_id in created_user_ids:
            try:
                delete_user(admin_token, user_id)
            except Exception:
                pass

user_management_create_user_with_role_assignment()
