# Practice 3 — Sunset Middleware: decorator `@deprecate_at` (RFC 8594)

Decorator `@deprecate_at(date, replacement)` trong [sunset.py](sunset.py):

- **Trước ngày sunset**: `200` + header `Sunset`, `Deprecation`, `Link`.
- **Từ ngày sunset trở đi**: `410 Gone` kèm `use_instead`.
- **Mỗi lần gọi** đều log `WARNING`.

| Endpoint | Sunset | Hôm nay |
|---|---|---|
| `/api/v0/users/{id}` | 2026-06-30 | Đã qua → `410` (để demo) |
| `/api/v1/users/{id}` | 2026-12-31 | `200` + header deprecation |
| `/api/v2/users/{id}` | — | Version thay thế |

## Cách chạy

Terminal 1 (server):

```powershell
cd "C:\Users\vulin\Documents\github\HK1_2627_INT3505E_1\week9\lab 3"; ..\..\.venv\Scripts\python app.py
```

Chạy test (8 passed):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## Kết quả

Chạy các lệnh dưới trong terminal 2 (PowerShell).

**curl 1:** v1 trước sunset → `200` (thêm `-i` để thấy header `Sunset`, `Deprecation`, `Link`)

```powershell
curl.exe localhost:5000/api/v1/users/1
```

```json
{
  "full_name": "Nguyễn Văn",
  "id": 1
}
```

**curl 2:** v0 sau sunset → `410 Gone`

```powershell
curl.exe localhost:5000/api/v0/users/1
```

```json
{
  "error": "gone",
  "sunset": "Tue, 30 Jun 2026 23:59:59 GMT",
  "use_instead": "/api/v2/users"
}
```

**curl 3:** v2 là version thay thế → `200`

```powershell
curl.exe localhost:5000/api/v2/users/1
```

```json
{
  "first_name": "Văn",
  "id": 1,
  "last_name": "Nguyễn"
}
```
