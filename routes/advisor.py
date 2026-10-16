from flask import Blueprint, request, jsonify
from services.advisory_engine import AdvisoryEngine, CIRCULAR_RULES

advisor_bp = Blueprint("advisor", __name__, url_prefix="/api/advisor")

@advisor_bp.route("/insights", methods=["GET"])
def get_insights():
    insights = AdvisoryEngine.get_operational_insights()
    return jsonify({
        "status": "success",
        "count": len(insights),
        "insights": insights
    })

@advisor_bp.route("/rules", methods=["GET"])
def get_rules():
    return jsonify({
        "status": "success",
        "rules": CIRCULAR_RULES
    })

@advisor_bp.route("/query", methods=["POST"])
def query_advisor():
    body = request.get_json() or {}
    question = body.get("question", "").strip()

    if not question:
        return jsonify({
            "status": "error",
            "message": "Question parameter is required."
        }), 400

    response = AdvisoryEngine.answer_query(question)
    return jsonify({
        "status": "success",
        "data": response
    })
