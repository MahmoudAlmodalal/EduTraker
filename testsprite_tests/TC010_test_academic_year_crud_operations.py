import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_academic_year_crud_operations():
    session = requests.Session()
    # Authenticate as admin to get JWT access token
    login_data = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    login_resp = session.post(f"{BASE_URL}/api/portal/auth/login/", json=login_data, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("tokens", {}).get("access")
    assert token, "Access token missing in login response"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 1: Create a user with role manager_workstream (required for workstream creation)
    mgr_ws_email = f"mgrws_{uuid.uuid4().hex[:8]}@test.com"
    manager_ws_payload = {
        "email": mgr_ws_email,
        "full_name": "Manager Workstream Test",
        "password": "test1234",
        "role": "manager_workstream"
    }
    user_create_resp = session.post(f"{BASE_URL}/api/users/create/", json=manager_ws_payload, headers=headers, timeout=TIMEOUT)
    assert user_create_resp.status_code == 201, f"Manager Workstream user creation failed: {user_create_resp.text}"
    manager_ws_user = user_create_resp.json()
    manager_ws_id = manager_ws_user.get("id")
    assert manager_ws_id, "Manager Workstream user ID missing"

    # Step 1.5: Create a user with role manager_school (required for school creation manager_id)
    mgr_school_email = f"mgrschool_{uuid.uuid4().hex[:8]}@test.com"
    manager_school_payload = {
        "email": mgr_school_email,
        "full_name": "Manager School Test",
        "password": "test1234",
        "role": "manager_school"
    }
    user_school_resp = session.post(f"{BASE_URL}/api/users/create/", json=manager_school_payload, headers=headers, timeout=TIMEOUT)
    assert user_school_resp.status_code == 201, f"Manager School user creation failed: {user_school_resp.text}"
    manager_school_user = user_school_resp.json()
    manager_school_id = manager_school_user.get("id")
    assert manager_school_id, "Manager School user ID missing"

    # Step 2: Create a workstream with this manager
    workstream_payload = {
        "name": f"Workstream {uuid.uuid4().hex[:6]}",
        "manager_id": manager_ws_id,
        "max_user": 10
    }
    workstream_resp = session.post(f"{BASE_URL}/api/workstream/", json=workstream_payload, headers=headers, timeout=TIMEOUT)
    assert workstream_resp.status_code == 201, f"Workstream creation failed: {workstream_resp.text}"
    workstream = workstream_resp.json()
    workstream_id = workstream.get("id")
    assert workstream_id, "Workstream ID missing"

    # Step 3: Create a school with workstream_id and manager_id
    school_payload = {
        "school_name": f"School {uuid.uuid4().hex[:6]}",
        "work_stream_id": workstream_id,
        "manager_id": manager_school_id
    }
    school_resp = session.post(f"{BASE_URL}/api/manager/schools/create/", json=school_payload, headers=headers, timeout=TIMEOUT)
    assert school_resp.status_code == 201, f"School creation failed: {school_resp.text}"
    school = school_resp.json()
    school_id = school.get("id")
    assert school_id, "School ID missing"

    # Now proceed with academic year CRUD operations inside try-finally to cleanup
    try:
        # Create academic year
        academic_year_payload = {
            "name": f"Academic Year {uuid.uuid4().hex[:6]}",
            "start_date": "2026-09-01",
            "end_date": "2027-06-30"
        }
        create_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/create/"
        create_resp = session.post(create_url, json=academic_year_payload, headers=headers, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Academic Year creation failed: {create_resp.text}"
        academic_year = create_resp.json()
        academic_year_id = academic_year.get("id")
        assert academic_year_id, "Academic Year ID missing"

        base_academic_year_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/"
        list_url = f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/"

        # List academic years - verify our created academic year is in list
        list_resp = session.get(list_url, headers=headers, timeout=TIMEOUT)
        assert list_resp.status_code == 200, f"Listing academic years failed: {list_resp.text}"
        academic_years = list_resp.json()
        assert any(ay.get("id") == academic_year_id for ay in academic_years), "Created academic year not found in list"

        # Get academic year detail
        get_resp = session.get(base_academic_year_url, headers=headers, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"Getting academic year details failed: {get_resp.text}"
        academic_year_detail = get_resp.json()
        assert academic_year_detail.get("id") == academic_year_id, "Academic year ID mismatch on get"

        # Update academic year (patch)
        update_payload = {
            "name": f"Updated Academic Year {uuid.uuid4().hex[:6]}"
        }
        update_resp = session.patch(base_academic_year_url, json=update_payload, headers=headers, timeout=TIMEOUT)
        assert update_resp.status_code == 200, f"Updating academic year failed: {update_resp.text}"
        updated_academic_year = update_resp.json()
        assert updated_academic_year.get("name") == update_payload["name"], "Academic year name not updated"

        # Delete academic year
        delete_resp = session.delete(base_academic_year_url, headers=headers, timeout=TIMEOUT)
        assert delete_resp.status_code == 204, f"Deleting academic year failed: {delete_resp.text}"

        # Verify academic year deletion by trying to get it (should 404)
        get_after_delete_resp = session.get(base_academic_year_url, headers=headers, timeout=TIMEOUT)
        assert get_after_delete_resp.status_code == 404, "Academic year still exists after deletion"

    finally:
        # Cleanup: Delete school
        del_school_resp = session.delete(f"{BASE_URL}/api/manager/schools/{school_id}/", headers=headers, timeout=TIMEOUT)
        if del_school_resp.status_code not in [204, 404]:
            raise AssertionError(f"Failed to delete school {school_id}: {del_school_resp.text}")

        # Delete workstream
        del_ws_resp = session.post(f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/", headers=headers, timeout=TIMEOUT)
        if del_ws_resp.status_code not in [200, 204, 404]:
            raise AssertionError(f"Failed to deactivate workstream {workstream_id}: {del_ws_resp.text}")

        # Delete manager_workstream user
        del_user_resp = session.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=headers, timeout=TIMEOUT)
        if del_user_resp.status_code not in [204, 404]:
            raise AssertionError(f"Failed to delete user {manager_ws_id}: {del_user_resp.text}")

        # Delete manager_school user
        del_user_school_resp = session.delete(f"{BASE_URL}/api/users/{manager_school_id}/", headers=headers, timeout=TIMEOUT)
        if del_user_school_resp.status_code not in [204, 404]:
            raise AssertionError(f"Failed to delete user {manager_school_id}: {del_user_school_resp.text}")

test_academic_year_crud_operations()
