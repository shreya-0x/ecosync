import json
from flask import Blueprint, request, jsonify
from database.db import get_db_connection
from services.simulation_engine import SimulationEngine

digital_twin_bp = Blueprint("digital_twin", __name__, url_prefix="/api")

# Valid lifecycle state machine
LIFECYCLE_SEQUENCE = ["Detected", "Classified", "Verified", "Collected", "Sorted", "Processed"]
VALID_TRANSITIONS = {
    "Detected": ["Classified"],
    "Classified": ["Verified"],
    "Verified": ["Collected"],
    "Collected": ["Sorted"],
    "Sorted": ["Processed"],
    "Processed": []
}

@digital_twin_bp.route("/digital-twin", methods=["GET"])
def get_digital_twin_state():
    """Returns the full topology and operational state of the EcoSync digital twin."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Facilities
        cursor.execute("SELECT * FROM facilities ORDER BY id ASC")
        facilities = [dict(row) for row in cursor.fetchall()]

        # 2. Collection Points
        cursor.execute("SELECT * FROM collection_points ORDER BY id ASC")
        collection_points = [dict(row) for row in cursor.fetchall()]

        # 3. Active Batches
        cursor.execute("""
            SELECT id, material_category, sub_type, estimated_weight_kg, purity_score, 
                   status, origin_collection_point_id, current_facility_id, is_simulated, updated_at
            FROM waste_batches 
            ORDER BY updated_at DESC LIMIT 50
        """)
        batches = [dict(row) for row in cursor.fetchall()]

        # 4. Topology Links / Material Flow Routes
        links = [
            {"source": "CP-ALPHA", "target": "MRF-01", "type": "feed", "label": "Bulk Municipal Transport"},
            {"source": "CP-BETA", "target": "MRF-01", "type": "feed", "label": "Logistics Route Alpha"},
            {"source": "CP-GAMMA", "target": "MRF-01", "type": "feed", "label": "Downtown Express Route"},
            {"source": "CP-DELTA", "target": "MRF-01", "type": "feed", "label": "Industrial Yard Transit"},
            {"source": "MRF-01", "target": "PRP-02", "type": "inter-facility", "label": "Polymer Flake Transit (Plastics)"},
            {"source": "MRF-01", "target": "FPU-03", "type": "inter-facility", "label": "OCC & Fiber Slurry Transit (Paper)"},
            {"source": "MRF-01", "target": "MSR-04", "type": "inter-facility", "label": "Ferrous/Non-Ferrous Shred (Metals)"},
            {"source": "MRF-01", "target": "GBC-05", "type": "inter-facility", "label": "Optical Cullet Stream (Glass)"}
        ]

        # 5. Pipeline stage counts
        cursor.execute("SELECT status, COUNT(*), SUM(estimated_weight_kg) FROM waste_batches GROUP BY status")
        stage_summary = {
            stage: {"count": 0, "weight_kg": 0.0} for stage in LIFECYCLE_SEQUENCE
        }
        for row in cursor.fetchall():
            st, cnt, w = row[0], row[1], row[2]
            if st in stage_summary:
                stage_summary[st] = {"count": cnt, "weight_kg": round(w or 0.0, 1)}

    return jsonify({
        "status": "success",
        "topology": {
            "facilities": facilities,
            "collection_points": collection_points,
            "flow_links": links
        },
        "stage_summary": stage_summary,
        "recent_batches": batches,
        "simulation": SimulationEngine.get_status()
    })

@digital_twin_bp.route("/facilities", methods=["GET"])
def get_facilities():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facilities ORDER BY id ASC")
        facilities = [dict(row) for row in cursor.fetchall()]
    return jsonify({"status": "success", "facilities": facilities})

@digital_twin_bp.route("/batches", methods=["GET"])
def get_batches():
    material = request.args.get("material")
    status = request.args.get("status")
    facility = request.args.get("facility")
    simulated = request.args.get("simulated") # '1', '0', or None

    query = "SELECT * FROM waste_batches WHERE 1=1"
    params = []

    if material:
        query += " AND material_category = ?"
        params.append(material)
    if status:
        query += " AND status = ?"
        params.append(status)
    if facility:
        query += " AND current_facility_id = ?"
        params.append(facility)
    if simulated in ("0", "1"):
        query += " AND is_simulated = ?"
        params.append(int(simulated))

    query += " ORDER BY updated_at DESC LIMIT 100"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        batches = [dict(row) for row in cursor.fetchall()]

    return jsonify({"status": "success", "batches": batches, "count": len(batches)})

@digital_twin_bp.route("/batches/<batch_id>", methods=["GET"])
def get_batch_detail(batch_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM waste_batches WHERE id = ?", (batch_id,))
        batch = cursor.fetchone()
        if not batch:
            return jsonify({"status": "error", "message": f"Batch '{batch_id}' not found."}), 404

        cursor.execute("SELECT * FROM batch_audit_log WHERE batch_id = ? ORDER BY timestamp ASC", (batch_id,))
        audit_log = [dict(row) for row in cursor.fetchall()]

    data = dict(batch)
    data["audit_log"] = audit_log
    data["next_valid_states"] = VALID_TRANSITIONS.get(data["status"], [])
    return jsonify({"status": "success", "data": data})

@digital_twin_bp.route("/batches/<batch_id>/transition", methods=["POST"])
def transition_batch(batch_id):
    """
    Validates and executes an operational state transition.
    Enforces that invalid state leaps are rejected with clear explanation.
    """
    body = request.get_json() or {}
    target_status = body.get("target_status")
    notes = body.get("notes", "Manual state transition via Digital Twin control.")
    actor = body.get("actor", "Operations Supervisor")

    if not target_status:
        return jsonify({"status": "error", "message": "target_status is required."}), 400

    if target_status not in LIFECYCLE_SEQUENCE:
        return jsonify({
            "status": "error", 
            "message": f"Invalid status '{target_status}'. Must be one of: {', '.join(LIFECYCLE_SEQUENCE)}"
        }), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, is_simulated FROM waste_batches WHERE id = ?", (batch_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": f"Batch '{batch_id}' not found."}), 404

        current_status = row["status"]
        valid_next = VALID_TRANSITIONS.get(current_status, [])

        if target_status not in valid_next:
            return jsonify({
                "status": "error",
                "message": f"Invalid transition: Cannot move batch from '{current_status}' to '{target_status}'. Valid next state(s): {', '.join(valid_next) if valid_next else 'None (Terminal state)'}"
            }), 400

        # Update batch status
        cursor.execute("""
            UPDATE waste_batches 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (target_status, batch_id))

        # Record in audit log
        cursor.execute("""
            INSERT INTO batch_audit_log (batch_id, previous_status, new_status, notes, actor)
            VALUES (?, ?, ?, ?, ?)
        """, (batch_id, current_status, target_status, notes, actor))

        conn.commit()

    return jsonify({
        "status": "success",
        "message": f"Batch '{batch_id}' successfully transitioned from '{current_status}' to '{target_status}'.",
        "previous_status": current_status,
        "new_status": target_status
    })

