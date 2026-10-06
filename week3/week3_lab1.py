from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post.", "author_id": 1, "tags": ["rest"]},
]
next_id = 2

DEFAULT_SIZE = 20
MAX_SIZE = 100

def find_post(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None

@app.route("api/v1/posts", methods=["GET"])
def list_posts():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify({"error": "Page and size must be int"}), 400

    items = POSTS
    author_id = request.args.get("author_id")
    if author_id:
        items = [post for post in items if str(post["author_id"]) == author_id]
    tag = request.args.get("tag")
    if tag:
        items = [post for post in items if tag in post["tags"]]
    total = len(items)
    start = (page - 1) * size

    return jsonify({
        "data": items[start:start + size],
        "pagination": {
            "page": page,
            "size": size,
            "total": total
        }
    }), 200

@app.route("api/v1/posts", methods=["POST"])
def create_post():
    global next_id
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json(silcent=True) or {}
    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")

    if not title:
        return jsonify({"error": "Title is required"}), 422
    if not content:
        return jsonify({"error": "Content is required"}), 422
    if not author_id:
        return jsonify({"error": "Author ID is required"}), 422

    post = {
        "id": next_id,
        "title": title,
        "content": content,
        "author_id": author_id,
        "tags": data.get("tags", [])
    }
    next_id += 1
    POSTS.append(post)
    response = make_response(jsonify(post), 201)
    response.headers["Location"] = f"/api/v1/posts/{post['id']}"
    return response

@app.route("api/v1/posts/<int:post_id>", methods=["PATCH"])
def update_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    for field in ("title", "content"):
        value = (data[field] or "").strip()
        if  not value:
            return jsonify({"error": f"{field} cannot be empty"}), 422
        post[field] = value
    if "tags" in data:
        post["tags"] = data["tags"]
    return jsonify(post), 200

@app.route("api/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post), 200

@app.route("api/v1/posts/<int:post_id>", methods=["PATCH"])
def update_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    for field in ("title", "content"):
        value = (data[field] or "").strip()
        if not value:
            return jsonify({"error": f"{field} cannot be empty"}), 422
        post[field] = value
    if "tags" in data:
        post["tags"] = data["tags"]
    return jsonify(post), 200

@app.route("api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    POSTS.remove(post)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True) #both wifi and localhost works fine.