# Practice 2 — Header Versioning với decorator `@api_version`

Cả 3 version dùng chung một URL `GET /users/{id}`. Client chọn version qua header `X-API-Version`, và response gắn `X-API-Version-Served` để debug.

## 1. Bốn điểm cần nhớ và cách làm trong [app.py](app.py)

| # | Yêu cầu | Cách làm |
|---|---|---|
| ① | Decorator parse `X-API-Version`, thiếu thì dùng default | Không gửi header thì nhận `LATEST = "2"` |
| ② | Trả header `X-API-Version-Served` | Gắn vào mọi response hợp lệ, kể cả 404 |
| ③ | Endpoint trả dict | Handler trả `dict` hoặc `(dict, status)`; decorator lo `jsonify` |
| ④ | Version lạ → 400, không fallback | Trả `400` kèm danh sách version hỗ trợ |

So với code mẫu trên slide, tôi sửa hai chỗ:

- **User không tồn tại giờ trả 404.** Trên slide, `return {"error": "not found"}` trả HTTP **200**. Decorator nay nhận thêm dạng `(body, status)` nên trả được 404 thật.
- **Thêm header `Vary: X-API-Version`.** Khi version nằm trong header thay vì URL, CDN hoặc proxy phải tách cache theo header này. Nếu không, client v1 có thể nhận nhầm response v2 đã được cache.

## 2. Cách chạy

```powershell
cd "week9\lab 2"
..\..\.venv\Scripts\python app.py
```

Chạy test (**6 passed**):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## 3. curl và kết quả

Các lệnh dưới đây chạy được trong Git Bash; trên PowerShell hãy dùng `curl.exe`. Kết quả là output thật.

**Default → bản stable mới nhất (v2)**

```bash
curl -i localhost:5000/users/1
```

```http
HTTP/1.1 200 OK
X-API-Version-Served: 2
Vary: X-API-Version

{"email":"a@vnu.vn","first_name":"Văn","id":1,"last_name":"Nguyễn"}
```

**Chọn v1**

```bash
curl -i -H "X-API-Version: 1" localhost:5000/users/1
```

```http
HTTP/1.1 200 OK
X-API-Version-Served: 1
Vary: X-API-Version

{"full_name":"Văn Nguyễn","id":1}
```

**Dated version**

```bash
curl -i -H "X-API-Version: 2024-06-20" localhost:5000/users/1
```

```http
HTTP/1.1 200 OK
X-API-Version-Served: 2024-06-20
Vary: X-API-Version

{"email":"a@vnu.vn","first_name":"Văn","id":1,"last_name":"Nguyễn"}
```

**Version không hỗ trợ → 400**

```bash
curl -i -H "X-API-Version: 99" localhost:5000/users/1
```

```http
HTTP/1.1 400 BAD REQUEST

{"error":"unsupported version","requested":"99","supported":["1","2","2024-06-20"]}
```
