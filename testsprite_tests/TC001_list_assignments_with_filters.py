import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
ASSIGNMENTS_ENDPOINT = "/api/teacher/assignments/"

USERNAME = "g@gh.com"
PASSWORD = "1"
TIMEOUT = 30

def get_jwt_token():
    url = BASE_URL + "/api/token/"
    response = requests.post(
        url,
        json={"username": USERNAME, "password": PASSWORD},
        timeout=TIMEOUT
    )
    response.raise_for_status()
    token = response.json().get("access")
    assert token, "No access token returned"
    return token

def create_assignment(token, assignment_data):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        BASE_URL + ASSIGNMENTS_ENDPOINT,
        headers=headers,
        json=assignment_data,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()

def delete_assignment(token, assignment_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(
        f"{BASE_URL}{ASSIGNMENTS_ENDPOINT}{assignment_id}/",
        headers=headers,
        timeout=TIMEOUT
    )
    return response.status_code

def list_assignments(token, filters=None):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = filters or {}
    response = requests.get(
        BASE_URL + ASSIGNMENTS_ENDPOINT,
        headers=headers,
        params=params,
        timeout=TIMEOUT
    )
    return response

def test_list_assignments_with_filters():
    token = get_jwt_token()
    assert token is not None, "Authentication failed: No JWT token obtained."

    today_str = date.today().isoformat()
    due_date_1 = (date.today() + timedelta(days=7)).isoformat()
    due_date_2 = (date.today() + timedelta(days=14)).isoformat()

    assignment_data_1 = {
        "title": "Test Assignment for filter exam_type",
        "exam_type": "quiz",
        "full_mark": 50,
        "due_date": due_date_1,
        "description": "Assignment to test filtering by exam_type"
    }
    assignment_data_2 = {
        "title": "Second Test Assignment with unique title",
        "exam_type": "final",
        "full_mark": 100,
        "due_date": due_date_2,
        "description": "Assignment to test due_date and title filters"
    }

    created_ids = []
    try:
        created_1 = create_assignment(token, assignment_data_1)
        created_ids.append(created_1["id"])
        created_2 = create_assignment(token, assignment_data_2)
        created_ids.append(created_2["id"])

        resp = list_assignments(token)
        assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
        assignments = resp.json()
        assert isinstance(assignments, list), "Response is not a list"
        returned_ids = {item["id"] for item in assignments}
        assert created_1["id"] in returned_ids, "Created assignment 1 not in list"
        assert created_2["id"] in returned_ids, "Created assignment 2 not in list"

        resp = list_assignments(token, filters={"exam_type": "quiz"})
        assert resp.status_code == 200
        assignments = resp.json()
        assert all(item["exam_type"] == "quiz" for item in assignments)
        assert any(item["id"] == created_1["id"] for item in assignments)
        assert all(item["id"] != created_2["id"] for item in assignments)

        due_date_from = (date.today() + timedelta(days=8)).isoformat()
        resp = list_assignments(token, filters={"due_date_from": due_date_from})
        assert resp.status_code == 200
        assignments = resp.json()
        for item in assignments:
            assert item.get("due_date") >= due_date_from

        due_date_to = (date.today() + timedelta(days=10)).isoformat()
        resp = list_assignments(token, filters={"due_date_to": due_date_to})
        assert resp.status_code == 200
        assignments = resp.json()
        for item in assignments:
            assert item.get("due_date") <= due_date_to

        filter_title = "Second Test Assignment with unique title"
        resp = list_assignments(token, filters={"title": filter_title})
        assert resp.status_code == 200
        assignments = resp.json()
        assert any(item["title"] == filter_title for item in assignments)

        filters = {
            "exam_type": "final",
            "due_date_from": (date.today() + timedelta(days=10)).isoformat(),
            "title": "Second Test Assignment with unique title"
        }
        resp = list_assignments(token, filters=filters)
        assert resp.status_code == 200
        assignments = resp.json()
        for item in assignments:
            assert item["exam_type"] == "final"
            assert item["due_date"] >= filters["due_date_from"]
            assert item["title"] == filters["title"]
        assert any(item["id"] == created_2["id"] for item in assignments)

    finally:
        for aid in created_ids:
            try:
                delete_assignment(token, aid)
            except Exception:
                pass

test_list_assignments_with_filters()