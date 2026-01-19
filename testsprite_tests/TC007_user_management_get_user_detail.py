import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ROLE_INFO = {
    "student": {"workstream_id": "1"},
    "teacher": {"workstream_id": "1"},
    "secretary": {"workstream_id": "1"},
    "manager_school": {},
    "manager_workstream": {"workstream_id": "1"},
    "guardian": {"workstream_id": "1"},
    "admin": {},
    "guest": {},
}

ROLE_LOGIN_PATH = {
    "student": "/api/workstream/{workstream_id}/auth/login/",
    "teacher": "/api/workstream/{workstream_id}/auth/login/",
    "secretary": "/api/workstream/{workstream_id}/auth/login/",
    "manager_workstream": "/api/portal/auth/login/",
    "manager_school": "/api/portal/auth/login/",
    "guardian": "/api/workstream/{workstream_id}/auth/login/",
    "admin": "/api/portal/auth/login/",
    "guest": "/api/portal/auth/login/",
}

ROLE_CREDENTIALS = {
    # These credentials are assumed for the test environment
    "admin": {"email": "admin@test.com", "password": "test1234"},
    "manager_school": {"email": "manager_school@test.com", "password": "test1234"},
    "manager_workstream": {"email": "manager_workstream@test.com", "password": "test1234"},
    "teacher": {"email": "teacher1@test.com", "password": "test1234"},
    "student": {"email": "student1@test.com", "password": "test1234"},
    "secretary": {"email": "secretary1@test.com", "password": "test1234"},
    "guardian": {"email": "guardian1@test.com", "password": "test1234"},
    "guest": {"email": "guest1@test.com", "password": "test1234"},
}

# Headers for requests without auth or for login
COMMON_HEADERS = {
    "Content-Type": "application/json"
}


def login(role):
    path_tpl = ROLE_LOGIN_PATH[role]
    wk_id = ROLE_INFO[role].get("workstream_id")
    path = path_tpl.format(workstream_id=wk_id) if "{workstream_id}" in path_tpl else path_tpl
    url = BASE_URL + path
    credentials = ROLE_CREDENTIALS.get(role)
    if not credentials:
        # For guest or roles without preset credentials, register a guest and login
        if role == "guest":
            # Register guest
            guest_email = f"guest_{uuid.uuid4().hex[:8]}@test.com"
            reg_data = {
                "email": guest_email,
                "password": "test1234",
                "password_confirm": "test1234",
                "full_name": "Guest User",
            }
            reg_url = BASE_URL + "/api/portal/auth/register/"
            r_reg = requests.post(reg_url, json=reg_data, headers=COMMON_HEADERS, timeout=TIMEOUT)
            assert r_reg.status_code == 201
            credentials = {"email": guest_email, "password": "test1234"}
        else:
            raise ValueError(f"No credentials for role {role}")

    login_payload = {"email": credentials["email"], "password": credentials["password"]}
    r = requests.post(url, json=login_payload, headers=COMMON_HEADERS, timeout=TIMEOUT)

    if role in ("admin", "manager_school", "manager_workstream", "guest"):
        # Portal login roles: expect 200 or 403
        if r.status_code == 200:
            data = r.json()
            assert "access" in data and "refresh" in data and "user" in data
            return data["access"]
        elif r.status_code == 403:
            return None
        else:
            assert False, f"Login for role {role} returned unexpected status {r.status_code}"
    else:
        # Workstream login roles: expect 200 or 403 (403 treated as unauthorized)
        if r.status_code == 200:
            data = r.json()
            assert "access" in data and "refresh" in data and "user" in data
            return data["access"]
        elif r.status_code == 403:
            return None
        else:
            assert False, f"Workstream login for role {role} returned status {r.status_code}"


def create_user(token):
    url = BASE_URL + "/api/users/create/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@test.com"
    user_data = {
        "email": unique_email,
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    r = requests.post(url, json=user_data, headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    created_user = r.json()
    user_id = created_user.get("id")
    assert user_id is not None
    return user_id, unique_email


def delete_user(user_id, token):
    url = BASE_URL + f"/api/users/{user_id}/deactivate/"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    # Deactivate then delete user if there were API to delete; assuming deactivation sufficient
    r = requests.post(url, headers=headers, timeout=TIMEOUT)
    if r.status_code not in (204, 404):
        r.raise_for_status()


def test_user_management_get_user_detail():
    roles = [
        "student",
        "teacher",
        "secretary",
        "manager_school",
        "manager_workstream",
        "guardian",
        "admin",
        "guest"
    ]

    # Pre-create a user resource with admin token to use for successful GETs
    admin_token = login("admin")
    user_id, _ = create_user(admin_token)

    try:
        for role in roles:
            token = None
            try:
                token = login(role)
            except Exception:
                token = None

            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            # 1) Test successful GET of the created user when authorized
            url = BASE_URL + f"/api/users/{user_id}/"
            r = requests.get(url, headers=headers, timeout=TIMEOUT)

            if role in ("admin", "manager_school", "manager_workstream"):
                # These roles should be authorized to get user details
                assert r.status_code == 200, f"Role {role} should get 200 but got {r.status_code}"
                data = r.json()
                assert "email" in data and "id" in data
                assert data["id"] == user_id
            else:
                # Other roles likely 403 or 401 due to RBAC
                assert r.status_code in (401, 403), f"Role {role} expected 401/403 but got {r.status_code}"

            # 2) Test GET on invalid user id returns 404 with "User not found." detail
            invalid_user_id = "00000000-0000-0000-0000-000000000000"
            url_invalid = BASE_URL + f"/api/users/{invalid_user_id}/"
            r_invalid = requests.get(url_invalid, headers=headers, timeout=TIMEOUT)

            # If role is unauthorized, 401 or 403 is possible, accept that
            if r_invalid.status_code in (401, 403):
                # Unauthorized access is acceptable outcome
                pass
            else:
                assert r_invalid.status_code == 404, f"Role {role} should get 404 for invalid user but got {r_invalid.status_code}"
                try:
                    error_data = r_invalid.json()
                    detail = error_data.get("detail", "").lower()
                    assert "not found" in detail or "user not found" in detail
                except Exception:
                    assert False, f"Invalid user 404 response for role {role} missing or malformed JSON detail."
    finally:
        # Clean up created user
        delete_user(user_id, admin_token)


test_user_management_get_user_detail()
