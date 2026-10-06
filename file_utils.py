import os
import shutil
import time
import zipfile
import tempfile
from typing import List, Optional, Tuple
from cryptography import x509
from cryptography.hazmat.primitives import serialization

import config
import crypto_utils
from security import logger


class TempFileManager:
    """Manages temporary user file sessions and performs automatic cleanup."""

    @staticmethod
    def create_user_temp_dir(user_id: int) -> str:
        user_dir = os.path.join(config.TEMP_DIR, f"user_{user_id}_{int(time.time())}")
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    @staticmethod
    def cleanup_user_temp_dir(user_dir: str):
        if user_dir and os.path.exists(user_dir):
            try:
                shutil.rmtree(user_dir)
                logger.info(f"Cleaned up temp directory: {user_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory {user_dir}: {e}")

    @staticmethod
    def cleanup_expired_temp_files():
        """Periodically remove expired temp directories."""
        now = time.time()
        if not os.path.exists(config.TEMP_DIR):
            return

        for entry in os.listdir(config.TEMP_DIR):
            full_path = os.path.join(config.TEMP_DIR, entry)
            if os.path.isdir(full_path):
                try:
                    mtime = os.path.getmtime(full_path)
                    if now - mtime > config.TEMP_FILE_LIFETIME_SEC:
                        shutil.rmtree(full_path)
                        logger.info(f"Removed expired temp folder: {entry}")
                except Exception as e:
                    logger.error(f"Failed to delete expired temp file {entry}: {e}")


class ApkInspector:
    """Extracts signing certificate fingerprints and metadata from APK files."""

    @staticmethod
    def inspect_apk(apk_bytes: bytes) -> Tuple[bool, str]:
        try:
            with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as tmp:
                tmp.write(apk_bytes)
                tmp_path = tmp.name

            try:
                certs_found = []
                with zipfile.ZipFile(tmp_path, 'r') as zf:
                    for name in zf.namelist():
                        if name.startswith("META-INF/") and (name.endswith(".RSA") or name.endswith(".DSA") or name.endswith(".EC")):
                            cert_data = zf.read(name)
                            # Attempt PKCS7 DER parsing
                            try:
                                pkcs7_cert = x509.load_der_x509_certificate(cert_data)
                                certs_found.append(pkcs7_cert)
                            except Exception:
                                pass

                if not certs_found:
                    return True, "<b>APK Inspection Summary</b>\n--------------------------------\nAPK loaded successfully. No standard v1 RSA/DSA/EC signing certificates found in META-INF/ (may use v2/v3 signature scheme only)."

                cert = certs_found[0]
                cert_der = cert.public_bytes(serialization.Encoding.DER)
                sha256 = crypto_utils.calculate_hash(cert_der, "sha256")
                sha1 = crypto_utils.calculate_hash(cert_der, "sha1")
                md5 = crypto_utils.calculate_hash(cert_der, "md5")

                info = [
                    "<b>APK Certificate Inspection Summary</b>",
                    "--------------------------------",
                    f"<b>Subject:</b> <code>{cert.subject.rfc4514_string()}</code>",
                    f"<b>Issuer:</b> <code>{cert.issuer.rfc4514_string()}</code>",
                    f"<b>Valid Until:</b> {cert.not_valid_after_utc.strftime('%Y-%m-%d')}",
                    "",
                    "<b>Signing Fingerprints:</b>",
                    f"<b>SHA-256:</b> <code>{sha256}</code>",
                    f"<b>SHA-1:</b> <code>{sha1}</code>",
                    f"<b>MD5:</b> <code>{md5}</code>"
                ]

                return True, "\n".join(info)

            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            return False, f"APK Inspection Error: {str(e)}"
