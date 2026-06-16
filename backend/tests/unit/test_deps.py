import pytest
from fastapi import HTTPException
from unittest.mock import patch
from jose import JWTError

from app.core.security import create_access_token
from app.api.v1.deps import get_current_user, require_fa, require_fa_with_position


class TestGetCurrentUser:
    async def test_valid_token_returns_full_payload(self):
        token = create_access_token("alice", "fa", position="chief")
        payload = await get_current_user(token=token)
        assert payload["sub"] == "alice"
        assert payload["role"] == "fa"
        assert payload["position"] == "chief"

    async def test_valid_token_without_position(self):
        token = create_access_token("bob", "bba")
        payload = await get_current_user(token=token)
        assert payload["sub"] == "bob"
        assert "position" not in payload

    async def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token="not.a.valid.token")
        assert exc.value.status_code == 401

    async def test_missing_sub_raises_401(self):
        with patch("app.api.v1.deps.decode_access_token", return_value={"role": "fa"}):
            with pytest.raises(HTTPException) as exc:
                await get_current_user(token="any.token")
        assert exc.value.status_code == 401

    async def test_expired_token_raises_401(self):
        with patch(
            "app.api.v1.deps.decode_access_token",
            side_effect=JWTError("Signature has expired"),
        ):
            with pytest.raises(HTTPException) as exc:
                await get_current_user(token="expired.token")
        assert exc.value.status_code == 401
        assert "WWW-Authenticate" in exc.value.headers

    async def test_coordinator_flag_preserved(self):
        token = create_access_token("coord", "bba", coordinator=True)
        payload = await get_current_user(token=token)
        assert payload.get("coordinator") is True


class TestRequireFa:
    async def test_fa_role_is_allowed(self):
        payload = {"sub": "alice", "role": "fa"}
        result = await require_fa(user=payload)
        assert result is payload

    async def test_fa_role_case_insensitive(self):
        payload = {"sub": "alice", "role": "FA"}
        result = await require_fa(user=payload)
        assert result is payload

    async def test_division_role_raises_403(self):
        for role in ("bba", "hld", "sci", "ss", "thm", "faa", "mba", "mm"):
            payload = {"sub": "user", "role": role}
            with pytest.raises(HTTPException) as exc:
                await require_fa(user=payload)
            assert exc.value.status_code == 403

    async def test_unknown_role_raises_403(self):
        payload = {"sub": "user", "role": "admin"}
        with pytest.raises(HTTPException) as exc:
            await require_fa(user=payload)
        assert exc.value.status_code == 403

    async def test_missing_role_raises_403(self):
        payload = {"sub": "user"}
        with pytest.raises(HTTPException) as exc:
            await require_fa(user=payload)
        assert exc.value.status_code == 403


class TestRequireFaWithPosition:
    async def test_fa_with_chief_is_allowed(self):
        payload = {"sub": "alice", "role": "fa", "position": "chief"}
        result = await require_fa_with_position(user=payload)
        assert result is payload

    async def test_fa_with_chairman_is_allowed(self):
        payload = {"sub": "alice", "role": "fa", "position": "chairman"}
        result = await require_fa_with_position(user=payload)
        assert result is payload

    async def test_fa_with_head_is_allowed(self):
        payload = {"sub": "alice", "role": "fa", "position": "head"}
        result = await require_fa_with_position(user=payload)
        assert result is payload

    async def test_fa_without_position_raises_403(self):
        payload = {"sub": "alice", "role": "fa"}
        with pytest.raises(HTTPException) as exc:
            await require_fa_with_position(user=payload)
        assert exc.value.status_code == 403

    async def test_fa_with_empty_position_raises_403(self):
        payload = {"sub": "alice", "role": "fa", "position": ""}
        with pytest.raises(HTTPException) as exc:
            await require_fa_with_position(user=payload)
        assert exc.value.status_code == 403

    async def test_fa_with_none_position_raises_403(self):
        payload = {"sub": "alice", "role": "fa", "position": None}
        with pytest.raises(HTTPException) as exc:
            await require_fa_with_position(user=payload)
        assert exc.value.status_code == 403

    async def test_division_with_position_raises_403(self):
        payload = {"sub": "bob", "role": "bba", "position": "head"}
        with pytest.raises(HTTPException) as exc:
            await require_fa_with_position(user=payload)
        assert exc.value.status_code == 403
