# Practice 1 — URI Path Versioning: User API v1 → v2 với Flask Blueprint

- **v1** (`/v1/users/{id}`): trả `full_name`. Mọi response có header `Sunset`, `Deprecation`, `Link` vì v1 sắp tắt.
- **v2** (`/v2/users/{id}`): trả `first_name` + `last_name` (breaking change so với v1). Có thêm `POST /v2/users`.
- Spec của cả 2 version: [openapi.yaml](openapi.yaml).

## Cách chạy

Terminal 1 (server):

```powershell
cd "C:\Users\vulin\Documents\github\HK1_2627_INT3505E_1\week9\lab 1"; ..\..\.venv\Scripts\python app.py
```

Chạy test (9 passed):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## Kết quả

Chạy các lệnh dưới trong terminal 2 (PowerShell).

**curl 1:** `GET /v1/users/2` — schema v1 (`full_name`) → `200`

```powershell
curl.exe localhost:5000/v1/users/2
```

```json
{
  "email": "binh.tran@example.com",
  "full_name": "Tran Thi Binh",
  "id": 2
}
```

**curl 2:** `GET /v2/users/1` — schema v2 (`first_name`, `last_name`) → `200`

```powershell
curl.exe localhost:5000/v2/users/1
```

```json
{
  "email": "an.nguyen@example.com",
  "first_name": "An",
  "id": 1,
  "last_name": "Nguyen"
}
```

**curl 3:** cùng user 1 qua v1 → `200` (thêm `-i` để thấy header `Sunset`, `Deprecation`, `Link`)

```powershell
curl.exe localhost:5000/v1/users/1
```

```json
{
  "email": "an.nguyen@example.com",
  "full_name": "Nguyen Van An",
  "id": 1
}
```

**curl 4:** `POST /v2/users` — tạo user → `201`

```powershell
curl.exe -X POST localhost:5000/v2/users -H "Content-Type: application/json" -d '{\"first_name\":\"Dung\",\"last_name\":\"Pham\",\"email\":\"dung.pham@example.com\"}'
```

```json
{
  "email": "dung.pham@example.com",
  "first_name": "Dung",
  "id": 4,
  "last_name": "Pham"
}
```

**curl 5:** user vừa tạo đọc được qua v1 → `200`

```powershell
curl.exe localhost:5000/v1/users/4
```

```json
{
  "email": "dung.pham@example.com",
  "full_name": "Pham Dung",
  "id": 4
}
```

**curl 6:** POST thiếu field → `400`

```powershell
curl.exe -X POST localhost:5000/v2/users -H "Content-Type: application/json" -d '{\"first_name\":\"Dung\"}'
```

```json
{
  "error": "Missing or empty fields",
  "fields": [
    "last_name",
    "email"
  ]
}
```
