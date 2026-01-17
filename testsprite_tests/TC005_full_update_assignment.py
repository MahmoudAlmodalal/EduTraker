import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/portal/auth/login/"  # Fixed login URL based on server URL patterns
ASSIGNMENTS_URL = f"{BASE_URL}/api/teacher/assignments/"

USERNAME = "g@gh.com"
PASSWORD = "1"

TIMEOUT = 30


def get_jwt_token():
    """
    Obtain JWT token using username and password from assumed JWT token endpoint.
    Raise assertion error if token cannot be obtained.
    """
    token_url = LOGIN_URL
    try:
        response = requests.post(token_url, json={"username": USERNAME, "password": PASSWORD}, timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to get token, status code: {response.status_code}, resp={response.text}"
        token = response.json().get("access")
        assert token is not None, "Token not found in response"
        return token
    except requests.RequestException as e:
        raise AssertionError(f"Request exception when obtaining token: {e}")


def full_update_assignment():
    # Obtain JWT token to set in Authorization header
    token = get_jwt_token()
    assert token is not None, "JWT token must be obtained for authentication"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # First, create a new assignment to update
    create_payload = {
        "title": "Test Full Update Assignment",
        "exam_type": "assignment",
        "full_mark": 100,
        "description": "Initial description",
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        # purposely omit assignment_code to test auto-generation
    }
    assignment_id = None
    try:
        create_resp = requests.post(ASSIGNMENTS_URL, json=create_payload, headers=headers, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Expected 201 on create, got {create_resp.status_code}, resp={create_resp.text}"
        created_assignment = create_resp.json()
        assignment_id = created_assignment.get("id")
        assert assignment_id is not None, "Created assignment has no id"

        # Prepare full update payload
        # According to PRD, for PUT full update, must provide all required fields
        update_payload = {
            "title": "Updated Full Assignment Title",
            "exam_type": "quiz",
            "full_mark": 85.5,
            "description": "Updated description for full update test",
            "due_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "assignment_code": "FULLUPD20260113"
        }

        update_url = f"{ASSIGNMENTS_URL}{assignment_id}/"

        # Perform the full update with PUT
        update_resp = requests.put(update_url, json=update_payload, headers=headers, timeout=TIMEOUT)

        # Validate success response
        assert update_resp.status_code == 200, f"Expected 200 on full update, got {update_resp.status_code}, resp={update_resp.text}"
        updated_assignment = update_resp.json()

        # Validate each updated field is reflected in the response
        assert updated_assignment.get("title") == update_payload["title"], "Title not updated correctly"
        assert updated_assignment.get("exam_type") == update_payload["exam_type"], "Exam type not updated correctly"
        assert updated_assignment.get("description") == update_payload["description"], "Description not updated correctly"
        assert updated_assignment.get("due_date") == update_payload["due_date"], "Due date not updated correctly"
        assert updated_assignment.get("assignment_code") == update_payload["assignment_code"], "Assignment code not updated correctly"
        # full_mark is returned as string according to schema
        assert float(updated_assignment.get("full_mark")) == update_payload["full_mark"], "Full mark not updated correctly"

        # Test error case: invalid data - missing required field (title)
        invalid_payload = {
            "exam_type": "final",
            "full_mark": 50
        }
        error_resp = requests.put(update_url, json=invalid_payload, headers=headers, timeout=TIMEOUT)
        assert error_resp.status_code == 400, f"Expected 400 on invalid full update, got {error_resp.status_code}"

        # Test error case: unauthorized access (simulate by invalid token or no auth)
        bad_headers = {"Authorization": "Bearer invalidtoken", "Content-Type": "application/json"}
        unauthorized_resp = requests.put(update_url, json=update_payload, headers=bad_headers, timeout=TIMEOUT)
        assert unauthorized_resp.status_code in (401, 403), f"Expected 401/403 on invalid token, got {unauthorized_resp.status_code}"

        # Test error case: assignment not found (use improbable ID)
        notfound_url = f"{ASSIGNMENTS_URL}99999999/"
        notfound_resp = requests.put(notfound_url, json=update_payload, headers=headers, timeout=TIMEOUT)
        assert notfound_resp.status_code == 404, f"Expected 404 on updating non-existent assignment, got {notfound_resp.status_code}"

    finally:
        # Cleanup: delete created assignment if exists
        if assignment_id is not None:
            del_url = f"{ASSIGNMENTS_URL}{assignment_id}/"
            try:
                del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
                # Accepted status 204 No Content or 403 forbidden if permission issues
                if del_resp.status_code not in (204, 403, 404):
                    raise AssertionError(f"Unexpected delete response code: {del_resp.status_code}, resp={del_resp.text}")
            except requests.RequestException:
                pass


full_update_assignment()
