import base64
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

CUSTOMERS_DATA = [
    {"id": f"customer_{i}", "name": "customer_{i}", "email": "customer{1}@example.com"} 
    for i in range(1, 67)
]

DEFINE_PAGE_SIZE = 10
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



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)