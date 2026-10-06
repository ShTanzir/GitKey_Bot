import re
import time
import logging
from typing import Dict, List
import config

# Configure safe logging (NEVER print passwords or sensitive secrets)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GitKeyBot")


class RateLimiter:
    def __init__(self, limit_per_min: int = config.RATE_LIMIT_ACTIONS_PER_MIN):
        self.limit_per_min = limit_per_min
        self.user_timestamps: Dict[int, List[float]] = {}

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        timestamps = self.user_timestamps.get(user_id, [])
        # Keep only timestamps within the last 60 seconds
        timestamps = [ts for ts in timestamps if now - ts < 60.0]
        
        if len(timestamps) >= self.limit_per_min:
            self.user_timestamps[user_id] = timestamps
            return False
            
        timestamps.append(now)
        self.user_timestamps[user_id] = timestamps
        return True


rate_limiter = RateLimiter()


def sanitize_filename(filename: str, default: str = "gitkey_export") -> str:
    """Sanitize user input to prevent path traversal or invalid characters."""
    if not filename:
        return default
    # Remove directory separators and non-alphanumeric chars
    cleaned = re.sub(r'[^a-zA-Z0-9_\-]', '', filename.strip())
    return cleaned if cleaned else default


def sanitize_dn_field(text: str) -> str:
    """Sanitize Distinguished Name fields (CN, O, OU, L, ST, C)."""
    if not text:
        return ""
    # Remove comma and equals to prevent DN injection
    return re.sub(r'[,=]', ' ', text.strip())
