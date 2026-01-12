import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_classroom_crud_operations():
    # Admin login to get access token
    login_payload = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    login_resp = requests.post(f"{BASE_URL}/api/portal/auth/login/", json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, "Admin login failed"
    access_token = login_resp.json().get("tokens", {}).get("access")
    assert access_token, "Access token not found in login response"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Helper function to create a user with specified role
    def create_user(role, email_suffix):
        user_data = {
            "username": f"user_{role}_{uuid.uuid4().hex[:8]}",
            "email": f"{role}_{uuid.uuid4().hex[:8]}_{email_suffix}@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "role": role,
            "is_active": True
        }
        resp = requests.post(f"{BASE_URL}/api/users/create/", json=user_data, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Failed to create {role} user"
        return resp.json()

    # Create Workstream Manager user
    ws_manager = create_user("workstream_manager", "wsmanager")

    # Create Workstream with manager_id
    workstream_data = {
        "name": f"Workstream_{uuid.uuid4().hex[:8]}",
        "manager_id": ws_manager["id"]
    }
    resp_ws = requests.post(f"{BASE_URL}/api/workstream/", json=workstream_data, headers=headers, timeout=TIMEOUT)
    assert resp_ws.status_code == 201, "Failed to create workstream"
    workstream = resp_ws.json()
    workstream_id = workstream["id"]

    # Create School Manager user
    school_manager = create_user("school_manager", "schoolmanager")

    # Create School with manager_id
    school_data = {
        "name": f"School_{uuid.uuid4().hex[:8]}",
        "manager_id": school_manager["id"]
    }
    resp_school = requests.post(f"{BASE_URL}/api/manager/schools/create/", json=school_data, headers=headers, timeout=TIMEOUT)
    assert resp_school.status_code == 201, "Failed to create school"
    school = resp_school.json()
    school_id = school["id"]

    # Create Academic Year for the School
    academic_year_data = {
        "name": f"AcademicYear_{uuid.uuid4().hex[:8]}",
        "start_date": "2025-09-01",
        "end_date": "2026-06-30"
    }
    resp_ay = requests.post(f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/create/", json=academic_year_data, headers=headers, timeout=TIMEOUT)
    assert resp_ay.status_code == 201, "Failed to create academic year"
    academic_year = resp_ay.json()
    academic_year_id = academic_year["id"]

    classroom_id = None

    try:
        # Create Classroom
        classroom_data = {
            "name": f"Classroom_{uuid.uuid4().hex[:8]}",
            "description": "Test classroom description"
        }
        create_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/classrooms/create/"
        resp_create = requests.post(create_url, json=classroom_data, headers=headers, timeout=TIMEOUT)
        assert resp_create.status_code == 201, "Failed to create classroom"
        classroom = resp_create.json()
        classroom_id = classroom["id"]
        assert classroom["name"] == classroom_data["name"]
        assert classroom["description"] == classroom_data["description"]

        # Retrieve Classroom
        get_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/classrooms/{classroom_id}/"
        resp_get = requests.get(get_url, headers=headers, timeout=TIMEOUT)
        assert resp_get.status_code == 200, "Failed to retrieve classroom"
        classroom_get = resp_get.json()
        assert classroom_get["id"] == classroom_id
        assert classroom_get["name"] == classroom_data["name"]

        # Update Classroom
        updated_data = {
            "name": f"Updated_{classroom_data['name']}",
            "description": "Updated classroom description"
        }
        resp_patch = requests.patch(get_url, json=updated_data, headers=headers, timeout=TIMEOUT)
        assert resp_patch.status_code == 200, "Failed to update classroom"
        classroom_updated = resp_patch.json()
        assert classroom_updated["name"] == updated_data["name"]
        assert classroom_updated["description"] == updated_data["description"]

        # Access control test: attempt retrieval without auth (should fail)
        resp_unauth = requests.get(get_url, timeout=TIMEOUT)
        assert resp_unauth.status_code == 401 or resp_unauth.status_code == 403, "Unauthorized access should be denied"

    finally:
        # Cleanup: delete classroom if created
        if classroom_id:
            del_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/classrooms/{classroom_id}/"
            del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
            assert del_resp.status_code == 204, "Failed to delete classroom"

        # Cleanup: delete academic year
        if 'academic_year_id' in locals():
            resp_del_ay = requests.delete(f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/", headers=headers, timeout=TIMEOUT)
            assert resp_del_ay.status_code == 204, "Failed to delete academic year"

        # Cleanup: delete school
        if 'school_id' in locals():
            resp_del_school = requests.delete(f"{BASE_URL}/api/manager/schools/{school_id}/", headers=headers, timeout=TIMEOUT)
            assert resp_del_school.status_code == 204, "Failed to delete school"

        # Cleanup: delete workstream
        if 'workstream_id' in locals():
            resp_del_ws = requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=headers, timeout=TIMEOUT)
            # Deletion for workstream may or may not be allowed; check for 204 or 405 (method not allowed)
            assert resp_del_ws.status_code in [204, 405], "Failed to delete or disable workstream (405 means not allowed)"

        # Cleanup: delete users
        def delete_user(user_id):
            resp = requests.delete(f"{BASE_URL}/api/users/{user_id}/", headers=headers, timeout=TIMEOUT)
            assert resp.status_code == 204, f"Failed to delete user id {user_id}"

        if 'school_manager' in locals():
            delete_user(school_manager["id"])
        if 'ws_manager' in locals():
            delete_user(ws_manager["id"])

test_classroom_crud_operations()
