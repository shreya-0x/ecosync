import os
import sys
import uuid
import json
import logging
from pathlib import Path
from PIL import Image, UnidentifiedImageError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from services.model_loader import ModelManager, COCO_MATERIAL_MAP
from services.waste_guide_service import resolve_model_detection, get_category_info
from database.db import get_db_connection

logger = logging.getLogger("ecosync.waste_detector")

def run_waste_detection(image_path: str, conf_threshold: float = 0.25):
    """
    Executes real YOLO multi-object detection on the given image path.
    Extracts normalized and pixel-based bounding boxes,
    maps detected classes to distinct concepts (Detection, Identity, Material, Category, Disposal),
    and attaches the 8-point 'How to Handle This Waste' citizen guidance.
    """
    path_obj = Path(image_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Target image not found: {image_path}")

    # Validate image using PIL
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Corrupted or invalid image format: {str(e)}")

    model = ModelManager.get_model()
    if model is None:
        raise RuntimeError("Computer vision model is not loaded or unavailable.")

    # Run actual YOLO inference
    results = model(image_path, conf=conf_threshold, verbose=False)
    
    detections = []
    category_summary = {}

    if len(results) > 0 and results[0].boxes is not None:
        boxes_data = results[0].boxes
        
        for idx, box in enumerate(boxes_data):
            # Coordinates in pixels [x1, y1, x2, y2]
            xyxy = box.xyxy[0].tolist()
            conf = float(box.conf[0].item())
            class_id = int(box.cls[0].item())
            raw_class = model.names.get(class_id, f"class_{class_id}").lower()
            
            x1, y1, x2, y2 = xyxy
            # Ensure within image bounds
            x1 = max(0.0, min(float(x1), float(orig_w)))
            y1 = max(0.0, min(float(y1), float(orig_h)))
            x2 = max(0.0, min(float(x2), float(orig_w)))
            y2 = max(0.0, min(float(y2), float(orig_h)))

            # Normalized coordinates (0.0 to 1.0)
            norm_x1 = round(x1 / orig_w, 4) if orig_w > 0 else 0
            norm_y1 = round(y1 / orig_h, 4) if orig_h > 0 else 0
            norm_x2 = round(x2 / orig_w, 4) if orig_w > 0 else 0
            norm_y2 = round(y2 / orig_h, 4) if orig_h > 0 else 0
            norm_w = round(norm_x2 - norm_x1, 4)
            norm_h = round(norm_y2 - norm_y1, 4)

            # Resolve detection into distinct concepts
            resolved = resolve_model_detection(raw_class)
            
            # Legacy mapping fallback for compatibility
            legacy_map = COCO_MATERIAL_MAP.get(raw_class, {
                "material": resolved["candidate_material"],
                "sub_type": resolved["object_identity"],
                "confidence_weight": 0.50
            })

            candidate_material = resolved["candidate_material"]
            sub_type = legacy_map.get("sub_type", resolved["object_identity"])
            suggested_category = resolved["suggested_category"]
            
            # Review flag for low confidence or unmapped items
            needs_review = conf < 0.40 or not resolved["supported"]

            det_obj = {
                "detection_id": f"det_{idx + 1}_{uuid.uuid4().hex[:6]}",
                "index": idx + 1,
                "raw_class": raw_class,
                "object_identity": resolved["object_identity"],
                "candidate_material": candidate_material,
                "sub_type": sub_type,
                "suggested_category": suggested_category,
                "category_info": resolved["category_info"],
                "confidence": round(conf, 4),
                "confidence_pct": round(conf * 100, 1),
                "needs_review": needs_review,
                "status": "unverified",
                "estimated_weight_kg": resolved["estimated_weight_kg"],
                "how_to_handle": resolved["how_to_handle"],
                "safety_warning": resolved["safety_warning"],
                "bounding_box": {
                    "pixel": {
                        "x1": round(x1, 1),
                        "y1": round(y1, 1),
                        "x2": round(x2, 1),
                        "y2": round(y2, 1),
                        "width": round(x2 - x1, 1),
                        "height": round(y2 - y1, 1)
                    },
                    "normalized": {
                        "x1": norm_x1,
                        "y1": norm_y1,
                        "x2": norm_x2,
                        "y2": norm_y2,
                        "width": norm_w,
                        "height": norm_h
                    }
                }
            }
            detections.append(det_obj)
            
            # Tally category
            category_summary[suggested_category] = category_summary.get(suggested_category, 0) + 1

    # Record detection batch in DB
    detection_id = f"SCAN-{uuid.uuid4().hex[:8].upper()}"
    filename = Path(image_path).name

    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO detections (id, image_filename, image_width, image_height, model_version, raw_detections_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                detection_id,
                filename,
                orig_w,
                orig_h,
                Config.YOLO_CHECKPOINT,
                json.dumps(detections)
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Error persisting detection to DB: {e}")

    return {
        "detection_batch_id": detection_id,
        "image": {
            "filename": filename,
            "width": orig_w,
            "height": orig_h,
            "aspect_ratio": round(orig_w / orig_h, 3) if orig_h > 0 else 1.0
        },
        "model": {
            "name": Config.YOLO_CHECKPOINT,
            "confidence_threshold": conf_threshold
        },
        "count": len(detections),
        "category_summary": category_summary,
        "detections": detections,
        "uncertainty_note": (
            "No objects detected with sufficient confidence. Please choose a category manually below or refer to the Waste Guide." 
            if len(detections) == 0 else None
        )
    }
