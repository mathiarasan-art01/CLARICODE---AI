"""
onecompiler_integration.py — fixed success detection + full language table
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# NOTE: Do NOT cache the API key as a module-level variable.
# It must be read with os.getenv() inside each function call so that
# load_dotenv() in app.py always has time to populate os.environ first.
ONECOMPILER_URL = "https://api.onecompiler.com/v1/run"

LANGUAGES = {
    "ada":          ("ada",          "Ada",                    ".adb",    "Programming"),
    "assembly":     ("assembly",     "Assembly",               ".asm",    "Programming"),
    "awk":          ("awk",          "AWK",                    ".awk",    "Programming"),
    "bash":         ("bash",         "Bash",                   ".sh",     "Shell"),
    "sh":           ("bash",         "Shell (Bash)",           ".sh",     "Shell"),
    "basic":        ("basic",        "Basic",                  ".bas",    "Basic"),
    "brainfuck":    ("brainfk",      "BrainFK",                ".bf",     "Esoteric"),
    "bf":           ("brainfk",      "BrainFK",                ".bf",     "Esoteric"),
    "bun":          ("bun",          "Bun",                    ".js",     "JavaScript"),
    "c":            ("c",            "C",                      ".c",      "C/C++"),
    "cpp":          ("cpp",          "C++",                    ".cpp",    "C/C++"),
    "c++":          ("cpp",          "C++",                    ".cpp",    "C/C++"),
    "csharp":       ("csharp",       "C#",                     ".cs",     "C#"),
    "cs":           ("csharp",       "C#",                     ".cs",     "C#"),
    "clojure":      ("clojure",      "Clojure",                ".clj",    "Clojure"),
    "cobol":        ("cobol",        "COBOL",                  ".cbl",    "COBOL"),
    "coffeescript": ("coffeescript", "CoffeeScript",           ".coffee", "JavaScript"),
    "commonlisp":   ("commonlisp",   "Common Lisp",            ".lisp",   "Lisp"),
    "lisp":         ("commonlisp",   "Common Lisp",            ".lisp",   "Lisp"),
    "crystal":      ("crystal",      "Crystal",                ".cr",     "Crystal"),
    "d":            ("d",            "D",                      ".d",      "D"),
    "dart":         ("dart",         "Dart",                   ".dart",   "Dart"),
    "deno":         ("deno",         "Deno",                   ".ts",     "JavaScript"),
    "elixir":       ("elixir",       "Elixir",                 ".ex",     "Elixir"),
    "erlang":       ("erlang",       "Erlang",                 ".erl",    "Erlang"),
    "fsharp":       ("fsharp",       "F#",                     ".fs",     "F#"),
    "fs":           ("fsharp",       "F#",                     ".fs",     "F#"),
    "forth":        ("forth",        "Forth",                  ".forth",  "Forth"),
    "fortran":      ("fortran",      "Fortran",                ".f90",    "Fortran"),
    "go":           ("go",           "Go",                     ".go",     "Go"),
    "golang":       ("go",           "Go",                     ".go",     "Go"),
    "groovy":       ("groovy",       "Groovy",                 ".groovy", "Groovy"),
    "haskell":      ("haskell",      "Haskell",                ".hs",     "Haskell"),
    "haxe":         ("haxe",         "Haxe",                   ".hx",     "Haxe"),
    "java":         ("java",         "Java",                   ".java",   "Java"),
    "javascript":   ("javascript",   "JavaScript",             ".js",     "JavaScript"),
    "js":           ("javascript",   "JavaScript",             ".js",     "JavaScript"),
    "jshell":       ("jshell",       "JShell",                 ".jsh",    "Java"),
    "julia":        ("julia",        "Julia",                  ".jl",     "Julia"),
    "kotlin":       ("kotlin",       "Kotlin",                 ".kt",     "Kotlin"),
    "kt":           ("kotlin",       "Kotlin",                 ".kt",     "Kotlin"),
    "lua":          ("lua",          "Lua",                    ".lua",    "Lua"),
    "nim":          ("nim",          "Nim",                    ".nim",    "Nim"),
    "nodejs":       ("nodejs",       "Node.js",                ".js",     "JavaScript"),
    "node":         ("nodejs",       "Node.js",                ".js",     "JavaScript"),
    "objectivec":   ("objectivec",   "Objective-C",            ".m",      "Objective-C"),
    "objc":         ("objectivec",   "Objective-C",            ".m",      "Objective-C"),
    "ocaml":        ("ocaml",        "OCaml",                  ".ml",     "OCaml"),
    "octave":       ("octave",       "Octave",                 ".m",      "Octave"),
    "matlab":       ("octave",       "Octave (MATLAB-compat)", ".m",      "Octave"),
    "pascal":       ("pascal",       "Pascal",                 ".pas",    "Pascal"),
    "perl":         ("perl",         "Perl",                   ".pl",     "Perl"),
    "php":          ("php",          "PHP",                    ".php",    "PHP"),
    "prolog":       ("prolog",       "Prolog",                 ".pl",     "Prolog"),
    "python":       ("python",       "Python 3",               ".py",     "Python"),
    "python3":      ("python",       "Python 3",               ".py",     "Python"),
    "py":           ("python",       "Python 3",               ".py",     "Python"),
    "python2":      ("python2",      "Python 2",               ".py",     "Python"),
    "r":            ("r",            "R",                      ".r",      "R"),
    "racket":       ("racket",       "Racket",                 ".rkt",    "Racket"),
    "ruby":         ("ruby",         "Ruby",                   ".rb",     "Ruby"),
    "rb":           ("ruby",         "Ruby",                   ".rb",     "Ruby"),
    "rust":         ("rust",         "Rust",                   ".rs",     "Rust"),
    "rs":           ("rust",         "Rust",                   ".rs",     "Rust"),
    "scala":        ("scala",        "Scala",                  ".scala",  "Scala"),
    "scheme":       ("scheme",       "Scheme",                 ".scm",    "Scheme"),
    "smalltalk":    ("smalltalk",    "Smalltalk",              ".st",     "Smalltalk"),
    "swift":        ("swift",        "Swift",                  ".swift",  "Swift"),
    "tcl":          ("tcl",          "Tcl",                    ".tcl",    "Tcl"),
    "text":         ("text",         "Plain Text",             ".txt",    "Other"),
    "plaintext":    ("text",         "Plain Text",             ".txt",    "Other"),
    "typescript":   ("typescript",   "TypeScript",             ".ts",     "TypeScript"),
    "ts":           ("typescript",   "TypeScript",             ".ts",     "TypeScript"),
    "vb":           ("vb",           "Visual Basic (VB.NET)",  ".vb",     "Visual Basic"),
    "visualbasic":  ("vb",           "Visual Basic (VB.NET)",  ".vb",     "Visual Basic"),
    "zig":          ("zig",          "Zig",                    ".zig",    "Zig"),
    "mysql":        ("mysql",        "MySQL",                  ".sql",    "Database"),
    "postgresql":   ("postgresql",   "PostgreSQL",             ".sql",    "Database"),
    "postgres":     ("postgresql",   "PostgreSQL",             ".sql",    "Database"),
    "sqlite":       ("sqlite",       "SQLite",                 ".sql",    "Database"),
    "sql":          ("sqlite",       "SQLite",                 ".sql",    "Database"),
    "mongodb":      ("mongodb",      "MongoDB",                ".js",     "Database"),
    "redis":        ("redis",        "Redis",                  ".redis",  "Database"),
    "mariadb":      ("mariadb",      "MariaDB",                ".sql",    "Database"),
    "sqlserver":    ("sqlserver",    "Microsoft SQL Server",   ".sql",    "Database"),
}

DEFAULT_FILENAMES = {
    "java": "Main.java", "kotlin": "Main.kt", "scala": "Main.scala",
    "groovy": "Main.groovy", "swift": "main.swift",
    "c": "main.c", "cpp": "main.cpp", "csharp": "Main.cs", "fsharp": "Main.fs",
    "vb": "Main.vb", "python": "main.py", "python2": "main.py",
    "ruby": "main.rb", "php": "main.php", "go": "main.go", "rust": "main.rs",
    "typescript": "main.ts", "javascript": "main.js", "nodejs": "main.js",
    "r": "main.r", "lua": "main.lua", "bash": "main.sh",
    "mysql": "query.sql", "postgresql": "query.sql",
    "sqlite": "query.sql", "mongodb": "query.js",
}


def resolve_language(language: str) -> tuple:
    key = str(language).lower().strip()
    if key in LANGUAGES:
        oc_id, display, ext, _ = LANGUAGES[key]
        return oc_id, display, ext
    for k, (oc_id, display, ext, cat) in LANGUAGES.items():
        if key in display.lower():
            return oc_id, display, ext
    raise ValueError(f"Unknown language: '{language}'.")


def _default_filename(oc_id: str, ext: str) -> str:
    return DEFAULT_FILENAMES.get(oc_id, f"main{ext}")


def submit(code: str, language: str, stdin: str = "", files: list = None) -> dict:
    try:
        oc_id, lang_name, ext = resolve_language(language)
    except ValueError as e:
        return _error(str(e))

    if not code and not files:
        return _error("No code provided.")

    if not files:
        files = [{"name": _default_filename(oc_id, ext), "content": code}]

    # Read API key fresh on every call — never use a module-level cached value
    api_key = os.getenv("ONECOMPILER_API_KEY", "").strip()
    if not api_key:
        return _error(
            "ONECOMPILER_API_KEY is missing or empty in your .env file.\n"
            "Get a free key at: https://onecompiler.com/api-console\n"
            "Add this line to backend/.env:  ONECOMPILER_API_KEY=your_key_here"
        )

    payload = {"language": oc_id, "stdin": stdin or "", "files": files}
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}

    try:
        resp = requests.post(ONECOMPILER_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return _error("Cannot connect to OneCompiler. Check your internet connection.")
    except requests.exceptions.Timeout:
        return _error("OneCompiler timed out (30s). Please try again.")
    except requests.exceptions.HTTPError as e:
        code_num = e.response.status_code if e.response else "?"
        if code_num == 401:
            return _error("Invalid OneCompiler API key (401).\nUpdate ONECOMPILER_API_KEY in backend/.env\nGet key: https://onecompiler.com/api-console")
        if code_num == 429:
            return _error("OneCompiler rate limit exceeded. Wait a moment and try again.")
        return _error(f"OneCompiler HTTP error {code_num}: {e}")
    except Exception as e:
        return _error(f"Unexpected error: {e}")

    api_status   = data.get("status",         "failed") or "failed"
    stdout       = data.get("stdout",         "") or ""
    stderr       = data.get("stderr",         "") or ""
    exception    = data.get("exception",      "") or ""
    exec_time    = data.get("executionTime",  "")
    compile_time = data.get("compilationTime","")
    memory       = data.get("memoryUsed",     "")
    limit_left   = data.get("limitRemaining", data.get("limitPerMonthRemaining", 0))
    api_error    = data.get("error",          "") or ""

    is_accepted = (api_status == "success" and not exception and not api_error)

    if api_status == "failed":
        status_desc = _map_api_error(api_error)
    elif exception:
        status_desc = "Runtime Error"
    else:
        status_desc = "Accepted"

    status_id     = 3 if is_accepted else 0
    error_message = _build_error_message(status_desc, exception, stderr, api_error)

    return {
        "stdout":          stdout,
        "stderr":          stderr,
        "compile_output":  "",
        "exception":       exception,
        "status":          status_desc,
        "status_id":       status_id,
        "is_accepted":     is_accepted,
        "time":            str(exec_time)    if exec_time    else "",
        "compile_time":    str(compile_time) if compile_time else "",
        "memory":          str(memory)       if memory       else "",
        "language":        lang_name,
        "error":           not is_accepted,
        "error_message":   error_message,
        "limit_remaining": int(limit_left)   if limit_left   else 0,
    }


def submit_batch(code: str, language: str, stdin_list: list, files: list = None) -> list:
    try:
        oc_id, lang_name, ext = resolve_language(language)
    except ValueError as e:
        return [_error(str(e))]

    if not files:
        files = [{"name": _default_filename(oc_id, ext), "content": code}]

    payload = {"language": oc_id, "stdin": stdin_list, "files": files}
    api_key = os.getenv("ONECOMPILER_API_KEY", "").strip()
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}

    try:
        resp = requests.post(ONECOMPILER_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        results = resp.json()
    except Exception as e:
        return [_error(f"Batch execution failed: {e}")]

    out = []
    for item in results:
        exception  = item.get("exception", "") or ""
        api_status = item.get("status",    "failed") or "failed"
        is_ok      = (api_status == "success" and not exception)
        out.append({
            "stdout":      item.get("stdout",    "") or "",
            "stderr":      item.get("stderr",    "") or "",
            "exception":   exception,
            "status":      "Accepted" if is_ok else "Runtime Error",
            "status_id":   3 if is_ok else 0,
            "is_accepted": is_ok,
            "time":        str(item.get("executionTime", "")),
            "memory":      "",
            "language":    lang_name,
            "error":       not is_ok,
            "error_message": exception,
            "stdin_used":  item.get("stdin", ""),
        })
    return out


def get_all_languages() -> list:
    seen, result = set(), []
    for key, (oc_id, label, ext, category) in LANGUAGES.items():
        if oc_id not in seen:
            seen.add(oc_id)
            result.append({"key": key, "id": oc_id, "label": label, "ext": ext, "category": category})
    return sorted(result, key=lambda x: (x["category"], x["label"]))


def get_languages_by_category() -> dict:
    groups = {}
    for lang in get_all_languages():
        groups.setdefault(lang["category"], []).append(lang)
    return groups


def get_language_ids() -> dict:
    seen, result = set(), {}
    for key, (oc_id, *_) in LANGUAGES.items():
        if oc_id not in seen:
            seen.add(oc_id)
            result[key] = oc_id
    return result


def is_language_supported(language: str) -> bool:
    try:
        resolve_language(language)
        return True
    except ValueError:
        return False


def _map_api_error(api_error: str) -> str:
    error_map = {
        "E001": "Time Limit Exceeded",
        "E002": "API Quota Exceeded",
        "E003": "Invalid API Key — update ONECOMPILER_API_KEY in .env",
        "E004": "API Key Missing — add ONECOMPILER_API_KEY to .env",
        "E005": "STDIN Too Long",
        "E006": "Unsupported Language",
    }
    if not api_error:
        return "Execution Failed"
    for code, desc in error_map.items():
        if code in api_error:
            return desc
    return f"API Error: {api_error}"


def _build_error_message(status_desc, exception, stderr, api_error) -> str:
    if status_desc == "Accepted":
        return ""
    parts = []
    if api_error:
        parts.append(f"API Error: {api_error}")
    if exception:
        parts.append(f"Exception:\n{exception.strip()}")
    if stderr:
        parts.append(f"Error Output:\n{stderr.strip()}")
    return "\n\n".join(parts) if parts else status_desc


def _error(message: str) -> dict:
    return {
        "stdout": "", "stderr": "", "compile_output": "", "exception": "",
        "status": "Error", "status_id": 0, "is_accepted": False,
        "time": "", "compile_time": "", "memory": "", "language": "",
        "error": True, "error_message": message, "limit_remaining": 0,
    }