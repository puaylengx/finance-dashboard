import pytest

from app.core.security import (
    DIVISION_ROLES,
    FA_ROLES,
    ILIKE_ROOT_OVERRIDE,
    POSITION_ROLES,
    extract_claims,
    is_division,
    is_fa,
)


class TestPositionRoles:
    def test_all_positions_defined(self):
        assert "chief" in POSITION_ROLES
        assert "chairman" in POSITION_ROLES
        assert "head" in POSITION_ROLES

    def test_no_false_positives(self):
        assert "user" not in POSITION_ROLES
        assert "fa" not in POSITION_ROLES
        assert "bba" not in POSITION_ROLES


class TestDivisionRoles:
    def test_all_divisions_covered(self):
        expected = {"bba", "hld", "sci", "ss", "thm", "faa", "mba", "mm"}
        assert DIVISION_ROLES == expected

    def test_fa_not_division(self):
        assert "fa" not in DIVISION_ROLES


class TestIlikeRootOverride:
    def test_sci_lab_override(self):
        assert ILIKE_ROOT_OVERRIDE.get("sci_lab") == "SCI"

    def test_normal_role_no_override(self):
        assert "bba" not in ILIKE_ROOT_OVERRIDE
        assert "fa" not in ILIKE_ROOT_OVERRIDE


class TestExtractClaimsEdgeCases:
    @pytest.mark.parametrize("job_title, expected_role, expected_pos", [
        ("dept,fa", "fa", None),
        ("dept,fa,chief", "fa", "chief"),
        ("dept,fa,chairman", "fa", "chairman"),
        ("dept,bba,head", "bba", "head"),
        ("bba", "bba", None),
        ("dept,type,bba,head", "bba", "head"),
        (",,,", "user", None),
    ])
    def test_various_formats(self, job_title, expected_role, expected_pos):
        claims = extract_claims(job_title)
        assert claims["role"] == expected_role
        assert claims["position"] == expected_pos
