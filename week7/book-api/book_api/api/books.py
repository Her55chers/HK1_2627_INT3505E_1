from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from ..errors import BadRequest, Conflict, NotFound, OutOfStock
from ..extensions import db
from ..models import Book
from .schemas import BookIn, BookOut, BookPatch, PageArgs, ReserveIn

books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")


def get_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("body phải là JSON object")
    return data


def get_book_or_404(book_id):
    book = db.session.get(Book, book_id)
    if book is None or book.archived:  # sách đã xóa mềm coi như không tồn tại
        raise NotFound(f"book {book_id} not found")
    return book


# GET /api/v1/books?page=1&size=20
@books_bp.get("")
def list_books():
    args = PageArgs().load(request.args)
    page, size = args["page"], args["size"]
    base = db.select(Book).where(Book.archived.is_(False))
    rows = db.session.execute(
        base.order_by(Book.id).offset((page - 1) * size).limit(size)
    ).scalars().all()
    total = db.session.scalar(
        db.select(db.func.count()).select_from(Book).where(Book.archived.is_(False)))
    return {"items": BookOut(many=True).dump(rows),
            "page": page, "size": size, "total": total}, 200


# GET /api/v1/books/<id>
@books_bp.get("/<int:book_id>")
def get_book(book_id):
    return BookOut().dump(get_book_or_404(book_id)), 200


# POST /api/v1/books
@books_bp.post("")
def create_book():
    body = BookIn().load(get_json())
    book = Book(**body)
    db.session.add(book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("isbn already exists")
    return BookOut().dump(book), 201


# PATCH /api/v1/books/<id>  — chỉ field có trong body mới đổi
@books_bp.patch("/<int:book_id>")
def patch_book(book_id):
    body = BookPatch().load(get_json(), partial=True)
    book = get_book_or_404(book_id)
    for k, v in body.items():
        setattr(book, k, v)
    db.session.commit()
    return BookOut().dump(book), 200


# DELETE /api/v1/books/<id>  — soft delete
@books_bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = get_book_or_404(book_id)
    book.archived = True
    db.session.commit()
    return "", 204


# POST /api/v1/books/<id>/reserve   body: {"qty": 1}
@books_bp.post("/<int:book_id>/reserve")
def reserve_book(book_id):
    qty = ReserveIn().load(get_json())["qty"]
    book = get_book_or_404(book_id)
    take_stock(book, qty)
    db.session.commit()
    return BookOut().dump(book), 200


def take_stock(book, qty):
    """Giảm tồn kho, không cho < 0. Dùng chung cho reserve và order."""
    if book.qty_in_stock < qty:
        raise OutOfStock(f"only {book.qty_in_stock} left")
    book.qty_in_stock -= qty
