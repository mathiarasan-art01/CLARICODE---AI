"""
routes/compiler.py  — fixed AI analysis trigger logic
"""

from flask import Blueprint, request, jsonify
from compiler_engine import (
    run_code, run_batch,
    get_supported_languages, get_supported_languages_grouped,
)
from code_converter import convert_code, get_conversion_languages
from error_analyzer import analyze_error, analyze_successful_run

compiler_bp = Blueprint("compiler", __name__)


@compiler_bp.route("/run", methods=["POST"])
def run():
    data = request.get_json()

    if not data or not data.get("code", "").strip():
        return jsonify({
            "error": True, "ai_analysis": "No code provided.",
            "stdout": "", "stderr": "", "exception": "",
            "status": "Error", "time": "", "memory": "",
            "limit_remaining": 0
        }), 400

    code     = data["code"].strip()
    language = data.get("language", "python").strip().lower()
    stdin    = data.get("stdin", "")

    result = run_code(code, language, stdin)

    # ── Decide AI mode based on actual execution outcome ──────────────────────
    # A run is truly successful only when:
    #   status_id == 3  OR  status == "Accepted"  (no compile/runtime error)
    status_id   = result.get("status_id", 0)
    status_desc = result.get("status", "")
    is_accepted = (status_id == 3) or (str(status_desc).lower() == "accepted")

    # Collect all error text in one place
    error_text = " ".join(filter(None, [
        result.get("compile_output", ""),
        result.get("exception", ""),
        result.get("stderr", ""),
        result.get("error_message", ""),
    ])).strip()

    ai_analysis = ""

    if is_accepted:
        # Successful run → positive / educational summary
        output_text = result.get("stdout", "").strip()
        ai_analysis = analyze_successful_run(code, output_text, language)
    elif error_text:
        # Real error → explain and fix
        ai_analysis = analyze_error(code, error_text, language)

    result["ai_analysis"] = ai_analysis
    result["is_accepted"] = is_accepted   # send to frontend for colour logic
    return jsonify(result)


@compiler_bp.route("/batch", methods=["POST"])
def batch():
    data = request.get_json()
    if not data or not data.get("code", "").strip():
        return jsonify({"error": True, "message": "No code provided."}), 400

    code       = data["code"].strip()
    language   = data.get("language", "python").strip().lower()
    stdin_list = data.get("stdin", [])
    if not isinstance(stdin_list, list):
        stdin_list = [str(stdin_list)]

    return jsonify(run_batch(code, language, stdin_list))


@compiler_bp.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data:
        return jsonify({"error": True, "message": "No data provided.",
                        "converted_code": "", "notes": ""}), 400
    return jsonify(convert_code(
        data.get("code", "").strip(),
        data.get("from_lang", "python"),
        data.get("to_lang",   "javascript"),
    ))


@compiler_bp.route("/languages", methods=["GET"])
def languages():
    grouped = request.args.get("grouped", "false").lower() == "true"
    if grouped:
        return jsonify({
            "compiler_languages":   get_supported_languages_grouped(),
            "conversion_languages": get_conversion_languages(),
        })
    return jsonify({
        "compiler_languages":   get_supported_languages(),
        "conversion_languages": get_conversion_languages(),
    })