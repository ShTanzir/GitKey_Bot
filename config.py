import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Telegram Bot Token (REQUIRED)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Server & Deployment Configuration
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() in ("true", "1", "yes")

# Security & Limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
TEMP_FILE_LIFETIME_SEC = int(os.getenv("TEMP_FILE_LIFETIME_SEC", "1800")) # 30 mins
RATE_LIMIT_ACTIONS_PER_MIN = int(os.getenv("RATE_LIMIT_ACTIONS_PER_MIN", "30"))

# File Directories
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Safe Default Settings
DEFAULT_HIDE_SECRETS = True
DEFAULT_CONFIRM_BEFORE_EXPORT = True
