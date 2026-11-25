"""Practice 4 — Blue-Green routing: 1 URL POST /orders, chọn v1 hoặc v2 theo cohort.

Chạy: python app.py  (port 5000). Đổi % rollout: $env:V2_PERCENT = "100"
"""
import logging

from flask import Flask, jsonify, request

import config
from gateway import dispatch

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="body must be a JSON object"), 400
    which, reason, result = dispatch(body)
    resp = jsonify(result)
    resp.headers["X-Order-Handler"] = which
    resp.headers["X-Route-Reason"] = reason
    return resp, (201 if which == "v2" else 200)


@app.get("/rollout")
def rollout():
    """Xem cấu hình rollout hiện tại."""
    return {"v2_percent": config.V2_PERCENT,
            "v2_cohorts": sorted(config.V2_COHORTS),
            "v2_force_accounts": sorted(config.V2_FORCE_ACCOUNTS)}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
