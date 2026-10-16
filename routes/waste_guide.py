from flask import Blueprint, request, jsonify
from services.waste_guide_service import (
    WASTE_CATEGORIES,
    ITEM_GUIDES,
    search_waste_guide,
    get_item_guidance,
    get_category_info
)

waste_guide_bp = Blueprint("waste_guide", __name__, url_prefix="/api")

@waste_guide_bp.route("/waste-guide", methods=["GET"])
def get_waste_guide():
    """
    Search and retrieve waste items from the comprehensive Responsible Citizen Guide.
    Query parameters:
    - q: search term (e.g. 'bottle', 'banana', 'battery', 'oil')
    - category: filter by 1 of the 8 canonical categories
    - locality: optional locality to tailor guidance
    """
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    locality = request.args.get("locality", "")

    items = search_waste_guide(query=q, category=category, locality=locality)
    return jsonify({
        "status": "success",
        "count": len(items),
        "query": q,
        "category_filter": category,
        "locality": locality,
        "items": items
    })

@waste_guide_bp.route("/waste-guide/categories", methods=["GET"])
def get_waste_categories():
    """Returns the 8 official broad waste categories and bin conventions."""
    return jsonify({
        "status": "success",
        "categories": list(WASTE_CATEGORIES.values())
    })

@waste_guide_bp.route("/waste-guide/item/<item_id>", methods=["GET"])
def get_item_detail(item_id):
    """Returns full 8-point responsible handling guidance for a specific item."""
    item = get_item_guidance(item_id)
    if not item:
        return jsonify({"status": "error", "message": f"Item '{item_id}' not found in guide."}), 404

    item_copy = dict(item)
    item_copy["category_info"] = get_category_info(item["category"])
    return jsonify({
        "status": "success",
        "item": item_copy
    })
