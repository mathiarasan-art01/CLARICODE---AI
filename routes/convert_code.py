from flask import Blueprint, request, jsonify
from code_converter import convert_code_ai

convert_bp = Blueprint("convert_code", __name__)

@convert_bp.route("/", methods=["POST"])
def convert_code():
    data = request.get_json()
    code = data.get("code")
    target_language = data.get("target_language")

    if not code or not target_language:
        return jsonify({"error": True, "message": "Code and target language are required."}), 400

    try:
        converted = convert_code_ai(code, target_language)
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

    return jsonify({"converted_code": converted})