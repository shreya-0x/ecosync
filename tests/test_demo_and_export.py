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

def test_demo_status_endpoint(client):
    response = client.get("/api/demo/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["demo_mode_available"] is True
    assert "counts" in data
    assert data["counts"]["demo_household_records"] >= 0

def test_demo_walkthrough_endpoint(client):
    response = client.get("/api/demo/walkthrough")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["steps"]) >= 5

def test_demo_reset_endpoint(client):
    response = client.post("/api/demo/reset")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"

def test_csv_export_endpoint(client):
    response = client.get("/api/history/export")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Content-Disposition" in response.headers
    assert "ecosync_household_waste_impact_history.csv" in response.headers["Content-Disposition"]
    csv_text = response.data.decode("utf-8")
    assert "Scan ID,Item Name,Category" in csv_text

def test_scenario_comparison_output(client):
    response = client.post("/api/simulation/scenario", json={
        "daily_volume_tons": 200.0,
        "segregation_rate_pct": 85.0,
        "collection_capacity_tpd": 260.0,
        "processing_capacity_tpd": 220.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "comparison" in data
    comp = data["comparison"]
    assert "baseline" in comp
    assert "scenario" in comp
    assert "deltas" in comp
    assert "diversion_rate_diff_pct" in comp["deltas"]
    assert "landfill_avoided_diff_tons" in comp["deltas"]

def test_all_eight_categories_covered(client):
    # Verify waste guide items cover all 8 categories
    categories_resp = client.get("/api/waste-guide/categories")
    cat_data = categories_resp.get_json()["categories"]
    assert len(cat_data) == 8

    guide_resp = client.get("/api/waste-guide")
    items = guide_resp.get_json()["items"]
    present_cats = set(item["category"] for item in items)
    for c in cat_data:
        assert c["name"] in present_cats, f"Category '{c['name']}' has no items in waste guide"
