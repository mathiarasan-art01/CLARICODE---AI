"""
compiler_engine.py
Public API for code execution — delegates to onecompiler_integration.py.
Called by routes/compiler.py.
Drop-in replacement; same function signatures as before.
"""

from onecompiler_integration import (
    submit,
    submit_batch,
    get_all_languages,
    get_language_ids,
    get_languages_by_category,
    is_language_supported,
)


def run_code(code: str, language: str, stdin: str = "") -> dict:
    """Execute code. Returns normalised result dict."""
    return submit(code, language, stdin)


def run_batch(code: str, language: str, stdin_list: list) -> list:
    """Run same code against multiple stdin values (test cases)."""
    return submit_batch(code, language, stdin_list)


def get_supported_languages() -> list:
    """Returns [{"value": key, "label": display_name}, ...] for the frontend."""
    return [
        {"value": lang["key"], "label": lang["label"]}
        for lang in get_all_languages()
    ]


def get_supported_languages_grouped() -> dict:
    """Returns languages grouped by category for the frontend."""
    return get_languages_by_category()