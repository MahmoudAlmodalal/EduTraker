import requests
import uuid

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token/"
ASSIGNMENTS_URL = f"{BASE_URL}/api/teacher/assignments/"

USERNAME = "g@gh.com"
PASSWORD = "1"
TIMEOUT = 30

def get_jwt_token(username, password):
    try:
        resp = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        token = resp.json().get("access")
        assert token is not None, "No access token returned"
        return token
    except Exception as e:
        raise RuntimeError(f"Failed to obtain JWT token: {e}")

def create_assignment(token):
    assignment_data = {
        "title": f"Test Delete Assignment {uuid.uuid4()}",
        "exam_type": "assignment",
        "full_mark": 10.0,
        "description": "Temporary assignment for delete test."
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(
            ASSIGNMENTS_URL,
            json=assignment_data,
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        assert resp.status_code == 201, f"Expected 201 Created, got {resp.status_code}"
        data = resp.json()
        assert "id" in data, "Created assignment response missing 'id'"
        return data["id"]
    except Exception as e:
        raise RuntimeError(f"Failed to create assignment: {e}")

def delete_assignment(token, assignment_id):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.delete(
            f"{ASSIGNMENTS_URL}{assignment_id}/",
            headers=headers,
            timeout=TIMEOUT
        )
        return resp
    except Exception as e:
        raise RuntimeError(f"Failed to delete assignment: {e}")

def test_delete_assignment_permanently():
    token = get_jwt_token(USERNAME, PASSWORD)
    assignment_id = None
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new assignment to delete
    assignment_id = create_assignment(token)

    try:
        # Delete the created assignment
        response = delete_assignment(token, assignment_id)
        assert response.status_code == 204, f"Expected 204 No Content on delete, got {response.status_code}"
        # Confirm deletion by attempting to retrieve the deleted assignment
        get_resp = requests.get(
            f"{ASSIGNMENTS_URL}{assignment_id}/",
            headers=headers,
            timeout=TIMEOUT
        )
        assert get_resp.status_code == 404, f"Expected 404 Not Found for deleted assignment, got {get_resp.status_code}"

        # Test deleting non-existent assignment returns 404
        non_existent_id = 99999999
        del_resp = delete_assignment(token, non_existent_id)
        assert del_resp.status_code == 404, f"Expected 404 Not Found for deleting non-existent assignment, got {del_resp.status_code}"

        # Optional: Test deleting assignment without permission - this would require setup of another user's assignment,
        # skipping since test data is limited to own assignments only.

    finally:
        # Cleanup: assignment should be deleted by test, but if not due to failure, try to delete forcibly
        if assignment_id is not None:
            try:
                delete_assignment(token, assignment_id)
            except Exception:
                pass

test_delete_assignment_permanently()