import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
EMAIL = "admin@test.com"
PASSWORD = "test1234"

def test_jwt_token_refresh():
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    refresh_url = f"{BASE_URL}/api/auth/token/refresh/"

    # Login to get access and refresh tokens
    login_payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        login_response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    login_data = login_response.json()
    assert "access" in login_data, "Login response missing access token"
    assert "refresh" in login_data, "Login response missing refresh token"
    refresh_token = login_data["refresh"]

    # Use refresh token to get a new access token
    refresh_payload = {
        "refresh": refresh_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        refresh_response = requests.post(refresh_url, json=refresh_payload, headers=headers, timeout=TIMEOUT)
        refresh_response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Token refresh request failed: {e}"

    refresh_data = refresh_response.json()
    assert "access" in refresh_data, "Refresh response missing new access token"
    new_access_token = refresh_data["access"]
    assert isinstance(new_access_token, str) and new_access_token, "New access token should be a non-empty string"
    assert new_access_token != login_data["access"], "New access token should differ from old one"


test_jwt_token_refresh()
