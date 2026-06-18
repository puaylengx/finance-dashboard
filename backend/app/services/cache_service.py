# Moved to app.core.cache — this file is kept for backward compatibility only
from app.core.cache import (  # noqa: F401
    get_cached,
    invalidate_coordinator_cache,
    invalidate_pattern,
    set_cached,
)
