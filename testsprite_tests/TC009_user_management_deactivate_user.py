import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

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

# Admin and manager roles login at portal login endpoint, others at workstream login
PORTAL_LOGIN_ROLES = {"admin", "manager_school", "manager_workstream"}
WORKSTREAM_LOGIN_ROLES = {"student", "teacher", "secretary", "guardian", "guest"}

# Credentials for login by role (if demo users exist). We will create test users for this test.
# To simplify, we define credentials for portal login roles here:
PORTAL_ROLE_CREDENTIALS = {
    "admin": {"email": "admin@test.com", "password": "test1234"},
    "manager_school": {"email": "manager_school@test.com", "password": "test1234"},
    "manager_workstream": {"email": "manager_workstream@test.com", "password": "test1234"},
}

# For roles using workstream login, we need a workstream_id.
# Assuming workstream_id = 1 exists for testing.
WORKSTREAM_ID = 1

def register_guest_user(email, password):
    url = f"{BASE_URL}/api/portal/auth/register/"
    payload = {
        "email": email,
        "password": password,
        "password_confirm": password,
        "full_name": "Guest User"
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def login_portal(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"email": email, "password": password}
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    return resp

def login_workstream(workstream_id, email, password):
    url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
    payload = {"email": email, "password": password}
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    return resp

def create_user(admin_token, email, password, role="student", first_name="Test", last_name="User"):
    url = f"{BASE_URL}/api/users/create/"
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "email": email,
        "password": password,
        "password_confirm": password,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def delete_user(admin_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/"
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    # deletion may not be implemented, so ignore errors here

def deactivate_user(user_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    return resp

def test_user_management_deactivate_user():
    # First, login as admin to create users and for test cleanup
    admin_cred = PORTAL_ROLE_CREDENTIALS["admin"]
    admin_login_resp = login_portal(admin_cred["email"], admin_cred["password"] )
    assert admin_login_resp.status_code == 200, "Admin login failed"
    admin_access_token = admin_login_resp.json().get("access")
    assert admin_access_token, "Admin access token missing"

    # Create a user to deactivate
    test_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "TestPass123!"
    user_role = "teacher"  # choose a role different from admin to test RBAC
    created_user = create_user(admin_access_token, test_email, test_password, role=user_role)
    user_id = created_user.get("id")
    assert user_id, "Created user ID not found"

    # Login tokens dict for all roles
    role_tokens = {}

    # Prepare to register and login guest user since guest login is via portal
    # For guest role, we register to get the user because no default guest credentials exist
    guest_email = f"guest_{uuid.uuid4().hex[:8]}@test.com"
    guest_password = "GuestPass123!"
    guest_register_resp = register_guest_user(guest_email, guest_password)
    assert guest_register_resp.get("email") == guest_email

    # Function to get token for each role
    def get_token_for_role(role):
        if role in PORTAL_LOGIN_ROLES:
            creds = PORTAL_ROLE_CREDENTIALS.get(role)
            if not creds:
                # create user for this role using admin
                email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
                password = "TestPass123!"
                created = create_user(admin_access_token, email, password, role=role)
                # check created user id
                assert created.get("id"), f"Failed to create user for role {role}"
                creds = {"email": email, "password": password}
            resp = login_portal(creds["email"], creds["password"])
            assert resp.status_code == 200, f"Login failed for role {role}"
            return resp.json().get("access")
        elif role == "guest":
            resp = login_portal(guest_email, guest_password)
            assert resp.status_code == 200, "Guest login failed"
            return resp.json().get("access")
        elif role in WORKSTREAM_LOGIN_ROLES:
            if role == "guest":
                return None
            # Create user for this role in workstream (except guest handled above)
            email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
            password = "TestPass123!"
            # We create user via admin to ensure user exists, then login via workstream
            created = create_user(admin_access_token, email, password, role=role)
            assert created.get("id"), f"Failed to create user for role {role}"
            resp = login_workstream(WORKSTREAM_ID, email, password)
            assert resp.status_code == 200, f"Workstream login failed for role {role}"
            return resp.json().get("access")
        else:
            return None


    # Obtain tokens for all roles
    for role in ROLES:
        token = get_token_for_role(role)
        role_tokens[role] = token

    try:
        # Test deactivation with each role
        for role in ROLES:
            token = role_tokens.get(role)
            assert token or role == "guest", f"Token missing for role {role}"

            resp = deactivate_user(token, user_id) if token else None

            if role in {"admin", "manager_school", "manager_workstream"}:
                # These roles should be authorized and get 204 No Content
                assert resp is not None, f"No response for role {role}"
                assert resp.status_code == 204, f"Role {role} expected 204, got {resp.status_code}"
                # No content expected in body
                assert not resp.content or resp.content == b'', f"Role {role} response body not empty"
            else:
                # Other roles are unauthorized: 403 or 401
                # resp might be None if no token - treat as unauthorized
                if resp is None:
                    # No token provided means unauthorized
                    pass
                else:
                    assert resp.status_code in (401, 403), f"Role {role} expected 401/403, got {resp.status_code}"

    finally:
        # Cleanup: delete created user by admin token
        try:
            delete_user(admin_access_token, user_id)
        except Exception:
            pass

test_user_management_deactivate_user()
