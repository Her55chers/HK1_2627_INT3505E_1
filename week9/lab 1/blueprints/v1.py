from datetime import datetime, timezone
from email.utils import format_datetime

from flask import Blueprint
from .users_data import users_data

bp = Blueprint('v1', __name__)

# Mở rộng 3: v1 sắp tắt -> mọi response của v1 gắn Sunset (RFC 8594) + Deprecation
V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
SUCCESSOR = "/v2/users"


@bp.after_request
def add_sunset_headers(response):
    response.headers["Sunset"] = format_datetime(V1_SUNSET, usegmt=True)
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = f'<{SUCCESSOR}>; rel="successor-version"'
    return response


@bp.route('/<int:uid>', methods=['GET'])
def get_user(uid):
    user = users_data.get(uid)
    if not user:
        return {"error": "User not found"}, 404
    return {"id": uid,
            "full_name": user["full_name"],
            "email": user["email"]}, 200
