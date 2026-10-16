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

def test_waste_categories(client):
    response = client.get("/api/waste-guide/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["categories"]) == 8
    cat_names = [c["name"] for c in data["categories"]]
    assert "Recyclable materials" in cat_names
    assert "Organic and biodegradable waste" in cat_names
    assert "Hazardous waste" in cat_names
    assert "Electronic waste" in cat_names
    assert "Municipal solid waste" in cat_names

def test_waste_guide_search(client):
    # Search for bottle
    response = client.get("/api/waste-guide?q=bottle")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    first = data["items"][0]
    assert "how_to_prepare" in first["guide"] or "what_to_do_now" in first["guide"]

def test_waste_guide_item_detail(client):
    response = client.get("/api/waste-guide/item/plastic_bottle")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    item = data["item"]
    guide = item["guide"]
    assert "what_is_it" in guide
    assert "what_to_do_now" in guide
    assert "which_bin" in guide
    assert "how_to_prepare" in guide
    assert "what_to_avoid" in guide
    assert "where_should_it_go" in guide
    assert "why_matters" in guide
    assert "citizen_action" in guide

def test_scenario_simulation_endpoint(client):
    response = client.post("/api/simulation/scenario", json={
        "daily_volume_tons": 250.0,
        "segregation_rate_pct": 75.0,
        "collection_capacity_tpd": 300.0,
        "processing_capacity_tpd": 200.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["is_simulation"] is True
    assert "diversion_rate_pct" in data["metrics"]
    assert "collection_utilization_pct" in data["metrics"]
    assert "recommendation" in data

def test_household_impact_and_history(client):
    # Confirm a household item
    client.post("/api/classifications/confirm", json={
        "item_name": "PET Mineral Water Bottle",
        "confirmed_category": "Recyclable materials",
        "material": "PET #1 Plastic",
        "confidence": 0.94,
        "action_taken": "Rinsed & Placed in Blue Bin",
        "estimated_weight_kg": 0.025
    })

    # Test household impact endpoint
    impact_resp = client.get("/api/household/impact")
    assert impact_resp.status_code == 200
    imp = impact_resp.get_json()
    assert imp["status"] == "success"
    assert "household_metrics" in imp
    assert imp["household_metrics"]["total_items_confirmed"] > 0
    assert "verification_separation" in imp
    assert "methodology" in imp

    # Test history endpoint
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200
    hist = hist_resp.get_json()
    assert hist["status"] == "success"
    assert hist["count"] > 0
