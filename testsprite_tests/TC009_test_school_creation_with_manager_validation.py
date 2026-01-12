import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
HEADERS_JSON = {"Content-Type": "application/json"}


def login_portal(email, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"email": email, "password": password}
    resp = requests.post(url, json=payload, headers=HEADERS_JSON, timeout=TIMEOUT)
    resp.raise_for_status()
    tokens = resp.json().get("tokens", {})
    access = tokens.get("access")
    if not access:
        raise Exception("Access token not found after login")
    return access


def create_user(access_token, email, full_name, password, role):
    url = f"{BASE_URL}/api/users/create/"
    headers = {"Authorization": f"Bearer {access_token}", **HEADERS_JSON}
    payload = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "password_confirm": password,
        "role": role,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    user = resp.json()
    if not user or "id" not in user:
        raise Exception("User creation failed - no user id returned")
    return user


def delete_user(access_token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    # allow 200 or 204 as success for delete
    if resp.status_code not in (200, 204):
        raise Exception(f"Failed to delete user id {user_id}, status: {resp.status_code}")


def create_workstream(access_token, name, manager_id, max_user=10):
    url = f"{BASE_URL}/api/workstream/"
    headers = {"Authorization": f"Bearer {access_token}", **HEADERS_JSON}
    payload = {
        "name": name,
        "manager_id": manager_id,
        "max_user": max_user,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    workstream = resp.json()
    if "id" not in workstream:
        raise Exception("Workstream creation failed - no id returned")
    return workstream


def delete_workstream(access_token, workstream_id):
    url = f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, headers=headers, timeout=TIMEOUT)
    if resp.status_code not in (200, 204):
        # fallback to actual delete if deactivate endpoint does not remove
        del_url = f"{BASE_URL}/api/workstreams/{workstream_id}/"
        del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
        if del_resp.status_code not in (200, 204):
            raise Exception(f"Failed to delete workstream id {workstream_id}, status: {del_resp.status_code}")


def create_school(access_token, school_name, work_stream_id, manager_id=None):
    url = f"{BASE_URL}/api/manager/schools/create/"
    headers = {"Authorization": f"Bearer {access_token}", **HEADERS_JSON}
    payload = {
        "school_name": school_name,
        "work_stream_id": work_stream_id,
    }
    if manager_id:
        payload["manager_id"] = manager_id
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    school = resp.json()
    if "id" not in school:
        raise Exception("School creation failed - no id returned")
    return school


def delete_school(access_token, school_id):
    url = f"{BASE_URL}/api/manager/schools/{school_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    if resp.status_code not in (200, 204):
        raise Exception(f"Failed to delete school id {school_id}, status: {resp.status_code}")


def test_school_creation_with_manager_validation():
    access_token = login_portal(ADMIN_EMAIL, ADMIN_PASSWORD)

    # Create a manager_workstream user (required for workstream creation)
    mw_email = f"mw_{uuid.uuid4().hex[:8]}@test.com"
    mw_full_name = "Workstream Manager Test"
    mw_password = "WmPass123!"
    manager_workstream_user = create_user(access_token, mw_email, mw_full_name, mw_password, "manager_workstream")

    # Create a workstream with the above manager_workstream user
    workstream_name = f"Test WS {uuid.uuid4().hex[:6]}"
    workstream = create_workstream(access_token, workstream_name, manager_workstream_user["id"]) 

    # Create a manager_school user (to assign optionally to the school)
    ms_email = f"ms_{uuid.uuid4().hex[:8]}@test.com"
    ms_full_name = "School Manager Test"
    ms_password = "MsPass123!"
    manager_school_user = create_user(access_token, ms_email, ms_full_name, ms_password, "manager_school")

    # We'll create 2 schools: one without a manager, one with a manager_school assigned

    created_school_ids = []
    try:
        # Create school without manager_id
        school_name_wo_manager = f"SchoolNoMgr {uuid.uuid4().hex[:6]}"
        school1 = create_school(access_token, school_name_wo_manager, workstream["id"], manager_id=None)
        created_school_ids.append(school1["id"])

        # Validate response keys and values
        assert school1["school_name"] == school_name_wo_manager
        assert school1["work_stream_id"] == workstream["id"]
        assert "manager_id" not in school1 or school1.get("manager_id") in (None, "")

        # Create school WITH manager_id as manager_school role user
        school_name_with_manager = f"SchoolWithMgr {uuid.uuid4().hex[:6]}"
        school2 = create_school(access_token, school_name_with_manager, workstream["id"], manager_id=manager_school_user["id"])
        created_school_ids.append(school2["id"])

        assert school2["school_name"] == school_name_with_manager
        assert school2["work_stream_id"] == workstream["id"]
        assert school2["manager_id"] == manager_school_user["id"]

        # Negative test: try to create school with invalid manager role (e.g. use manager_workstream user as manager_school)
        url = f"{BASE_URL}/api/manager/schools/create/"
        headers = {"Authorization": f"Bearer {access_token}", **HEADERS_JSON}
        invalid_payload = {
            "school_name": f"InvalidSchool {uuid.uuid4().hex[:6]}",
            "work_stream_id": workstream["id"],
            "manager_id": manager_workstream_user["id"],  # manager_workstream user, invalid as school manager
        }
        resp = requests.post(url, json=invalid_payload, headers=headers, timeout=TIMEOUT)
        # Expect bad request (400) or forbidden (403)
        assert resp.status_code in (400, 403)

    finally:
        # Clean up created schools
        for school_id in created_school_ids:
            try:
                delete_school(access_token, school_id)
            except Exception:
                pass
        # Clean up created workstream and users
        try:
            delete_workstream(access_token, workstream["id"])
        except Exception:
            pass
        try:
            delete_user(access_token, manager_workstream_user["id"])
        except Exception:
            pass
        try:
            delete_user(access_token, manager_school_user["id"])
        except Exception:
            pass


test_school_creation_with_manager_validation()
