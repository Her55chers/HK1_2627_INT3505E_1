"""Practice 2 — chạy: python -m pytest -v (trong thư mục lab 2)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    return app.test_client()


def test_default_is_latest_v2(client):
    res = client.get("/users/1")
    assert res.status_code == 200
    assert res.headers["X-API-Version-Served"] == "2"
    assert set(res.get_json()) == {"id", "first_name", "last_name", "email"}


def test_explicit_v1(client):
    res = client.get("/users/1", headers={"X-API-Version": "1"})
    assert res.headers["X-API-Version-Served"] == "1"
    assert res.get_json() == {"id": 1, "full_name": "Văn Nguyễn"}


def test_dated_version(client):
    res = client.get("/users/1", headers={"X-API-Version": "2024-06-20"})
    assert res.status_code == 200
    assert res.headers["X-API-Version-Served"] == "2024-06-20"
    assert "first_name" in res.get_json()


def test_unsupported_version_is_400_no_fallback(client):
    res = client.get("/users/1", headers={"X-API-Version": "99"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "unsupported version"
    assert "X-API-Version-Served" not in res.headers


def test_not_found_is_real_404(client):
    res = client.get("/users/999", headers={"X-API-Version": "1"})
    assert res.status_code == 404
    assert res.headers["X-API-Version-Served"] == "1"


def test_vary_header_for_caches(client):
    assert client.get("/users/1").headers["Vary"] == "X-API-Version"
