import copy
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities_returns_all_activities():
    with TestClient(app_module.app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_success():
    encoded_name = quote("Chess Club", safe="")
    email = "newstudent@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.post(f"/activities/{encoded_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    encoded_name = quote("Chess Club", safe="")
    email = "daniel@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.post(f"/activities/{encoded_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_unknown_activity_returns_404():
    encoded_name = quote("Nonexistent Activity", safe="")
    email = "student@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.post(f"/activities/{encoded_name}/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success():
    encoded_name = quote("Chess Club", safe="")
    email = "daniel@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.delete(f"/activities/{encoded_name}/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_nonregistered_student_returns_400():
    encoded_name = quote("Chess Club", safe="")
    email = "missing@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.delete(f"/activities/{encoded_name}/unregister", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered"


def test_unregister_unknown_activity_returns_404():
    encoded_name = quote("Nonexistent Activity", safe="")
    email = "student@mergington.edu"

    with TestClient(app_module.app) as client:
        response = client.delete(f"/activities/{encoded_name}/unregister", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
