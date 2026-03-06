"""
routes/compiler.py
Blueprint for /compiler endpoints using OneCompiler API.

  POST /compiler/run        — Execute code (single stdin)
  POST /compiler/batch      — Execute code with multiple stdin test cases
  POST /compiler/convert    — Convert code between languages (AI)
  GET  /compiler/languages  — All supported languages
"""

from flask import Blueprint, request, jsonify
from compiler_engine import (
    run_code,
    run_batch,
    get_supported_languages,
    get_supported_languages_grouped,
)
from code_converter import convert_code, get_conversion_languages
from error_analyzer import analyze_error, analyze_successful_run

compiler_bp = Blueprint("compiler", __name__)


# ── Run single code execution ────────────────────────────────────────────────
@compiler_bp.route("/run", methods=["POST"])
def run():
    """
    Request:  { "code": str, "language": str, "stdin": str (optional) }
    Response: { stdout, stderr, exception, status, time, memory,
                language, error, ai_analysis, limit_remaining }
    """
    data = request.get_json()

    if not data or not data.get("code", "").strip():
        return jsonify({
            "error": True,
            "ai_analysis": "No code provided.",
            "stdout": "", "stderr": "", "status": "Error",
            "time": "", "memory": "", "limit_remaining": 0
        }), 400

    code     = data["code"].strip()
    language = data.get("language", "python").strip().lower()
    stdin    = data.get("stdin", "")

    result = run_code(code, language, stdin)

    # AI analysis — error explanation OR success summary
    ai_analysis = ""
    if result.get("error") and result.get("error_message"):
        ai_analysis = analyze_error(code, result["error_message"], language)
    elif not result.get("error") and result.get("stdout"):
        ai_analysis = analyze_successful_run(code, result["stdout"], language)

    result["ai_analysis"] = ai_analysis
    return jsonify(result)


# ── Batch execution (multiple test cases) ────────────────────────────────────
@compiler_bp.route("/batch", methods=["POST"])
def batch():
    """
    Request:  { "code": str, "language": str, "stdin": ["input1", "input2", ...] }
    Response: [ {stdout, stderr, status, error, stdin_used}, ... ]
    """
    data = request.get_json()

    if not data or not data.get("code", "").strip():
        return jsonify({"error": True, "message": "No code provided."}), 400

    code       = data["code"].strip()
    language   = data.get("language", "python").strip().lower()
    stdin_list = data.get("stdin", [])

    if not isinstance(stdin_list, list):
        stdin_list = [str(stdin_list)]

    results = run_batch(code, language, stdin_list)
    return jsonify(results)


# ── Code conversion ──────────────────────────────────────────────────────────
@compiler_bp.route("/convert", methods=["POST"])
def convert():
    """
    Request:  { "code": str, "from_lang": str, "to_lang": str }
    Response: { converted_code, notes, error, message }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": True, "message": "No data provided.",
                        "converted_code": "", "notes": ""}), 400

    code      = data.get("code", "").strip()
    from_lang = data.get("from_lang", "python")
    to_lang   = data.get("to_lang",   "javascript")

    result = convert_code(code, from_lang, to_lang)
    return jsonify(result)


# ── Language list ────────────────────────────────────────────────────────────
@compiler_bp.route("/languages", methods=["GET"])
def languages():
    """Returns all supported languages for the frontend dropdowns."""
    grouped = request.args.get("grouped", "false").lower() == "true"

    if grouped:
        return jsonify({
            "compiler_languages":    get_supported_languages_grouped(),
            "conversion_languages":  get_conversion_languages(),
        })

    return jsonify({
        "compiler_languages":   get_supported_languages(),
        "conversion_languages": get_conversion_languages(),
    })