from flask import Blueprint, request, jsonify
from database.db import get_db_connection
from services.impact_calculator import calculate_material_impact

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")

@analytics_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Computes real-time circular economy analytics and environmental impact.
    All calculations are derived directly from the SQLite records with transparent conversion factors.
    """
    material_filter = request.args.get("material")
    facility_filter = request.args.get("facility")
    status_filter = request.args.get("status")
    include_simulated = request.args.get("include_simulated", "1") == "1"

    query = "SELECT * FROM waste_batches WHERE 1=1"
    params = []

    if not include_simulated:
        query += " AND is_simulated = 0"
    if material_filter:
        query += " AND material_category = ?"
        params.append(material_filter)
    if facility_filter:
        query += " AND current_facility_id = ?"
        params.append(facility_filter)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        batches = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM facilities")
        facilities = [dict(row) for row in cursor.fetchall()]

    # Aggregations
    total_batches = len(batches)
    total_weight_kg = sum(b["estimated_weight_kg"] for b in batches)
    
    # Material breakdown
    materials_summary = {}
    status_summary = {}
    facility_workload = {}

    total_avoided_co2 = 0.0
    total_energy_kwh = 0.0
    total_landfill_m3 = 0.0
    total_virgin_offset_kg = 0.0

    for b in batches:
        mat = b["material_category"]
        st = b["status"]
        fac = b["current_facility_id"] or "Unassigned"
        wt = b["estimated_weight_kg"]
        purity = b["purity_score"]

        # Material summary
        if mat not in materials_summary:
            materials_summary[mat] = {"count": 0, "weight_kg": 0.0, "processed_weight_kg": 0.0}
        materials_summary[mat]["count"] += 1
        materials_summary[mat]["weight_kg"] = round(materials_summary[mat]["weight_kg"] + wt, 2)
        if st == "Processed":
            materials_summary[mat]["processed_weight_kg"] = round(materials_summary[mat]["processed_weight_kg"] + wt, 2)

        # Status summary
        status_summary[st] = status_summary.get(st, 0) + 1

        # Facility summary
        facility_workload[fac] = facility_workload.get(fac, 0.0) + wt

        # Environmental impacts
        impact = calculate_material_impact(mat, wt, purity)
        total_avoided_co2 += impact["metrics"]["avoided_ghg_emissions_kg_co2e"]
        total_energy_kwh += impact["metrics"]["energy_saved_kwh"]
        total_landfill_m3 += impact["metrics"]["landfill_diverted_volume_m3"]
        total_virgin_offset_kg += impact["metrics"]["virgin_material_offset_kg"]

    # Compute verified recovery rate
    processed_weight = sum(b["estimated_weight_kg"] for b in batches if b["status"] == "Processed")
    recovery_rate_pct = round((processed_weight / total_weight_kg * 100), 1) if total_weight_kg > 0 else 0.0

    return jsonify({
        "status": "success",
        "filters_applied": {
            "material": material_filter,
            "facility": facility_filter,
            "status": status_filter,
            "include_simulated": include_simulated
        },
        "headline_metrics": {
            "total_batches_tracked": total_batches,
            "total_weight_kg": round(total_weight_kg, 1),
            "total_weight_metric_tons": round(total_weight_kg / 1000.0, 3),
            "processed_weight_kg": round(processed_weight, 1),
            "recovery_rate_pct": recovery_rate_pct,
            "active_facilities_count": len(facilities)
        },
        "environmental_impact": {
            "avoided_ghg_emissions_kg_co2e": round(total_avoided_co2, 1),
            "avoided_ghg_emissions_mt_co2e": round(total_avoided_co2 / 1000.0, 3),
            "energy_saved_kwh": round(total_energy_kwh, 1),
            "landfill_diverted_volume_m3": round(total_landfill_m3, 2),
            "virgin_material_offset_kg": round(total_virgin_offset_kg, 1),
            "methodology_note": "Calculations derived from EPA WARM v15 and circular material density offsets based on recorded batch weights and purity coefficients."
        },
        "material_distribution": materials_summary,
        "status_distribution": status_summary,
        "facility_workload": facility_workload
    })

@analytics_bp.route("/household/impact", methods=["GET"])
def get_household_impact():
    """
    Returns honest, transparent household-level waste impact metrics.
    Explicitly distinguishes:
    - Scanned items
    - User-confirmed items
    - Self-reported disposed actions
    - Verified municipal collection & processed records
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Scanned items count (from detections table)
        cursor.execute("SELECT COUNT(*) FROM detections")
        total_scans = cursor.fetchone()[0]

        # 2. Confirmed household items
        cursor.execute("SELECT * FROM household_scans ORDER BY created_at DESC")
        household_records = [dict(row) for row in cursor.fetchall()]

        # 3. Verified municipal facility processed records (for clear contrast)
        cursor.execute("SELECT COUNT(*), SUM(estimated_weight_kg) FROM waste_batches WHERE status = 'Processed'")
        proc_row = cursor.fetchone()
        verified_processed_count = proc_row[0] or 0
        verified_processed_kg = round(proc_row[1] or 0.0, 1)

    confirmed_count = len(household_records)
    total_household_weight_kg = sum(r["estimated_weight_kg"] for r in household_records)

    # Breakdown by category
    category_counts = {}
    category_weights = {}
    action_counts = {}

    diverted_weight_kg = 0.0
    avoided_co2e_kg = 0.0
    energy_saved_kwh = 0.0

    from services.waste_guide_service import WASTE_CATEGORIES

    for r in household_records:
        cat = r["category"]
        act = r["action_taken"]
        wt = r["estimated_weight_kg"]

        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_weights[cat] = round(category_weights.get(cat, 0.0) + wt, 2)
        action_counts[act] = action_counts.get(act, 0) + 1

        # Calculate avoided environmental footprints if segregated away from landfill
        if cat in ["Recyclable materials", "Organic and biodegradable waste", "Electronic waste"]:
            diverted_weight_kg += wt
            cat_info = WASTE_CATEGORIES.get(cat, {})
            avoided_co2e_kg += wt * cat_info.get("diverted_co2_factor_per_kg", 1.0)
            energy_saved_kwh += wt * cat_info.get("energy_saved_kwh_per_kg", 2.0)

    # Trends over time
    trends = []
    daily_groups = {}
    for r in household_records:
        day = (r["created_at"] or "")[:10]
        if day:
            daily_groups[day] = daily_groups.get(day, 0) + 1
    for d in sorted(daily_groups.keys()):
        trends.append({"date": d, "items_confirmed": daily_groups[d]})

    # Demo records separation
    demo_count = sum(1 for r in household_records if r.get("is_demo") == 1)
    real_count = confirmed_count - demo_count

    return jsonify({
        "status": "success",
        "household_metrics": {
            "total_scans_performed": total_scans,
            "total_items_confirmed": confirmed_count,
            "real_items_count": real_count,
            "demo_items_count": demo_count,
            "estimated_household_weight_kg": round(total_household_weight_kg, 2),
            "diverted_weight_kg": round(diverted_weight_kg, 2),
            "avoided_ghg_emissions_kg_co2e": round(avoided_co2e_kg, 2),
            "energy_saved_kwh": round(energy_saved_kwh, 2),
            "category_distribution": category_counts,
            "category_weights_kg": category_weights,
            "actions_distribution": action_counts,
            "activity_trend": trends
        },
        "verification_separation": {
            "household_self_reported": {
                "items_confirmed": confirmed_count,
                "real_items": real_count,
                "demo_items": demo_count,
                "weight_diverted_kg": round(diverted_weight_kg, 2),
                "status_note": "Self-reported citizen actions based on standard item unit weights (includes labeled demo data)."
            },
            "municipal_facility_verified": {
                "batches_processed": verified_processed_count,
                "weight_processed_kg": verified_processed_kg,
                "status_note": "Physically received and verified at municipal material recovery centers."
            }
        },
        "methodology": {
            "weight_estimation": "Standardized benchmark item unit weights (e.g., PET bottle ~25g, can ~15g, phone ~180g).",
            "emissions_factors": "EPA WARM v15 lifecycle offsets applied per verified category.",
            "scientific_honesty_statement": "Scans and user actions reflect household self-reported compliance. Real recycling yields depend on municipal sorting infrastructure."
        }
    })

