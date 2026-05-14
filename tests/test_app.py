import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities():
    """Test getting all activities returns correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Should return a dictionary
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    required_keys = ["description", "schedule", "max_participants", "participants"]
    for key in required_keys:
        assert key in first_activity

    # Participants should be a list
    assert isinstance(first_activity["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Use an activity with available spots
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_duplicate():
    """Test that duplicate signup is prevented"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signup for non-existent activity returns 404"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregistration from an activity"""
    # First signup
    client.post("/activities/Programming%20Class/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]
    assert "Programming Class" in data["message"]


def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notregistered@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"]


def test_unregister_nonexistent_activity():
    """Test unregister from non-existent activity returns 404"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]