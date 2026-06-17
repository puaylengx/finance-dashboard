from collections import namedtuple
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ColDesc = namedtuple("ColDesc", ["name"])

_COL_NAMES = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
_COORD_TUPLE = (1, "alice", True, None, None, "admin", None)


def _make_mock_db(fetchone_return, fetchall_return=None):
    mock_cur = AsyncMock()
    mock_cur.description = [ColDesc(name=n) for n in _COL_NAMES]
    mock_cur.execute = AsyncMock()
    mock_cur.fetchone = AsyncMock(return_value=fetchone_return)
    mock_cur.fetchall = AsyncMock(return_value=fetchall_return or [])
    mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
    mock_cur.__aexit__ = AsyncMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.cursor = MagicMock(return_value=mock_cur)
    mock_conn.commit = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)

    return mock_conn, mock_cur


class TestRowToDict:
    def test_basic_conversion(self):
        from app.services.coordinator_service import _row_to_dict
        desc = [ColDesc("id"), ColDesc("username"), ColDesc("active")]
        result = _row_to_dict(desc, (42, "bob", False))
        assert result == {"id": 42, "username": "bob", "active": False}

    def test_converts_created_at_to_thai_tz(self):
        from app.services.coordinator_service import _row_to_dict
        utc_dt = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        desc = [ColDesc("id"), ColDesc("created_at")]
        result = _row_to_dict(desc, (1, utc_dt))
        assert result["created_at"].utcoffset().total_seconds() == 7 * 3600

    def test_converts_updated_at_to_thai_tz(self):
        from app.services.coordinator_service import _row_to_dict
        utc_dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        desc = [ColDesc("id"), ColDesc("updated_at")]
        result = _row_to_dict(desc, (1, utc_dt))
        assert result["updated_at"].utcoffset().total_seconds() == 7 * 3600

    def test_none_datetime_not_converted(self):
        from app.services.coordinator_service import _row_to_dict
        desc = [ColDesc("id"), ColDesc("created_at"), ColDesc("updated_at")]
        result = _row_to_dict(desc, (1, None, None))
        assert result["created_at"] is None
        assert result["updated_at"] is None


@pytest.mark.asyncio
class TestAddCoordinator:
    async def test_returns_coordinator_dict(self):
        from app.services.coordinator_service import add_coordinator
        mock_conn, mock_cur = _make_mock_db(fetchone_return=_COORD_TUPLE)

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", AsyncMock()):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await add_coordinator(username="alice", created_by="admin")

        assert result["username"] == "alice"
        assert result["id"] == 1
        assert result["active"] is True

    async def test_commits_transaction(self):
        from app.services.coordinator_service import add_coordinator
        mock_conn, _ = _make_mock_db(fetchone_return=_COORD_TUPLE)

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", AsyncMock()):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            await add_coordinator(username="alice", created_by="admin")

        mock_conn.commit.assert_called_once()

    async def test_invalidates_cache_for_username(self):
        from app.services.coordinator_service import add_coordinator
        mock_conn, _ = _make_mock_db(fetchone_return=_COORD_TUPLE)
        invalidate = AsyncMock()

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", invalidate):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            await add_coordinator(username="alice", created_by="admin")

        invalidate.assert_called_once_with("alice")


@pytest.mark.asyncio
class TestToggleCoordinator:
    async def test_returns_updated_dict(self):
        from app.services.coordinator_service import toggle_coordinator
        toggled = (1, "alice", False, None, None, "admin", "admin2")
        mock_conn, _ = _make_mock_db(fetchone_return=toggled)

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", AsyncMock()):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await toggle_coordinator(coord_id=1, updated_by="admin2")

        assert result["id"] == 1
        assert result["active"] is False

    async def test_returns_none_when_not_found(self):
        from app.services.coordinator_service import toggle_coordinator
        mock_conn, _ = _make_mock_db(fetchone_return=None)

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", AsyncMock()):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await toggle_coordinator(coord_id=999, updated_by="admin")

        assert result is None

    async def test_commits_on_success(self):
        from app.services.coordinator_service import toggle_coordinator
        mock_conn, _ = _make_mock_db(fetchone_return=_COORD_TUPLE)

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", AsyncMock()):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            await toggle_coordinator(coord_id=1, updated_by="admin")

        mock_conn.commit.assert_called_once()

    async def test_invalidates_cache_on_success(self):
        from app.services.coordinator_service import toggle_coordinator
        mock_conn, _ = _make_mock_db(fetchone_return=_COORD_TUPLE)
        invalidate = AsyncMock()

        with patch("app.services.coordinator_service.get_db") as mock_gdb, \
             patch("app.services.coordinator_service.invalidate_coordinator_cache", invalidate):
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            await toggle_coordinator(coord_id=1, updated_by="admin")

        invalidate.assert_called_once_with("alice")