@analytics_bp.route("/history", methods=["GET"])
def get_activity_history():
    """Returns chronological activity history of citizen scans and confirmations with optional search/filter."""
    limit = int(request.args.get("limit", 100))
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    is_demo = request.args.get("is_demo")

    query = "SELECT * FROM household_scans WHERE 1=1"
    params = []

    if search:
        query += " AND (item_name LIKE ? OR material LIKE ? OR user_notes LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if category:
        query += " AND category = ?"
        params.append(category)
    if is_demo in ("0", "1"):
        query += " AND is_demo = ?"
        params.append(int(is_demo))

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]

    return jsonify({
        "status": "success",
        "count": len(records),
        "history": records
    })

@analytics_bp.route("/history/export", methods=["GET"])
def export_activity_history_csv():
    """Exports confirmed household scans as an RFC-4180 compliant CSV document."""
    import io
    import csv
    from flask import Response
    from services.waste_guide_service import WASTE_CATEGORIES

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, item_name, category, material, confidence, 
                   action_taken, estimated_weight_kg, user_notes, is_demo, created_at
            FROM household_scans
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header Row
    writer.writerow([
        "Scan ID",
        "Item Name",
        "Category",
        "Material Composition",
        "Model Confidence",
        "Action Taken",
        "Estimated Weight (kg)",
        "Avoided GHG (kg CO2e)",
        "Energy Conserved (kWh)",
        "Record Type",
        "User Notes",
        "Timestamp (UTC)"
    ])

    for row in rows:
        cat = row["category"]
        wt = row["estimated_weight_kg"] or 0.0
        cat_info = WASTE_CATEGORIES.get(cat, {})
        co2_factor = cat_info.get("diverted_co2_factor_per_kg", 0.0) if cat in ["Recyclable materials", "Organic and biodegradable waste", "Electronic waste"] else 0.0
        energy_factor = cat_info.get("energy_saved_kwh_per_kg", 0.0) if cat in ["Recyclable materials", "Organic and biodegradable waste", "Electronic waste"] else 0.0

        avoided_co2 = round(wt * co2_factor, 3)
        energy_saved = round(wt * energy_factor, 2)
        rec_type = "DEMO DATA" if row["is_demo"] == 1 else "VERIFIED CITIZEN ACTION"

        writer.writerow([
            row["id"],
            row["item_name"],
            cat,
            row["material"] or "N/A",
            f"{round((row['confidence'] or 0.0) * 100, 1)}%",
            row["action_taken"],
            round(wt, 3),
            avoided_co2,
            energy_saved,
            rec_type,
            row["user_notes"] or "",
            row["created_at"]
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=ecosync_household_waste_impact_history.csv",
            "Cache-Control": "no-cache"
        }
    )
