from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message=""):
        super().__init__(message)
        self.message = message


class BadRequest(ApiError):
    status_code = 400; code = "bad_request"


class NotFound(ApiError):
    status_code = 404; code = "not_found"


class Conflict(ApiError):
    status_code = 409; code = "conflict"


class OutOfStock(ApiError):
    status_code = 409; code = "out_of_stock"


def register_error_handlers(app):
    # Mọi lỗi trả về: {"error": "...", "detail": "..."}
    @app.errorhandler(ApiError)
    def _api(err):
        return jsonify(error=err.code, detail=err.message), err.status_code

    @app.errorhandler(ValidationError)
    def _validation(err):
        return jsonify(error="validation_error", detail=err.messages), 422

    @app.errorhandler(HTTPException)
    def _http(err):
        return jsonify(error=err.name.lower().replace(" ", "_"),
                       detail=err.description), err.code

    @app.errorhandler(Exception)
    def _unhandled(err):
        app.logger.exception("unhandled error")
        return jsonify(error="internal_error", detail="server error"), 500
