import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_academic_year_crud_operations():
    headers = {"Content-Type": "application/json"}

    # Step 1: Login as admin to get access token
    login_data = {
        "username": "admin@test.com",
        "password": "test1234"
    }
    login_resp = requests.post(f"{BASE_URL}/api/portal/auth/login/", json=login_data, timeout=TIMEOUT)
    assert login_resp.status_code == 200, "Admin login failed"
    access_token = login_resp.json()['tokens']['access']
    auth_headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Step 2: Create a user with role 'manager_school' to use as manager_id for school creation
    user_payload = {
        "email": "school_manager_for_academic_year_test@test.com",
        "password": "Password123!",
        "password_confirm": "Password123!",
        "role": "manager_school",
        "first_name": "Manager",
        "last_name": "School"
    }
    user_resp = requests.post(f"{BASE_URL}/api/users/create/", json=user_payload, headers=auth_headers, timeout=TIMEOUT)
    assert user_resp.status_code == 201, f"Failed to create manager_school user: {user_resp.text}"
    manager_user = user_resp.json()
    manager_id = manager_user["id"]

    try:
        # Step 3: Create a school with the created manager_id
        school_payload = {
            "name": "Test School for Academic Year",
            "manager_id": manager_id,
            "address": "123 Test St",
            "description": "Test school description"
        }
        school_resp = requests.post(f"{BASE_URL}/api/manager/schools/create/", json=school_payload, headers=auth_headers, timeout=TIMEOUT)
        assert school_resp.status_code == 201, f"Failed to create school: {school_resp.text}"
        school = school_resp.json()
        school_id = school["id"]

        try:
            # Step 4: CREATE Academic Year
            academic_year_payload = {
                "name": "2026-2027",
                "start_date": "2026-09-01",
                "end_date": "2027-06-30"
            }
            create_ay_resp = requests.post(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/create/",
                json=academic_year_payload,
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert create_ay_resp.status_code == 201, f"Failed to create academic year: {create_ay_resp.text}"
            academic_year = create_ay_resp.json()
            academic_year_id = academic_year["id"]

            # Step 5: RETRIEVE Academic Year
            get_ay_resp = requests.get(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/",
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert get_ay_resp.status_code == 200, f"Failed to get academic year: {get_ay_resp.text}"
            retrieved_ay = get_ay_resp.json()
            assert retrieved_ay["name"] == academic_year_payload["name"], "Academic year name mismatch"
            assert retrieved_ay["start_date"] == academic_year_payload["start_date"], "Start date mismatch"
            assert retrieved_ay["end_date"] == academic_year_payload["end_date"], "End date mismatch"

            # Step 6: UPDATE Academic Year
            update_payload = {
                "name": "2026-2027 Updated",
                "end_date": "2027-07-15"
            }
            update_ay_resp = requests.patch(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/",
                json=update_payload,
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert update_ay_resp.status_code == 200, f"Failed to update academic year: {update_ay_resp.text}"
            updated_ay = update_ay_resp.json()
            assert updated_ay["name"] == update_payload["name"], "Academic year name update failed"
            assert updated_ay["end_date"] == update_payload["end_date"], "Academic year end date update failed"

            # Step 7: DELETE Academic Year
            delete_ay_resp = requests.delete(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/",
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert delete_ay_resp.status_code == 204, f"Failed to delete academic year: {delete_ay_resp.text}"

            # Step 8: Verify deletion by attempting to get the deleted academic year
            verify_deleted_resp = requests.get(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/",
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert verify_deleted_resp.status_code == 404, "Deleted academic year still accessible"

        finally:
            # Clean up: Delete the school
            delete_school_resp = requests.delete(
                f"{BASE_URL}/api/manager/schools/{school_id}/",
                headers=auth_headers,
                timeout=TIMEOUT
            )
            assert delete_school_resp.status_code == 204, f"Failed to delete school: {delete_school_resp.text}"

    finally:
        # Clean up: Delete the manager_school user
        delete_user_resp = requests.delete(
            f"{BASE_URL}/api/users/{manager_id}/",
            headers=auth_headers,
            timeout=TIMEOUT
        )
        assert delete_user_resp.status_code == 204, f"Failed to delete manager_school user: {delete_user_resp.text}"

test_academic_year_crud_operations()