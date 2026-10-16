import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_digital_twin_topology(client):
    response = client.get("/api/digital-twin")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["topology"]["facilities"]) >= 5
    assert len(data["topology"]["collection_points"]) >= 4

def test_valid_batch_state_transition(client):
    # Create a batch
    confirm_resp = client.post("/api/classifications/confirm", json={
        "confirmed_category": "Metal",
        "sub_type": "Aluminum Cans",
        "estimated_weight_kg": 20.0,
        "purity_score": 0.98,
        "origin_collection_point_id": "CP-GAMMA",
        "current_facility_id": "MSR-04"
    })
    batch_id = confirm_resp.get_json()["batch_id"]

    # Valid transition: Verified -> Collected
    trans_resp = client.post(f"/api/batches/{batch_id}/transition", json={
        "target_status": "Collected",
        "notes": "Picked up by logistics truck"
    })
    assert trans_resp.status_code == 200
    assert trans_resp.get_json()["new_status"] == "Collected"

def test_invalid_batch_state_transition(client):
    # Create a batch with Verified status
    confirm_resp = client.post("/api/classifications/confirm", json={
        "confirmed_category": "Glass",
        "sub_type": "Cullet",
        "estimated_weight_kg": 50.0
    })
    batch_id = confirm_resp.get_json()["batch_id"]

    # Invalid illegal leap: Verified -> Processed (must go through Collected -> Sorted first!)
    trans_resp = client.post(f"/api/batches/{batch_id}/transition", json={
        "target_status": "Processed",
        "notes": "Attempting invalid leap"
    })
    assert trans_resp.status_code == 400
    assert "Invalid transition" in trans_resp.get_json()["message"]

def test_simulation_step_and_reset(client):
    step_resp = client.post("/api/simulation/step")
    assert step_resp.status_code == 200
    assert step_resp.get_json()["status"] == "success"

    reset_resp = client.post("/api/simulation/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.get_json()["status"] == "reset_complete"
