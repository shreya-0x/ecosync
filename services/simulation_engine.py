import uuid
import json
import logging
from datetime import datetime
from database.db import get_db_connection

logger = logging.getLogger("ecosync.simulation_engine")

class SimulationEngine:
    _is_running = False
    _tick_count = 0

    @classmethod
    def get_status(cls):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM waste_batches WHERE is_simulated = 1")
            sim_batches = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM simulation_events")
            total_events = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM simulation_events ORDER BY id DESC LIMIT 5")
            recent_events = [dict(row) for row in cursor.fetchall()]

        return {
            "is_running": cls._is_running,
            "tick_count": cls._tick_count,
            "simulated_batches_count": sim_batches,
            "total_simulation_events": total_events,
            "recent_events": recent_events
        }

    @classmethod
    def step(cls):
        """Advances simulation by one deterministic operational interval."""
        cls._tick_count += 1
        events_generated = []

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Look for uncollected verified batches or generate new simulated collection batch
            cursor.execute("""
                SELECT id, status, material_category, estimated_weight_kg, current_facility_id 
                FROM waste_batches 
                WHERE is_simulated = 1 AND status != 'Processed'
                ORDER BY updated_at ASC LIMIT 1
            """)
            batch = cursor.fetchone()

            if batch:
                batch_id, status, mat, weight, facility = batch
                
                # Valid lifecycle state machine:
                # Detected -> Classified -> Verified -> Collected -> Sorted -> Processed
                transitions = {
                    "Detected": "Classified",
                    "Classified": "Verified",
                    "Verified": "Collected",
                    "Collected": "Sorted",
                    "Sorted": "Processed"
                }
                next_status = transitions.get(status)

                if next_status:
                    cursor.execute("""
                        UPDATE waste_batches 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (next_status, batch_id))

                    note = f"[SIMULATED] Automated operational transition from {status} to {next_status}"
                    cursor.execute("""
                        INSERT INTO batch_audit_log (batch_id, previous_status, new_status, notes, actor)
                        VALUES (?, ?, ?, ?, 'Simulation State Engine')
                    """, (batch_id, status, next_status, note))

                    event_desc = f"[SIMULATED] Batch {batch_id} ({mat}, {weight}kg) progressed to {next_status}"
                    cursor.execute("""
                        INSERT INTO simulation_events (event_type, entity_id, description, payload_json)
                        VALUES ('BATCH_TRANSITION', ?, ?, ?)
                    """, (batch_id, event_desc, json.dumps({"previous": status, "next": next_status})))

                    events_generated.append(event_desc)
            else:
                # Generate a new simulated batch at a collection point
                cursor.execute("SELECT id, name FROM collection_points ORDER BY fill_level_pct DESC LIMIT 1")
                cp = cursor.fetchone()
                cp_id = cp["id"] if cp else "CP-ALPHA"

                new_batch_id = f"SIM-{cls._tick_count:04d}-{uuid.uuid4().hex[:4].upper()}"
                materials = [
                    ("Plastic", "HDPE Natural Pellets", 620.0, "PRP-02"),
                    ("Metal", "Secondary Aluminum Shred", 480.0, "MSR-04"),
                    ("Cardboard", "OCC Baler Grade", 1150.0, "FPU-03"),
                    ("Glass", "Amber Cullet", 740.0, "GBC-05")
                ]
                selected_mat = materials[cls._tick_count % len(materials)]

                cursor.execute("""
                    INSERT INTO waste_batches (id, detection_id, material_category, sub_type, estimated_weight_kg, purity_score, status, origin_collection_point_id, current_facility_id, is_simulated)
                    VALUES (?, NULL, ?, ?, ?, 0.94, 'Verified', ?, ?, 1)
                """, (new_batch_id, selected_mat[0], selected_mat[1], selected_mat[2], cp_id, selected_mat[3]))

                cursor.execute("""
                    INSERT INTO batch_audit_log (batch_id, previous_status, new_status, notes, actor)
                    VALUES (?, 'Detected', 'Verified', '[SIMULATED] Automated aggregate stream ingestion', 'Sensor Simulation')
                """, (new_batch_id,))

                event_desc = f"[SIMULATED] Ingested verified batch {new_batch_id} ({selected_mat[0]}) at {cp_id}"
                cursor.execute("""
                    INSERT INTO simulation_events (event_type, entity_id, description, payload_json)
                    VALUES ('BATCH_INGEST', ?, ?, ?)
                """, (new_batch_id, event_desc, json.dumps({"material": selected_mat[0], "weight": selected_mat[2]})))

                events_generated.append(event_desc)

            # Fluctuate collection point fill levels deterministically
            cursor.execute("""
                UPDATE collection_points 
                SET fill_level_pct = CASE 
                    WHEN fill_level_pct >= 90 THEN 25.0
                    ELSE fill_level_pct + 4.5
                END
            """)

            conn.commit()

        return {
            "tick": cls._tick_count,
            "events_generated": events_generated,
            "status": "success"
        }

    @classmethod
    def reset(cls):
        """Cleans up all simulated batches and events, preserving real operational records."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM batch_audit_log WHERE batch_id IN (SELECT id FROM waste_batches WHERE is_simulated = 1)")
            cursor.execute("DELETE FROM waste_batches WHERE is_simulated = 1")
            cursor.execute("DELETE FROM simulation_events")
            cursor.execute("""
                INSERT INTO simulation_events (event_type, entity_id, description, payload_json)
                VALUES ('SIM_RESET', 'SYSTEM', 'Simulation reset to baseline state. Real records preserved.', '{}')
            """)
            conn.commit()

        cls._tick_count = 0
        return {"status": "reset_complete"}

    @classmethod
    def run_scenario_simulation(
        cls,
        daily_volume_tons: float = 200.0,
        segregation_rate_pct: float = 65.0,
        collection_capacity_tpd: float = 250.0,
        processing_capacity_tpd: float = 220.0
    ):
        """
        Pure mathematical scenario projection for the digital twin.
        Calculates estimated impacts of source segregation, collection frequency,
        and facility capacity WITHOUT modifying persistent database records.
        """
        # Constrain parameters to plausible ranges
        vol = max(10.0, min(1000.0, float(daily_volume_tons)))
        seg_pct = max(5.0, min(100.0, float(segregation_rate_pct)))
        coll_cap = max(20.0, min(1200.0, float(collection_capacity_tpd)))
        proc_cap = max(20.0, min(1000.0, float(processing_capacity_tpd)))

        # 1. Source Segregation Breakdown
        segregated_tons = round(vol * (seg_pct / 100.0), 2)
        residual_unsegregated_tons = round(vol - segregated_tons, 2)

        # 2. Collection Capacity & Logistics Utilization
        collection_utilization_pct = round((vol / coll_cap) * 100.0, 1)
        collection_overflow_tons = max(0.0, round(vol - coll_cap, 2))
        collection_status = (
            "Overloaded / Bin Overflow Imminent" if collection_utilization_pct > 100.0
            else "High Load" if collection_utilization_pct > 85.0
            else "Nominal Operating Capacity"
        )

        # 3. Processing Facility Bottleneck & Contamination Rejection
        # Low segregation causes higher contamination rejection
        contamination_rejection_rate = 0.05 if seg_pct >= 80.0 else (0.12 if seg_pct >= 50.0 else 0.25)
        clean_recoverable_tons = round(segregated_tons * (1.0 - contamination_rejection_rate), 2)
        contamination_loss_tons = round(segregated_tons * contamination_rejection_rate, 2)

        # Facility capacity constraint
        actually_processed_tons = min(clean_recoverable_tons, proc_cap)
        processing_utilization_pct = round((clean_recoverable_tons / proc_cap) * 100.0, 1)
        processing_bottleneck_tons = max(0.0, round(clean_recoverable_tons - proc_cap, 2))

        # 4. Total Diverted vs Landfilled
        total_landfilled_tons = round(residual_unsegregated_tons + contamination_loss_tons + processing_bottleneck_tons, 2)
        diversion_rate_pct = round((actually_processed_tons / vol) * 100.0, 1) if vol > 0 else 0.0

        # 5. Avoided Emissions & Energy (EPA WARM composite benchmark: ~1.25 MT CO2e avoided per ton recovered)
        avoided_co2e_metric_tons = round(actually_processed_tons * 1.25, 2)
        energy_saved_mwh = round(actually_processed_tons * 3.4, 2)

        # Actionable AI Recommendation
        if collection_utilization_pct > 100.0:
            scenario_recommendation = f"Urgent: Collection fleet is at {collection_utilization_pct}% capacity. Increase collection frequency or add routing trucks to prevent municipal overflow."
        elif processing_utilization_pct > 100.0:
            scenario_recommendation = f"Bottleneck detected: Material sorting facility is at {processing_utilization_pct}% capacity. Divert {processing_bottleneck_tons} tons/day to regional partner facilities."
        elif seg_pct < 60.0:
            scenario_recommendation = f"Low source segregation ({seg_pct}%) causes {contamination_loss_tons} tons/day lost to contamination. Launching household citizen education will recover {round(contamination_loss_tons * 0.7, 1)} tons/day."
        else:
            scenario_recommendation = f"Excellent operational efficiency: Source segregation at {seg_pct}% yields a {diversion_rate_pct}% landfill diversion rate and offsets {avoided_co2e_metric_tons} MT CO2e daily."

        # 6. Baseline Reference Projections (Default unoptimized municipal benchmark: 35% segregation)
        base_vol = vol
        base_seg_pct = 35.0
        base_coll_cap = 220.0
        base_proc_cap = 180.0

        base_segregated = round(base_vol * (base_seg_pct / 100.0), 2)
        base_unsegregated = round(base_vol - base_segregated, 2)
        base_contam_rate = 0.25 # high contamination at low segregation
        base_clean = round(base_segregated * (1.0 - base_contam_rate), 2)
        base_contam_loss = round(base_segregated * base_contam_rate, 2)
        base_proc = min(base_clean, base_proc_cap)
        base_bottleneck = max(0.0, round(base_clean - base_proc_cap, 2))
        base_landfill = round(base_unsegregated + base_contam_loss + base_bottleneck, 2)
        base_diversion = round((base_proc / base_vol) * 100.0, 1) if base_vol > 0 else 0.0
        base_co2 = round(base_proc * 1.25, 2)
        base_energy = round(base_proc * 3.4, 2)

        comparison = {
            "baseline": {
                "label": "City Baseline (Unoptimized: 35% Source Segregation)",
                "segregation_rate_pct": base_seg_pct,
                "diversion_rate_pct": base_diversion,
                "total_landfilled_tons": base_landfill,
                "contamination_loss_tons": base_contam_loss,
                "avoided_co2e_metric_tons": base_co2,
                "energy_saved_mwh": base_energy
            },
            "scenario": {
                "label": f"Simulated Scenario ({seg_pct}% Source Segregation)",
                "segregation_rate_pct": seg_pct,
                "diversion_rate_pct": diversion_rate_pct,
                "total_landfilled_tons": total_landfilled_tons,
                "contamination_loss_tons": contamination_loss_tons,
                "avoided_co2e_metric_tons": avoided_co2e_metric_tons,
                "energy_saved_mwh": energy_saved_mwh
            },
            "deltas": {
                "diversion_rate_diff_pct": round(diversion_rate_pct - base_diversion, 1),
                "landfill_avoided_diff_tons": round(base_landfill - total_landfilled_tons, 2),
                "contamination_saved_diff_tons": round(base_contam_loss - contamination_loss_tons, 2),
                "co2e_offset_diff_mt": round(avoided_co2e_metric_tons - base_co2, 2),
                "energy_saved_diff_mwh": round(energy_saved_mwh - base_energy, 2),
                "improvement_summary": (
                    f"Compared to unoptimized baseline, this scenario diverts an extra {round(base_landfill - total_landfilled_tons, 1)} tons/day from landfill, "
                    f"raising city diversion from {base_diversion}% to {diversion_rate_pct}% and abating an additional {round(avoided_co2e_metric_tons - base_co2, 1)} MT CO₂e daily."
                )
            }
        }

        return {
            "status": "success",
            "is_simulation": True,
            "inputs": {
                "daily_volume_tons": vol,
                "segregation_rate_pct": seg_pct,
                "collection_capacity_tpd": coll_cap,
                "processing_capacity_tpd": proc_cap
            },
            "metrics": {
                "collection_utilization_pct": collection_utilization_pct,
                "collection_overflow_tons": collection_overflow_tons,
                "collection_status": collection_status,
                "segregated_tons": segregated_tons,
                "residual_unsegregated_tons": residual_unsegregated_tons,
                "contamination_loss_tons": contamination_loss_tons,
                "actually_processed_tons": actually_processed_tons,
                "processing_utilization_pct": processing_utilization_pct,
                "processing_bottleneck_tons": processing_bottleneck_tons,
                "total_landfilled_tons": total_landfilled_tons,
                "diversion_rate_pct": diversion_rate_pct,
                "avoided_co2e_metric_tons": avoided_co2e_metric_tons,
                "energy_saved_mwh": energy_saved_mwh
            },
            "comparison": comparison,
            "recommendation": scenario_recommendation,
            "assumptions": [
                "1. Segregated stream is derived directly from household source separation percentage.",
                "2. Contamination rejection rate scales dynamically from 5% (high segregation >=80%) to 25% (low segregation <50%).",
                "3. Emissions reduction assumes composite EPA WARM factor of 1.25 MT CO2e avoided per ton recovered material.",
                "4. All projected values are clearly labeled as [SIMULATED SCENARIO] and do not alter real database records."
            ]
        }
