"""Application configuration."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "app.db"

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
ENABLE_AUTH = os.environ.get("ENABLE_AUTH", "true").lower() in ("1", "true", "yes")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "120"))

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
MAX_AUDIO_BYTES = int(os.environ.get("MAX_AUDIO_MB", "25")) * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".mp4", ".m4a", ".webm", ".mpeg", ".mpga"}

SUMMARY_STYLES = {
    "executive": "Executive Summary",
    "bullet_points": "Bullet Points",
    "action_items": "Action Items",
}
DEFAULT_SUMMARY_STYLE = "executive"
