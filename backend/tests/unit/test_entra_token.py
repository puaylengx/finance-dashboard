"""
Unit tests สำหรับ Entra ID token validation

ทดสอบทุก scenario ของ login_with_entra_token() โดยใช้ RSA key จริง
เพื่อยืนยันว่า backend validate token ถูกต้องก่อนนำไป integrate กับ Azure
"""
import base64
import math
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt as jose_jwt

# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def rsa_keys():
    """สร้าง RSA key pair สำหรับ test (ใช้ร่วมกันทั้ง module)"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return {"private": private_pem, "public": public_pem, "kid": "test-key-1"}


@pytest.fixture(scope="module")
def jwks(rsa_keys):
    """สร้าง JWKS จาก public key — format เดียวกับที่ Azure ส่งมา"""
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    pub = load_pem_public_key(rsa_keys["public"])
    nums = pub.public_numbers()

    def _b64url(n: int) -> str:
        byte_len = math.ceil(n.bit_length() / 8)
        return base64.urlsafe_b64encode(n.to_bytes(byte_len, "big")).rstrip(b"=").decode()

    return {
        "keys": [{
            "kty": "RSA", "use": "sig", "alg": "RS256",
            "kid": rsa_keys["kid"],
            "n": _b64url(nums.n),
            "e": _b64url(nums.e),
        }]
    }


def _make_token(rsa_keys: dict, claims: dict) -> str:
    """สร้าง RS256 JWT ด้วย test private key"""
    base = {
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iss": f"https://login.microsoftonline.com/test-tenant/v2.0",
    }
    return jose_jwt.encode(
        {**base, **claims},
        rsa_keys["private"],
        algorithm="RS256",
        headers={"kid": rsa_keys["kid"]},
    )


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestEntraTokenValidation:

    async def _call(self, jwks_data, token):
        """Helper: patch JWKS fetch แล้วเรียก login_with_entra_token"""
        from app.services import auth_service
        auth_service._entra_jwks_cache = None  # reset cache ทุก test

        with patch("app.core.config.settings.azure_tenant_id", "test-tenant"), \
             patch("app.core.config.settings.azure_client_id", "test-client-id"), \
             patch("app.services.auth_service._fetch_entra_jwks", AsyncMock(return_value=jwks_data)), \
             patch("app.services.auth_service.is_coordinator", AsyncMock(return_value=False)):
            from app.services.auth_service import login_with_entra_token
            return await login_with_entra_token(token)

    # ── happy path ────────────────────────────────────────────────────────────

    async def test_token_with_chief_position(self, rsa_keys, jwks):
        """token มี job_title = 'dept,fa,chief' → เข้าได้ด้วย position"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "user@company.com",
            "name": "Test Chief",
            "job_title": "dept,fa,chief",
        })
        result = await self._call(jwks, token)
        assert result is not None
        assert result.role == "fa"
        assert result.position == "chief"
        assert result.coordinator is False

    async def test_token_with_head_position(self, rsa_keys, jwks):
        """token มี job_title = 'dept,bba,head' → เข้าได้"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "head@company.com",
            "name": "BBA Head",
            "job_title": "dept,bba,head",
        })
        result = await self._call(jwks, token)
        assert result is not None
        assert result.role == "bba"
        assert result.position == "head"

    async def test_token_coordinator(self, rsa_keys, jwks):
        """user ไม่มี position แต่อยู่ใน coordinator table → เข้าได้"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "coord@company.com",
            "name": "Coordinator",
            "job_title": "dept,fa",
        })
        from app.services import auth_service
        auth_service._entra_jwks_cache = None

        with patch("app.core.config.settings.azure_tenant_id", "test-tenant"), \
             patch("app.core.config.settings.azure_client_id", "test-client-id"), \
             patch("app.services.auth_service._fetch_entra_jwks", AsyncMock(return_value=jwks)), \
             patch("app.services.auth_service.is_coordinator", AsyncMock(return_value=True)):
            from app.services.auth_service import login_with_entra_token
            result = await login_with_entra_token(token)

        assert result is not None
        assert result.coordinator is True
        assert result.role == "fa"

    # ── access denied ─────────────────────────────────────────────────────────

    async def test_token_no_position_not_coordinator(self, rsa_keys, jwks):
        """user ไม่มี position และไม่ใช่ coordinator → return None (→ 403)"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "nobody@company.com",
            "name": "Nobody",
            "job_title": "dept,fa",
        })
        result = await self._call(jwks, token)
        assert result is None

    async def test_token_empty_job_title(self, rsa_keys, jwks):
        """job_title ว่าง → role='user' ไม่มี position → return None"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "empty@company.com",
            "name": "Empty",
            "job_title": "",
        })
        result = await self._call(jwks, token)
        assert result is None

    async def test_token_missing_job_title_claim(self, rsa_keys, jwks):
        """token ไม่มี job_title claim เลย → return None"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "nojob@company.com",
            "name": "No Job Title",
            # ไม่มี job_title
        })
        result = await self._call(jwks, token)
        assert result is None

    # ── token validation errors ───────────────────────────────────────────────

    async def test_wrong_audience(self, rsa_keys, jwks):
        """token มี audience เป็น Graph (ไม่ใช่ client ID ของเรา) → return None"""
        token = _make_token(rsa_keys, {
            "aud": "https://graph.microsoft.com",   # ← ผิด
            "preferred_username": "user@company.com",
            "name": "Graph User",
            "job_title": "dept,fa,chief",
        })
        result = await self._call(jwks, token)
        assert result is None

    async def test_expired_token(self, rsa_keys, jwks):
        """token หมดอายุ → return None"""
        from app.services import auth_service
        auth_service._entra_jwks_cache = None

        expired_claims = {
            "aud": "test-client-id",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
            "preferred_username": "user@company.com",
            "name": "Expired",
            "job_title": "dept,fa,chief",
        }
        token = jose_jwt.encode(
            expired_claims, rsa_keys["private"], algorithm="RS256",
            headers={"kid": rsa_keys["kid"]},
        )
        result = await self._call(jwks, token)
        assert result is None

    async def test_unknown_kid(self, rsa_keys, jwks):
        """token มี kid ที่ไม่อยู่ใน JWKS → return None"""
        token = jose_jwt.encode(
            {
                "aud": "test-client-id",
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "preferred_username": "user@company.com",
                "name": "Test",
                "job_title": "dept,fa,chief",
            },
            rsa_keys["private"],
            algorithm="RS256",
            headers={"kid": "wrong-kid"},   # ← ไม่ match JWKS
        )
        result = await self._call(jwks, token)
        assert result is None

    async def test_not_configured(self):
        """AZURE_TENANT_ID หรือ AZURE_CLIENT_ID ว่าง → raise EntraNotConfiguredError"""
        from app.services.auth_service import EntraNotConfiguredError, login_with_entra_token
        with patch("app.core.config.settings.azure_tenant_id", ""), \
             patch("app.core.config.settings.azure_client_id", ""):
            with pytest.raises(EntraNotConfiguredError):
                await login_with_entra_token("any.token.here")

    # ── claim field variants ──────────────────────────────────────────────────

    async def test_jobTitle_camelcase(self, rsa_keys, jwks):
        """backend รองรับ 'jobTitle' (camelCase) ด้วย ไม่ใช่แค่ 'job_title'"""
        token = _make_token(rsa_keys, {
            "aud": "test-client-id",
            "preferred_username": "user@company.com",
            "name": "Camel User",
            "jobTitle": "dept,sci,chairman",   # ← camelCase
        })
        result = await self._call(jwks, token)
        assert result is not None
        assert result.position == "chairman"
        assert result.role == "sci"
