import requests
from requests.exceptions import RequestException
import datetime

BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = "/api/token/"  # Assuming a token endpoint exists at this path
ASSIGNMENTS_ENDPOINT = "/api/teacher/assignments/"

USERNAME = "g@gh.com"
PASSWORD = "1"


def get_jwt_token(username, password):
    url = f"{BASE_URL}/api/token/"
    try:
        response = requests.post(url, json={"username": username, "password": password}, timeout=30)
        response.raise_for_status()
        token = response.json().get("access")
        assert token is not None, "JWT access token not found in response"
        return token
    except RequestException as e:
        raise RuntimeError(f"Failed to obtain JWT token: {e}")


def create_assignment(token, assignment_data):
    url = f"{BASE_URL}{ASSIGNMENTS_ENDPOINT}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=assignment_data, headers=headers, timeout=30)
        response.raise_for_status()
        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create assignment: {e}")


def delete_assignment(token, assignment_id):
    url = f"{BASE_URL}{ASSIGNMENTS_ENDPOINT}{assignment_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        # 204 No Content is expected if deleted successfully
        if response.status_code not in (204, 404):  # 404 might occur if already deleted
            raise RuntimeError(f"Failed to delete assignment {assignment_id}. Status code: {response.status_code}")
    except RequestException as e:
        raise RuntimeError(f"Exception during assignment deletion: {e}")


def test_retrieve_assignment_details_by_id():
    token = get_jwt_token(USERNAME, PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # Prepare minimal valid assignment data (auto-generate code omitted)
    today = datetime.date.today().isoformat()
    assignment_data = {
        "title": "Test Retrieve Assignment",
        "exam_type": "quiz",
        "full_mark": 10.0,
        "description": "Testing assignment retrieval",
        "due_date": today,
    }

    assignment = None
    assignment_id = None

    try:
        # Create a new assignment to test retrieval
        assignment = create_assignment(token, assignment_data)
        assignment_id = assignment.get("id")
        assert assignment_id is not None, "Created assignment does not have an id"

        # 1) Test successful retrieval of the assignment details by ID
        url = f"{BASE_URL}{ASSIGNMENTS_ENDPOINT}{assignment_id}/"
        response = requests.get(url, headers=headers, timeout=30)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        data = response.json()
        # Validate returned fields match what was created
        assert data["id"] == assignment_id
        assert data["title"] == assignment_data["title"]
        assert data["exam_type"] == assignment_data["exam_type"]
        assert data["full_mark"] == str(assignment_data["full_mark"]) or data["full_mark"] == assignment_data["full_mark"]
        assert data["description"] == assignment_data["description"]
        assert data["due_date"] == assignment_data["due_date"]

        # 2) Test retrieval with non-existing assignment_id -> should return 404
        non_existing_id = 999999999
        url_non_exist = f"{BASE_URL}{ASSIGNMENTS_ENDPOINT}{non_existing_id}/"
        response_non_exist = requests.get(url_non_exist, headers=headers, timeout=30)
        assert response_non_exist.status_code == 404, f"Expected 404 Not Found for non-existing id, got {response_non_exist.status_code}"

        # 3) Test permission denied case:
        # We simulate this by trying to access the assignment with a different user token if possible.
        # Here, we try without token or with invalid token to check 403 or 401.

        # Without authentication header
        response_no_auth = requests.get(url, timeout=30)
        # Could be 401 Unauthorized or 403 Forbidden depending on implementation
        assert response_no_auth.status_code in (401, 403), f"Expected 401 or 403 without auth, got {response_no_auth.status_code}"

        # With invalid token
        headers_invalid = {"Authorization": "Bearer invalidtoken123"}
        response_invalid_auth = requests.get(url, headers=headers_invalid, timeout=30)
        assert response_invalid_auth.status_code in (401, 403), f"Expected 401 or 403 with invalid auth, got {response_invalid_auth.status_code}"

    finally:
        if assignment_id:
            try:
                delete_assignment(token, assignment_id)
            except Exception:
                pass


test_retrieve_assignment_details_by_id()