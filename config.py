"""
config.py — Central configuration for ClariCode backend
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Groq AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # OneCompiler (replaces Judge0)
    ONECOMPILER_API_KEY = os.getenv("ONECOMPILER_API_KEY", "")

    # Flask
    DEBUG      = os.getenv("FLASK_DEBUG", "True") == "True"

    # Defaults
    DEFAULT_LANGUAGE = "python"
    MAX_CODE_LENGTH  = 100000   # characters


config = Config()