from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants for each activity to restore after test
    original = {k: v["participants"][:] for k, v in app_module.activities.items()}
    yield
    for k, v in app_module.activities.items():
        v["participants"] = original[k][:]


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # sample check
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure not present
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Confirm added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # Confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
