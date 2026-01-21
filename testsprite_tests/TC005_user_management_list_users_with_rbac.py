import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

ROLE_CREDENTIALS = {
    "student": {
        "workstream_id": 1,
        "email": "student1@workstream1.edu",
        "password": "studentpass1"
    },
    "teacher": {
        "workstream_id": 1,
        "email": "teacher1@workstream1.edu",
        "password": "teacherpass1"
    },
    "secretary": {
        "workstream_id": 1,
        "email": "secretary1@workstream1.edu",
        "password": "secretarypass1"
    },
    "manager_school": {
        "email": "manager_school@test.com",
        "password": "managerpass1"
    },
    "manager_workstream": {
        "email": "manager_workstream@test.com",
        "password": "managerpass2"
    },
    "guardian": {
        "workstream_id": 1,
        "email": "guardian1@workstream1.edu",
        "password": "guardianpass1"
    },
    "admin": {
        "email": "admin@test.com",
        "password": "test1234"
    },
    "guest": {
        "email": "guest@test.com",
        "password": "guestpass1"
    }
}

# Expected HTTP status codes for unauthorized roles for users list
UNAUTHORIZED_ROLES = {"guest"}

# Roles that login via portal vs workstream:
PORTAL_ROLES = {"admin", "manager_school", "manager_workstream", "guest"}
WORKSTREAM_ROLES = {"student", "teacher", "secretary", "guardian"}

def login_portal(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
    if resp.status_code == 200:
        data = resp.json()
        access = data.get("access")
        refresh = data.get("refresh")
        if not isinstance(access, str) or not access:
            return None, None, resp.status_code, "Missing access token"
        if not isinstance(refresh, str) or not refresh:
            return None, None, resp.status_code, "Missing refresh token"
        return access, refresh, resp.status_code, None
    elif resp.status_code == 403:
        return None, None, resp.status_code, resp.json()
    else:
        return None, None, resp.status_code, resp.text

def login_workstream(workstream_id, email, password):
    url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
    if resp.status_code == 200:
        data = resp.json()
        access = data.get("access")
        refresh = data.get("refresh")
        if not isinstance(access, str) or not access:
            return None, None, resp.status_code, "Missing access token"
        if not isinstance(refresh, str) or not refresh:
            return None, None, resp.status_code, "Missing refresh token"
        return access, refresh, resp.status_code, None
    else:
        return None, None, resp.status_code, resp.text

def get_users_list(token):
    url = f"{BASE_URL}/api/users/"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(url, headers=headers, timeout=TIMEOUT)

def test_tc005_user_management_list_users_with_rbac():
    # Collect results and errors for each role
    results = {}

    # Login each role and test GET /api/users/
    for role, cred in ROLE_CREDENTIALS.items():
        access_token = None
        refresh_token = None
        status_login = None
        login_error = None

        if role in PORTAL_ROLES:
            # portal login
            email = cred.get("email")
            password = cred.get("password")
            access_token, refresh_token, status_login, login_error = login_portal(email, password)
        elif role in WORKSTREAM_ROLES:
            # workstream login
            ws_id = cred.get("workstream_id")
            email = cred.get("email")
            password = cred.get("password")
            access_token, refresh_token, status_login, login_error = login_workstream(ws_id, email, password)
        else:
            # unknown role, treat as no token
            access_token, refresh_token, status_login, login_error = None, None, None, "No login method"

        # If login failed with non 200/403, fail test for this role
        if status_login is None or (status_login not in [200, 403]):
            results[role] = {
                "error": f"Login unexpected status {status_login}, error: {login_error}"
            }
            continue

        # If login returned 403, no access token
        if status_login == 403:
            # Expect GET /api/users/ to be either 401 or 403
            resp = get_users_list(None)
            # It may also be 401 if no token provided
            if resp.status_code not in (401, 403):
                results[role] = {
                    "error": f"Login 403 but GET /api/users/ response status {resp.status_code} not 401 or 403"
                }
            else:
                results[role] = {"passed": True, "details": f"Login 403 matched GET /api/users/ {resp.status_code}"}
            continue

        # If no token for role that is authorized, fail test for this role
        if not access_token:
            results[role] = {"error": "No access token received"}
            continue

        # Use token in GET /api/users/
        resp = get_users_list(access_token)

        if role == "guest":
            # Guests should be unauthorized to list users: expect 401 or 403
            if resp.status_code not in (401, 403):
                results[role] = {"error": f"Guest role expected 401 or 403 but got {resp.status_code}"}
            else:
                results[role] = {"passed": True}
            continue

        # For roles that should be authorized, expect 200
        if resp.status_code == 200:
            # Validate RBAC and multi-tenancy isolation by checking users belong to role's school or workstream as applicable
            try:
                users = resp.json()
                # Validate that users is a list
                assert isinstance(users, list), f"Response data is not a list for role {role}"

                # Check all returned users have role and id fields
                for u in users:
                    assert isinstance(u, dict), f"User item is not dict for role {role}"
                    assert "id" in u, f"User missing id for role {role}"
                    assert "role" in u, f"User missing role for role {role}"

                # For manager_school and manager_workstream verify no data leakage
                if role == "manager_school":
                    school_ids = {u.get("school_id") for u in users if u.get("school_id") is not None}
                    assert len(school_ids) <= 1, "Data leakage across multiple schools detected for manager_school"
                if role == "manager_workstream":
                    workstream_ids = {u.get("workstream_id") for u in users if u.get("workstream_id") is not None}
                    assert len(workstream_ids) <= 1, "Data leakage across multiple workstreams detected for manager_workstream"

                results[role] = {"passed": True}
            except Exception as e:
                results[role] = {"error": f"RBAC/multi-tenancy validation failed: {str(e)}"}
        elif resp.status_code in (401, 403):
            results[role] = {"passed": True, "details": f"Received status {resp.status_code} for role {role}"}
        else:
            results[role] = {"error": f"Unexpected status {resp.status_code}"}

    # Assertions for final results
    assert "admin" in results and results["admin"].get("passed"), f"Admin role failed: {results.get('admin')}"
    assert "manager_school" in results and results["manager_school"].get("passed"), f"Manager_school failed: {results.get('manager_school')}"
    assert "manager_workstream" in results and results["manager_workstream"].get("passed"), f"Manager_workstream failed: {results.get('manager_workstream')}"
    assert "guest" in results and results["guest"].get("passed"), f"Guest role failed: {results.get('guest')}"
    for role in ["student", "teacher", "secretary", "guardian"]:
        assert role in results, f"{role} missing in results"
        r = results[role]
        assert r.get("passed") or "details" in r, f"{role} should be authorized or properly restricted, got: {r}"


test_tc005_user_management_list_users_with_rbac()
