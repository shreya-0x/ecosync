import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

logger = logging.getLogger("ecosync.model_loader")

# Class label mapping: maps standard pretrained COCO/object detection classes
# to candidated material categories in the circular economy lifecycle.
# We are completely honest: we distinguish between the raw detected object
# and the inferred material category, and indicate human verification is needed.
COCO_MATERIAL_MAP = {
    # Plastics / Polymers
    "bottle": {"material": "Plastic", "sub_type": "PET / HDPE Container", "confidence_weight": 0.88},
    "cup": {"material": "Plastic / Paper", "sub_type": "Composite Beverage Cup", "confidence_weight": 0.82},
    "toothbrush": {"material": "Plastic", "sub_type": "Composite Polymer Handle", "confidence_weight": 0.90},
    
    # Metal / Alloys
    "can": {"material": "Metal", "sub_type": "UBC Aluminum / Tinplate", "confidence_weight": 0.94},
    "knife": {"material": "Metal", "sub_type": "Stainless Steel Utensil", "confidence_weight": 0.85},
    "fork": {"material": "Metal", "sub_type": "Stainless Steel Utensil", "confidence_weight": 0.85},
    "spoon": {"material": "Metal", "sub_type": "Stainless Steel Utensil", "confidence_weight": 0.85},
    "scissors": {"material": "Metal", "sub_type": "Ferrous Alloy & Polymer", "confidence_weight": 0.85},
    
    # Paper / Cardboard / Fiber
    "book": {"material": "Paper", "sub_type": "Bound Cellulose Fibers", "confidence_weight": 0.90},
    "box": {"material": "Cardboard", "sub_type": "Corrugated Kraftboard", "confidence_weight": 0.92},
    "suitcase": {"material": "Cardboard / Composite", "sub_type": "Rigid Polymer / Fiber", "confidence_weight": 0.75},
    "backpack": {"material": "Composite Fiber", "sub_type": "Woven Synthetic Polymer", "confidence_weight": 0.75},
    
    # Glass / Silicates
    "wine glass": {"material": "Glass", "sub_type": "High-Purity Silicate Glass", "confidence_weight": 0.95},
    "vase": {"material": "Glass / Ceramic", "sub_type": "Silicate / Ceramic Matrix", "confidence_weight": 0.85},
    
    # Electronic Waste
    "cell phone": {"material": "Electronic Waste", "sub_type": "PCB & Lithium Battery Assembly", "confidence_weight": 0.92},
    "laptop": {"material": "Electronic Waste", "sub_type": "Chassis & Electronic Circuitry", "confidence_weight": 0.92},
    "mouse": {"material": "Electronic Waste / Plastic", "sub_type": "ABS Polymer & Micro-switch", "confidence_weight": 0.88},
    "keyboard": {"material": "Electronic Waste / Plastic", "sub_type": "ABS Polymer & Circuit Membrane", "confidence_weight": 0.88},
    "remote": {"material": "Electronic Waste / Plastic", "sub_type": "Injection Molded Plastic & PCB", "confidence_weight": 0.85}
}

class ModelManager:
    _instance = None
    _model = None
    _model_name = "None"
    _is_loaded = False
    _load_error = None
    _device = "cpu"
    _classes = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.initialize_model()

    def initialize_model(self):
        """Attempts to load official YOLO checkpoint with fallback handling."""
        try:
            # Check if ultralytics is available
            from ultralytics import YOLO
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            ModelManager._device = device

            # Check preferred checkpoint
            checkpoint_name = Config.YOLO_CHECKPOINT
            model_path = Config.MODEL_DIR / checkpoint_name

            # If not in models/ dir, check if file exists in root or let ultralytics download
            target = str(model_path) if model_path.exists() else checkpoint_name
            logger.info(f"Loading YOLO checkpoint from {target} (device: {device})...")

            model = YOLO(target)
            
            ModelManager._model = model
            ModelManager._model_name = checkpoint_name
            ModelManager._is_loaded = True
            ModelManager._load_error = None
            ModelManager._classes = model.names if hasattr(model, "names") else {}
            logger.info(f"Successfully loaded YOLO checkpoint '{checkpoint_name}' with {len(ModelManager._classes)} classes.")

        except ImportError as e:
            msg = f"Ultralytics or PyTorch package not yet loaded: {str(e)}"
            logger.warning(msg)
            ModelManager._is_loaded = False
            ModelManager._load_error = msg
        except Exception as e:
            msg = f"Failed to initialize YOLO model: {str(e)}"
            logger.error(msg)
            ModelManager._is_loaded = False
            ModelManager._load_error = msg

    @classmethod
    def get_model(cls):
        manager = cls.get_instance()
        if not manager._is_loaded:
            # Try reloading once in case dependencies just finished installing
            manager.initialize_model()
        return manager._model

    @classmethod
    def get_status(cls):
        manager = cls.get_instance()
        if not manager._is_loaded:
            manager.initialize_model()
            
        return {
            "is_loaded": manager._is_loaded,
            "model_name": manager._model_name,
            "device": manager._device,
            "classes_count": len(manager._classes) if manager._classes else 0,
            "sample_classes": list(manager._classes.values())[:10] if manager._classes else [],
            "material_mappings_supported": len(COCO_MATERIAL_MAP),
            "error": manager._load_error
        }
