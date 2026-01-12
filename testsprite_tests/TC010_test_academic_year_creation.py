import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_academic_year_creation():
    headers = {"Content-Type": "application/json"}

    # Step 1: Admin login to get access token
    login_payload = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    try:
        login_resp = requests.post(
            f"{BASE_URL}/api/portal/auth/login/",
            json=login_payload,
            timeout=TIMEOUT,
            headers=headers,
        )
        assert login_resp.status_code == 200
        access_token = login_resp.json()["tokens"]["access"]
    except Exception as e:
        assert False, f"Admin login failed: {e}"

    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Step 2: Create a manager_workstream user
    manager_ws_payload = {
        "email": "managerws_test_academic_year@test.com",
        "full_name": "Manager Workstream AcademicYear",
        "password": "Test1234!",
        "password_confirm": "Test1234!",
        "role": "manager_workstream"
    }
    try:
        user_create_resp = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=manager_ws_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert user_create_resp.status_code == 201
        manager_ws_id = user_create_resp.json()["id"]
    except Exception as e:
        assert False, f"Manager Workstream user creation failed: {e}"

    # Step 3: Create a workstream with the above manager id
    workstream_payload = {
        "name": "Workstream AcademicYear Test",
        "manager_id": manager_ws_id,
        "max_user": 10
    }
    try:
        workstream_resp = requests.post(
            f"{BASE_URL}/api/workstream/",
            json=workstream_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert workstream_resp.status_code == 201
        workstream_id = workstream_resp.json()["id"]
    except Exception as e:
        # Clean up manager user
        requests.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=auth_headers, timeout=TIMEOUT)
        assert False, f"Workstream creation failed: {e}"

    # Step 4: Create a manager_school user
    manager_school_payload = {
        "email": "managersc_academic_year@test.com",
        "full_name": "Manager School AcademicYear",
        "password": "Test1234!",
        "password_confirm": "Test1234!",
        "role": "manager_school"
    }
    try:
        user_school_resp = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=manager_school_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert user_school_resp.status_code == 201
        manager_school_id = user_school_resp.json()["id"]
    except Exception as e:
        # Cleanup workstream and manager_ws user
        requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=auth_headers, timeout=TIMEOUT)
        assert False, f"Manager School user creation failed: {e}"

    # Step 5: Create a school with the workstream and manager_school id
    school_payload = {
        "school_name": "Academic Year Test School",
        "work_stream_id": workstream_id,
        "manager_id": manager_school_id
    }
    try:
        school_resp = requests.post(
            f"{BASE_URL}/api/manager/schools/create/",
            json=school_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert school_resp.status_code == 201
        school_id = school_resp.json()["id"]
    except Exception as e:
        # Cleanup manager_school, workstream, manager_ws users
        requests.delete(f"{BASE_URL}/api/users/{manager_school_id}/", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=auth_headers, timeout=TIMEOUT)
        assert False, f"School creation failed: {e}"

    # Step 6: Create academic year for the school
    academic_year_payload = {
        "name": "2026-2027 Academic Year",
        "start_date": "2026-09-01",
        "end_date": "2027-06-30",
        "is_active": True
    }
    try:
        academic_year_resp = requests.post(
            f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/create/",
            json=academic_year_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert academic_year_resp.status_code == 201
        academic_year_data = academic_year_resp.json()
        assert academic_year_data["name"] == academic_year_payload["name"]
        assert academic_year_data["is_active"] is True
    except Exception as e:
        # Cleanup school, manager_school, workstream, manager_ws users
        try:
            requests.delete(f"{BASE_URL}/api/manager/schools/{school_id}/", headers=auth_headers, timeout=TIMEOUT)
        except Exception:
            pass
        requests.delete(f"{BASE_URL}/api/users/{manager_school_id}/", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=auth_headers, timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=auth_headers, timeout=TIMEOUT)
        assert False, f"Academic year creation failed: {e}"

    # Cleanup all created resources
    try:
        # Delete academic year
        academic_year_id = academic_year_data.get("id")
        if academic_year_id:
            requests.delete(
                f"{BASE_URL}/api/manager/schools/{school_id}/academic-years/{academic_year_id}/",
                headers=auth_headers,
                timeout=TIMEOUT,
            )
    except Exception:
        pass

    try:
        requests.delete(f"{BASE_URL}/api/manager/schools/{school_id}/", headers=auth_headers, timeout=TIMEOUT)
    except Exception:
        pass

    try:
        requests.delete(f"{BASE_URL}/api/users/{manager_school_id}/", headers=auth_headers, timeout=TIMEOUT)
    except Exception:
        pass

    try:
        requests.delete(f"{BASE_URL}/api/workstreams/{workstream_id}/", headers=auth_headers, timeout=TIMEOUT)
    except Exception:
        pass

    try:
        requests.delete(f"{BASE_URL}/api/users/{manager_ws_id}/", headers=auth_headers, timeout=TIMEOUT)
    except Exception:
        pass


test_academic_year_creation()
