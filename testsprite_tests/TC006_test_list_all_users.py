import requests

BASE_URL = "http://localhost:8000"
USERNAME = "admin@test.com"
PASSWORD = "test1234"
TIMEOUT = 30


def get_jwt_token():
    url = f"{BASE_URL}/api/portal/auth/login/"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "email": USERNAME,
        "password": PASSWORD
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        
        assert response.status_code == 200, f"Failed to login, expected 200 but got {response.status_code}"
        data = response.json()
        # Check for token under 'access' or 'access_token'
        access_token = data.get("access") or data.get("access_token")
        assert access_token is not None, "JWT access token not found in login response"
        return access_token
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"


def test_list_all_users():
    token = get_jwt_token()
    url = f"{BASE_URL}/api/users/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON"

    assert isinstance(data, list), f"Expected response to be a list but got {type(data)}"

    if data:
        user = data[0]
        assert isinstance(user, dict), f"Expected each user to be a dict but got {type(user)}"
        expected_keys = {"id", "email", "username", "roles"}
        missing_keys = expected_keys - user.keys()
        assert not missing_keys, f"User object missing keys: {missing_keys}"


test_list_all_users()