# Simulation Controls
@digital_twin_bp.route("/simulation/step", methods=["POST"])
def simulation_step():
    res = SimulationEngine.step()
    return jsonify(res)

@digital_twin_bp.route("/simulation/reset", methods=["POST"])
def simulation_reset():
    res = SimulationEngine.reset()
    return jsonify(res)

@digital_twin_bp.route("/simulation/status", methods=["GET"])
def simulation_status():
    return jsonify(SimulationEngine.get_status())

@digital_twin_bp.route("/simulation/scenario", methods=["POST"])
def simulation_scenario():
    """Calculates scenario projections for source segregation, volume, and facility capacities."""
    data = request.get_json() or {}
    daily_volume = float(data.get("daily_volume_tons", 200.0))
    segregation_rate = float(data.get("segregation_rate_pct", 65.0))
    collection_cap = float(data.get("collection_capacity_tpd", 250.0))
    processing_cap = float(data.get("processing_capacity_tpd", 220.0))

    projection = SimulationEngine.run_scenario_simulation(
        daily_volume_tons=daily_volume,
        segregation_rate_pct=segregation_rate,
        collection_capacity_tpd=collection_cap,
        processing_capacity_tpd=processing_cap
    )
    return jsonify(projection)

# Campus Smart Bins API
@digital_twin_bp.route("/bins", methods=["GET"])
def get_smart_bins():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM smart_bins ORDER BY current_fill_pct DESC")
        bins = [dict(row) for row in cursor.fetchall()]
    return jsonify({"status": "success", "bins": bins})

@digital_twin_bp.route("/bins/<bin_code>/service", methods=["POST"])
def service_smart_bin(bin_code):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE smart_bins 
            SET current_fill_pct = 0, status = 'Normal', last_serviced = CURRENT_TIMESTAMP
            WHERE code = ?
        """, (bin_code,))
        conn.commit()
        cursor.execute("SELECT * FROM smart_bins WHERE code = ?", (bin_code,))
        updated = dict(cursor.fetchone() or {})
    return jsonify({"status": "success", "message": f"Bin {bin_code} emptied & serviced.", "bin": updated})

# Dispatch Routes API
@digital_twin_bp.route("/routes", methods=["GET"])
def get_dispatch_routes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dispatch_routes ORDER BY id ASC")
        routes = [dict(row) for row in cursor.fetchall()]
    return jsonify({"status": "success", "routes": routes})

@digital_twin_bp.route("/routes/<route_id>/dispatch", methods=["POST"])
def dispatch_route(route_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dispatch_routes 
            SET status = 'Dispatched'
            WHERE id = ?
        """, (route_id,))
        conn.commit()
        cursor.execute("SELECT * FROM dispatch_routes WHERE id = ?", (route_id,))
        updated = dict(cursor.fetchone() or {})
    return jsonify({"status": "success", "message": f"Route {route_id} dispatched.", "route": updated})
