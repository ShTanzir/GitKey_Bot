import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa
from cryptography.hazmat.primitives.serialization import pkcs12

import crypto_utils
from security import sanitize_filename, sanitize_dn_field


@dataclass
class KeystoreConfig:
    project_name: str = "MyApp"
    alias: str = "key0"
    store_password: str = ""
    key_password: str = ""
    algorithm: str = "RSA"  # RSA, EC, DSA
    key_size: int = 2048
    validity_years: int = 25
    common_name: str = "Android Developer"
    organization: str = "GitKey App"
    organizational_unit: str = "Build"
    city: str = ""
    state: str = ""
    country: str = "US"


@dataclass
class KeystoreResult:
    project_name: str
    keystore_bytes: bytes
    base64_secret: str
    store_password: str
    alias: str
    key_password: str
    sha1_fingerprint: str
    sha256_fingerprint: str
    md5_fingerprint: str
    filename: str
    certificate_info: str


class KeystoreGenerator:
    @staticmethod
    def generate(config: KeystoreConfig) -> KeystoreResult:
        # 1. Key Generation
        alg_upper = config.algorithm.upper()
        if "EC" in alg_upper:
            curve = ec.SECP256R1()
            if config.key_size == 384:
                curve = ec.SECP384R1()
            elif config.key_size == 521:
                curve = ec.SECP521R1()
            private_key = ec.generate_private_key(curve)
        else: # Default RSA
            key_size = config.key_size if config.key_size in (2048, 3072, 4096) else 2048
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )

        # 2. Build Distinguished Name (DN)
        attributes = [
            x509.NameAttribute(x509.NameOID.COMMON_NAME, sanitize_dn_field(config.common_name or "Android Developer"))
        ]
        if config.organization:
            attributes.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, sanitize_dn_field(config.organization)))
        if config.organizational_unit:
            attributes.append(x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, sanitize_dn_field(config.organizational_unit)))
        if config.city:
            attributes.append(x509.NameAttribute(x509.NameOID.LOCALITY_NAME, sanitize_dn_field(config.city)))
        if config.state:
            attributes.append(x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, sanitize_dn_field(config.state)))
        if config.country and len(config.country) == 2:
            attributes.append(x509.NameAttribute(x509.NameOID.COUNTRY_NAME, sanitize_dn_field(config.country).upper()))

        subject = issuer = x509.Name(attributes)

        # 3. Validity Dates
        now = datetime.datetime.now(datetime.timezone.utc)
        valid_from = now - datetime.timedelta(days=1)
        years = config.validity_years if config.validity_years > 0 else 25
        valid_to = now + datetime.timedelta(days=365 * years)

        # 4. Certificate Creation
        cert = x509.CertificateBuilder()\
            .subject_name(subject)\
            .issuer_name(issuer)\
            .public_key(private_key.public_key())\
            .serial_number(x509.random_serial_number())\
            .not_valid_before(valid_from)\
            .not_valid_after(valid_to)\
            .sign(private_key, hashes.SHA256())

        # 5. PKCS12 Serialization
        p12_bytes = pkcs12.serialize_key_and_certificates(
            name=config.alias.encode('utf-8'),
            key=private_key,
            cert=cert,
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(config.store_password.encode('utf-8'))
        )

        # 6. Base64 Secret
        b64_secret = crypto_utils.encode_base64(p12_bytes)

        # 7. Fingerprints
        cert_der = cert.public_bytes(serialization.Encoding.DER)
        sha1 = crypto_utils.calculate_hash(cert_der, "sha1")
        sha256 = crypto_utils.calculate_hash(cert_der, "sha256")
        md5 = crypto_utils.calculate_hash(cert_der, "md5")

        filename = f"{sanitize_filename(config.project_name, 'upload_key')}-release.jks"

        cert_info = (
            f"DN: {subject.rfc4514_string()}\n"
            f"Valid: {valid_from.strftime('%Y-%m-%d')} to {valid_to.strftime('%Y-%m-%d')}\n"
            f"Alg: {config.algorithm} ({config.key_size} bits)"
        )

        return KeystoreResult(
            project_name=config.project_name,
            keystore_bytes=p12_bytes,
            base64_secret=b64_secret,
            store_password=config.store_password,
            alias=config.alias,
            key_password=config.key_password,
            sha1_fingerprint=sha1,
            sha256_fingerprint=sha256,
            md5_fingerprint=md5,
            filename=filename,
            certificate_info=cert_info
        )


class KeystoreInspector:
    @staticmethod
    def inspect(keystore_bytes: bytes, password: str) -> Tuple[bool, str]:
        try:
            private_key, cert, cas = pkcs12.load_key_and_certificates(
                keystore_bytes,
                password.encode('utf-8') if password else None
            )

            if not cert:
                return False, "No certificates found in the provided keystore."

            cert_der = cert.public_bytes(serialization.Encoding.DER)
            sha1 = crypto_utils.calculate_hash(cert_der, "sha1")
            sha256 = crypto_utils.calculate_hash(cert_der, "sha256")
            md5 = crypto_utils.calculate_hash(cert_der, "md5")

            info = [
                "<b>Keystore Inspection Summary</b>",
                "--------------------------------",
                f"<b>Subject:</b> <code>{cert.subject.rfc4514_string()}</code>",
                f"<b>Issuer:</b> <code>{cert.issuer.rfc4514_string()}</code>",
                f"<b>Valid From:</b> {cert.not_valid_before_utc.strftime('%Y-%m-%d %H:%M UTC')}",
                f"<b>Valid To:</b> {cert.not_valid_after_utc.strftime('%Y-%m-%d %H:%M UTC')}",
                f"<b>Serial Number:</b> <code>{cert.serial_number}</code>",
                "",
                "<b>Fingerprints:</b>",
                f"<b>SHA-256:</b> <code>{sha256}</code>",
                f"<b>SHA-1:</b> <code>{sha1}</code>",
                f"<b>MD5:</b> <code>{md5}</code>"
            ]

            return True, "\n".join(info)

        except Exception as e:
            return False, f"Inspection Failed (Check Password): {str(e)}"
