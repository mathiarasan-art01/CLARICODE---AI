def format_practice_response(validation_data: dict) -> dict:
    """
    Formats the output of validator.validate_practice() for the frontend.
    Passes through all fields; adds safe defaults if any are missing.
    """

    if not isinstance(validation_data, dict):
        return {
            "error": True,
            "message": "Invalid validation response."
        }

    detailed = validation_data.get("detailed_analysis", {})

    return {
        "status":    validation_data.get("status",      "incorrect"),
        "message":   validation_data.get("message",     "Review your approach and try again."),
        "explanation": validation_data.get("explanation", "Understanding the concept is key."),

        # Extra fields from llm_engine so the frontend can display richer feedback
        "error_detail": detailed.get("error", ""),   # what the error is
        "fix":          detailed.get("fix",   ""),   # corrected code snippet
        "concept":      detailed.get("concept", ""),

        "detailed_analysis": detailed
    }