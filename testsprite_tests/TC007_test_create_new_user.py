import requests

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin@test.com"
AUTH_PASSWORD = "test1234"
TIMEOUT = 30


def get_jwt_token(username, password):
    url = f"{BASE_URL}/api/portal/auth/login/"
    headers = {"Content-Type": "application/json"}
    data = {"email": username, "password": password}
    response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    json_data = response.json()
    if "access" in json_data:
        return json_data["access"]
    elif "token" in json_data:
        return json_data["token"]
    else:
        assert False, "No access token found in login response"


def test_create_new_user():
    token = get_jwt_token(AUTH_USERNAME, AUTH_PASSWORD)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    url = f"{BASE_URL}/api/users/create/"

    user_data = {
        "email": "newuser@example.com",
        "password": "StrongPassw0rd!",
        "first_name": "New",
        "last_name": "User",
        "role": "Teacher"
    }

    response = None
    created_user_id = None

    try:
        response = requests.post(url, json=user_data, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201, f"Expected status 201 Created but got {response.status_code}"
        response_data = response.json()
        assert "id" in response_data, "Response JSON must contain 'id'"
        created_user_id = response_data["id"]
        assert response_data.get("email") == user_data["email"], "Email in response does not match request"
        assert response_data.get("first_name") == user_data["first_name"], "First name in response does not match request"
        assert response_data.get("last_name") == user_data["last_name"], "Last name in response does not match request"
        assert response_data.get("role") == user_data["role"], "Role in response does not match request"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"
    except ValueError:
        assert False, "Response content is not valid JSON"
    finally:
        if created_user_id:
            try:
                delete_url = f"{BASE_URL}/api/users/{created_user_id}/"
                del_response = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                assert del_response.status_code in (204, 200), f"Failed to delete user, status code: {del_response.status_code}"
            except Exception:
                pass


test_create_new_user()