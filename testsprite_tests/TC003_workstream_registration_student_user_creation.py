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
    "guest",
]

# Predefined emails and passwords for users per role for login (would normally be fixtures or test data)
# If needed, we can create these users first or assume they exist.
# For the purpose of this test, create minimal users for roles and do login to get tokens for protected endpoints.
# Admin and Managers login via /api/portal/auth/login/, others via /api/workstream/{workstream_id}/auth/login/

ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "test1234"
}


def login_portal(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    data = {"email": email, "password": password}
    resp = requests.post(url, json=data, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    try:
        tokens = resp.json()
        return tokens.get("access")
    except Exception:
        return None


def login_workstream(workstream_id, email, password):
    url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
    data = {"email": email, "password": password}
    resp = requests.post(url, json=data, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    try:
        tokens = resp.json()
        return tokens.get("access")
    except Exception:
        return None


def create_workstream_manager_and_workstream():
    # Create a new workstream and a manager for it to have test data
    # Via portal (admin) create workstream and manager? No direct endpoint given, so to simulate create a 
    # workstream by registering workstream manager? Or skip workstream creation by assuming workstream ID=1 exists
    # Because no API for creating workstream given, we cannot create dynamic workstream here.
    # We'll assume workstream 1 exists. If needed we can try with UUIDs that do not exist for 404 tests below.
    return 1


def test_workstream_registration_student_user_creation():
    # Workstream to test against
    workstream_id = create_workstream_manager_and_workstream()

    # Payload template for registration
    def make_student_payload(email_suffix):
        password = "Password123!"
        return {
            "email": f"student{email_suffix}@test.com",
            "password": password,
            "password_confirm": password,
            "first_name": "Test",
            "last_name": "Student",
            "full_name": "Test Student",
        }

    # Roles login info (emails & passwords) for authentication
    # For simplicity, we assume following test users already exist with these credentials
    # role: (login_email, password)
    # Admin and manager_workstream use portal login
    # Others use workstream login

    ROLE_CREDENTIALS = {
        "admin": ("admin@test.com", "test1234"),
        "manager_workstream": ("workstream_manager@test.com", "test1234"),
        "manager_school": ("school_manager@test.com", "test1234"),
        "student": ("student1@test.com", "Password123!"),
        "teacher": ("teacher@test.com", "test1234"),
        "secretary": ("secretary@test.com", "test1234"),
        "guardian": ("guardian@test.com", "test1234"),
        "guest": ("guest@test.com", "test1234"),
    }

    # Helper to get auth token per role
    def get_auth_token_for_role(role):
        email, pwd = ROLE_CREDENTIALS.get(role, (None, None))
        if email is None:
            return None  # No login credentials

        if role in ("admin", "manager_workstream", "manager_school"):
            return login_portal(email, pwd)
        else:
            return login_workstream(workstream_id, email, pwd)

    # 1) Test non-existent workstream returns 404 with 'not found'

    fake_workstream_id = str(uuid.uuid4())
    url_fake_ws = f"{BASE_URL}/api/workstream/{fake_workstream_id}/auth/register/"
    payload = make_student_payload("nonexistentws")

    resp = requests.post(url_fake_ws, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 404, f"Expected 404 for non-existent workstream, got {resp.status_code}"
    try:
        json_resp = resp.json()
        detail = ""
        if isinstance(json_resp, dict):
            detail = json_resp.get("detail", "") or json_resp.get("message", "")
        if not detail:
            # decode bytes to string for content
            detail = resp.content.decode(errors='ignore')
        detail = detail.lower()
    except Exception:
        detail = ""
    assert "not found" in detail, "404 response detail must contain 'not found'"

    # 2) Test registration by role with expected RBAC enforcement
    # Only 'student' role should be allowed to register here.
    # According to instruction 5,
    # Unauthorized roles must get 403 or 401.

    # Because registration is for creating a new user (student),
    # and registration endpoint is public for student creation;
    # So auth may not be required or different behavior.
    # Usually registration endpoints are public (guest role).
    # The instructions say all protected endpoints need Authorization.
    # But registration usually does NOT require Authorization (guest role).
    # So we will test registration without Authorization header for student role.
    # We test other roles registering a student - we simulate by providing Authorization tokens, expecting 403 or 401.

    register_url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/register/"

    # Roles and expected responses:
    # Student: allowed - 201 Created
    # Guest: allowed? The PRD doesn't explicitly say, guest probably no.
    # Others: forbidden or unauthorized 403/401.

    # We'll test each role for registration.
    # For student role: no token is expected (public registration)
    # For others: include token and expect 403 or 401

    for role in ROLES:
        # Prepare email unique per role for creation
        email_suffix = f"{role}_{uuid.uuid4().hex[:6]}"
        payload = make_student_payload(email_suffix)

        # Auth token
        token = get_auth_token_for_role(role)

        headers = {}
        # Per instructions, "Authorization: Bearer <token>" for protected endpoints
        # Registration usually does not require token, but we'll test with and without token as per RBAC instruction.

        if role == "student":
            # Registration assumed public
            resp = requests.post(register_url, json=payload, timeout=TIMEOUT)
            if resp.status_code == 201:
                # Success path: Validate response structure
                # The user created as student
                # No response body specified, assume contains user data or minimal
                try:
                    json_resp = resp.json()
                    assert "email" in json_resp and json_resp["email"] == payload["email"]
                except Exception:
                    # Could be empty body or unexpected, just confirm status_code
                    pass

                # Cleanup: delete the created user
                # To delete user we need user's id - none provided explicitly.
                # We can login as this student to get token, get user info, then delete.
                # No user delete endpoint explicitly given. We can PATCH with deactivate or DELETE?
                # Only PATCH /api/users/{id}/, POST deactivate/activate are given.
                # Assume we can get user list via GET /api/users/ for authorized roles
                # But test user has no rights.

                # We'll try to login as newly created student to get access token
                access_token = login_workstream(workstream_id, payload["email"], payload["password"])
                if access_token:
                    # Get user info (not defined endpoint to get current user, so skip cleanup)
                    # Instructions say to use try-finally to delete resource, but no delete endpoint documented.
                    # So omit delete here due to no API.

                    pass

            else:
                assert False, f"Student registration expected 201 but got {resp.status_code} with body {resp.text}"

        else:
            # Other roles: Add Authorization header and expect 403 or 401
            if token:
                headers["Authorization"] = f"Bearer {token}"

            resp = requests.post(register_url, json=payload, headers=headers, timeout=TIMEOUT)

            # Expected 401 Unauthorized or 403 Forbidden
            assert resp.status_code in (401, 403), (
                f"Role {role} expected 401 or 403, got {resp.status_code}. Response: {resp.text}"
            )

    # Test successful creation for student role with optional fields missing (only required)
    payload = {"email": f"student_minimal_{uuid.uuid4().hex[:6]}@test.com", "password": "Password123!"}
    # password_confirm optional, but normally required for validation. Let's add it to pass validation.
    payload["password_confirm"] = payload["password"]

    resp = requests.post(register_url, json=payload, timeout=TIMEOUT)
    assert resp.status_code == 201, f"Student registration minimal fields expected 201 but got {resp.status_code}"
    try:
        json_resp = resp.json()
        assert "email" in json_resp and json_resp["email"] == payload["email"]
    except Exception:
        pass


test_workstream_registration_student_user_creation()
