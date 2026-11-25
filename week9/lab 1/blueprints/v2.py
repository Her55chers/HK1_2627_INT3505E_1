from flask import Blueprint, request
from .users_data import create_user, users_data

bp = Blueprint('v2', __name__)

REQUIRED = ("first_name", "last_name", "email")


def to_v2(uid, user):
    return {"id": uid,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]}


@bp.route('/<int:uid>', methods=['GET'])
def get_user(uid):
    user = users_data.get(uid)
    if not user:
        return {"error": "User not found"}, 404
    return to_v2(uid, user), 200


# Mở rộng 1: POST /v2/users — tạo user theo schema v2 (first_name + last_name)
@bp.route('', methods=['POST'])
def post_user():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return {"error": "Body must be a JSON object"}, 400
    missing = [f for f in REQUIRED
               if not isinstance(body.get(f), str) or not body[f].strip()]
    if missing:
        return {"error": "Missing or empty fields", "fields": missing}, 400
    if "@" not in body["email"]:
        return {"error": "Invalid email", "fields": ["email"]}, 400

    uid = create_user(body["first_name"].strip(), body["last_name"].strip(),
                      body["email"].strip())
    return to_v2(uid, users_data[uid]), 201, {"Location": f"/v2/users/{uid}"}
