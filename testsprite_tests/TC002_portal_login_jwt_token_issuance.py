import requests
import jwt
import time

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/portal/auth/login/"
TIMEOUT = 30

roles_credentials = {
    "student": {"email": "student@test.com", "password": "test1234"},
    "teacher": {"email": "teacher@test.com", "password": "test1234"},
    "secretary": {"email": "secretary@test.com", "password": "test1234"},
    "manager_school": {"email": "manager_school@test.com", "password": "test1234"},
    "manager_workstream": {"email": "manager_workstream@test.com", "password": "test1234"},
    "guardian": {"email": "guardian@test.com", "password": "test1234"},
    "admin": {"email": "admin@test.com", "password": "test1234"},
    "guest": {"email": "guest@test.com", "password": "test1234"},
}

allowed_roles = {"admin", "manager_workstream"}
unauthorized_roles = {"student", "teacher", "secretary", "manager_school", "guardian", "guest"}


def test_portal_login_jwt_token_issuance():
    for role, creds in roles_credentials.items():
        response = requests.post(
            LOGIN_ENDPOINT,
            json={"email": creds["email"], "password": creds["password"]},
            timeout=TIMEOUT,
        )

        if role in allowed_roles:
            # Expect 200
            assert (
                response.status_code == 200
            ), f"Role '{role}' expected 200, got {response.status_code}, response: {response.text}"
            data = response.json()

            # Validate presence of access and refresh tokens at TOP LEVEL
            assert "access" in data, f"Role '{role}' missing access token in response"
            assert "refresh" in data, f"Role '{role}' missing refresh token in response"
            assert "user" in data, f"Role '{role}' missing user object in response"

            access_token = data["access"]
            refresh_token = data["refresh"]

            # Decode tokens without verifying signature (to check payload only)
            access_payload = jwt.decode(
                access_token, options={"verify_signature": False}, algorithms=["HS256"]
            )
            refresh_payload = jwt.decode(
                refresh_token, options={"verify_signature": False}, algorithms=["HS256"]
            )

            # Check token types
            assert access_payload.get("token_type") == "access", f"Incorrect access token type for role '{role}'"
            assert refresh_payload.get("token_type") == "refresh", f"Incorrect refresh token type for role '{role}'"

            # Check user id in token matches user id in response body user object (if present)
            if "id" in data["user"] and "user_id" in access_payload:
                user_id = str(data["user"]["id"])
                token_user_id = str(access_payload["user_id"])
                assert user_id == token_user_id, f"Mismatch between access token user_id and user object id for role '{role}'"

            # Check expiration times: access token ~1 hour, refresh token ~7 days from iat
            iat_access = access_payload.get("iat")
            exp_access = access_payload.get("exp")
            iat_refresh = refresh_payload.get("iat")
            exp_refresh = refresh_payload.get("exp")
            assert iat_access is not None and exp_access is not None, f"Missing iat or exp in access token for role '{role}'"
            assert iat_refresh is not None and exp_refresh is not None, f"Missing iat or exp in refresh token for role '{role}'"

            access_lifetime = exp_access - iat_access
            refresh_lifetime = exp_refresh - iat_refresh

            # Allow some leeway in timing (±10 seconds)
            assert 3500 <= access_lifetime <= 3700, f"Access token lifetime out of expected range for role '{role}'"
            assert 604_700 <= refresh_lifetime <= 604_900, f"Refresh token lifetime out of expected range for role '{role}'"

        else:
            # Expect 403 for unauthorized roles
            assert (
                response.status_code == 403
            ), f"Role '{role}' expected 403, got {response.status_code}, response: {response.text}"


test_portal_login_jwt_token_issuance()
