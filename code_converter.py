"""
code_converter.py
Converts code from one programming language to another using AI.
Used by the compiler's language-conversion feature.
"""

from llm_engine import call_ai
import json
import re


def convert_code(code: str, from_lang: str, to_lang: str) -> dict:
    """
    Converts code from one language to another.
    Returns:
        {
            "converted_code": str,
            "notes": str,       # Any important conversion notes
            "error": bool,
            "message": str
        }
    """
    if not code or not code.strip():
        return {
            "converted_code": "",
            "notes": "",
            "error": True,
            "message": "No code provided to convert."
        }

    if from_lang.lower() == to_lang.lower():
        return {
            "converted_code": code,
            "notes": "Same language selected - no conversion needed.",
            "error": False,
            "message": "No conversion needed."
        }

    messages = [
        {
            "role": "system",
            "content": f"""You are an expert programmer who converts code between programming languages accurately.

Convert the given {from_lang} code to {to_lang}.

Rules:
- Preserve the exact same logic and behavior
- Use idiomatic {to_lang} patterns (not just a direct translation)
- Handle language-specific differences (e.g., 0-indexed vs 1-indexed, type declarations, etc.)
- If some feature doesn't exist in {to_lang}, use the closest equivalent and note it

Return ONLY valid JSON in this exact format (no markdown, no backticks):
{{
  "converted_code": "the full converted code here",
  "notes": "any important notes about the conversion, or empty string if none"
}}

Make sure the converted_code is a proper string with \\n for newlines."""
        },
        {
            "role": "user",
            "content": f"""Convert this {from_lang} code to {to_lang}:

{code}"""
        }
    ]

    try:
        result = call_ai(messages)

        # Try to parse JSON response
        try:
            # Strip markdown fences if present
            clean = re.sub(r"```(?:json)?|```", "", result).strip()
            parsed = json.loads(clean)
            return {
                "converted_code": parsed.get("converted_code", "").replace("\\n", "\n"),
                "notes": parsed.get("notes", ""),
                "error": False,
                "message": f"Successfully converted from {from_lang} to {to_lang}."
            }
        except json.JSONDecodeError:
            # Fallback: try to extract code block
            code_match = re.search(r'"converted_code"\s*:\s*"((?:[^"\\]|\\.)*)"', result, re.DOTALL)
            if code_match:
                converted = code_match.group(1).replace("\\n", "\n").replace('\\"', '"')
                return {
                    "converted_code": converted,
                    "notes": "",
                    "error": False,
                    "message": f"Converted from {from_lang} to {to_lang}."
                }

            # Last resort: return raw result
            return {
                "converted_code": result,
                "notes": "Note: Conversion result may need manual cleanup.",
                "error": False,
                "message": "Conversion completed with warnings."
            }

    except Exception as e:
        return {
            "converted_code": "",
            "notes": "",
            "error": True,
            "message": f"Code conversion failed: {str(e)}"
        }


def get_conversion_languages() -> list:
    """Returns list of languages available for conversion."""
    return [
        {"value": "python",     "label": "Python"},
        {"value": "javascript", "label": "JavaScript"},
        {"value": "c",          "label": "C"},
        {"value": "cpp",        "label": "C++"},
        {"value": "java",       "label": "Java"},
        {"value": "typescript", "label": "TypeScript"},
        {"value": "go",         "label": "Go"},
        {"value": "rust",       "label": "Rust"},
        {"value": "php",        "label": "PHP"},
        {"value": "ruby",       "label": "Ruby"},
        {"value": "csharp",     "label": "C#"},
        {"value": "swift",      "label": "Swift"},
        {"value": "kotlin",     "label": "Kotlin"},
        {"value": "bash",       "label": "Bash"},
        {"value": "r",          "label": "R"},
    ]