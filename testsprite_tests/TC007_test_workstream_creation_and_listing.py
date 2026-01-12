import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_workstream_creation_and_listing():
    # Admin user credentials
    admin_credentials = {
        "email": "admin@test.com",
        "password": "test1234"
    }

    # Helper function to login and return access token
    def portal_login(email, password):
        url = f"{BASE_URL}/api/portal/auth/login/"
        response = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()['tokens']['access']

    # Helper function to create user, returns user_id
    def create_user(access_token, user_data):
        url = f"{BASE_URL}/api/users/create/"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, json=user_data, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()['id']

    # Helper function to delete user
    def delete_user(access_token, user_id):
        url = f"{BASE_URL}/api/users/{user_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code not in (204, 404):
            resp.raise_for_status()

    # Helper function to create school, returns school_id
    def create_school(access_token, school_data):
        url = f"{BASE_URL}/api/manager/schools/create/"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, json=school_data, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()['id']

    # Helper function to delete school
    def delete_school(access_token, school_id):
        url = f"{BASE_URL}/api/manager/schools/{school_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code not in (204, 404):
            resp.raise_for_status()

    # Helper function to create workstream, returns workstream_id
    def create_workstream(access_token, workstream_data):
        url = f"{BASE_URL}/api/workstream/"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, json=workstream_data, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()['id']

    # Helper function to delete workstream
    def delete_workstream(access_token, workstream_id):
        url = f"{BASE_URL}/api/workstreams/{workstream_id}/"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code not in (204, 404):
            resp.raise_for_status()

    # Login as admin to perform managerial tasks
    admin_access_token = portal_login(**admin_credentials)

    # Create a user with role 'manager_workstream'
    manager_workstream_data = {
        "email": "manager_workstream@test.com",
        "username": "manager_workstream",
        "password": "Manager123!",
        "password_confirm": "Manager123!",
        "role": "manager_workstream",
        "first_name": "Manager",
        "last_name": "Workstream"
    }
    manager_workstream_id = None
    # Create a user with role 'manager_school'
    manager_school_data = {
        "email": "manager_school@test.com",
        "username": "manager_school",
        "password": "Manager123!",
        "password_confirm": "Manager123!",
        "role": "manager_school",
        "first_name": "Manager",
        "last_name": "School"
    }
    manager_school_id = None
    school_id = None
    workstream_id = None

    try:
        manager_workstream_id = create_user(admin_access_token, manager_workstream_data)
        manager_school_id = create_user(admin_access_token, manager_school_data)

        # Create School with manager_id = manager_school_id
        school_payload = {
            "name": "Test School",
            "address": "123 Test St",
            "manager_id": manager_school_id
        }
        school_id = create_school(admin_access_token, school_payload)

        # Create Workstream with manager_id = manager_workstream_id and attached school_id
        workstream_payload = {
            "name": "Test Workstream",
            "description": "Workstream for testing",
            "manager_id": manager_workstream_id,
            "schools": [school_id]
        }
        workstream_id = create_workstream(admin_access_token, workstream_payload)

        # Validate creation response by fetching workstream details
        url = f"{BASE_URL}/api/workstreams/{workstream_id}/"
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        workstream = resp.json()
        assert workstream['id'] == workstream_id
        assert workstream['manager_id'] == manager_workstream_id
        assert workstream['name'] == "Test Workstream"
        assert school_id in workstream.get('schools', [])

        # List workstreams and verify the created workstream is in the list
        url = f"{BASE_URL}/api/workstream/"
        list_resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        list_resp.raise_for_status()
        workstreams_list = list_resp.json()
        assert any(ws['id'] == workstream_id for ws in workstreams_list)

    finally:
        # Cleanup
        if workstream_id:
            try:
                delete_workstream(admin_access_token, workstream_id)
            except Exception:
                pass
        if school_id:
            try:
                delete_school(admin_access_token, school_id)
            except Exception:
                pass
        if manager_school_id:
            try:
                delete_user(admin_access_token, manager_school_id)
            except Exception:
                pass
        if manager_workstream_id:
            try:
                delete_user(admin_access_token, manager_workstream_id)
            except Exception:
                pass

test_workstream_creation_and_listing()
