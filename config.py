import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("ECOSYNC_SECRET_KEY", "ecosync-production-grade-key-2026-unbreak")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    # Database
    DATABASE_PATH = BASE_DIR / "database" / "ecosync.db"
    
    # Uploads
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # Computer Vision / YOLO
    MODEL_DIR = BASE_DIR / "models"
    # Starting YOLO checkpoint (e.g. yolo11n.pt, yolo8n.pt, or custom waste checkpoint)
    YOLO_CHECKPOINT = os.environ.get("ECOSYNC_YOLO_MODEL", "yolo11n.pt")
    DEFAULT_CONFIDENCE_THRESHOLD = 0.25
    
    # Optional Gemini / External AI Advisor
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    BASE_DIR = BASE_DIR

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.MODEL_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "database", exist_ok=True)
