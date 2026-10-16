import pytest
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from database.db import get_db_connection

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "model_ready" in data

def test_model_status(client):
    response = client.get("/api/model-status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["model"]["is_loaded"] is True
    assert data["model"]["classes_count"] == 80

def test_sample_image_detection(client):
    response = client.post("/api/detect", json={
        "sample_path": "static/images/samples/photo_mixed.jpg",
        "confidence_threshold": 0.15
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["count"] > 0
    first_det = data["data"]["detections"][0]
    assert "bounding_box" in first_det
    assert "normalized" in first_det["bounding_box"]
    assert "pixel" in first_det["bounding_box"]
    assert "candidate_material" in first_det

def test_confirm_classification(client):
    response = client.post("/api/classifications/confirm", json={
        "detection_batch_id": "TEST-SCAN-001",
        "confirmed_category": "Plastic",
        "sub_type": "HDPE Natural Bottles",
        "estimated_weight_kg": 12.5,
        "purity_score": 0.95,
        "origin_collection_point_id": "CP-ALPHA",
        "current_facility_id": "PRP-02"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "batch_id" in data

def test_person_class_resolution(client):
    from services.waste_detector import CLASSES_17_SPECS
    assert "person" in CLASSES_17_SPECS
    res = CLASSES_17_SPECS["person"]
    assert res["is_waste"] is False
    assert res["suggested_category"] == "Uncategorized"
    assert res["co2e_factor"] == 0.0

def test_reject_person_confirmation(client):
    # Attempting to confirm a Person into the waste ledger must be rejected
    response = client.post("/api/classifications/confirm", json={
        "detection_batch_id": "TEST-PERSON-001",
        "confirmed_category": "Uncategorized",
        "sub_type": "Person (Citizen / User)",
        "estimated_weight_kg": 70.0
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "Non-waste entities cannot be logged" in data["message"]

    # Household scan endpoint must also reject person
    h_response = client.post("/api/household/scans", json={
        "item_name": "Person (Citizen / User)",
        "category": "Uncategorized",
        "estimated_weight_kg": 0.0
    })
    assert h_response.status_code == 400
    h_data = h_response.get_json()
    assert h_data["status"] == "error"
    assert "Non-waste entities cannot be logged" in h_data["message"]

