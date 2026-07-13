import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def isolate_activities():
    """Make a deep copy of the in-memory activities and restore after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_structure():
    # Arrange
    client = TestClient(app)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_adds_participant():
    # Arrange
    client = TestClient(app)
    email = "testuser@example.com"
    activity = next(iter(activities.keys()))

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_duplicate_returns_400():
    # Arrange
    client = TestClient(app)
    email = "dup@example.com"
    activity = next(iter(activities.keys()))

    # Act
    resp1 = client.post(f"/activities/{activity}/signup?email={email}")
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp1.status_code == 200
    assert resp2.status_code == 400


def test_remove_participant():
    # Arrange
    client = TestClient(app)
    email = "remove@example.com"
    activity = next(iter(activities.keys()))
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_returns_400():
    # Arrange
    client = TestClient(app)
    email = "noone@example.com"
    activity = next(iter(activities.keys()))
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert resp.status_code == 400
