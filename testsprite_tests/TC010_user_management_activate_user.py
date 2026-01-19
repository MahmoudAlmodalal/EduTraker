import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ROLES = {
    "student": {
        "login_path": "/api/workstream/{workstream_id}/auth/login/",
        "credentials": {"email": "student@test.com", "password": "studentpass"},
        "workstream_id": "1"
    },
    "teacher": {
        "login_path": "/api/workstream/{workstream_id}/auth/login/",
        "credentials": {"email": "teacher@test.com", "password": "teacherpass"},
        "workstream_id": "1"
    },
    "secretary": {
        "login_path": "/api/workstream/{workstream_id}/auth/login/",
        "credentials": {"email": "secretary@test.com", "password": "secretarypass"},
        "workstream_id": "1"
    },
    "manager_school": {
        "login_path": "/api/portal/auth/login/",
        "credentials": {"email": "manager_school@test.com", "password": "managerschoolpass"}
    },
    "manager_workstream": {
        "login_path": "/api/portal/auth/login/",
        "credentials": {"email": "manager_workstream@test.com", "password": "managerworkstreampass"}
    },
    "guardian": {
        "login_path": "/api/workstream/{workstream_id}/auth/login/",
        "credentials": {"email": "guardian@test.com", "password": "guardianpass"},
        "workstream_id": "1"
    },
    "admin": {
        "login_path": "/api/portal/auth/login/",
        "credentials": {"email": "admin@test.com", "password": "test1234"}
    },
    "guest": {
        # Guests typically must register first; here we assume existing guest credentials for test
        "login_path": "/api/portal/auth/login/",
        "credentials": {"email": "guest@test.com", "password": "guestpass"}
    }
}

def login(role):
    role_info = ROLES[role]
    url = BASE_URL + role_info["login_path"]
    if "{workstream_id}" in url:
        url = url.format(workstream_id=role_info["workstream_id"])
    resp = requests.post(url, json=role_info["credentials"], timeout=TIMEOUT)
    if resp.status_code == 200:
        tokens = resp.json()
        access = tokens.get("access")
        refresh = tokens.get("refresh")
        assert access, f"Login success but no access token received for role '{role}'"
        assert refresh, f"Login success but no refresh token received for role '{role}'"
        return access
    elif resp.status_code in (401, 403):
        return None
    else:
        resp.raise_for_status()

def create_user(admin_token):
    url = f"{BASE_URL}/api/users/create/"
    unique_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "email": unique_email,
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 201, f"User creation failed: {resp.status_code} {resp.text}"
    data = resp.json()
    if "id" in data:
        return data["id"]
    elif "user" in data and "id" in data["user"]:
        return data["user"]["id"]
    else:
        assert False, "User ID not found in creation response"

def delete_user(admin_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Deactivate before deletion if API supports deletion, else skip.
    # Since no delete API is specified, deactivate for cleanup
    requests.post(url, headers=headers, timeout=TIMEOUT)

def test_user_management_activate_user():
    """
    Test POST /api/users/{id}/activate/ endpoint with all roles for RBAC and response validation.
    """
    # Login admin to create a test user and to cleanup
    admin_token = login("admin")
    assert admin_token, "Admin login failed; cannot proceed with user creation."

    # Create a user to activate
    user_id = None
    try:
        user_id = create_user(admin_token)
        assert user_id, "Failed to retrieve created user ID."

        url = f"{BASE_URL}/api/users/{user_id}/activate/"

        for role, role_info in ROLES.items():
            access_token = login(role)
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            resp = requests.post(url, headers=headers, timeout=TIMEOUT)

            if role in ("admin", "manager_school", "manager_workstream"):
                # These roles are expected to be authorized
                assert resp.status_code == 204, f"Role '{role}' expected 204 but got {resp.status_code}"
                # No content means empty body
                assert resp.text == "", f"Role '{role}' expected empty body but got: {resp.text}"
            else:
                # Other roles expected to be unauthorized
                assert resp.status_code in (401, 403), (
                    f"Role '{role}' expected 401/403 but got {resp.status_code}"
                )
                # Response JSON may contain detail message
                try:
                    detail = resp.json().get("detail", "").lower()
                    assert "not found" not in detail, "Unexpected 'not found' message in unauthorized response"
                except Exception:
                    pass
    finally:
        if user_id:
            # cleanup: deactivate user
            delete_user(admin_token, user_id)

test_user_management_activate_user()
