from flask import Blueprint
from sqlalchemy import text

from ..extensions import db

health_bp = Blueprint("health", __name__)


# Liveness — không chạm DB
@health_bp.get("/healthz")
def liveness():
    return {"status": "ok"}, 200


# Readiness — kiểm tra DB
@health_bp.get("/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}, 200
    except Exception:
        return {"status": "degraded", "db": "err"}, 503
