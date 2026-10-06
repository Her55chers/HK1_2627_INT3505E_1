import base64
import json
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

CUSTOMERS_DATA = [
    {"id": f"customer_{i}", "name": "customer_{i}", "email": "customer{1}@example.com"} 
    for i in range(1, 67)
]

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

def encode_cursor(id: str) -> str:
    cursor_data = {"id": id}
    json_bytes = json.dumps(cursor_data).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("utf-8")

def decode_cursor(cursor: str) -> str:
    try:
        json_bytes = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        cursor_data = json.loads(json_bytes.decode("utf-8"))
        return cursor_data.get("id")
    except Exception:
        return None

@app.route("/books", methods=["GET"])
def list_books():
    try:
        max_page_size = int(request.args.get("max_page_size", DEFAULT_PAGE_SIZE))
    except ValueError:
        return jsonify({"error": "max_page_size must be an integer"}), 400
    max_page_size = min(1, min(max_page_size, MAX_PAGE_SIZE))

    page_token = request.args.get("page_token")
    last_id = None

    if page_token:
        cursor = decode_cursor(page_token)
        if not cursor or "last_id" not in cursor:
            return jsonify({"error": "Invalid page_token or have expired"}), 400
        last_id = cursor["last_id"]

    filtered_customers = CUSTOMERS_DATA
    if last_id:
        filtered_customers = [customer for customer in CUSTOMERS_DATA if customer["id"] > last_id]
    results = filtered_customers[:max_page_size]

    next_page_token = None
    if len(filtered_customers) > max_page_size:
        next_page_token = encode_cursor(results[-1]["id"])

    return jsonify({
        "customers": results,
        "next_page_token": next_page_token
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)