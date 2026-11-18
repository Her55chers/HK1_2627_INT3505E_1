from flask import Blueprint
from .users_data import users_data
bp = Blueprint('v2', __name__)

@bp.route('/<int:uid>', methods=['GET'])
def get_user(uid):
    user = users_data.get(uid)
    if not user:
        return {"error": "User not found"}, 404
    return {"id": uid,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]}, 200