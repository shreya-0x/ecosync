import os
import sys
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify

from config import Config
from database.db import init_db
from services.model_loader import ModelManager
from routes.scanner import scanner_bp
from routes.digital_twin import digital_twin_bp
from routes.analytics import analytics_bp
from routes.advisor import advisor_bp
from routes.waste_guide import waste_guide_bp
from routes.demo import demo_bp

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(Config)

    # Initialize Database Schema & Seed Data
    init_db()

    # Pre-warm model in background
    ModelManager.get_instance()

    # Register Blueprints
    app.register_blueprint(scanner_bp)
    app.register_blueprint(digital_twin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(advisor_bp)
    app.register_blueprint(waste_guide_bp)
    app.register_blueprint(demo_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        model_status = ModelManager.get_status()
        return jsonify({
            "status": "healthy",
            "service": "EcoSync Environmental Intelligence Platform",
            "model_ready": model_status["is_loaded"],
            "model_name": model_status["model_name"],
            "database": str(Config.DATABASE_PATH.name)
        })

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(413)
    def handle_large_file(e):
        return jsonify({"status": "error", "message": "Uploaded file exceeds maximum 16MB limit."}), 413

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"status": "error", "message": "Internal processing error."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"============================================================")
    print(f"  ECOSYNC ENVIRONMENTAL INTELLIGENCE PLATFORM RUNNING")
    print(f"  Local URL: http://127.0.0.1:{port}")
    print(f"============================================================")
    app.run(host="127.0.0.1", port=port, debug=Config.DEBUG)
