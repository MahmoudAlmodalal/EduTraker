import requests
import uuid

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_user_creation_with_roles():
    admin_email = "admin@test.com"
    admin_password = "test1234"
    headers = {"Content-Type": "application/json"}

    # Login as admin to get access token
    login_resp = requests.post(
        f"{BASE_URL}/api/portal/auth/login/",
        json={"email": admin_email, "password": admin_password},
        headers=headers,
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    admin_token = login_resp.json().get("tokens", {}).get("access", None)
    assert admin_token, "No admin access token received"
    auth_headers = {**headers, "Authorization": f"Bearer {admin_token}"}

    created_users = []
    try:
        # Step 1: Create a user with role manager_workstream (required to create a workstream manager)
        manager_workstream_email = f"mgr_ws_{uuid.uuid4().hex[:8]}@test.com"
        manager_workstream_payload = {
            "email": manager_workstream_email,
            "full_name": "Manager Workstream Test",
            "password": "StrongPass123!",
            "role": "manager_workstream",
        }
        resp_mgr_ws = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=manager_workstream_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_mgr_ws.status_code == 201, f"Manager workstream user creation failed: {resp_mgr_ws.text}"
        mgr_ws_user = resp_mgr_ws.json()
        manager_workstream_id = mgr_ws_user.get("id")
        assert manager_workstream_id, "No ID returned for manager_workstream user"
        created_users.append(manager_workstream_id)

        # Step 3: Create a user with role 'student' and optional fields work_stream and school omitted
        student_email = f"student_{uuid.uuid4().hex[:8]}@test.com"
        student_payload = {
            "email": student_email,
            "full_name": "Student Test",
            "password": "StrongPass123!",
            "role": "student",
        }
        resp_student = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=student_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_student.status_code == 201, f"Student user creation failed: {resp_student.text}"
        student_user = resp_student.json()
        student_id = student_user.get("id")
        assert student_id, "No ID returned for student user"
        created_users.append(student_id)

        # Step 4: Create a user with role 'teacher' (optional fields skipped)
        teacher_email = f"teacher_{uuid.uuid4().hex[:8]}@test.com"
        teacher_payload = {
            "email": teacher_email,
            "full_name": "Teacher Test",
            "password": "StrongPass123!",
            "role": "teacher",
        }
        resp_teacher = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=teacher_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_teacher.status_code == 201, f"Teacher user creation failed: {resp_teacher.text}"
        teacher_user = resp_teacher.json()
        teacher_id = teacher_user.get("id")
        assert teacher_id, "No ID returned for teacher user"
        created_users.append(teacher_id)

        # Step 5: Create a user with role 'manager_school' (optional fields skipped)
        manager_school_email = f"mgr_school_{uuid.uuid4().hex[:8]}@test.com"
        manager_school_payload = {
            "email": manager_school_email,
            "full_name": "Manager School Test",
            "password": "StrongPass123!",
            "role": "manager_school",
        }
        resp_mgr_school = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=manager_school_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_mgr_school.status_code == 201, f"Manager school user creation failed: {resp_mgr_school.text}"
        mgr_school_user = resp_mgr_school.json()
        mgr_school_id = mgr_school_user.get("id")
        assert mgr_school_id, "No ID returned for manager_school user"
        created_users.append(mgr_school_id)

        # Step 6: Create a user with role 'admin'
        admin_role_email = f"admin_role_{uuid.uuid4().hex[:8]}@test.com"
        admin_role_payload = {
            "email": admin_role_email,
            "full_name": "Admin Role Test",
            "password": "StrongPass123!",
            "role": "admin",
        }
        resp_admin_role = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=admin_role_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_admin_role.status_code == 201, f"Admin role user creation failed: {resp_admin_role.text}"
        admin_role_user = resp_admin_role.json()
        admin_role_id = admin_role_user.get("id")
        assert admin_role_id, "No ID returned for admin role user"
        created_users.append(admin_role_id)

        # Step 8: Create a user with role 'secretary'
        secretary_email = f"secretary_{uuid.uuid4().hex[:8]}@test.com"
        secretary_payload = {
            "email": secretary_email,
            "full_name": "Secretary Test",
            "password": "StrongPass123!",
            "role": "secretary",
        }
        resp_secretary = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=secretary_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_secretary.status_code == 201, f"Secretary user creation failed: {resp_secretary.text}"
        secretary_user = resp_secretary.json()
        secretary_id = secretary_user.get("id")
        assert secretary_id, "No ID returned for secretary user"
        created_users.append(secretary_id)

        # Step 9: Create a user with role 'guardian'
        guardian_email = f"guardian_{uuid.uuid4().hex[:8]}@test.com"
        guardian_payload = {
            "email": guardian_email,
            "full_name": "Guardian Test",
            "password": "StrongPass123!",
            "role": "guardian",
        }
        resp_guardian = requests.post(
            f"{BASE_URL}/api/users/create/",
            json=guardian_payload,
            headers=auth_headers,
            timeout=TIMEOUT,
        )
        assert resp_guardian.status_code == 201, f"Guardian user creation failed: {resp_guardian.text}"
        guardian_user = resp_guardian.json()
        guardian_id = guardian_user.get("id")
        assert guardian_id, "No ID returned for guardian user"
        created_users.append(guardian_id)

    finally:
        # Cleanup: delete created users to maintain test environment cleanliness
        for user_id in created_users:
            del_resp = requests.delete(
                f"{BASE_URL}/api/users/{user_id}/",
                headers=auth_headers,
                timeout=TIMEOUT,
            )
            # We allow deletion errors to pass silently to not mask original test failures
            if del_resp.status_code not in (204, 404):
                print(f"Warning: Failed to delete user {user_id}, status: {del_resp.status_code}")


test_user_creation_with_roles()
