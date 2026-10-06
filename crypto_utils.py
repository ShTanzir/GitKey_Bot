import base64
import hashlib
import json
import secrets
import string
import uuid
from typing import Tuple


def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password."""
    if length < 8:
        length = 16
        
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    all_chars = lower + upper + digits + symbols

    # Ensure at least one character from each set
    pwd = [
        secrets.choice(lower),
        secrets.choice(upper),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]

    for _ in range(length - 4):
        pwd.append(secrets.choice(all_chars))

    # Shuffle characters
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def calculate_hash(data: bytes, algorithm: str) -> str:
    """Calculate MD5, SHA-1, or SHA-256 hash of binary data."""
    alg = algorithm.lower().replace("-", "")
    if alg == "md5":
        h = hashlib.md5(data)
    elif alg in ("sha1", "sha1"):
        h = hashlib.sha1(data)
    elif alg in ("sha256", "sha256"):
        h = hashlib.sha256(data)
    else:
        return f"Unsupported algorithm: {algorithm}"

    digest = h.digest()
    return ":".join(f"{b:02X}" for b in digest)


def calculate_raw_hex(data: bytes, algorithm: str) -> str:
    """Calculate raw hex string without colons."""
    alg = algorithm.lower().replace("-", "")
    if alg == "md5":
        return hashlib.md5(data).hexdigest()
    elif alg == "sha1":
        return hashlib.sha1(data).hexdigest()
    elif alg == "sha256":
        return hashlib.sha256(data).hexdigest()
    return ""


def encode_base64(data: bytes) -> str:
    """Encode bytes to Base64 without line breaks."""
    return base64.b64encode(data).decode('utf-8')


def decode_base64(b64_str: str) -> Tuple[bool, bytes, str]:
    """Decode Base64 string to bytes safely."""
    try:
        cleaned = b64_str.strip()
        decoded = base64.b64decode(cleaned)
        return True, decoded, f"Successfully decoded {len(decoded)} bytes."
    except Exception as e:
        return False, b"", f"Base64 Decode Error: {str(e)}"


def format_json(raw_json: str, indent: int = 4) -> Tuple[bool, str]:
    """Format and beautify JSON string."""
    try:
        parsed = json.loads(raw_json)
        return True, json.dumps(parsed, indent=indent)
    except Exception as e:
        return False, f"Invalid JSON: {str(e)}"


def generate_uuid_v4() -> str:
    """Generate a random v4 UUID."""
    return str(uuid.uuid4())
