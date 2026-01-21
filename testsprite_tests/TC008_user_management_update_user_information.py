import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ROLES = {
    "student": {"workstream_id": "1"},
    "teacher": {"workstream_id": "1"},
    "secretary": {"workstream_id": "1"},
    "manager_school": {},
    "manager_workstream": {"workstream_id": "1"},
    "guardian": {"workstream_id": "1"},
    "admin": {},
    "guest": {}
}

# Admin and Managers login via /api/portal/auth/login/
PORTAL_LOGIN_ROLES = {"admin", "manager_school", "manager_workstream"}
# Others login via /api/workstream/{workstream_id}/auth/login/
WORKSTREAM_LOGIN_ROLES = {"student", "teacher", "secretary", "guardian", "guest"}

# Credentials for login (using sample emails and password 'test1234')
CREDENTIALS = {
    "admin": {"email": "admin@test.com", "password": "test1234"},
    "manager_school": {"email": "manager_school@test.com", "password": "test1234"},
    "manager_workstream": {"email": "manager_workstream@test.com", "password": "test1234"},
    "student": {"email": "student1@test.com", "password": "test1234"},
    "teacher": {"email": "teacher1@test.com", "password": "test1234"},
    "secretary": {"email": "secretary1@test.com", "password": "test1234"},
    "guardian": {"email": "guardian1@test.com", "password": "test1234"},
    "guest": {"email": "guest1@test.com", "password": "test1234"},
}

def login(role):
    if role in PORTAL_LOGIN_ROLES:
        url = f"{BASE_URL}/api/portal/auth/login/"
        data = {
            "email": CREDENTIALS[role]["email"],
            "password": CREDENTIALS[role]["password"]
        }
        resp = requests.post(url, json=data, timeout=TIMEOUT)
        if resp.status_code == 200:
            tokens = resp.json()
            return tokens.get("access"), tokens.get("refresh")
        elif resp.status_code == 403:
            return None, None
        else:
            resp.raise_for_status()
    elif role in WORKSTREAM_LOGIN_ROLES:
        workstream_id = ROLES[role].get("workstream_id")
        url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
        data = {
            "email": CREDENTIALS[role]["email"],
            "password": CREDENTIALS[role]["password"]
        }
        resp = requests.post(url, json=data, timeout=TIMEOUT)
        if resp.status_code == 200:
            tokens = resp.json()
            return tokens.get("access"), tokens.get("refresh")
        else:
            resp.raise_for_status()
    else:
        raise ValueError(f"Unknown role {role}")

def create_user(token, role_to_create):
    url = f"{BASE_URL}/api/users/create/"
    headers = {"Authorization": f"Bearer {token}"}
    unique_email = f"testuser-{uuid.uuid4()}@test.com"
    payload = {
        "email": unique_email,
        "password": "pass1234",
        "password_confirm": "pass1234",
        "first_name": "Test",
        "last_name": "User",
        "role": role_to_create
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 201, f"User creation failed with status {resp.status_code}: {resp.text}"
    return resp.json()["id"], unique_email

def delete_user(token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    # Deactivate returns 204 No Content.
    # If fails, try hard delete if API allows (not in spec), so just ignore error here.
    # The test will sporadically leave test users, but we attempt best effort.


def test_tc008_user_management_update_user_information():
    roles = list(ROLES.keys())

    # We'll create one user as target for update under admin token (or manager token)
    # We create user as admin role, then test update access on that user for all roles

    # Login as admin to create the user for update target & cleanup
    admin_access, _ = login("admin")
    assert admin_access, "Admin login failed to obtain token"
    target_user_id = None
    try:
        target_user_id, target_email = create_user(admin_access, "student")
        patch_url = f"{BASE_URL}/api/users/{target_user_id}/"

        for role in roles:
            access_token, _ = login(role)
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

            # Prepare payload to update (for simplicity update first_name)
            update_payload = {"first_name": f"UpdatedBy{role.capitalize()}"}
            resp = requests.patch(patch_url, json=update_payload, headers=headers, timeout=TIMEOUT)

            # RBAC Enforcement and expected outcomes:
            # Roles allowed to update: admin, manager_school, manager_workstream (portal login roles with permissions)
            # Other roles should get 403 or 401 (unauthorized)
            if role in {"admin", "manager_school", "manager_workstream"}:
                assert resp.status_code == 204, (
                    f"Role {role} should have succeeded updating user but got {resp.status_code}: {resp.text}"
                )
                # No content should lead to empty body
                assert resp.text == "", f"Expected empty response body for 204 but got: {resp.text}"
            else:
                # Expect 403 Forbidden or 401 Unauthorized
                assert resp.status_code in {401, 403}, (
                    f"Role {role} should be forbidden from updating user but got {resp.status_code}: {resp.text}"
                )

    finally:
        # Cleanup: deactivate the created user if token valid
        if target_user_id and admin_access:
            delete_user(admin_access, target_user_id)


test_tc008_user_management_update_user_information()