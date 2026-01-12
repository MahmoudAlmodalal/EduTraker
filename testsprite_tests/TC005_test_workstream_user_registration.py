import requests


BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
TIMEOUT = 30


def test_workstream_user_registration():
    session = requests.Session()
    try:
        # Admin login to get access token
        login_resp = session.post(
            f"{BASE_URL}/api/portal/auth/login/",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        admin_access_token = login_resp.json()["tokens"]["access"]

        headers_admin = {"Authorization": f"Bearer {admin_access_token}"}

        # Create a user with role manager_workstream (required to create workstream)
        manager_email = "workstream_manager@test.com"
        manager_password = "ManWrk123!"
        create_manager_resp = session.post(
            f"{BASE_URL}/api/users/create/",
            headers=headers_admin,
            json={
                "email": manager_email,
                "full_name": "Workstream Manager",
                "password": manager_password,
                "role": "manager_workstream",
            },
            timeout=TIMEOUT,
        )
        assert create_manager_resp.status_code == 201, f"Manager user creation failed: {create_manager_resp.text}"
        manager_user = create_manager_resp.json()
        manager_id = manager_user["id"]

        # Create a workstream with required fields
        workstream_name = "Test Workstream Registration"
        max_user = 10
        create_workstream_resp = session.post(
            f"{BASE_URL}/api/workstream/",
            headers=headers_admin,
            json={
                "name": workstream_name,
                "manager_id": manager_id,
                "max_user": max_user,
            },
            timeout=TIMEOUT,
        )
        assert create_workstream_resp.status_code == 201, f"Workstream creation failed: {create_workstream_resp.text}"
        workstream = create_workstream_resp.json()
        workstream_id = workstream["id"]

        # Test successful registration where password and password_confirm match
        registration_url = f"{BASE_URL}/api/workstream/{workstream_id}/auth/register/"
        user_email = "newuser@test.com"
        user_full_name = "New Workstream User"
        user_password = "StrongPass123"
        user_role = "student"

        success_reg_resp = session.post(
            registration_url,
            json={
                "email": user_email,
                "full_name": user_full_name,
                "password": user_password,
                "password_confirm": user_password,
                "role": user_role,
            },
            timeout=TIMEOUT,
        )
        assert success_reg_resp.status_code == 201, f"Successful registration failed: {success_reg_resp.text}"
        success_reg_json = success_reg_resp.json()
        assert "user" in success_reg_json, "'user' not in success response"
        registered_user = success_reg_json["user"]
        assert registered_user.get("full_name") == user_full_name, "Registered user full_name mismatch"

        # Test failed registration when password and password_confirm do not match
        fail_reg_resp = session.post(
            registration_url,
            json={
                "email": "failuser@test.com",
                "full_name": "Fail User",
                "password": "Password123",
                "password_confirm": "Password321",
                "role": "student",
            },
            timeout=TIMEOUT,
        )
        assert fail_reg_resp.status_code == 400, f"Registration with mismatched password did not fail properly: {fail_reg_resp.text}"
        fail_json = fail_reg_resp.json()
        # Expecting some error about password confirmation mismatch in response
        password_confirm_errors = fail_json.get("password_confirm") or fail_json.get("non_field_errors") or {}
        assert password_confirm_errors, "No error info about password_confirm mismatch"

    finally:
        # Cleanup: Delete created users and workstream to avoid residual data

        # Delete registered user (successful registration)
        try:
            # Need to find ID of registered user from success_reg_json if available
            reg_user_id = success_reg_json["user"]["id"]
            del_user_resp = session.delete(
                f"{BASE_URL}/api/users/{reg_user_id}/",
                headers=headers_admin,
                timeout=TIMEOUT,
            )
            assert del_user_resp.status_code in (200, 204), f"Failed to delete registered user: {del_user_resp.text}"
        except Exception:
            pass

        # Delete workstream manager user
        try:
            del_manager_resp = session.delete(
                f"{BASE_URL}/api/users/{manager_id}/",
                headers=headers_admin,
                timeout=TIMEOUT,
            )
            assert del_manager_resp.status_code in (200, 204), f"Failed to delete manager user: {del_manager_resp.text}"
        except Exception:
            pass

        # Delete workstream
        try:
            del_workstream_resp = session.delete(
                f"{BASE_URL}/api/workstreams/{workstream_id}/",
                headers=headers_admin,
                timeout=TIMEOUT,
            )
            # If DELETE endpoint not supported, ignore failure here
            if del_workstream_resp.status_code not in (200, 204):
                # Alternative: try deactivate if delete unsupported
                patch_resp = session.post(
                    f"{BASE_URL}/api/workstreams/{workstream_id}/deactivate/",
                    headers=headers_admin,
                    timeout=TIMEOUT,
                )
                assert patch_resp.status_code in (200, 204), f"Failed to deactivate workstream: {patch_resp.text}"
        except Exception:
            pass


test_workstream_user_registration()