# ADR 003 — Draft Mode สำหรับ Local Development Authentication

**Status:** Accepted  
**Date:** 2026-06-19

## Context

Production authentication ใช้ Microsoft Entra ID (Azure AD) ซึ่งต้องการ:
- `AZURE_TENANT_ID` และ `AZURE_CLIENT_ID` จาก Azure portal
- Network access ไปยัง Microsoft identity endpoints
- User accounts ใน Azure AD

นักพัฒนาในช่วง development และ staging ยังไม่มี Azure AD setup ครบ การ require Entra ID authentication ตั้งแต่เริ่มจะทำให้ development ช้ามาก

## Decision

เพิ่ม **Draft Mode** (`DRAFT_MODE=true`) ที่เปิดใช้ `/auth/draft-login` endpoint:
- รับ `username` + `password` ตรงๆ
- ตรวจสอบกับ `AUTH_USERS_JSON` (JSON array ใน .env — local users เท่านั้น)
- Return JWT token format เดิมกับ Entra ID path

Production guard: `config.py` enforce ว่า `APP_ENV=production` + `DRAFT_MODE=true` → startup error

## Consequences

**Positive:**
- Dev/staging ไม่ต้องการ Azure AD — setup ง่าย ทดสอบเร็ว
- JWT payload format เหมือนกันทุก environment — endpoint logic ไม่ต้องแยก
- Guard ที่ startup ป้องกัน deploy draft mode เข้า production โดยบังเอิญ
- `AUTH_USERS_JSON` ไม่ commit ลง git (ถูก exclude ใน `.gitignore`)

**Negative:**
- มี code path พิเศษใน auth endpoint ที่ต้อง maintain ต่อไป
- ถ้า Guard ไม่ถูก set ใน production config → security risk (mitigated ด้วย startup validation)
- `AUTH_USERS_JSON` passwords ต้อง hash ด้วย bcrypt — ถ้าใส่ plain text จะ login ไม่ได้
