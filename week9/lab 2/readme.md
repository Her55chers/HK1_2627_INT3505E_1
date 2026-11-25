# Practice 2 — Header Versioning với decorator `@api_version`

Cùng một URL `GET /users/{id}`, client chọn version qua header `X-API-Version`:

- Không gửi header → dùng bản mới nhất (`2`).
- Response luôn có `X-API-Version-Served` và `Vary: X-API-Version`.
- Version không hỗ trợ → `400`, không fallback. User không tồn tại → `404` (code mẫu trên slide trả nhầm `200`).

## Cách chạy

Terminal 1 (server):

```powershell
cd "C:\Users\vulin\Documents\github\HK1_2627_INT3505E_1\week9\lab 2"; ..\..\.venv\Scripts\python app.py
```

Chạy test (6 passed):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## Kết quả

Chạy các lệnh dưới trong terminal 2 (PowerShell).

**curl 1:** không gửi header → v2, `200`

```powershell
curl.exe localhost:5000/users/1
```

```json
{
  "email": "a@vnu.vn",
  "first_name": "Văn",
  "id": 1,
  "last_name": "Nguyễn"
}
```

**curl 2:** `X-API-Version: 1` → v1, `200`

```powershell
curl.exe localhost:5000/users/1 -H "X-API-Version: 1"
```

```json
{
  "full_name": "Văn Nguyễn",
  "id": 1
}
```

**curl 3:** dated version `2024-06-20` → `200`

```powershell
curl.exe localhost:5000/users/1 -H "X-API-Version: 2024-06-20"
```

```json
{
  "email": "a@vnu.vn",
  "first_name": "Văn",
  "id": 1,
  "last_name": "Nguyễn"
}
```

**curl 4:** version không hỗ trợ → `400`

```powershell
curl.exe localhost:5000/users/1 -H "X-API-Version: 99"
```

```json
{
  "error": "unsupported version",
  "requested": "99",
  "supported": [
    "1",
    "2",
    "2024-06-20"
  ]
}
```

**curl 5:** user không tồn tại → `404`

```powershell
curl.exe localhost:5000/users/99
```

```json
{
  "error": "not found"
}
```
