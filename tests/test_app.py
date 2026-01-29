import sys
from pathlib import Path

# Ensure `src` is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow(client):
    activity = "Basketball"
    email = "teststudent@mergington.edu"

    # Ensure the test email is not present first (remove if exists)
    client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert f"Signed up {email}" in signup.json().get("message", "")

    # Verify participant present
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

    # Unregister
    unregister = client.delete(f"/activities/{activity}/participants?email={email}")
    assert unregister.status_code == 200
    assert f"Unregistered {email}" in unregister.json().get("message", "")

    # Verify removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    activity = "Soccer"
    email = "dupstudent@mergington.edu"

    # Ensure clean state
    client.delete(f"/activities/{activity}/participants?email={email}")

    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    client.delete(f"/activities/{activity}/participants?email={email}")


def test_unregister_nonexistent_returns_404(client):
    activity = "Drama Club"
    email = "nonexistent@mergington.edu"

    # Ensure not present
    client.delete(f"/activities/{activity}/participants?email={email}")

    r = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r.status_code == 404
