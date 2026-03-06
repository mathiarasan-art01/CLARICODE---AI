"""
routes/analyze_code.py
POST /analyze/
Returns structured AI analysis with:
  CONCEPT, EXPLANATION, ERROR (line number + fix code + fix explanation)
"""

from flask import Blueprint, request, jsonify
from llm_engine import analyze_code_with_ai

analyze_code_bp = Blueprint("analyze_code", __name__)


@analyze_code_bp.route("/", methods=["POST"])
def analyze_code():
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({"error": True, "message": "No code provided."})

    code    = data.get("code", "").strip()
    problem = data.get("problem", None)

    if not code:
        return jsonify({"error": True, "message": "Code is empty."})

    try:
        analysis = analyze_code_with_ai(code, problem)

        # Return all 12 structured fields to the frontend
        return jsonify({
            "concept":             analysis.get("concept",             ""),
            "explanation":         analysis.get("explanation",         ""),
            "has_error":           analysis.get("has_error",           False),
            "error_type":          analysis.get("error_type",          ""),
            "error_line_number":   analysis.get("error_line_number",   0),
            "error_line":          analysis.get("error_line",          ""),
            "error_description":   analysis.get("error_description",   ""),
            "fix_code":            analysis.get("fix_code",            ""),
            "fix_explanation":     analysis.get("fix_explanation",     ""),
            "hint":                analysis.get("hint",                ""),
            "what_you_did_right":  analysis.get("what_you_did_right",  ""),
            "concept_explanation": analysis.get("concept_explanation", ""),
        })

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({
            "error":       True,
            "message":     "Server error occurred.",
            "concept":     "",
            "explanation": "",
            "has_error":   True,
            "error_type":  "Server Error",
            "error_line_number": 0,
            "error_line":  "",
            "error_description": "Please check backend logs.",
            "fix_code":    "",
            "fix_explanation": "",
            "hint":        "",
            "what_you_did_right": "",
            "concept_explanation": "",
        })