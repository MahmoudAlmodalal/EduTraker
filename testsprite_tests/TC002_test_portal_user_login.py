import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_portal_user_login():
    url = f"{BASE_URL}/api/portal/auth/login/"
    payload = {
        "email": "admin@test.com",
        "password": "test1234"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to login failed: {e}"

    json_data = response.json()

    assert "tokens" in json_data, "Response JSON does not contain 'tokens' key"
    assert isinstance(json_data["tokens"], dict), "'tokens' should be a dictionary"
    assert "access" in json_data["tokens"], "'tokens' does not contain 'access' token"
    assert "refresh" in json_data["tokens"], "'tokens' does not contain 'refresh' token"
    assert isinstance(json_data["tokens"]["access"], str) and len(json_data["tokens"]["access"]) > 0, "'access' token should be a non-empty string"
    assert isinstance(json_data["tokens"]["refresh"], str) and len(json_data["tokens"]["refresh"]) > 0, "'refresh' token should be a non-empty string"

test_portal_user_login()