import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request, url_for
from sqlalchemy import DateTime, and_, func, literal, or_, select
from sqlalchemy.orm import selectinload

from models import Book, BookAuthor, Category, db

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

DEFAULT_LIMIT, MAX_LIMIT = 20, 100
DEFAULT_STRATEGY = "cursor"
STRATEGIES = ("offset", "cursor")
DEFAULT_SORT = "-id"
MAX_SORT_KEYS = 3
CURSOR_VERSION = 1

EPOCH = datetime(1, 1, 1, tzinfo=timezone.utc)

class ApiError(Exception):
    def __init__(self, error, message, status=400):
        super().__init__(message)
        self.error, self.message, self.status = error, message, status


@bp.errorhandler(ApiError)
def _handle_api_error(e):
    return jsonify(error=e.error, message=e.message), e.status


@dataclass(frozen=True)
class SortField:
    expr: object      
    attr: str            
    kind: str             


SORT_FIELDS = {
    "id": SortField(Book.id, "id", "int"),
    "title": SortField(Book.title, "title", "str"),
    "stock": SortField(Book.stock, "stock", "int"),
    "published_date": SortField(Book.published_date, "published_date", "datetime"),
}


def parse_sort(raw):
    parts = [p.strip() for p in (raw or DEFAULT_SORT).split(",") if p.strip()]
    if not parts:
        raise ApiError("bad_sort", "sort không được rỗng")
    if len(parts) > MAX_SORT_KEYS:
        raise ApiError("bad_sort", f"tối đa {MAX_SORT_KEYS} key sort")

    keys, seen = [], set()
    for p in parts:
        desc = p.startswith("-")
        name = p[1:] if desc else p
        if name not in SORT_FIELDS:
            raise ApiError("bad_sort", f"không sort được theo '{name}'. "
                                       f"Hợp lệ: {', '.join(SORT_FIELDS)}")
        if name in seen:
            raise ApiError("bad_sort", f"key '{name}' bị lặp")
        seen.add(name)
        keys.append((name, desc))

    if "id" not in seen:
        keys.append(("id", keys[0][1]))
    return keys


def normalize_sort(keys):
    return ",".join(("-" if d else "") + n for n, d in keys)


def order_clauses(keys):
    return [SORT_FIELDS[n].expr.desc() if d else SORT_FIELDS[n].expr.asc() for n, d in keys]


def keyset_condition(keys, values):
    """Điều kiện "đứng sau bản ghi cuối" cho sort nhiều key, kể cả chiều lẫn lộn.

    (k1 > v1) OR (k1 = v1 AND k2 < v2) OR (k1 = v1 AND k2 = v2 AND id > v3) ...
    Không dùng tuple_(a, b) > (x, y) được vì nó chỉ đúng khi mọi key cùng chiều.
    """
    branches = []
    for i, (name, desc) in enumerate(keys):
        expr = SORT_FIELDS[name].expr
        equal_prefix = [SORT_FIELDS[n].expr == values[j] for j, (n, _) in enumerate(keys[:i])]
        step = expr < values[i] if desc else expr > values[i]
        branches.append(and_(*equal_prefix, step))
    return or_(*branches)

def parse_genres(raw):
    if raw is None:
        return []
    slugs = sorted({s.strip().lower() for s in raw.split(",") if s.strip()})
    if not slugs:
        raise ApiError("bad_filter", "genre không được rỗng")
    return slugs


def filter_conditions(genres):
    conds = []
    if genres:
        conds.append(Book.category.has(Category.slug.in_(genres)))
    return conds

def _secret():
    key = current_app.config.get("CURSOR_SECRET") or current_app.config.get("SECRET_KEY")
    return (key or "dev-cursor-secret").encode()


