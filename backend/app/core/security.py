import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Role constants ────────────────────────────────────────────────────────────

POSITION_ROLES = frozenset({"chief", "chairman", "head"})
DIVISION_ROLES = frozenset({"bba", "hld", "sci", "ss", "thm", "faa", "mba", "mm"})
FA_ROLES       = frozenset({"fa"})

# Some roles need broader ILIKE root for subunit matching (e.g. "sci_lab" → SCI%)
ILIKE_ROOT_OVERRIDE: dict[str, str] = {
    "sci_lab": "SCI",
}

# ── Encryption ────────────────────────────────────────────────────────────────

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.encryption_key
        if not key:
            key = Fernet.generate_key().decode()
            logger.warning("ENCRYPTION_KEY not set — using ephemeral key (data survives only until restart)")
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_value(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode()).decode()


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(
    username: str,
    role: str,
    position: str | None = None,
    coordinator: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": username,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expires_seconds),
    }
    if position:
        payload["position"] = position
    if coordinator:
        payload["coordinator"] = True
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# ── Permission helpers ────────────────────────────────────────────────────────

def extract_claims(job_title: str) -> dict:
    """Parse Entra ID jobTitle → {"role": str, "position": str | None}.

    Expected formats:
      "group,unit"                → role=unit
      "group,unit,position"       → role=unit, position=position
      "group,type,unit,position"  → role=unit, position=position
    Position (chief/chairman/head) is always the last segment when present.
    """
    parts = [p.strip().lower() for p in job_title.split(",") if p.strip()]
    if not parts:
        return {"role": "user", "position": None}

    if parts[-1] in POSITION_ROLES:
        position = parts[-1]
        role = parts[-2] if len(parts) >= 2 else "user"
    else:
        position = None
        role = parts[-1]

    return {"role": role, "position": position}


def has_access_by_position(position: str | None) -> bool:
    return bool(position) and position.lower() in POSITION_ROLES


def is_fa(role: str) -> bool:
    return role.lower() in FA_ROLES


def is_division(role: str) -> bool:
    return role.lower() in DIVISION_ROLES


# ── Cache helpers ─────────────────────────────────────────────────────────────

def params_hash(params: dict) -> str:
    content = str(sorted((k, v) for k, v in params.items() if v is not None))
    return hashlib.md5(content.encode()).hexdigest()[:16]
