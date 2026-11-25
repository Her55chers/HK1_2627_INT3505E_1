"""Practice 3 — test 3 tình huống: trước sunset, sau sunset, log warning.

Chạy: python -m pytest -v (trong thư mục lab 3)
"""
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sunset  # noqa: E402
from app import V1_SUNSET, app  # noqa: E402


@pytest.fixture()
def client():
    return app.test_client()


def freeze(monkeypatch, when):
    monkeypatch.setattr(sunset, "now_utc", lambda: when)


# 1. Trước sunset: 200 + Sunset + Deprecation + Link
def test_before_sunset_returns_200_with_headers(client, monkeypatch):
    freeze(monkeypatch, V1_SUNSET - timedelta(days=1))
    res = client.get("/api/v1/users/1")
    assert res.status_code == 200
    assert res.headers["Sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"
    assert res.headers["Deprecation"] == "true"
    assert res.headers["Link"] == '</api/v2/users>; rel="successor-version"'
    assert res.get_json()["full_name"] == "Nguyễn Văn"


# 2. Từ thời điểm sunset trở đi: 410 Gone
@pytest.mark.parametrize("delta", [timedelta(0), timedelta(seconds=1), timedelta(days=30)])
def test_at_or_after_sunset_returns_410(client, monkeypatch, delta):
    freeze(monkeypatch, V1_SUNSET + delta)
    res = client.get("/api/v1/users/1")
    assert res.status_code == 410
    body = res.get_json()
    assert body["error"] == "gone"
    assert body["use_instead"] == "/api/v2/users"
    assert "successor-version" in res.headers["Link"]


# 3. Mỗi call log warning
def test_each_call_logs_warning(client, monkeypatch, caplog):
    freeze(monkeypatch, V1_SUNSET - timedelta(days=1))
    with caplog.at_level(logging.WARNING, logger="sunset"):
        client.get("/api/v1/users/1")
        client.get("/api/v1/users/1")
    calls = [r for r in caplog.records if "deprecated_call /api/v1/users/1" in r.getMessage()]
    assert len(calls) == 2


def test_error_status_is_kept_before_sunset(client, monkeypatch):
    freeze(monkeypatch, V1_SUNSET - timedelta(days=1))
    res = client.get("/api/v1/users/999")
    assert res.status_code == 404
    assert res.headers["Deprecation"] == "true"


def test_v0_already_gone_with_real_clock(client):
    assert datetime.now(timezone.utc) > datetime(2026, 6, 30, tzinfo=timezone.utc)
    assert client.get("/api/v0/users/1").status_code == 410


def test_v2_not_deprecated(client):
    res = client.get("/api/v2/users/1")
    assert res.status_code == 200
    assert "Sunset" not in res.headers and "Deprecation" not in res.headers
