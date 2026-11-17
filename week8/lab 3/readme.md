# Lab 3 — Build Newman-runnable collection

| File | Nội dung |
|---|---|
| `books-api.postman_collection.json` | Collection của starter + folder `error-cases/` |
| `local.postman_environment.json` | Environment: `base_url = http://127.0.0.1:5000` |
| `run-newman.ps1` | Script chạy Newman (kiểm server trước, xuất CLI + JUnit) |
| `reports/junit.xml` | JUnit report thật — **16 testcase** |
| `reports/newman-cli.log` | Output CLI thật của lần chạy trên |

## Đã làm theo yêu cầu

| Yêu cầu | Cách làm |
|---|---|
| **A.** Folder `error-cases/` với 2 request | `POST /books — missing title` (body chỉ có `author`) và `GET /books/9999 — not found` |
| **B.** Mỗi request ≥ 2 `pm.test` (status + body) | 5 happy path có sẵn 2 test mỗi request. Error cases: test status (400/404) + test `code` (`VALIDATION_ERROR`/`NOT_FOUND`) và `message` không rỗng; POST còn kiểm `errors[].field` chứa `title` |
| **C.** `book_id` qua collectionVariable | `POST /books — create` chạy `pm.collectionVariables.set("book_id", id)`; GET/PUT/DELETE dùng `{{book_id}}`. DELETE có thêm test `book_id came from collectionVariable` để chứng minh URL dùng đúng biến |
| **D.** Newman `-r cli,junit`, nộp `junit.xml` | [reports/junit.xml](reports/junit.xml) |

Kết quả lần chạy thật: **7 request, 16 assertion, 0 fail, tổng 684 ms** (< 10 s, ≥ 7 testcase).

```
□ books
└ GET /books — initial list            [200 OK]          √ 200 OK  √ body is array
└ POST /books — create                 [201 CREATED]     √ 201 Created  √ positive id
└ GET /books/{id} — read               [200 OK]          √ 200 OK  √ expected fields
└ PUT /books/{id} — replace            [200 OK]          √ 200 OK  √ updated title
└ DELETE /books/{id} — delete          [204 NO CONTENT]  √ 204 No Content  √ empty body  √ book_id came from collectionVariable
□ error-cases
└ POST /books — missing title          [400 BAD REQUEST] √ 400 Bad Request  √ code is VALIDATION_ERROR with message  √ errors contains field title
└ GET /books/9999 — not found          [404 NOT FOUND]   √ 404 Not Found  √ code is NOT_FOUND with message
```

## Cách chạy (PowerShell)

**Terminal 1** — chạy Books API của starter (lần đầu cần tạo venv):

```powershell
cd week8\resources
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force instance | Out-Null
.venv\Scripts\python -m app --port 5000
```

> Starter lưu SQLite tại `instance/books.db` nhưng không tự tạo thư mục `instance/`, nên phải tạo trước, nếu không app báo `unable to open database file`.

**Terminal 2** — chạy collection:

```powershell
cd "week8\lab 3"
powershell -ExecutionPolicy Bypass -File .\run-newman.ps1
```

Hoặc gọi Newman trực tiếp:

```powershell
npx newman run books-api.postman_collection.json -e local.postman_environment.json -r cli,junit --reporter-junit-export reports/junit.xml
```

Collection không phụ thuộc DB rỗng: `book_id` lấy từ response của POST, còn `9999` chỉ cần chưa tồn tại.
