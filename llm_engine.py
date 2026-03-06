import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    """Create Groq client fresh each call so the API key is always current."""
    return Groq(api_key=os.getenv("GROQ_API_KEY", ""))


# ─────────────────────────────────────────────────────────────────────────────
# Core AI caller
# ─────────────────────────────────────────────────────────────────────────────

def call_ai(messages):
    response = _get_client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
        max_tokens=4000
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# Code Analysis
# Used by: analyze_code.py route  +  validator.py
#
# New return keys (12 total):
#   concept, explanation,
#   has_error (bool),
#   error_type, error_line_number (int), error_line,
#   error_description, fix_code, fix_explanation,
#   hint, what_you_did_right, concept_explanation
# ─────────────────────────────────────────────────────────────────────────────

def analyze_code_with_ai(code: str, problem: str = None) -> dict:

    if not problem:
        problem = "Analyze this code carefully."

    # Number every line so AI can reference exact line numbers
    numbered_code = _number_lines(code)

    messages = [
        {
            "role": "system",
            "content": """You are an expert programming teacher and debugger.

The code is shown with line numbers like:
  1 | first line of code
  2 | second line of code

Return STRICT JSON only. No markdown. No backticks. No text outside the JSON.

{
  "concept": "Explain the main programming concept this code uses. Write 5-8 numbered points. Simple English.",
  "explanation": "Explain what this code does step by step. Write minimum 8 numbered steps. Reference line numbers.",
  "has_error": true,
  "error_type": "Syntax Error / Runtime Error / Logic Error / Compilation Error / No Error",
  "error_line_number": 5,
  "error_line": "exact text of the line that has the error, copied from the code",
  "error_description": "What is wrong on that line and why it causes the error. 2-4 sentences.",
  "fix_code": "The complete corrected version of the entire code. No markdown backticks inside this value.",
  "fix_explanation": "What you changed in the fix and why it solves the problem. 3-5 sentences.",
  "hint": "One short sentence telling the student exactly what to fix.",
  "what_you_did_right": "One encouraging sentence about what is correct in the code.",
  "concept_explanation": "2-3 sentence summary of the core concept being practiced."
}

Strict rules:
- has_error must be boolean true or false. NOT a string.
- error_line_number must be an integer. Use 0 if no error.
- If NO error exists: has_error=false, error_type="No Error", error_line_number=0, error_line="", error_description="No errors found. The code is correct.", fix_code="Code is correct.", fix_explanation="No fix needed."
- Never use curly braces inside any string value.
- Always return all 12 keys.
- error_line must be the exact code text copied from that line."""
        },
        {
            "role": "user",
            "content": f"Problem:\n{problem}\n\nCode (with line numbers):\n{numbered_code}"
        }
    ]

    result = call_ai(messages)
    return safe_json_parse(result)


# ─────────────────────────────────────────────────────────────────────────────
# Line numbering
# ─────────────────────────────────────────────────────────────────────────────

def _number_lines(code: str) -> str:
    lines = code.splitlines()
    width = len(str(len(lines)))
    return "\n".join(
        f"{str(i + 1).rjust(width)} | {line}"
        for i, line in enumerate(lines)
    )


# ─────────────────────────────────────────────────────────────────────────────
# JSON helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_json_block(text: str) -> str:
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    start = text.find("{")
    if start == -1:
        return text

    depth = 0
    in_string   = False
    escape_next = False
    end         = start

    for i, ch in enumerate(text[start:], start=start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    return text[start:end + 1]


def safe_json_parse(result: str) -> dict:

    fallback = {
        "concept":             "",
        "explanation":         "",
        "has_error":           True,
        "error_type":          "Parse Error",
        "error_line_number":   0,
        "error_line":          "",
        "error_description":   "AI response parsing failed. Please try again.",
        "fix_code":            "",
        "fix_explanation":     "",
        "hint":                "Could not parse AI response.",
        "what_you_did_right":  "",
        "concept_explanation": "",
    }

    def _extract_fields(parsed: dict) -> dict:
        raw = parsed.get("has_error", True)
        has_error = (raw.strip().lower() != "false") if isinstance(raw, str) else bool(raw)

        try:
            line_num = int(parsed.get("error_line_number", 0))
        except (TypeError, ValueError):
            line_num = 0

        return {
            "concept":             str(parsed.get("concept",             "")).strip(),
            "explanation":         str(parsed.get("explanation",         "")).strip(),
            "has_error":           has_error,
            "error_type":          str(parsed.get("error_type",          "")).strip(),
            "error_line_number":   line_num,
            "error_line":          str(parsed.get("error_line",          "")).strip(),
            "error_description":   str(parsed.get("error_description",   "")).strip(),
            "fix_code":            str(parsed.get("fix_code",            "")).strip(),
            "fix_explanation":     str(parsed.get("fix_explanation",     "")).strip(),
            "hint":                str(parsed.get("hint",                "")).strip(),
            "what_you_did_right":  str(parsed.get("what_you_did_right",  "")).strip(),
            "concept_explanation": str(parsed.get("concept_explanation", "")).strip(),
        }

    # Strategy 1 — direct parse
    try:
        return _extract_fields(json.loads(result))
    except Exception:
        pass

    # Strategy 2 — extract JSON block then parse
    try:
        return _extract_fields(json.loads(extract_json_block(result)))
    except Exception:
        pass

    # Strategy 3 — regex per field
    try:
        def _re_str(key):
            m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', result, re.DOTALL)
            return m.group(1).replace("\\n", "\n").replace('\\"', '"').strip() if m else ""

        def _re_bool(key):
            m = re.search(rf'"{key}"\s*:\s*(true|false)', result, re.IGNORECASE)
            return m.group(1).lower() == "true" if m else True

        def _re_int(key):
            m = re.search(rf'"{key}"\s*:\s*(\d+)', result)
            return int(m.group(1)) if m else 0

        return {
            "concept":             _re_str("concept"),
            "explanation":         _re_str("explanation"),
            "has_error":           _re_bool("has_error"),
            "error_type":          _re_str("error_type"),
            "error_line_number":   _re_int("error_line_number"),
            "error_line":          _re_str("error_line"),
            "error_description":   _re_str("error_description"),
            "fix_code":            _re_str("fix_code"),
            "fix_explanation":     _re_str("fix_explanation"),
            "hint":                _re_str("hint"),
            "what_you_did_right":  _re_str("what_you_did_right"),
            "concept_explanation": _re_str("concept_explanation"),
        }
    except Exception:
        pass

    return fallback