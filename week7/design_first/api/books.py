from connexion import NoContent
from sqlalchemy import select

from ..errors import Conflict, field_error
from ..extensions import db
from ..models import Author, Book, Borrow
from .common import get_or_404, paginate, parse_uuid

NOT_FOUND = "Không tìm thấy sách với id đã cung cấp"
PLAIN_FIELDS = ("title", "description", "isbn", "category", "published_year")


def _author_id(value):
    author_id = parse_uuid(value, "author_id")
    if db.session.get(Author, author_id) is None:
        raise field_error("author_id", "Tác giả không tồn tại")
    return author_id


def get_books(page=1, limit=10, title=None, category_id=None):
    stmt = select(Book).order_by(Book.created_at.desc(), Book.id)
    if title:
        stmt = stmt.where(Book.title.icontains(title, autoescape=True))
    if category_id:
        stmt = stmt.where(Book.category_id == parse_uuid(category_id, "category_id"))
    return paginate(stmt, page, limit), 200


def create_book(body):
    book = Book(
        author_id=_author_id(body["author_id"]),
        category_id=parse_uuid(body["category_id"], "category_id"),
        quantity=body["quantity"],
        available_quantity=body["quantity"],
    )
    for field in PLAIN_FIELDS:
        if field in body:
            setattr(book, field, body[field])
    db.session.add(book)
    db.session.commit()
    return {"data": book.to_dict()}, 201


def get_book_by_id(id):
    return {"data": get_or_404(Book, id, NOT_FOUND).to_dict()}, 200


def update_book(id, body):
    book = get_or_404(Book, id, NOT_FOUND, with_for_update=True)
    for field in PLAIN_FIELDS:
        if field in body:
            setattr(book, field, body[field])
    if "author_id" in body:
        book.author_id = _author_id(body["author_id"])
    if "category_id" in body:
        book.category_id = parse_uuid(body["category_id"], "category_id")

    quantity = body.get("quantity", book.quantity)
    available = body.get("available_quantity", book.available_quantity + quantity - book.quantity)
    if not 0 <= available <= quantity:
        raise field_error(
            "available_quantity", "Số sách sẵn có phải nằm trong khoảng từ 0 đến tổng số lượng"
        )
    book.quantity = quantity
    book.available_quantity = available
    db.session.commit()
    return {"data": book.to_dict()}, 200


def delete_book(id):
    book = get_or_404(Book, id, NOT_FOUND)
    if db.session.scalar(select(Borrow.id).where(Borrow.book_id == book.id).limit(1)):
        raise Conflict("Sách đã có phiếu mượn, không thể xóa")
    db.session.delete(book)
    db.session.commit()
    return NoContent, 204