def _b64e(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _dump_value(kind, v):
    if kind == "datetime":
        return (v or EPOCH).isoformat()
    return v


def _load_value(kind, v):
    if kind == "int":
        if not isinstance(v, int) or isinstance(v, bool):
            raise ValueError
        return v
    if kind == "str":
        if not isinstance(v, str):
            raise ValueError
        return v
    return datetime.fromisoformat(v)


def encode_cursor(keys, genres, last_book):
    state = {
        "v": CURSOR_VERSION,
        "s": normalize_sort(keys),
        "g": genres,
        "k": [_dump_value(SORT_FIELDS[n].kind, getattr(last_book, SORT_FIELDS[n].attr))
              for n, _ in keys],
    }
    body = json.dumps(state, separators=(",", ":"), ensure_ascii=False).encode()
    sig = hmac.new(_secret(), body, hashlib.sha256).digest()[:16]
    return f"{_b64e(body)}.{_b64e(sig)}"


def decode_cursor(token, keys, genres):
    try:
        body_b64, sig_b64 = token.split(".")
        body = _b64d(body_b64)
        expected = hmac.new(_secret(), body, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(expected, _b64d(sig_b64)):
            raise ValueError
        state = json.loads(body)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise ApiError("invalid_cursor", "cursor không hợp lệ hoặc đã bị sửa")

    if state.get("v") != CURSOR_VERSION:
        raise ApiError("invalid_cursor", "cursor thuộc phiên bản cũ, hãy bắt đầu lại từ trang đầu")
    if state.get("s") != normalize_sort(keys) or state.get("g") != genres:
        raise ApiError("cursor_mismatch",
                       "cursor được tạo với sort/genre khác; giữ nguyên sort và genre khi phân trang "
                       "hoặc bỏ cursor để bắt đầu lại")
    raw_values = state.get("k")
    if not isinstance(raw_values, list) or len(raw_values) != len(keys):
        raise ApiError("invalid_cursor", "cursor không hợp lệ")
    try:
        return [_load_value(SORT_FIELDS[n].kind, v) for (n, _), v in zip(keys, raw_values)]
    except (ValueError, TypeError):
        raise ApiError("invalid_cursor", "cursor không hợp lệ")


def int_arg(name, default, minimum):
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ApiError("bad_param", f"{name} phải là số nguyên")
    if value < minimum:
        raise ApiError("bad_param", f"{name} phải >= {minimum}")
    return value


def page_url(**overrides):
    args = request.args.to_dict()
    args.update({k: str(v) for k, v in overrides.items()})
    return url_for("books.list_books", **args)


def base_query(conds, keys):
    return (select(Book)
            .where(*conds)
            .order_by(*order_clauses(keys))
            .options(selectinload(Book.authors_links).selectinload(BookAuthor.author)))


@bp.get("")
def list_books():
    strategy = request.args.get("strategy", DEFAULT_STRATEGY).lower()
    if strategy not in STRATEGIES:
        raise ApiError("bad_strategy", f"strategy phải là một trong: {', '.join(STRATEGIES)}")

    limit = min(int_arg("limit", DEFAULT_LIMIT, 1), MAX_LIMIT)
    keys = parse_sort(request.args.get("sort"))
    genres = parse_genres(request.args.get("genre"))
    conds = filter_conditions(genres)

    if strategy == "offset":
        if "cursor" in request.args:
            raise ApiError("bad_param", "cursor chỉ dùng với strategy = cursor")
        return _offset_page(conds, keys, limit)

    if "offset" in request.args:
        raise ApiError("bad_param", "offset chỉ dùng với strategy = offset")
    return _cursor_page(conds, keys, genres, limit)


def _offset_page(conds, keys, limit):
    offset = int_arg("offset", 0, 0)
    total = db.session.scalar(select(func.count(Book.id)).where(*conds))
    rows = db.session.scalars(base_query(conds, keys).offset(offset).limit(limit)).all()

    has_more = offset + len(rows) < total
    links = {}
    if has_more:
        links["next"] = page_url(strategy="offset", offset=offset + limit, limit=limit)
    if offset > 0:
        links["prev"] = page_url(strategy="offset", offset=max(offset - limit, 0), limit=limit)

    body = {
        "data": [b.to_dict() for b in rows],
        "pagination": {
            "strategy": "offset",
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": has_more,
            "next_offset": offset + limit if has_more else None,
        },
        "links": links,
    }
    return _with_link_header(body, links)


def _cursor_page(conds, keys, genres, limit):
    q = base_query(conds, keys)
    raw = request.args.get("cursor")
    if raw:
        q = q.where(keyset_condition(keys, decode_cursor(raw, keys, genres)))

    rows = db.session.scalars(q.limit(limit + 1)).all()  
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(keys, genres, rows[-1]) if has_more and rows else None

    links = {"next": page_url(strategy="cursor", cursor=next_cursor, limit=limit)} if next_cursor else {}
    body = {
        "data": [b.to_dict() for b in rows],
        "pagination": {
            "strategy": "cursor",
            "limit": limit,
            "next_cursor": next_cursor,
            "has_more": has_more,
        },
        "links": links,
    }
    return _with_link_header(body, links)


def _with_link_header(body, links):
    resp = jsonify(body)
    if links:
        resp.headers["Link"] = ", ".join(f'<{u}>; rel="{rel}"' for rel, u in links.items())
    return resp
