# ADR 004 — Redis สำหรับ Response Caching

**Status:** Accepted  
**Date:** 2026-06-19

## Context

Finance dashboard query (`_SQL_DASHBOARD`) เป็น CTE query ขนาดใหญ่ที่ aggregate ข้อมูลจาก `erp_transactions` table ซึ่งอาจมีหลักแสน rows สำหรับปีงบประมาณเดียว แต่ละ request ใช้เวลา 0.5–3 วินาทีขึ้นอยู่กับ filter

ข้อมูลมี characteristics:
- อ่านบ่อยมาก (หลาย user query dashboard พร้อมกัน)
- เปลี่ยนแปลงน้อย (ข้อมูล ERP update เป็น batch ไม่ใช่ real-time)
- Query result ขึ้นกับ params + role ของ user

ทางเลือก:
1. In-memory cache ใน application process
2. Redis external cache
3. PostgreSQL materialized view

## Decision

เลือก **Redis** เป็น response cache layer โดย:
- Cache key: `seamless:v1:finance:{prefix}:{role}:{params_hash}`
- TTL: `REDIS_TTL_DEFAULT=300s` (finance), `REDIS_TTL_MASTER=3600s` (master data)
- Cache invalidation: เมื่อ coordinator toggle (`invalidate_coordinator_cache`)
- Graceful degradation: ถ้า Redis ไม่พร้อม (`get_redis() is None`) → query DB โดยตรง ไม่ crash

## Consequences

**Positive:**
- Query ซ้ำ (same params, same role) ตอบจาก Redis ใน <5ms แทน 500–3000ms
- Cache shared ระหว่าง multiple workers — ไม่เกิด cold cache เมื่อ scale
- TTL-based expiry อัตโนมัติ — ไม่ต้อง implement cache invalidation logic ซับซ้อน
- Idempotency keys สำหรับ write APIs ใช้ Redis เดิม (TTL 24h)

**Negative:**
- เพิ่ม infrastructure dependency — Redis ต้องรัน
- Cache key ผิด → wrong data served (mitigated ด้วย `params_hash` ครอบคลุม role)
- Redis ใช้ JSON serialization → ไม่รองรับ Decimal โดยตรง (ใช้ `default=str`)
- Coordinator role cache (`seamless:v1:auth:coordinator:{username}`) ต้อง invalidate ทุกครั้งที่ toggle
