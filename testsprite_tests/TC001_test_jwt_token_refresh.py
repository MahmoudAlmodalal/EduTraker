import requests

BASE_URL = "http://localhost:8000"
ADMIN_AUTH = ("admin@test.com", "test1234")
TIMEOUT = 30


def test_jwt_token_refresh():
    session = requests.Session()

    # Step 1: Login as admin to obtain refresh token
    login_url = f"{BASE_URL}/api/portal/auth/login/"
    login_payload = {
        "email": ADMIN_AUTH[0],
        "password": ADMIN_AUTH[1]
    }
    try:
        login_resp = session.post(login_url, json=login_payload, timeout=TIMEOUT)
        login_resp.raise_for_status()
        tokens = login_resp.json().get("tokens", {})
        assert "access" in tokens and "refresh" in tokens, "Login response missing tokens"
        refresh_token = tokens["refresh"]

        # Step 2: Use refresh token to get new access token
        refresh_url = f"{BASE_URL}/api/auth/token/refresh/"
        refresh_payload = {"refresh": refresh_token}
        refresh_resp = session.post(refresh_url, json=refresh_payload, timeout=TIMEOUT)
        refresh_resp.raise_for_status()
        refreshed_tokens = refresh_resp.json()
        assert "access" in refreshed_tokens, "Refresh response missing new access token"

        new_access_token = refreshed_tokens["access"]
        assert isinstance(new_access_token, str) and len(new_access_token) > 0, "Invalid new access token"

    except requests.RequestException as e:
        assert False, f"Request failed: {str(e)}"


test_jwt_token_refresh()