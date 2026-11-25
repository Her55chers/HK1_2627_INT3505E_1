"""Practice 2 — Header versioning với decorator @api_version.

Cùng URL GET /users/<id>; client chọn version qua header X-API-Version.
Chạy: python app.py  (port 5000)
"""
from functools import wraps

from flask import Flask, jsonify, request

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}

USERS = {
    1: {"f": "Văn", "l": "Nguyễn", "e": "a@vnu.vn"},
    2: {"f": "Trang", "l": "Trần", "e": "b@vnu.vn"},
}

app = Flask(__name__)
app.json.ensure_ascii = False  # trả tiếng Việt dễ đọc thay vì \uXXXX


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # ① Parse X-API-Version — thiếu thì dùng default (bản stable mới nhất)
            v = request.headers.get("X-API-Version", default).strip()
            # ④ Version lạ -> 400, không fallback âm thầm
            if v not in supported:
                response = jsonify(error="unsupported version", requested=v,
                                   supported=sorted(supported))
                response.status_code = 400
                return response
            # ③ Endpoint trả dict (hoặc (dict, status))
            result = fn(v, *args, **kwargs)
            body, status = result if isinstance(result, tuple) else (result, 200)
            response = jsonify(body)
            response.status_code = status
            # ② Header cho biết version thực sự được phục vụ (debug + đo adoption)
            response.headers["X-API-Version-Served"] = v
            # Cache (CDN/proxy) phải tách theo header version, nếu không sẽ trả nhầm schema
            response.headers["Vary"] = "X-API-Version"
            return response
        return wrapper
    return decorate


@app.route("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    u = USERS.get(uid)
    if not u:
        return {"error": "not found"}, 404
    if version == "1":
        return {"id": uid, "full_name": u["f"] + " " + u["l"]}
    # "2" và bản dated "2024-06-20" dùng cùng schema v2
    return {"id": uid, "first_name": u["f"], "last_name": u["l"], "email": u["e"]}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
