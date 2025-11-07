import copy
import importlib

from fastapi.testclient import TestClient


appmod = importlib.import_module("src.app")
client = TestClient(appmod.app)


def setup_function(function):
    # snapshot original activities so tests can mutate safely
    function._orig_activities = copy.deepcopy(appmod.activities)


def teardown_function(function):
    # restore original activities after each test
    appmod.activities.clear()
    appmod.activities.update(function._orig_activities)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    email = "pytest.user@example.com"
    activity = "Chess Club"

    # Ensure not present initially
    assert email not in appmod.activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify present
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    data = resp2.json()
    assert email in data[activity]["participants"]

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp3.status_code == 200
    assert "Unregistered" in resp3.json().get("message", "")

    # Verify removed
    resp4 = client.get("/activities")
    assert resp4.status_code == 200
    assert email not in resp4.json()[activity]["participants"]
