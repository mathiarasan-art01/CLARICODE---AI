from llm_engine import analyze_code_with_ai


def validate_practice(code: str, problem: str = None) -> dict:
    """
    Validates student practice code using AI analysis.
    Uses new 12-field structure from llm_engine.
    """
    analysis = analyze_code_with_ai(code, problem)

    if not isinstance(analysis, dict):
        return {
            "status": "incorrect",
            "message": "AI returned an unexpected response format.",
            "explanation": "Unable to analyze the code properly.",
            "detailed_analysis": {}
        }

    has_error = analysis.get("has_error", True)
    status    = "correct" if not has_error else "incorrect"

    if status == "correct":
        message = analysis.get("what_you_did_right") or "Great job! Your solution looks correct."
    else:
        message = analysis.get("hint") or analysis.get("error_description") or "There seems to be an issue in your code."

    return {
        "status":    status,
        "message":   message,
        "explanation": analysis.get("concept_explanation") or analysis.get("concept") or "",
        "detailed_analysis": analysis,
    }