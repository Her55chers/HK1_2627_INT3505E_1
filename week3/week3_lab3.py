import base64
import json
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

CUSTOMERS_DATA = [
    {"id": i, 
     "name": f"customer_{i}", 
     "email": f"customer{i}@example.com",
     "status": "premium" if i % 2 == 0 else "normal"} 
    for i in range(1, 67)
]

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
SORTABLE_FIELDS = ["id", "name", "email", "status"]

def encode_cursor(sort_by, order, last_value, last_id) -> str:
    raw = json.dumps({
        "sort_by": sort_by,
        "order": order,
        "last_value": last_value,
        "last_id": last_id
    }).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")

def decode_cursor(cursor: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        data = json.loads(raw.decode("utf-8"))
        required = {"sort_by", "order", "last_value", "last_id"}
        if not all(isinstance(data.get(key), (str, int)) for key in required):
            return None
        return data
    except Exception:
        return None

@app.route("/books", methods=["GET"])
def list_books():
    try:
        max_page_size = int(request.args.get("max_page_size", DEFAULT_PAGE_SIZE))
    except ValueError:
        return jsonify({"error": "max_page_size must be an integer"}), 400
    max_page_size = max(1, min(max_page_size, MAX_PAGE_SIZE))

    customers = CUSTOMERS_DATA

    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc").lower()
    if sort_by not in SORTABLE_FIELDS:
        return jsonify({"error": f"Invalid sort_by field. Must be one of {SORTABLE_FIELDS}"}), 400
    if order not in ["asc", "desc"]:
        return jsonify({"error": "Invalid order. Must be 'asc' or 'desc'"}), 400
    descending = order == "desc"

    id_filter = request.args.get("id")
    status_filter = request.args.get("status")

    if id_filter:
        customers = [customer for customer in customers if customer["id"] == id_filter]
    if status_filter:
        customers = [customer for customer in customers if customer["status"] == status_filter]

    customers = sorted(customers, key=lambda x: (x[sort_by], x["id"]), reverse=descending)
    
    page_token = request.args.get("page_token")

    if page_token:
        cursor = decode_cursor(page_token)
        if cursor is None:
            return jsonify({"error": "Invalid page_token"}), 400
        if cursor["sort_by"] != sort_by or cursor["order"] != order:
            return jsonify({"error": "page_token does not match the current sort_by and order parameters"}), 400

        last_key = (cursor["last_value"], cursor["last_id"])   # (value, id)
        try:
            if descending:
                customers = [customer for customer in customers if (customer[sort_by], customer["id"]) < last_key]
            else:
                customers = [customer for customer in customers if (customer[sort_by], customer["id"]) > last_key]
        except TypeError:
            return jsonify({"error": "Invalid page_token"}), 400

    page = customers[: max_page_size + 1]
    has_more = len(page) > max_page_size
    results = page[:max_page_size]

    next_page_token = None
    if has_more:
        last = results[-1]
        next_page_token = encode_cursor(sort_by, order, last[sort_by], last["id"])

    return jsonify({
        "customers": results,
        "next_page_token": next_page_token,
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)