# Week 5 – Books API: curl & proof

```bash
flask --app app seed
flask --app app run --port 5000
```

## 1. Offset pagination

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?strategy=offset&limit=2&offset=0"
```

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:09 GMT
Content-Type: application/json
Content-Length: 795
Link: </api/v1/books?strategy=offset&limit=2&offset=2>; rel="next"
Connection: close

{
  "data": [
    {
      "id": 45,
      "title": "Book 03",
      "description": "Mô tả sách số 45",
      "stock": 1,
      "category_id": 1,
      "published_date": null,
      "authors": [
        {
          "id": 1,
          "name": "Author 1"
        }
      ]
    },
    {
      "id": 44,
      "title": "Book 02",
      "description": "Mô tả sách số 44",
      "stock": 0,
      "category_id": 3,
      "published_date": "2008-09-01T00:00:00",
      "authors": [
        {
          "id": 5,
          "name": "Author 5"
        }
      ]
    }
  ],
  "pagination": {
    "strategy": "offset",
    "limit": 2,
    "offset": 0,
    "total": 45,
    "has_more": true,
    "next_offset": 2
  },
  "links": {
    "next": "/api/v1/books?strategy=offset&limit=2&offset=2"
  }
}

```

## 2. Offset pagination

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?strategy=offset&limit=2&offset=2"
```

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:09 GMT
Content-Type: application/json
Content-Length: 874
Link: </api/v1/books?strategy=offset&limit=2&offset=4>; rel="next", </api/v1/books?strategy=offset&limit=2&offset=0>; rel="prev"
Connection: close

{
  "data": [
    {
      "id": 43,
      "title": "Book 01",
      "description": "Mô tả sách số 43",
      "stock": 3,
      "category_id": 2,
      "published_date": "2007-08-01T00:00:00",
      "authors": [
        {
          "id": 4,
          "name": "Author 4"
        }
      ]
    },
    {
      "id": 42,
      "title": "Book 00",
      "description": "Mô tả sách số 42",
      "stock": 2,
      "category_id": 1,
      "published_date": "2006-07-01T00:00:00",
      "authors": [
        {
          "id": 3,
          "name": "Author 3"
        }
      ]
    }
  ],
  "pagination": {
    "strategy": "offset",
    "limit": 2,
    "offset": 2,
    "total": 45,
    "has_more": true,
    "next_offset": 4
  },
  "links": {
    "next": "/api/v1/books?strategy=offset&limit=2&offset=4",
    "prev": "/api/v1/books?strategy=offset&limit=2&offset=0"
  }
}

```

## 3. Cursor pagination

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=2"
```

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 895
Link: </api/v1/books?limit=2&strategy=cursor&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlag>; rel="next"
Connection: close

{
  "data": [
    {
      "id": 45,
      "title": "Book 03",
      "description": "Mô tả sách số 45",
      "stock": 1,
      "category_id": 1,
      "published_date": null,
      "authors": [
        {
          "id": 1,
          "name": "Author 1"
        }
      ]
    },
    {
      "id": 44,
      "title": "Book 02",
      "description": "Mô tả sách số 44",
      "stock": 0,
      "category_id": 3,
      "published_date": "2008-09-01T00:00:00",
      "authors": [
        {
          "id": 5,
          "name": "Author 5"
        }
      ]
    }
  ],
  "pagination": {
    "strategy": "cursor",
    "limit": 2,
    "next_cursor": "eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlag",
    "has_more": true
  },
  "links": {
    "next": "/api/v1/books?limit=2&strategy=cursor&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlag"
  }
}

```

## 4. Cursor pagination – trang tiếp theo

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=2&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlag"
```

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 912
Link: </api/v1/books?limit=2&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0Ml19.vE8ZvjtTEHFOrlPNlbP3kQ&strategy=cursor>; rel="next"
Connection: close

{
  "data": [
    {
      "id": 43,
      "title": "Book 01",
      "description": "Mô tả sách số 43",
      "stock": 3,
      "category_id": 2,
      "published_date": "2007-08-01T00:00:00",
      "authors": [
        {
          "id": 4,
          "name": "Author 4"
        }
      ]
    },
    {
      "id": 42,
      "title": "Book 00",
      "description": "Mô tả sách số 42",
      "stock": 2,
      "category_id": 1,
      "published_date": "2006-07-01T00:00:00",
      "authors": [
        {
          "id": 3,
          "name": "Author 3"
        }
      ]
    }
  ],
  "pagination": {
    "strategy": "cursor",
    "limit": 2,
    "next_cursor": "eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0Ml19.vE8ZvjtTEHFOrlPNlbP3kQ",
    "has_more": true
  },
  "links": {
    "next": "/api/v1/books?limit=2&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0Ml19.vE8ZvjtTEHFOrlPNlbP3kQ&strategy=cursor"
  }
}

```

