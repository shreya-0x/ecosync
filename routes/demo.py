"""
EcoSync Platform Evaluation Blueprint
Provides endpoints for Executive Evaluators & Municipal Stakeholders:
- Demo status & record segregation
- Guided executive walkthrough steps
- Demo data reset & baseline re-seeding
- Clean operational mode initialization
- Preset scenarios for Digital Twin
"""

from flask import Blueprint, jsonify, request
from database.db import get_db_connection, reset_demo_data, seed_demo_household_data

demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")

@demo_bp.route("/status", methods=["GET"])
def get_demo_status():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM household_scans WHERE is_demo = 1")
        demo_household = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM household_scans WHERE is_demo = 0")
        real_household = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM waste_batches WHERE is_simulated = 1")
        sim_batches = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM waste_batches WHERE is_simulated = 0")
        real_batches = cursor.fetchone()[0]

    return jsonify({
        "status": "success",
        "demo_mode_available": True,
        "counts": {
            "demo_household_records": demo_household,
            "real_household_records": real_household,
            "simulated_facility_batches": sim_batches,
            "operational_facility_batches": real_batches
        },
        "label": "DEMO DATA",
        "notice": "Demonstration records are clearly separated and can be reset at any time."
    })

@demo_bp.route("/clean-mode", methods=["POST"])
def enable_clean_mode():
    """Initializes clean user mode by clearing seeded demo scans, ready for live citizen scans."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM household_scans WHERE is_demo = 1")
            conn.commit()
        return jsonify({
            "status": "success",
            "message": "Clean operational mode initialized. Ready for genuine live scans."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@demo_bp.route("/reset", methods=["POST"])
def reset_demo():
    """Resets all demonstration data to baseline while preserving genuine user records."""
    res = reset_demo_data()
    return jsonify(res)

@demo_bp.route("/walkthrough", methods=["GET"])
def get_walkthrough():
    """Executive Platform Walkthrough Guide."""
    return jsonify({
        "status": "success",
        "title": "EcoSync 60-Second Executive Platform Tour",
        "problem_statement": "Municipal Smart Waste Management & Circular Economy Platform",
        "steps": [
            {
                "step": 1,
                "title": "Explore Household Hub",
                "target_view": "home",
                "action": "Check real-time community stats and quick bin lookup for everyday items."
            },
            {
                "step": 2,
                "title": "Live Computer Vision Scanner",
                "target_view": "scanner",
                "action": "Click 'Water Bottles' or open live webcam. See genuine YOLO11n bounding boxes, material identification, and 8-point citizen guidance."
            },
            {
                "step": 3,
                "title": "8-Category Responsible Citizen Guide",
                "target_view": "guide",
                "action": "Search tricky items like batteries, cooking oil, or pizza boxes. Inspect safety warnings and preparation steps."
            },
            {
                "step": 4,
                "title": "Circular Waste Digital Twin",
                "target_view": "twin",
                "action": "Move the Source Segregation slider to 85%. Watch real-time Before/After scenario comparison, bottleneck alerts, and avoided emissions recalculate instantly."
            },
            {
                "step": 5,
                "title": "Household Impact & CSV Export",
                "target_view": "impact",
                "action": "Review documented EPA WARM impact metrics derived from confirmed actions and download the verified CSV report."
            },
            {
                "step": 6,
                "title": "Grounded AI Advisor",
                "target_view": "advisor",
                "action": "Tap suggestion chips (e.g. 'How do I dispose of old phone batteries?') to test AI guidance with offline fallback."
            }
        ]
    })
