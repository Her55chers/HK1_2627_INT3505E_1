from flask import Blueprint
from sqlalchemy.orm import selectinload

from ..errors import NotFound
from ..extensions import db
from ..models import Order, OrderItem
from .books import get_book_or_404, get_json, take_stock
from .schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

# Eager load items + book -> luôn 3 query, không bị N+1
WITH_ITEMS = selectinload(Order.items).selectinload(OrderItem.book)


# GET /api/v1/orders
@orders_bp.get("")
def list_orders():
    rows = db.session.execute(
        db.select(Order).options(WITH_ITEMS).order_by(Order.id)
    ).scalars().all()
    return {"items": OrderOut(many=True).dump(rows)}, 200


# GET /api/v1/orders/<id>
@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = db.session.execute(
        db.select(Order).options(WITH_ITEMS).where(Order.id == order_id)
    ).scalar_one_or_none()
    if order is None:
        raise NotFound(f"order {order_id} not found")
    return OrderOut().dump(order), 200


# POST /api/v1/orders
# body: {"customer_name": "An", "items": [{"book_id": 1, "qty": 2}]}
@orders_bp.post("")
def create_order():
    body = OrderIn().load(get_json())
    order = Order(customer_name=body["customer_name"], total_cents=0)
    try:
        for it in body["items"]:
            book = get_book_or_404(it["book_id"])
            take_stock(book, it["qty"])
            order.items.append(OrderItem(
                book=book, qty=it["qty"], unit_price_cents=book.price_cents))
            order.total_cents += it["qty"] * book.price_cents
        db.session.add(order)
        db.session.commit()
    except Exception:
        db.session.rollback()  # lỗi 1 item -> không lưu gì cả
        raise
    return OrderOut().dump(order), 201
