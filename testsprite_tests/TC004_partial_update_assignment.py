import requests

BASE_URL = "http://localhost:8000"
AUTH_CREDENTIALS = {"username": "g@gh.com", "password": "1"}
TIMEOUT = 30

def get_jwt_token():
    url = f"{BASE_URL}/api/token/"
    resp = requests.post(url, json=AUTH_CREDENTIALS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["access"]

def create_assignment(token):
    url = f"{BASE_URL}/api/teacher/assignments/"
    payload = {
        "title": "Test Assignment for Patch",
        "exam_type": "quiz",
        "full_mark": 10.0,
        "description": "Initial description",
        "due_date": "2026-12-31"
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def delete_assignment(token, assignment_id):
    url = f"{BASE_URL}/api/teacher/assignments/{assignment_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers, timeout=TIMEOUT)
    # no error if already deleted or not found, ignore errors on delete
    return response.status_code

def patch_assignment(token, assignment_id, patch_data):
    url = f"{BASE_URL}/api/teacher/assignments/{assignment_id}/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    resp = requests.patch(url, json=patch_data, headers=headers, timeout=TIMEOUT)
    return resp

def test_partial_update_assignment():
    token = get_jwt_token()
    assignment = None
    try:
        # Create a new assignment to patch
        assignment = create_assignment(token)
        assignment_id = assignment['id']

        # Valid partial update data
        patch_data = {
            "title": "Updated Title - Partial Patch",
            "full_mark": 15.5
        }
        resp = patch_assignment(token, assignment_id, patch_data)
        assert resp.status_code == 200, f"Expected 200 but got {resp.status_code}"
        data = resp.json()
        assert data['id'] == assignment_id
        assert data['title'] == patch_data['title']
        assert float(data['full_mark']) == patch_data['full_mark']

        # Validation error: invalid exam_type enum value
        invalid_data = {"exam_type": "invalid_enum"}
        resp_err = patch_assignment(token, assignment_id, invalid_data)
        assert resp_err.status_code == 400

        # Validation error: full_mark less than minimum
        invalid_data = {"full_mark": 0}
        resp_err = patch_assignment(token, assignment_id, invalid_data)
        assert resp_err.status_code == 400

        # Permission denied: simulate by using an invalid token
        bad_token = "invalidtoken"
        url = f"{BASE_URL}/api/teacher/assignments/{assignment_id}/"
        headers = {
            "Authorization": f"Bearer {bad_token}",
            "Content-Type": "application/json"
        }
        resp_perm = requests.patch(url, json=patch_data, headers=headers, timeout=TIMEOUT)
        assert resp_perm.status_code in [401, 403]

        # Assignment not found
        nonexistent_id = 999999999
        resp_404 = patch_assignment(token, nonexistent_id, patch_data)
        assert resp_404.status_code == 404

    finally:
        # Clean up the created assignment
        if assignment:
            delete_assignment(token, assignment['id'])

test_partial_update_assignment()
