# Practice 3 — Sunset Middleware: decorator `@deprecate_at` (RFC 8594)

Decorator `@deprecate_at(date, replacement)` trong [sunset.py](sunset.py) hoạt động như sau:

- **Trước ngày sunset**: endpoint chạy bình thường, response gắn `Sunset: <HTTP-date>`, `Deprecation: true` và `Link: <replacement>; rel="successor-version"`.
- **Từ ngày sunset trở đi**: trả **410 Gone** kèm `use_instead`.
- **Mỗi lần gọi** đều log `WARNING`, để đo còn bao nhiêu client đang dùng version cũ.

Các endpoint trong [app.py](app.py):

| Endpoint | Sunset | Trạng thái hôm nay |
|---|---|---|
| `/api/v0/users/{id}` | 2026-06-30 | Đã qua → **410** (dùng để demo, không phải chờ tới 2027) |
| `/api/v1/users/{id}` | 2026-12-31 | Sắp tắt → 200 + header deprecation |
| `/api/v2/users/{id}` | — | Version thay thế, không có header deprecation |

So với code mẫu trên slide, tôi thêm:

- Hàm `now_utc()` tách riêng, để test giả lập được thời điểm trước, đúng lúc và sau sunset.
- Response 410 cũng có `Link` tới version thay thế, và cũng được log (`sunset_call`). Như vậy vẫn thấy client nào còn gọi sau khi đã tắt.

## 1. Cách chạy

```powershell
cd "week9\lab 3"
..\..\.venv\Scripts\python app.py
```

Chạy test (**8 passed**):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

Ba tình huống của đề được test như sau:

- **Trước sunset → 200 + headers**: `test_before_sunset_returns_200_with_headers`.
- **Đúng lúc / sau sunset → 410**: `test_at_or_after_sunset_returns_410`, gồm 3 thời điểm: đúng giây sunset, +1 giây và +30 ngày.
- **Mỗi call log warning**: `test_each_call_logs_warning`.

## 2. curl và kết quả

Các lệnh dưới đây chạy được trong Git Bash; trên PowerShell hãy dùng `curl.exe`. Kết quả là output thật.

**Trước sunset: HTTP 200**

```bash
curl -i localhost:5000/api/v1/users/1
```

```http
HTTP/1.1 200 OK
Sunset: Thu, 31 Dec 2026 23:59:59 GMT
Deprecation: true
Link: </api/v2/users>; rel="successor-version"

{"full_name":"Nguyễn Văn","id":1}
```

**Sau sunset: HTTP 410 Gone**

```bash
curl -i localhost:5000/api/v0/users/1
```

```http
HTTP/1.1 410 GONE
Link: </api/v2/users>; rel="successor-version"

{"error":"gone","sunset":"Tue, 30 Jun 2026 23:59:59 GMT","use_instead":"/api/v2/users"}
```

**Version thay thế: không có header deprecation**

```bash
curl -i localhost:5000/api/v2/users/1
```

```http
HTTP/1.1 200 OK

{"first_name":"Văn","id":1,"last_name":"Nguyễn"}
```

**Server log**

```
WARNING sunset: deprecated_call /api/v1/users/1 127.0.0.1
WARNING sunset: sunset_call /api/v0/users/1 127.0.0.1 (gone since Tue, 30 Jun 2026 23:59:59 GMT)
```
