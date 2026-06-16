import pytest
from jose import JWTError

from app.core.security import (
    POSITION_ROLES,
    create_access_token,
    decode_access_token,
    encrypt_value,
    decrypt_value,
    extract_claims,
    has_access_by_position,
    is_division,
    is_fa,
    params_hash,
)


class TestExtractClaims:
    def test_role_only(self):
        r = extract_claims("dept,fa")
        assert r == {"role": "fa", "position": None}

    def test_with_position_chief(self):
        r = extract_claims("dept,fa,chief")
        assert r["role"] == "fa"
        assert r["position"] == "chief"

    def test_with_position_chairman(self):
        r = extract_claims("dept,type,fa,chairman")
        assert r["role"] == "fa"
        assert r["position"] == "chairman"

    def test_with_position_head(self):
        r = extract_claims("dept,bba,head")
        assert r["role"] == "bba"
        assert r["position"] == "head"

    def test_empty_string(self):
        r = extract_claims("")
        assert r == {"role": "user", "position": None}

    def test_single_segment(self):
        r = extract_claims("bba")
        assert r["role"] == "bba"
        assert r["position"] is None

    def test_case_insensitive(self):
        r = extract_claims("DEPT,FA,CHIEF")
        assert r["role"] == "fa"
        assert r["position"] == "chief"


class TestRoleHelpers:
    def test_is_fa(self):
        assert is_fa("fa") is True
        assert is_fa("FA") is True
        assert is_fa("bba") is False

    def test_is_division(self):
        for div in ("bba", "hld", "sci", "ss", "thm", "faa", "mba", "mm"):
            assert is_division(div) is True
        assert is_division("fa") is False
        assert is_division("unknown") is False

    def test_has_access_by_position(self):
        assert has_access_by_position("chief") is True
        assert has_access_by_position("chairman") is True
        assert has_access_by_position("head") is True
        assert has_access_by_position(None) is False
        assert has_access_by_position("user") is False


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token("alice", "fa", position="chief")
        payload = decode_access_token(token)
        assert payload["sub"] == "alice"
        assert payload["role"] == "fa"
        assert payload["position"] == "chief"

    def test_coordinator_flag(self):
        token = create_access_token("bob", "bba", coordinator=True)
        payload = decode_access_token(token)
        assert payload["coordinator"] is True

    def test_invalid_token_raises(self):
        with pytest.raises(JWTError):
            decode_access_token("not.a.valid.token")

    def test_no_position_when_not_set(self):
        token = create_access_token("carol", "ss")
        payload = decode_access_token(token)
        assert "position" not in payload


class TestEncryption:
    def test_roundtrip(self):
        plaintext = "sensitive-data-123"
        ciphertext = encrypt_value(plaintext)
        assert ciphertext != plaintext
        assert decrypt_value(ciphertext) == plaintext

    def test_different_ciphertexts(self):
        # Fernet includes nonce, so same plaintext → different ciphertext each time
        c1 = encrypt_value("hello")
        c2 = encrypt_value("hello")
        assert c1 != c2


class TestParamsHash:
    def test_same_params_same_hash(self):
        p = {"year": 2025, "month_from": 1, "q": None}
        assert params_hash(p) == params_hash(p)

    def test_different_params_different_hash(self):
        assert params_hash({"year": 2025}) != params_hash({"year": 2024})
