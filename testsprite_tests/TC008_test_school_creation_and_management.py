import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_school_creation_and_management():
    session = requests.Session()

    def admin_login():
        url = f"{BASE_URL}/api/portal/auth/login/"
        payload = {"email": "admin@test.com", "password": "test1234"}
        resp = session.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()['tokens']['access']

    def create_user(role, email, password="Userpass123!"):
        url = f"{BASE_URL}/api/users/create/"
        payload = {
            "email": email,
            "password": password,
            "password_confirm": password,
            "role": role,
            "first_name": "Test",
            "last_name": "Manager"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def delete_user(user_id):
        url = f"{BASE_URL}/api/users/{user_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.delete(url, headers=headers, timeout=TIMEOUT)
        return resp

    def create_school(manager_id, name="Test School"):
        url = f"{BASE_URL}/api/manager/schools/create/"
        payload = {
            "name": name,
            "manager_id": manager_id,
            "address": "123 Test St",
            "phone": "1234567890",
            "email": "school@test.com"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def get_school(school_id):
        url = f"{BASE_URL}/api/manager/schools/{school_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def update_school(school_id, update_data):
        url = f"{BASE_URL}/api/manager/schools/{school_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.patch(url, json=update_data, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def delete_school(school_id):
        url = f"{BASE_URL}/api/manager/schools/{school_id}/"
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.delete(url, headers=headers, timeout=TIMEOUT)
        return resp

    admin_token = admin_login()
    # Create user with role school_manager
    school_manager_email = "schmanager_test@test.com"
    school_manager = create_user("school_manager", school_manager_email)
    school_manager_id = school_manager["id"]

    school_id = None

    try:
        # Create school
        school = create_school(manager_id=school_manager_id)
        school_id = school["id"]
        assert school["manager_id"] == school_manager_id
        assert school["name"] == "Test School"

        # Retrieve school
        school_get = get_school(school_id)
        assert school_get["id"] == school_id
        assert school_get["manager_id"] == school_manager_id
        assert school_get["name"] == "Test School"

        # Update school
        new_name = "Updated Test School"
        updated_school = update_school(school_id, {"name": new_name})
        assert updated_school["id"] == school_id
        assert updated_school["name"] == new_name

        # Verify update persisted
        school_get_after_update = get_school(school_id)
        assert school_get_after_update["name"] == new_name

    finally:
        # Cleanup: delete school
        if school_id:
            resp = delete_school(school_id)
            assert resp.status_code in [204, 200]

        # Cleanup: delete user
        if school_manager_id:
            respu = delete_user(school_manager_id)
            assert respu.status_code in [204, 200]

test_school_creation_and_management()