## 5. Lọc genre + sort nhiều key

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=3&genre=tech,novel&sort=stock,-title"
```

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 1314
Link: </api/v1/books?limit=3&genre=tech,novel&sort=stock,-title&strategy=cursor&cursor=eyJ2IjoxLCJzIjoic3RvY2ssLXRpdGxlLGlkIiwiZyI6WyJub3ZlbCIsInRlY2giXSwiayI6WzAsIkJvb2sgMDQiLDRdfQ.Fo3uQIVUah2m9EkHwLtYkQ>; rel="next"
Connection: close

{
  "data": [
    {
      "id": 12,
      "title": "Book 05",
      "description": "Mô tả sách số 12",
      "stock": 0,
      "category_id": 1,
      "published_date": "2003-01-01T00:00:00",
      "authors": [
        {
          "id": 3,
          "name": "Author 3"
        }
      ]
    },
    {
      "id": 40,
      "title": "Book 05",
      "description": "Mô tả sách số 40",
      "stock": 0,
      "category_id": 2,
      "published_date": null,
      "authors": [
        {
          "id": 1,
          "name": "Author 1"
        }
      ]
    },
    {
      "id": 4,
      "title": "Book 04",
      "description": "Mô tả sách số 4",
      "stock": 0,
      "category_id": 2,
      "published_date": "2004-05-01T00:00:00",
      "authors": [
        {
          "id": 5,
          "name": "Author 5"
        }
      ]
    }
  ],
  "pagination": {
    "strategy": "cursor",
    "limit": 3,
    "next_cursor": "eyJ2IjoxLCJzIjoic3RvY2ssLXRpdGxlLGlkIiwiZyI6WyJub3ZlbCIsInRlY2giXSwiayI6WzAsIkJvb2sgMDQiLDRdfQ.Fo3uQIVUah2m9EkHwLtYkQ",
    "has_more": true
  },
  "links": {
    "next": "/api/v1/books?limit=3&genre=tech,novel&sort=stock,-title&strategy=cursor&cursor=eyJ2IjoxLCJzIjoic3RvY2ssLXRpdGxlLGlkIiwiZyI6WyJub3ZlbCIsInRlY2giXSwiayI6WzAsIkJvb2sgMDQiLDRdfQ.Fo3uQIVUah2m9EkHwLtYkQ"
  }
}

```

## 6. Lỗi: sort không hợp lệ

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?sort=price"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 122
Connection: close

{
  "error": "bad_sort",
  "message": "không sort được theo 'price'. Hợp lệ: id, title, stock, published_date"
}

```

## 7. Lỗi: strategy không hợp lệ

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?strategy=page"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 94
Connection: close

{
  "error": "bad_strategy",
  "message": "strategy phải là một trong: offset, cursor"
}

```

## 8. Lỗi: limit không hợp lệ

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=abc"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 73
Connection: close

{
  "error": "bad_param",
  "message": "limit phải là số nguyên"
}

```

## 9. Lỗi: dùng offset với strategy=cursor

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?strategy=cursor&offset=10"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 86
Connection: close

{
  "error": "bad_param",
  "message": "offset chỉ dùng với strategy = offset"
}

```

## 10. Lỗi: cursor bị sửa

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=2&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlaA"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 96
Connection: close

{
  "error": "invalid_cursor",
  "message": "cursor không hợp lệ hoặc đã bị sửa"
}

```

## 11. Lỗi: cursor dùng với sort khác

```bash
curl -i "http://127.0.0.1:5000/api/v1/books?limit=2&sort=title&cursor=eyJ2IjoxLCJzIjoiLWlkIiwiZyI6W10sImsiOls0NF19.vPxqjQvrfC7l9ZSsHFdlag"
```

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.9 Python/3.14.7
Date: Tue, 20 Oct 2026 18:17:10 GMT
Content-Type: application/json
Content-Length: 184
Connection: close

{
  "error": "cursor_mismatch",
  "message": "cursor được tạo với sort/genre khác; giữ nguyên sort và genre khi phân trang hoặc bỏ cursor để bắt đầu lại"
}

```

