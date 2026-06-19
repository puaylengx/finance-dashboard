# ADR 002 — psycopg3 Async Pool แทน SQLAlchemy ORM

**Status:** Accepted  
**Date:** 2026-06-19

## Context

FastAPI application ต้องการ PostgreSQL client ที่ทำงานแบบ async ได้ เพื่อไม่ block event loop ขณะรอ DB query ทางเลือกหลักคือ SQLAlchemy (พร้อม asyncpg) และ psycopg3 (psycopg[binary,pool])

ลักษณะ query ในโปรเจกต์:
- Finance dashboard ใช้ CTE query ที่ซับซ้อน 200+ บรรทัด
- ไม่ต้องการ ORM — query เป็น SQL แล้วทำ transformation ใน Python
- ต้องการ connection pool ที่รองรับ high concurrency (dashboard ถูก query พร้อมกันหลาย users)

## Decision

เลือก **psycopg3 (`psycopg[binary,pool]`)** โดยตรง ไม่ใช้ SQLAlchemy ORM

```python
# database.py
from psycopg_pool import AsyncConnectionPool
pool = AsyncConnectionPool(conninfo=..., min_size=2, max_size=20)
```

## Consequences

**Positive:**
- SQL query เขียนตรง — ไม่มี ORM abstraction layer ที่ generate SQL ไม่คาดคิด
- psycopg3 เป็น native async ตาม PEP 3156 — performance ดีกว่า psycopg2 + gevent
- `binary` format ลด serialization overhead สำหรับ NUMERIC/JSONB columns
- Connection pool tunable ผ่าน `DB_POOL_MIN_SIZE` / `DB_POOL_MAX_SIZE` environment variables

**Negative:**
- ต้องเขียน SQL query ด้วยมือทุก query — ไม่มี migration generator จาก ORM models
- ไม่มี ORM-level type safety — column mismatch ต้อง catch ที่ runtime
- ถ้าต้องการ model-based validation ในอนาคต ต้อง map rows → dict → Pydantic schema เอง
