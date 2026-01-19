import requests
import uuid

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/portal/auth/register/"
TIMEOUT = 30

def test_portal_registration_guest_user_creation():
    headers = {"Content-Type": "application/json"}

    # Test data sets for success cases
    success_payloads = [
        # Required fields only but include full_name as backend expects it
        {
            "email": f"guest_{uuid.uuid4()}@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Guest User"
        },
        # Required + first_name and last_name + full_name
        {
            "email": f"guest_{uuid.uuid4()}@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "GuestFirst",
            "last_name": "GuestLast",
            "full_name": "GuestFirst GuestLast"
        },
        # Required + full_name only
        {
            "email": f"guest_{uuid.uuid4()}@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Guest FullName"
        },
    ]

    # Test success registrations
    created_user_emails = []
    try:
        for payload in success_payloads:
            response = requests.post(
                BASE_URL + REGISTER_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=TIMEOUT
            )
            assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
            # Removed incorrect assertion on response body as PRD does not specify returning user data on registration
            created_user_emails.append(payload["email"])

        # Test validation error: password_confirm does not match password
        invalid_payload = {
            "email": f"guest_{uuid.uuid4()}@example.com",
            "password": "StrongPass123!",
            "password_confirm": "MismatchPass123!",
            "full_name": "Guest Mismatch"
        }
        resp_invalid = requests.post(
            BASE_URL + REGISTER_ENDPOINT,
            json=invalid_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp_invalid.status_code == 400, f"Expected 400 for password mismatch, got {resp_invalid.status_code}"
        error_resp = resp_invalid.json()
        error_fields = error_resp.get("password_confirm") or error_resp.get("non_field_errors") or error_resp.get("detail")
        assert error_fields is not None, f"Expected validation error detail, got: {error_resp}"

        # Test validation error: missing required fields (no password_confirm is optional, but usually recommended)
        missing_email_payload = {
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "full_name": "Missing Email"
        }
        resp_missing_email = requests.post(
            BASE_URL + REGISTER_ENDPOINT,
            json=missing_email_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp_missing_email.status_code == 400, f"Expected 400 for missing email, got {resp_missing_email.status_code}"
        error_resp = resp_missing_email.json()
        assert "email" in error_resp, f"Expected email validation error, got: {error_resp}"

        missing_password_payload = {
            "email": f"guest_{uuid.uuid4()}@example.com",
            "password_confirm": "StrongPass123!",
            "full_name": "Missing Password"
        }
        resp_missing_password = requests.post(
            BASE_URL + REGISTER_ENDPOINT,
            json=missing_password_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp_missing_password.status_code == 400, f"Expected 400 for missing password, got {resp_missing_password.status_code}"
        error_resp = resp_missing_password.json()
        assert "password" in error_resp, f"Expected password validation error, got: {error_resp}"

    finally:
        # No user deletion endpoint described for guest registration, so no cleanup possible
        pass


test_portal_registration_guest_user_creation()
