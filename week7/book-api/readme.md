## Chạy local bằng Docker

```bash
docker compose up -d --build
```

Container `api` tự tạo bảng (`flask init-db`) rồi chạy Gunicorn ở cổng **5000**. Container `db` là Postgres 16, dữ liệu lưu trong volume `pgdata`.

Thêm 3 cuốn sách mẫu:

```bash
docker compose exec api flask seed
```

## Các endpoint — curl và kết quả


### Health

#### `GET /healthz` — liveness (không chạm DB)

```bash
curl -s http://localhost:5000/healthz
```

`200 OK`

```json
{ "status": "ok" }
```

#### `GET /ready` — readiness (kiểm tra kết nối DB)

```bash
curl -s http://localhost:5000/ready
```

`200 OK`

```json
{ "db": "ok", "status": "ok" }
```

### Books

#### `GET /api/v1/books` — danh sách (phân trang, bỏ qua sách đã xoá)

```bash
curl -s http://localhost:5000/api/v1/books
```

`200 OK`

```json
{
  "items": [
    {
      "archived": false,
      "author": "Robert C. Martin",
      "id": 1,
      "isbn": "978-0132350884",
      "price_cents": 35000,
      "qty_in_stock": 10,
      "title": "Clean Code"
    },
    {
      "archived": false,
      "author": "Martin Kleppmann",
      "id": 2,
      "isbn": "978-1449373320",
      "price_cents": 45000,
      "qty_in_stock": 5,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "archived": false,
      "author": "Gang of Four",
      "id": 3,
      "isbn": "978-0201633610",
      "price_cents": 40000,
      "qty_in_stock": 3,
      "title": "Design Patterns"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 3
}
```

```bash
curl -s "http://localhost:5000/api/v1/books?page=1&size=2"
```

`200 OK`

```json
{
  "items": [
    { "archived": false, "author": "Robert C. Martin", "id": 1, "isbn": "978-0132350884", "price_cents": 35000, "qty_in_stock": 10, "title": "Clean Code" },
    { "archived": false, "author": "Martin Kleppmann", "id": 2, "isbn": "978-1449373320", "price_cents": 45000, "qty_in_stock": 5, "title": "Designing Data-Intensive Applications" }
  ],
  "page": 1,
  "size": 2,
  "total": 3
}
```

#### `GET /api/v1/books/{id}` 

```bash
curl -s http://localhost:5000/api/v1/books/1
```

`200 OK`

```json
{
  "archived": false,
  "author": "Robert C. Martin",
  "id": 1,
  "isbn": "978-0132350884",
  "price_cents": 35000,
  "qty_in_stock": 10,
  "title": "Clean Code"
}
```

#### `POST /api/v1/books` — tạo sách

```bash
curl -s -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"isbn":"978-0596007126","title":"Head First Design Patterns","author":"Eric Freeman","price_cents":30000,"qty_in_stock":7}'
```

`201 Created`

```json
{
  "archived": false,
  "author": "Eric Freeman",
  "id": 4,
  "isbn": "978-0596007126",
  "price_cents": 30000,
  "qty_in_stock": 7,
  "title": "Head First Design Patterns"
}
```

Trùng ISBN:

```bash
curl -s -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"isbn":"978-0596007126","title":"Dup","price_cents":1}'
```

`409 Conflict`

```json
{ "detail": "isbn already exists", "error": "conflict" }
```

Dữ liệu không hợp lệ:

```bash
curl -s -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"title":"","price_cents":-5}'
```

`422 Unprocessable Entity`

```json
{
  "detail": {
    "isbn": ["Missing data for required field."],
    "price_cents": ["Must be greater than or equal to 0."],
    "title": ["Length must be between 1 and 255."]
  },
  "error": "validation_error"
}
```

Body không phải JSON:

```bash
curl -s -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d 'not json'
```

`400 Bad Request`

```json
{ "detail": "body phải là JSON object", "error": "bad_request" }
```

#### `PATCH /api/v1/books/{id}` — cập nhật một phần


```bash
curl -s -X PATCH http://localhost:5000/api/v1/books/4 \
  -H "Content-Type: application/json" \
  -d '{"price_cents":28000}'
```

`200 OK`

```json
{
  "archived": false,
  "author": "Eric Freeman",
  "id": 4,
  "isbn": "978-0596007126",
  "price_cents": 28000,
  "qty_in_stock": 7,
  "title": "Head First Design Patterns"
}
```

#### `POST /api/v1/books/{id}/reserve` 

```bash
curl -s -X POST http://localhost:5000/api/v1/books/1/reserve \
  -H "Content-Type: application/json" \
  -d '{"qty":2}'
```

`200 OK` — `qty_in_stock` giảm từ 10 xuống 8

```json
{
  "archived": false,
  "author": "Robert C. Martin",
  "id": 1,
  "isbn": "978-0132350884",
  "price_cents": 35000,
  "qty_in_stock": 8,
  "title": "Clean Code"
}
```

Không đủ hàng:

```bash
curl -s -X POST http://localhost:5000/api/v1/books/3/reserve \
  -H "Content-Type: application/json" \
  -d '{"qty":99}'
```

`409 Conflict`

```json
{ "detail": "only 3 left", "error": "out_of_stock" }
```

#### `DELETE /api/v1/books/{id}` — xoá mềm

```bash
curl -s -i -X DELETE http://localhost:5000/api/v1/books/4
```

`204 No Content` (body rỗng)

```bash
curl -s http://localhost:5000/api/v1/books/4
```

`404 Not Found`

```json
{ "detail": "book 4 not found", "error": "not_found" }
```

### Orders

#### `POST /api/v1/orders` 

```bash
curl -s -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"An","items":[{"book_id":1,"qty":2},{"book_id":2,"qty":1}]}'
```

`201 Created`

```json
{
  "customer_name": "An",
  "id": 1,
  "items": [
    { "book_id": 1, "book_title": "Clean Code", "qty": 2, "unit_price_cents": 35000 },
    { "book_id": 2, "book_title": "Designing Data-Intensive Applications", "qty": 1, "unit_price_cents": 45000 }
  ],
  "total_cents": 115000
}
```

Không đủ hàng:

```bash
curl -s -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Binh","items":[{"book_id":3,"qty":100}]}'
```

`409 Conflict`

```json
{ "detail": "only 3 left", "error": "out_of_stock" }
```

#### `GET /api/v1/orders` 

```bash
curl -s http://localhost:5000/api/v1/orders
```

`200 OK`

```json
{
  "items": [
    {
      "customer_name": "An",
      "id": 1,
      "items": [
        { "book_id": 1, "book_title": "Clean Code", "qty": 2, "unit_price_cents": 35000 },
        { "book_id": 2, "book_title": "Designing Data-Intensive Applications", "qty": 1, "unit_price_cents": 45000 }
      ],
      "total_cents": 115000
    }
  ]
}
```

#### `GET /api/v1/orders/{id}` 

```bash
curl -s http://localhost:5000/api/v1/orders/1
```

`200 OK`

```json
{
  "customer_name": "An",
  "id": 1,
  "items": [
    { "book_id": 1, "book_title": "Clean Code", "qty": 2, "unit_price_cents": 35000 },
    { "book_id": 2, "book_title": "Designing Data-Intensive Applications", "qty": 1, "unit_price_cents": 45000 }
  ],
  "total_cents": 115000
}
```

Không tồn tại:

```bash
curl -s http://localhost:5000/api/v1/orders/999
```

`404 Not Found`

```json
{ "detail": "order 999 not found", "error": "not_found" }
```
