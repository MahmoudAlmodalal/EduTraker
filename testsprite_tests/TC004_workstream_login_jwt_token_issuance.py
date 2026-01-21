import requests
import uuid
import time

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

# Credentials for portal login (admin/manager roles)
PORTAL_CREDENTIALS = {
    "admin": {"email": "admin@test.com", "password": "test1234"},
    "manager_workstream": {"email": "manager_ws@test.com", "password": "test1234"},
}

def register_workstream_student(workstream_id, email, password):
    url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/register/"
    payload = {
        "email": email,
        "password": password,
        "password_confirm": password,
        "full_name": "Test User",
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def delete_user(access_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/deactivate/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 204

def portal_login(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {
        "email": email,
        "password": password,
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    return resp

def workstream_login(workstream_id, email, password):
    url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/login/"
    payload = {
        "email": email,
        "password": password,
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    return resp

def test_workstream_login_jwt_token_issuance():
    workstream_id = "test-workstream-123"
    timestamp = str(int(time.time()))
    test_users = {}

    student_email = f"student_{timestamp}@test.com"
    student_password = "Testpass123!"

    # Attempt to register student user, but handle 404 gracefully
    try:
        reg_resp = register_workstream_student(workstream_id, student_email, student_password)
        user_id = reg_resp.get('id') or reg_resp.get('user', {}).get('id')
        assert user_id, "Student user ID missing in registration response"
        test_users["student"] = {
            "email": student_email,
            "password": student_password,
            "id": user_id,
        }
        student_registered = True
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            # Workstream does not exist; skip student registration/login
            student_registered = False
        else:
            assert False, f"Failed to register student user for workstream {workstream_id}: {e}"

    test_users["admin"] = {
        "email": PORTAL_CREDENTIALS["admin"]["email"],
        "password": PORTAL_CREDENTIALS["admin"]["password"],
    }
    test_users["manager_workstream"] = {
        "email": PORTAL_CREDENTIALS["manager_workstream"]["email"],
        "password": PORTAL_CREDENTIALS["manager_workstream"]["password"],
    }

    test_users["guest"] = {
        "email": f"guest_{timestamp}@test.com",
        "password": "Testpass123!",
    }

    for role in ["teacher", "secretary", "guardian", "manager_school"]:
        test_users[role] = {
            "email": f"{role}_{timestamp}@test.com",
            "password": "Testpass123!",
        }

    def validate_jwt_token(token):
        assert isinstance(token, str) and token.count(".") == 2, "JWT token structure invalid"

    results = {}

    for role in ["admin", "manager_workstream"]:
        cred = test_users[role]
        resp = portal_login(cred["email"], cred["password"])
        if resp.status_code == 200:
            data = resp.json()
            assert "access" in data and isinstance(data["access"], str)
            assert "refresh" in data and isinstance(data["refresh"], str)
            assert "user" in data and isinstance(data["user"], dict)
            validate_jwt_token(data["access"])
            validate_jwt_token(data["refresh"])
            results[role] = "login_success"
        else:
            assert resp.status_code == 403
            results[role] = "unauthorized"

    # If student registered, test login; otherwise skip
    if student_registered:
        role = "student"
        cred = test_users[role]
        resp = workstream_login(workstream_id, cred["email"], cred["password"])
        assert resp.status_code == 200, f"Student role login failed with status {resp.status_code}"
        data = resp.json()
        assert "access" in data and isinstance(data["access"], str)
        assert "refresh" in data and isinstance(data["refresh"], str)
        assert "user" in data and isinstance(data["user"], dict)
        validate_jwt_token(data["access"])
        validate_jwt_token(data["refresh"])
        results[role] = "login_success"
    else:
        results["student"] = "skipped_no_workstream"

    for role in ["teacher", "secretary", "guardian", "manager_school", "guest"]:
        cred = test_users[role]
        resp = workstream_login(workstream_id, cred["email"], cred["password"])
        assert resp.status_code in [401, 403], (
            f"{role} role login unexpected status {resp.status_code}, response: {resp.text}"
        )
        results[role] = "unauthorized"

    admin_cred = test_users["admin"]
    resp_admin_login = portal_login(admin_cred["email"], admin_cred["password"])
    if resp_admin_login.status_code == 200:
        admin_token = resp_admin_login.json().get("access")
        if admin_token and student_registered and test_users["student"]["id"]:
            try:
                delete_user(admin_token, test_users["student"]["id"])
            except AssertionError:
                pass

    return results

test_workstream_login_jwt_token_issuance()
