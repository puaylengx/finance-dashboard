# ADR 001 — SSH Tunnel for Database Connection

**Status:** Accepted  
**Date:** 2026-06-19

## Context

ฐานข้อมูล PostgreSQL ตั้งอยู่บน internal network ขององค์กร ไม่เปิด port 5432 ออก internet โดยตรง การเชื่อมต่อจาก application server (หรือ developer machine) ต้องผ่าน jump/bastion host ที่เปิด SSH port 22 ไว้เท่านั้น

ทางเลือกที่พิจารณา:
1. เปิด DB port ตรงผ่าน firewall rule
2. ใช้ SSH tunnel ผ่าน bastion host
3. ใช้ VPN สำหรับทุก connection

## Decision

เลือก **SSH tunnel** (`sshtunnel` + `paramiko` library) โดยให้ application เปิด tunnel ก่อน connect pool

Config ผ่าน environment:
```
DB_MODE=ssh
SSH_HOST=jump.server.com
SSH_USERNAME=deploy-user
SSH_KEY_PATH=/path/to/private_key
```

## Consequences

**Positive:**
- ไม่ต้องเปิด DB port ออก internet — attack surface น้อยที่สุด
- ใช้ SSH key-based auth ซึ่งมี audit trail และ revoke ได้ต่อ key
- Dev/staging ใช้ `DB_MODE=direct` ได้โดยไม่ต้องเปลี่ยน code

**Negative:**
- เพิ่ม connection latency เล็กน้อย (~1-2ms per query round-trip)
- ต้องมี SSH key management — rotate key ทุก X เดือน
- ถ้า SSH tunnel หลุด pool ต้อง reconnect ทั้งหมด (handled ใน `database.py` ด้วย retry logic)
- `sshtunnel` library ไม่ support async natively — run ใน thread แยก
