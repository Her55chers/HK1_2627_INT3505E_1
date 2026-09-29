from flask import Flask, jsonify, request, make_response


app = Flask(__name__)
BOOKS =[]
_next_id = 1

@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200
#curl  http://127.0.0.1:5000/books

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    if title is None or title.strip() == "":
        return jsonify({"error": "Title is required"}), 422
    if author is None or author.strip() == "":
        return jsonify({"error": "Author is required"}), 422

    book = {
        "id": _next_id,
        "title": title,
        "author": author
    }
    BOOKS.append(book)
    _next_id += 1

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books {book['id']}"
    return response
# curl -i -X POST http://127.0.1:5000/books -H "Content-Type: application/json" -d "{\"title\": \"abc\", \"author\": \"cba\"}"

@app.route("/books/<int:book_id>", methods=["GET"])
def fetch(book_id):
    book = next(())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)