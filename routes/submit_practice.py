from flask import Blueprint, request, jsonify
from validator import validate_practice
from formatter import format_practice_response

submit_practice_bp = Blueprint("submit_practice", __name__)

@submit_practice_bp.route("/", methods=["POST"])
def practice():
    data = request.get_json()
    code = data.get("code")
    problem = data.get("problem")

    if not code:
        return jsonify({"error": True, "message": "Code is required"}), 400

    # Validate and format response
    validation_result = validate_practice(code, problem)
    formatted = format_practice_response(validation_result)

    return jsonify(formatted)