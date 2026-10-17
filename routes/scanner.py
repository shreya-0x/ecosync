import os
import uuid
import json
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from config import Config
from services.waste_detector import run_waste_detection
from services.model_loader import ModelManager
from database.db import get_db_connection

scanner_bp = Blueprint("scanner", __name__, url_prefix="/api")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@scanner_bp.route("/model-status", methods=["GET"])
def get_model_status():
    status = ModelManager.get_status()
    return jsonify({
        "status": "success",
        "model": status
    })

@scanner_bp.route("/scanner/samples", methods=["GET"])
def get_sample_images():
    samples_dir = Config.BASE_DIR / "static" / "images" / "samples"
    samples = []
    if samples_dir.exists():
        for file in samples_dir.glob("*.jpg"):
            samples.append({
                "id": file.stem,
                "name": file.stem.replace("photo_", "").replace("sample_", "").replace("_", " ").title(),
                "url": f"/static/images/samples/{file.name}",
                "filename": file.name
            })
    return jsonify({
        "status": "success",
        "samples": samples
    })

@scanner_bp.route("/detect", methods=["POST"])
def detect_waste():
    """
    Primary endpoint for real multi-object waste detection.
    Accepts:
    - multipart/form-data with 'image' file
    - or JSON with 'sample_path' to use one of the built-in sample images
    """
    conf_threshold = float(request.form.get("confidence_threshold", Config.DEFAULT_CONFIDENCE_THRESHOLD))
    saved_filepath = None

    if "image" in request.files:
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"status": "error", "message": "No file selected."}), 400
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error", 
                "message": f"Unsupported file type. Allowed formats: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            }), 400

        clean_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex[:10]}_{clean_name}"
        saved_filepath = Config.UPLOAD_FOLDER / unique_name
        file.save(str(saved_filepath))

    elif request.is_json and "sample_path" in request.json:
        # User requested inspection of a sample image
        sample_path_rel = request.json["sample_path"].lstrip("/")
        sample_file = Config.BASE_DIR / sample_path_rel
        if not sample_file.exists():
            return jsonify({"status": "error", "message": "Sample image not found."}), 404
        saved_filepath = sample_file
        conf_threshold = float(request.json.get("confidence_threshold", Config.DEFAULT_CONFIDENCE_THRESHOLD))

    elif request.is_json and "image_base64" in request.json:
        # Live camera frame capture encoded in Base64 Data URL
        try:
            import base64
            data_uri = request.json["image_base64"]
            header, encoded = data_uri.split(",", 1) if "," in data_uri else ("", data_uri)
            image_bytes = base64.b64decode(encoded)
            unique_name = f"cam_{uuid.uuid4().hex[:10]}.jpg"
            saved_filepath = Config.UPLOAD_FOLDER / unique_name
            with open(saved_filepath, "wb") as f:
                f.write(image_bytes)
            conf_threshold = float(request.json.get("confidence_threshold", Config.DEFAULT_CONFIDENCE_THRESHOLD))
        except Exception as e:
            return jsonify({"status": "error", "message": f"Could not process camera image: {e}"}), 400

    else:
        return jsonify({"status": "error", "message": "No image payload provided."}), 400

    try:
        results = run_waste_detection(str(saved_filepath), conf_threshold=conf_threshold)
        # Add relative URL for the image so frontend can display it
        rel_url = f"/uploads/{saved_filepath.name}" if "uploads" in str(saved_filepath) else f"/{saved_filepath.relative_to(Config.BASE_DIR).as_posix()}"
        results["image"]["url"] = rel_url
        return jsonify({"status": "success", "data": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@scanner_bp.route("/classifications/confirm", methods=["POST"])
@scanner_bp.route("/household/scans", methods=["POST"])
def confirm_classification():
    """
    Records human verification, citizen disposal action, or category correction into SQLite,
    persisting the record to both household_scans (is_demo=0) and waste_batches.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload."}), 400

    detection_id = data.get("detection_batch_id") or data.get("detection_id")
    confirmed_category = data.get("confirmed_category") or data.get("category")
    sub_type = data.get("sub_type") or data.get("item_name") or "Standard Secondary Material"
    item_name = data.get("item_name") or sub_type
    weight_kg = float(data.get("estimated_weight_kg", 0.05))
    purity_score = float(data.get("purity_score", 0.92))
    origin_cp = data.get("origin_collection_point_id", "CP-ALPHA")
    facility_id = data.get("current_facility_id", "MRF-01")
    image_path = data.get("image_url") or data.get("image_path") or ""
    action_taken = data.get("action_taken", "Confirmed & Segregated")
    confidence = float(data.get("confidence", 0.88))
    material = data.get("material", sub_type)
    notes = data.get("user_notes") or data.get("notes") or "Verified through EcoSync Vision Studio console."

    if not confirmed_category:
        return jsonify({"status": "error", "message": "confirmed_category is required."}), 400

    new_batch_id = f"BATCH-{uuid.uuid4().hex[:6].upper()}"
    household_scan_id = f"HS-{uuid.uuid4().hex[:8].upper()}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Update detections record if provided and exists
        valid_detection_fk = None
        if detection_id:
            cursor.execute("SELECT id FROM detections WHERE id = ?", (detection_id,))
            if cursor.fetchone():
                valid_detection_fk = detection_id
                cursor.execute("""
                    UPDATE detections 
                    SET human_verified = 1, confirmed_category = ?
                    WHERE id = ?
                """, (confirmed_category, detection_id))

        # 2. Insert new waste batch with Verified status
        cursor.execute("""
            INSERT INTO waste_batches (
                id, detection_id, material_category, sub_type, estimated_weight_kg, 
                purity_score, status, origin_collection_point_id, current_facility_id, 
                image_path, is_simulated
            ) VALUES (?, ?, ?, ?, ?, ?, 'Verified', ?, ?, ?, 0)
        """, (
            new_batch_id, valid_detection_fk, confirmed_category, sub_type, 
            weight_kg, purity_score, origin_cp, facility_id, image_path
        ))

        # 3. Add to audit log
        cursor.execute("""
            INSERT INTO batch_audit_log (batch_id, previous_status, new_status, notes, actor)
            VALUES (?, 'Classified', 'Verified', ?, 'Citizen User')
        """, (new_batch_id, notes))

        # 4. Insert into household_scans table for household citizen impact tracking (Real record: is_demo = 0)
        cursor.execute("""
            INSERT INTO household_scans (
                id, detection_id, image_url, item_name, category, material, 
                confidence, action_taken, estimated_weight_kg, user_notes, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            household_scan_id, valid_detection_fk, image_path, item_name, 
            confirmed_category, material, confidence, action_taken, weight_kg, notes
        ))

        conn.commit()

    return jsonify({
        "status": "success",
        "message": f"Waste item '{item_name}' successfully recorded and logged into persistent database.",
        "batch_id": new_batch_id,
        "id": household_scan_id
    })
