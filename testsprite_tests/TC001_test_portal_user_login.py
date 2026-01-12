import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/portal/auth/login/"
TIMEOUT = 30

def test_portal_user_login():
    payload = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to portal login failed: {e}"
    json_response = response.json()
    assert "tokens" in json_response, "Response JSON does not contain 'tokens' key"
    tokens = json_response["tokens"]
    assert isinstance(tokens, dict), "'tokens' is not a dictionary"
    assert "access" in tokens, "'tokens' object does not contain 'access' token"
    assert "refresh" in tokens, "'tokens' object does not contain 'refresh' token"
    access_token = tokens["access"]
    refresh_token = tokens["refresh"]
    assert isinstance(access_token, str) and len(access_token) > 0, "'access' token is not a valid string"
    assert isinstance(refresh_token, str) and len(refresh_token) > 0, "'refresh' token is not a valid string"

test_portal_user_login()
