import sqlite3
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema_file = Config.BASE_DIR / "database" / "schema.sql"
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if table already exists without is_demo column (migration safeguard)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='household_scans'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(household_scans)")
            columns = [row[1] for row in cursor.fetchall()]
            if "is_demo" not in columns:
                cursor.execute("ALTER TABLE household_scans ADD COLUMN is_demo INTEGER DEFAULT 0")

        conn.executescript(schema_sql)

        # Check if facilities already seeded
        cursor.execute("SELECT COUNT(*) FROM facilities")
        if cursor.fetchone()[0] == 0:
            seed_initial_data(conn)

        # Check if household_scans already has demo data seeded
        cursor.execute("SELECT COUNT(*) FROM household_scans")
        if cursor.fetchone()[0] == 0:
            seed_demo_household_data(conn)

        conn.commit()

def seed_initial_data(conn):
    cursor = conn.cursor()
    
    # 1. Facilities
    facilities = [
        (
            "MRF-01",
            "Metro Resource Recovery Facility",
            "High-Speed Optical Sorting",
            "Zone 1 - North Logistics Corridor",
            "operational",
            320.0,
            214.5,
            "Plastic,Metal,Paper,Cardboard,Glass",
            0.94
        ),
        (
            "PRP-02",
            "Piedmont Polymer Reclamation Center",
            "Mechanical Flaking & Pelletizing",
            "Zone 3 - Southern Industrial Sector",
            "operational",
            180.0,
            142.8,
            "Plastic",
            0.91
        ),
        (
            "FPU-03",
            "Cascadia Fiber & Pulp Processing Hub",
            "Hydropulping & De-inking",
            "Zone 2 - Western Waterway Terminal",
            "operational",
            250.0,
            198.2,
            "Paper,Cardboard",
            0.89
        ),
        (
            "MSR-04",
            "Apex Non-Ferrous & Alloy Refiners",
            "Eddy-Current Separation & Secondary Smelting",
            "Zone 4 - Eastern Metallurgical Belt",
            "operational",
            210.0,
            158.4,
            "Metal",
            0.96
        ),
        (
            "GBC-05",
            "ClearCycle Glass Beneficiation Works",
            "Optical Color Separation & Cullet Sizing",
            "Zone 1 - Harbor District",
            "operational",
            140.0,
            96.7,
            "Glass",
            0.93
        )
    ]
    cursor.executemany("""
        INSERT INTO facilities (id, name, facility_type, location, status, capacity_tpd, current_load_tpd, supported_materials, efficiency_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, facilities)

    # 2. Collection Points
    collection_points = [
        ("CP-ALPHA", "Harbor Bulk Material Aggregator", "Waterfront", 45.5152, -122.6784, 68.0, "MRF-01"),
        ("CP-BETA", "Central Distribution Logistics Depot", "North Metro", 45.5284, -122.6852, 42.0, "MRF-01"),
        ("CP-GAMMA", "Civic Center Commercial Collection Hub", "Downtown Core", 45.5190, -122.6738, 86.5, "MRF-01"),
        ("CP-DELTA", "Eastside Material Aggregation Yard", "East Metro", 45.5228, -122.6450, 31.0, "MRF-01")
    ]
    cursor.executemany("""
        INSERT INTO collection_points (id, name, zone, latitude, longitude, fill_level_pct, assigned_facility_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, collection_points)

    # 3. Baseline Waste Batches with real operational stages
    batches = [
        ("BATCH-8801", None, "Plastic", "PET Flakes / Beverage Bottles", 1240.0, 0.94, "Processed", "CP-ALPHA", "PRP-02", 0),
        ("BATCH-8802", None, "Metal", "UBC Aluminum Pressed Cans", 890.0, 0.97, "Sorted", "CP-GAMMA", "MSR-04", 0),
        ("BATCH-8803", None, "Cardboard", "OCC Baler Grade 11", 1650.0, 0.92, "Collected", "CP-BETA", "FPU-03", 0),
        ("BATCH-8804", None, "Glass", "Clean Cullet Mixed Color", 1120.0, 0.95, "Verified", "CP-DELTA", "GBC-05", 0),
        ("BATCH-8805", None, "Plastic", "HDPE Natural Blow-Molded", 760.0, 0.93, "Sorted", "CP-ALPHA", "PRP-02", 0),
        ("BATCH-8806", None, "Paper", "De-inked High Grade Kraft", 920.0, 0.88, "Processed", "CP-GAMMA", "FPU-03", 0),
        ("BATCH-8807", None, "Metal", "Aerosol & Mixed Ferrous Tinplate", 430.0, 0.89, "Collected", "CP-DELTA", "MRF-01", 0),
        ("BATCH-8808", None, "Plastic", "Mixed Rigid Polypropylene", 580.0, 0.86, "Classified", "CP-BETA", "MRF-01", 0)
    ]
    cursor.executemany("""
        INSERT INTO waste_batches (id, detection_id, material_category, sub_type, estimated_weight_kg, purity_score, status, origin_collection_point_id, current_facility_id, is_simulated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batches)

    # 4. Audit Log entries for initial batches
    audit_entries = [
        ("BATCH-8801", "Sorted", "Processed", "Thermal pelletizing and optical purity scan completed at PRP-02", "PRP-02 System"),
        ("BATCH-8802", "Collected", "Sorted", "Eddy current sorting separation verified purity score 0.97", "MSR-04 System"),
        ("BATCH-8803", "Verified", "Collected", "Dispatched transport carrier TRK-04 from CP-BETA", "Logistics Controller"),
        ("BATCH-8804", "Classified", "Verified", "Spectroscopic confirmation of non-hazardous silicate glass", "Inspector Lab"),
        ("BATCH-8805", "Collected", "Sorted", "Near-infrared polymer resonance sorting completed", "PRP-02 System"),
        ("BATCH-8806", "Sorted", "Processed", "Hydropulp slurry refined and secondary fibers bailed", "FPU-03 System"),
        ("BATCH-8807", "Verified", "Collected", "Consolidated in bulk hopper at CP-DELTA", "Fleet Operator"),
        ("BATCH-8808", "Detected", "Classified", "Multi-spectral resonance profile matched rigid PP", "MRF-01 Sensor")
    ]
    cursor.executemany("""
        INSERT INTO batch_audit_log (batch_id, previous_status, new_status, notes, actor)
        VALUES (?, ?, ?, ?, ?)
    """, audit_entries)

    # 5. Simulation seed event
    cursor.execute("""
        INSERT INTO simulation_events (event_type, entity_id, description, payload_json)
        VALUES ('SYSTEM_INIT', 'ECOSYNC_CORE', 'EcoSync operational database schema and seed data initialized', '{}')
    """)

def seed_demo_household_data(conn):
    """
    Seeds a realistic, diverse set of clearly-labelled fictional demonstration
    household scan records covering all 8 waste categories with timestamps
    distributed over the past 5 days.
    """
    cursor = conn.cursor()
    demo_scans = [
        (
            "DEMO-HS-01", None, "/static/images/samples/photo_bottles.jpg",
            "PET Mineral Water Bottle (500ml)", "Recyclable materials", "PET #1 Plastic",
            0.94, "Placed in Recycling Bin", 0.025,
            "[DEMO DATA] Rinsed empty bottle, crushed flat, kept cap attached.", 1,
            "datetime('now', '-4 days', '+2 hours')"
        ),
        (
            "DEMO-HS-02", None, "/static/images/samples/photo_cans.jpg",
            "Aluminum Beverage Can", "Recyclable materials", "UBC Aluminum Alloy",
            0.96, "Placed in Recycling Bin", 0.015,
            "[DEMO DATA] Emptied soda can, placed in blue dry recycling bin.", 1,
            "datetime('now', '-4 days', '+5 hours')"
        ),
        (
            "DEMO-HS-03", None, "",
            "Kitchen Vegetable Peels & Coffee Grounds", "Organic and biodegradable waste", "Organic Biomass",
            0.95, "Composted at Home / Wet Bin", 0.450,
            "[DEMO DATA] Daily food preparation scraps added to kitchen counter compost bucket.", 1,
            "datetime('now', '-3 days', '+1 hour')"
        ),
        (
            "DEMO-HS-04", None, "/static/images/samples/sample_boxes.jpg",
            "Corrugated Shipping Box (Flattened)", "Recyclable materials", "Corrugated Kraft Paperboard",
            0.92, "Placed in Recycling Bin", 0.280,
            "[DEMO DATA] Removed packing tape, flattened carton to save truck volume.", 1,
            "datetime('now', '-3 days', '+6 hours')"
        ),
        (
            "DEMO-HS-05", None, "",
            "Used AA Alkaline Batteries (Pack of 4)", "Hazardous waste", "Zinc-Manganese Alkaline",
            0.91, "Saved for Hazardous Depot", 0.095,
            "[DEMO DATA] Covered terminals with clear Scotch tape; kept in plastic container.", 1,
            "datetime('now', '-2 days', '+3 hours')"
        ),
        (
            "DEMO-HS-06", None, "",
            "Retired USB-C Charging Cable & Adapter", "Electronic waste", "ABS Polymer & Copper Wiring",
            0.89, "Kept for E-Waste Drop-off", 0.120,
            "[DEMO DATA] Non-functioning mobile phone charger cord bundled for supermarket e-waste box.", 1,
            "datetime('now', '-2 days', '+7 hours')"
        ),
        (
            "DEMO-HS-07", None, "",
            "Cooled Frying Oil (Sealed Glass Jar)", "Liquid waste", "Vegetable Triglyceride Lipids",
            0.88, "Saved for Hazardous Depot", 0.350,
            "[DEMO DATA] Never poured down sink! Strained cooled oil into screw-top jar for biofuel pickup.", 1,
            "datetime('now', '-1 days', '+2 hours')"
        ),
        (
            "DEMO-HS-08", None, "",
            "Greasy Delivery Pizza Box Bottom", "Municipal solid waste", "Oil-Contaminated Cellulose",
            0.93, "Disposed in General Trash", 0.080,
            "[DEMO DATA] Tore clean top lid for paper recycling; oily bottom discarded in general trash.", 1,
            "datetime('now', '-1 days', '+8 hours')"
        ),
        (
            "DEMO-HS-09", None, "",
            "Expired Antibiotic Tablets & Blister Pack", "Biomedical and healthcare waste", "Pharmaceutical Formulation",
            0.87, "Saved for Hazardous Depot", 0.035,
            "[DEMO DATA] Kept in blister pack for pharmacy prescription medication return kiosk.", 1,
            "datetime('now', '-6 hours')"
        ),
        (
            "DEMO-HS-10", None, "",
            "Broken Bathroom Ceramic Tile Shards", "Construction and demolition waste", "Glazed Ceramic Silicate",
            0.85, "Disposed in General Trash", 1.650,
            "[DEMO DATA] Bagged heavy ceramic shards from DIY bathroom repair for municipal skip.", 1,
            "datetime('now', '-1 hours')"
        )
    ]

    for item in demo_scans:
        cursor.execute(f"""
            INSERT OR REPLACE INTO household_scans (
                id, detection_id, image_url, item_name, category, material,
                confidence, action_taken, estimated_weight_kg, user_notes, is_demo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {item[11]})
        """, item[:11])

def reset_demo_data():
    """
    Resets all demo records in household_scans and simulation events,
    leaving any real citizen scans (is_demo = 0) completely intact.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM household_scans WHERE is_demo = 1")
        seed_demo_household_data(conn)
        conn.commit()
    return {"status": "success", "message": "Demo data successfully reset to baseline."}

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", Config.DATABASE_PATH)
