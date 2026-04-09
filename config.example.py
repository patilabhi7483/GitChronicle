"""
config.example.py - TEMPLATE CONFIGURATION FILE
================================================
Copy this file to config.py and fill in your actual API keys.
NEVER commit config.py to version control - it's in .gitignore.
"""

import os

# Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "commitstory.db")

# Gemini AI API
# Get your FREE key at: https://aistudio.google.com/
# Free tier: 15 RPM, 1,500 RPD, 1M tokens/day
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_MODEL = "gemini-3-flash-preview"

# GitHub API (used for repository URL analysis on github.com)
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN", "YOUR_GITHUB_TOKEN_HERE")
GITHUB_API_BASE_URL = os.environ.get("GITHUB_API_BASE_URL", "https://api.github.com")
GITHUB_API_TIMEOUT_SECONDS = int(os.environ.get("GITHUB_API_TIMEOUT_SECONDS", "20"))
GITHUB_API_USER_AGENT = os.environ.get("GITHUB_API_USER_AGENT", "CommitStory/1.0")

# Branding
APP_NAME = "Commit Story"
APP_TAGLINE = "Turn your git history into a human story"
APP_VERSION = "1.0.0"

# Analysis Limits
MAX_COMMITS_PER_ANALYSIS = 500
MAX_PASTE_CHARS = 50_000
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024

# Git / Cloning
TEMP_CLONE_DIR = os.path.join(BASE_DIR, "temp")
CLONE_DEPTH = 200
ENABLE_GIT_CLONE_FALLBACK = True
ALLOWED_REPO_HOSTS = [
    "github.com",
    "gitlab.com",
    "bitbucket.org",
]

# Narrative Formats
NARRATIVE_FORMATS = [
    ("release", "Release Notes"),
    ("standup", "Standup Summary"),
    ("onboarding", "Onboarding Story"),
    ("portfolio", "Portfolio README"),
]
DEFAULT_NARRATIVE_FORMAT = "release"

# Feature Flags
ENABLE_HISTORY = True
ENABLE_SHARE = True

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "generate-a-secret-key-here")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
