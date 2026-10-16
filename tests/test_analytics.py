import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from services.impact_calculator import calculate_material_impact

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_impact_calculator():
    # Test Plastic impact calculation
    res = calculate_material_impact("Plastic", 1000.0, 0.90)
    assert res["effective_recovered_weight_kg"] == 900.0
    assert res["metrics"]["avoided_ghg_emissions_kg_co2e"] > 0
    assert res["metrics"]["energy_saved_kwh"] > 0
    assert res["metrics"]["landfill_diverted_volume_m3"] > 0
    assert "EPA WARM" in res["methodology"]["source"]

def test_analytics_api(client):
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "headline_metrics" in data
    assert data["headline_metrics"]["total_batches_tracked"] > 0
    assert "environmental_impact" in data
    assert "material_distribution" in data

def test_advisor_insights_and_query(client):
    # Test insights
    ins_resp = client.get("/api/advisor/insights")
    assert ins_resp.status_code == 200
    ins_data = ins_resp.get_json()
    assert ins_data["status"] == "success"
    assert "insights" in ins_data

    # Test grounded query
    query_resp = client.post("/api/advisor/query", json={
        "question": "What are the contamination risks for Plastic PET?"
    })
    assert query_resp.status_code == 200
    q_data = query_resp.get_json()
    assert q_data["status"] == "success"
    assert "PVC" in q_data["data"]["answer"] or "Plastic" in q_data["data"]["answer"]
