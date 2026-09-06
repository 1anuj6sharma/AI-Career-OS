"""
Token encryption at rest (spec §5).

`ENCRYPTION_KEY` is required by `Settings`, so a running application always has
one.  If it is malformed we fail loudly at import rather than silently storing
plaintext credentials — a "works but insecure" fallback is worse than a startup
error.
"""
from __future__ import annotations

from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.logging import logger


class TokenCipherUnavailable(RuntimeError):
    pass


def _build_cipher() -> Fernet:
    key = (settings.ENCRYPTION_KEY or "").strip()
    if not key:
        raise TokenCipherUnavailable(
            "ENCRYPTION_KEY is not set. Integration tokens cannot be stored securely. "
            "Generate one with: python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(key.encode())
    except (ValueError, TypeError) as exc:
        raise TokenCipherUnavailable(
            "ENCRYPTION_KEY is not a valid Fernet key (32 url-safe base64-encoded bytes)."
        ) from exc


class TokenCipher:
    """Encrypt/decrypt provider credentials. Never logs a token value."""

    def __init__(self) -> None:
        self._fernet = _build_cipher()

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        if not plaintext:
            return None
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        """
        Return None when the ciphertext cannot be read (rotated key, corrupt
        row).  Callers treat None as "credential unusable → reauth required".
        """
        if not ciphertext:
            return None
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except (InvalidToken, ValueError):
            logger.warning("Stored credential could not be decrypted; treating as expired.")
            return None


_cipher: Optional[TokenCipher] = None


def get_cipher() -> TokenCipher:
    global _cipher
    if _cipher is None:
        _cipher = TokenCipher()
    return _cipher
