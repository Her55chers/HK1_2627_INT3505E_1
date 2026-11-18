from flask import Blueprint
from .users_data import users_data

bp = Blueprint('v1', __name__)

@bp.route('/<int:uid>', methods=['GET'])
def get_user(uid):
    user = users_data.get(uid)
    if not user:
        return {"error": "User not found"}, 404
    return {"id": uid,
            "full_name": user["full_name"],
            "email": user["email"]}, 200