-- EcoSync SQLite Database Schema
-- Material Intelligence & Circular Economy Platform

CREATE TABLE IF NOT EXISTS facilities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    facility_type TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'operational',
    capacity_tpd REAL NOT NULL,
    current_load_tpd REAL NOT NULL DEFAULT 0.0,
    supported_materials TEXT NOT NULL,
    efficiency_rate REAL NOT NULL DEFAULT 0.92,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collection_points (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    zone TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    fill_level_pct REAL NOT NULL DEFAULT 45.0,
    last_pickup_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_facility_id TEXT,
    FOREIGN KEY (assigned_facility_id) REFERENCES facilities(id)
);

CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    image_filename TEXT NOT NULL,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    raw_detections_json TEXT NOT NULL,
    human_verified INTEGER DEFAULT 0,
    confirmed_category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS waste_batches (
    id TEXT PRIMARY KEY,
    detection_id TEXT,
    material_category TEXT NOT NULL,
    sub_type TEXT NOT NULL,
    estimated_weight_kg REAL NOT NULL DEFAULT 1.0,
    purity_score REAL NOT NULL DEFAULT 0.90,
    status TEXT NOT NULL DEFAULT 'Detected',
    origin_collection_point_id TEXT,
    current_facility_id TEXT,
    image_path TEXT,
    is_simulated INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detection_id) REFERENCES detections(id),
    FOREIGN KEY (origin_collection_point_id) REFERENCES collection_points(id),
    FOREIGN KEY (current_facility_id) REFERENCES facilities(id)
);

CREATE TABLE IF NOT EXISTS batch_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    notes TEXT,
    actor TEXT NOT NULL DEFAULT 'System',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES waste_batches(id)
);

CREATE TABLE IF NOT EXISTS simulation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    entity_id TEXT,
    description TEXT NOT NULL,
    payload_json TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Household Citizen Scan & Disposal Records
CREATE TABLE IF NOT EXISTS household_scans (
    id TEXT PRIMARY KEY,
    detection_id TEXT,
    image_url TEXT,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    material TEXT,
    confidence REAL DEFAULT 0.0,
    action_taken TEXT NOT NULL DEFAULT 'Confirmed',
    estimated_weight_kg REAL NOT NULL DEFAULT 0.05,
    user_notes TEXT,
    is_demo INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detection_id) REFERENCES detections(id)
);

CREATE INDEX IF NOT EXISTS idx_household_is_demo ON household_scans(is_demo);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_batches_status ON waste_batches(status);
CREATE INDEX IF NOT EXISTS idx_batches_material ON waste_batches(material_category);
CREATE INDEX IF NOT EXISTS idx_batches_facility ON waste_batches(current_facility_id);
CREATE INDEX IF NOT EXISTS idx_audit_batch ON batch_audit_log(batch_id);
CREATE INDEX IF NOT EXISTS idx_household_category ON household_scans(category);
CREATE INDEX IF NOT EXISTS idx_household_action ON household_scans(action_taken);
