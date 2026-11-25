"""Practice 4 — hai implementation của "tạo đơn hàng" chạy song song (blue = v1, green = v2)."""
import itertools

_ids = itertools.count(1001)


def v1_create_order(body):
    """v1 (blue): schema cũ, phẳng; trả 200."""
    return {
        "order_id": next(_ids),
        "account": body.get("account_id"),
        "status": "accepted",
    }


def v2_create_order(body):
    """v2 (green): schema mới — id dạng chuỗi, state rõ ràng, items có cấu trúc; trả 201."""
    items = body.get("items") or []
    return {
        "id": f"ord_{next(_ids)}",
        "account_id": body.get("account_id"),
        "state": "created",
        "items": [{"sku": i.get("sku"), "qty": int(i.get("qty", 1))}
                  for i in items if isinstance(i, dict)],
    }
