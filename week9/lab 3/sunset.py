"""Practice 3 — decorator @deprecate_at(date) theo RFC 8594 (Sunset header).

- Trước sunset: response bình thường + Sunset + Deprecation: true (+ Link successor).
- Từ thời điểm sunset trở đi: 410 Gone, kèm chỉ dẫn sang version thay thế.
- Mỗi call vào endpoint deprecated đều log warning để đo còn bao nhiêu client dùng.
"""
import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import jsonify, request

log = logging.getLogger("sunset")


def http_date(dt):
    return format_datetime(dt, usegmt=True)


def now_utc():
    """Tách riêng để test có thể giả lập thời gian (monkeypatch)."""
    return datetime.now(timezone.utc)


def _link(replacement):
    return f'<{replacement}>; rel="successor-version"'


def deprecate_at(sunset_date, replacement=None):
    def wrap(fn):
        @wraps(fn)
        def inner(*a, **kw):
            if now_utc() >= sunset_date:
                log.warning("sunset_call %s %s (gone since %s)", request.path,
                            request.remote_addr, http_date(sunset_date))
                r = jsonify({"error": "gone", "sunset": http_date(sunset_date),
                             "use_instead": replacement})
                r.status_code = 410
                if replacement:
                    r.headers["Link"] = _link(replacement)
                return r

            result = fn(*a, **kw)
            body, status = result if isinstance(result, tuple) else (result, 200)
            r = jsonify(body)
            r.status_code = status
            r.headers["Sunset"] = http_date(sunset_date)
            r.headers["Deprecation"] = "true"
            if replacement:
                r.headers["Link"] = _link(replacement)
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            return r
        return inner
    return wrap
