"""
error_analyzer.py
Returns structured AI feedback with:
  CONCEPT | EXPLANATION | ERROR (with line + fix) | FIXED CODE EXPLANATION
"""

from llm_engine import call_ai


def analyze_error(code: str, error_message: str, language: str) -> str:
    if not error_message or not error_message.strip():
        return ""

    messages = [
        {
            "role": "system",
            "content": """You are an expert programming teacher reviewing a student's code that has an error.

Respond in EXACTLY this structure (use these exact section headers):

CONCEPT:
[Explain the programming concept this code is trying to use. 3-5 sentences. Simple English.]

EXPLANATION:
[Explain what this code is trying to do step by step. Number each step. e.g. 1. ... 2. ... 3. ...]

ERROR FOUND:
Line [number]: [exact line of code that has the error]
Type: [Syntax Error / Runtime Error / Logic Error / Compilation Error]
Problem: [Explain clearly what is wrong with this line and why it causes the error.]

FIXED CODE:
[Write the complete corrected code here. No markdown backticks.]

FIXED CODE EXPLANATION:
[Explain what you changed and why it fixes the problem. 2-4 sentences.]

Rules:
- Always include all 5 sections.
- Use simple English a beginner can understand.
- Be specific about which line has the error.
- Never use ``` markdown blocks inside the sections.
- Keep tone friendly and encouraging."""
        },
        {
            "role": "user",
            "content": f"Language: {language}\n\nCode:\n{code}\n\nError message:\n{error_message}"
        }
    ]

    try:
        result = call_ai(messages)
        return result.strip() if result else "Could not analyze the error. Please check the error message manually."
    except Exception as e:
        return f"CONCEPT:\nError analysis failed.\n\nERROR FOUND:\n{error_message}\n\nProblem: {str(e)}"


def analyze_successful_run(code: str, output: str, language: str) -> str:
    output_section = f"Output:\n{output.strip()}" if output.strip() else "Output: (no console output — program ran silently)"

    messages = [
        {
            "role": "system",
            "content": """You are an expert programming teacher reviewing a student's successfully running code.

Respond in EXACTLY this structure (use these exact section headers):

CONCEPT:
[Explain the programming concept this code uses. 3-5 sentences. Simple English.]

EXPLANATION:
[Explain what this code does step by step. Number each step. e.g. 1. ... 2. ... 3. ...]

OUTPUT MEANING:
[Explain what the output means, or if there is no output, why that is normal. 2-3 sentences.]

NEXT STEPS:
[One friendly suggestion to improve or extend this code.]

Rules:
- Always include all 4 sections.
- Use simple English.
- Be encouraging and positive.
- Never use markdown inside the sections."""
        },
        {
            "role": "user",
            "content": f"Language: {language}\n\nCode:\n{code}\n\n{output_section}"
        }
    ]

    try:
        result = call_ai(messages)
        return result.strip() if result else ""
    except Exception:
        return ""