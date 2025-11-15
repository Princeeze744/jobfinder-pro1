"""
Configuration Module
Handles all environment variables and system settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================
# API CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("❌ ERROR: ANTHROPIC_API_KEY not found in .env file!")

# Claude Model Configuration
CLAUDE_MODEL = "claude-opus-4-1-20250805"
MAX_TOKENS = 2000
TEMPERATURE = 0.3  # Lower temperature for accurate CV analysis

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = SRC_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = SRC_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# OUTPUT FILES
# ============================================================
CV_ANALYSIS_OUTPUT = DATA_DIR / "cv_analysis.json"
COMPANIES_OUTPUT = DATA_DIR / "companies_output.json"
EMAILS_OUTPUT = DATA_DIR / "emails_output.json"
LOG_FILE = LOGS_DIR / "application.log"

# ============================================================
# LOGGING CONFIGURATION
# ============================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

# ============================================================
# EMAIL CONFIGURATION
# ============================================================
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# ============================================================
# WEB SEARCH CONFIGURATION
# ============================================================
SEARCH_RESULTS_LIMIT = 10
REQUEST_TIMEOUT = 10  # seconds

# ============================================================
# SYSTEM SETTINGS
# ============================================================
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
VERBOSE_OUTPUT = True
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

print("✅ Configuration loaded successfully!")