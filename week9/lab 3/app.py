"""Practice 3 — dùng @deprecate_at cho API v1 (và v0 đã quá hạn để demo 410).

Chạy: python app.py  (port 5000)
"""
import logging
from datetime import datetime, timezone

from flask import Flask

from sunset import deprecate_at

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = Flask(__name__)
app.json.ensure_ascii = False

# v1 sắp tắt — vẫn chạy nhưng báo trước ngày tắt
V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
# v0 đã qua ngày sunset — dùng để demo 410 Gone mà không phải chờ tới 2027
V0_SUNSET = datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc)

USERS = {1: {"first_name": "Văn", "last_name": "Nguyễn"}}


@app.route("/api/v0/users/<int:uid>")
@deprecate_at(V0_SUNSET, replacement="/api/v2/users")
def get_v0(uid):
    return {"id": uid, "name": "Nguyễn Văn A"}


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    u = USERS.get(uid)
    if not u:
        return {"error": "not found"}, 404
    return {"id": uid, "full_name": f"{u['last_name']} {u['first_name']}"}


@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):
    u = USERS.get(uid)
    if not u:
        return {"error": "not found"}, 404
    return {"id": uid, **u}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
