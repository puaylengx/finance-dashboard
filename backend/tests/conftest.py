import pytest
from cryptography.fernet import Fernet
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.core.security import create_access_token
import app.core.security as _security_module


@pytest.fixture(autouse=True, scope="session")
def valid_encryption_key():
    """Provide a valid Fernet key for all tests.
    Needed because .env inline comments are parsed as the key value."""
    key = Fernet.generate_key().decode()
    original = _security_module._fernet
    _security_module._fernet = None
    with patch("app.core.config.settings.encryption_key", key):
        yield
    _security_module._fernet = original


@pytest.fixture
def fa_token() -> str:
    return create_access_token("fa_user", "fa", position="chief")


@pytest.fixture
def division_token() -> str:
    return create_access_token("bba_user", "bba")


@pytest.fixture
def coordinator_token() -> str:
    return create_access_token("coord_user", "bba", coordinator=True)


@pytest.fixture
def auth_headers_fa(fa_token: str) -> dict:
    return {"Authorization": f"Bearer {fa_token}"}


@pytest.fixture
def auth_headers_division(division_token: str) -> dict:
    return {"Authorization": f"Bearer {division_token}"}


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
def mock_db():
    """Mock the database pool so tests don't need a real DB."""
    mock_cur = AsyncMock()
    mock_cur.description = []
    mock_cur.fetchone = AsyncMock(return_value=None)
    mock_cur.fetchall = AsyncMock(return_value=[])
    mock_cur.execute = AsyncMock()

    mock_conn = MagicMock()
    mock_conn.cursor = MagicMock(return_value=mock_cur)
    mock_conn.commit = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)

    mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
    mock_cur.__aexit__ = AsyncMock(return_value=False)

    with patch("app.core.database.get_db") as mock_get_db:
        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
        yield mock_conn, mock_cur


@pytest.fixture
def mock_redis():
    """Mock Redis so tests don't need a real Redis."""
    with patch("app.core.redis_client.get_redis", return_value=None):
        yield
