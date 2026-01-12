import requests

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "test1234"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30


def get_admin_access_token():
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["tokens"]["access"]


def create_user(token, email, full_name, password, role):
    url = f"{BASE_URL}/api/users/create/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    payload = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "password_confirm": password,
        "role": role,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    return resp


def delete_user(token, user_id):
    url = f"{BASE_URL}/api/users/{user_id}/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()


def test_user_creation_with_role_validation():
    access_token = get_admin_access_token()

    valid_role = "teacher"
    invalid_role = "invalid_role_xyz"
    email = "autotestuser+valid@example.com"
    full_name = "Auto Test User Valid"
    password = "TestPass1234!"

    # Create user with valid role
    resp_valid = create_user(access_token, email, full_name, password, valid_role)
    try:
        assert resp_valid.status_code in (201, 200), \
            f"Expected 201 or 200, got {resp_valid.status_code}"
        user = resp_valid.json()
        assert user.get("email") == email, "Email mismatch in created user"
        assert user.get("full_name") == full_name, "Full name mismatch in created user"
        assert user.get("role") == valid_role, "Role mismatch in created user"
        user_id = user.get("id")
        assert user_id is not None, "Created user missing 'id'"
    except Exception:
        # Cleanup if user created
        if resp_valid.status_code in [201, 200] and 'user_id' in locals():
            delete_user(access_token, user_id)
        raise

    # Create user with invalid role - expect error response
    email_invalid = "autotestuser+invalid@example.com"
    full_name_invalid = "Auto Test User Invalid"
    resp_invalid = create_user(access_token, email_invalid, full_name_invalid, password, invalid_role)
    # Typically, validation error returns 400 Bad Request
    assert resp_invalid.status_code == 400, f"Expected 400 for invalid role, got {resp_invalid.status_code}"
    json_response = resp_invalid.json()
    # The error should mention role field or role choices
    role_errors = json_response.get("role") or json_response.get("errors") or json_response
    assert any(
        (isinstance(role_errors, dict) and any("role" in k.lower() or "choice" in k.lower() for k in role_errors.keys()))
        or (isinstance(role_errors, list) and any("role" in e.lower() or "choice" in e.lower() for e in role_errors))
        or ("role" in str(role_errors).lower())
    ), f"Expected role validation error message, got {json_response}"

    # Cleanup created user with valid role
    delete_user(access_token, user_id)


test_user_creation_with_role_validation()
