from flask import Flask, jsonify, request, make_response


app = Flask(__name__)
BOOKS =[]
DEFAULT_SIZE = 20
MAX_SIZE = 100
_next_id = 1

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify({"error": "Page and size must be int"}), 400
    page = max(page,1)
    size = max(min(size,MAX_SIZE),1)

    filter = BOOKS
    author = request.args.get("author")
    if author:
        filter = [book for book in filter if book["author"] == author]
    q = request.args.get("q"or"").lower()
    if q:
        filter = [book for book in filter if q in book["title"].lower()]

    total = len(filter)
    start = (page - 1) * size
    end = start + size
    items = filter[start:end]
    last = (total + size -1) // size

    def u(p):
        return f"/books?page={p}&size={size}"
    links = {
        "self": u(page),
        "first": u(1),
        "last": u(last)
    }
    if page > 1: links["prev"] = u(page - 1)
    if end < total: links["next"] = u(page + 1)
    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "last": last,
            "links": links
        }
    }
    response = make_response(jsonify(body), 200)
    response.headers["Cache-Control"] = "public, max-age=67"
    return response
#curl  http://127.0.0.1:5000/books

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    price = data.get("price", 0.0)

    if title is None or title.strip() == "":
        return jsonify({"error": "Title is required"}), 422
    if author is None or author.strip() == "":
        return jsonify({"error": "Author is required"}), 422
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Price must be a positive float number"}), 422

    book = {
        "id": _next_id,
        "title": title,
        "author": author,
        "price": price
    }
    BOOKS.append(book)
    _next_id += 1

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books {book['id']}"
    return response
# curl -i -X POST http://127.0.1:5000/books -H "Content-Type: application/json" -d "{\"title\": \"abc\", \"author\": \"cba\"}"

@app.route("/books/<int:book_id>", methods=["GET"])
def fetch(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    response = make_response(jsonify(book), 200)
    response.headers["Location"] = f"/books/{book['id']}"
    return response

@app.route("/books/<int:book_id>", methods=["PUT"])
def put(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    price = data.get("price")

    if title is None or title.strip() == "":
        return jsonify({"error": "Title is required"}), 422
    if author is None or author.strip() == "":
        return jsonify({"error": "Author is required"}), 422
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Price must be a positive float number"}), 422
    
    book["title"] = title
    book["author"] = author
    book["price"] = price

    response = make_response(jsonify(book), 200)
    response.headers["Location"] = f"/books/{book['id']}"
    return response

@app.route("/books/<int:book_id>", methods=["PATCH"])
def patch(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    price = data.get("price")

    if title:
        book["title"] = title
    if author:
        book["author"] = author
    if price is not None and isinstance(price, (int, float)) and price > 0:
        book["price"] = price

    response = make_response(jsonify(book), 200)
    response.headers["Location"] = f"/books/{book['id']}"
    return response

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    BOOKS.pop(book)
    return jsonify({""}), 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)