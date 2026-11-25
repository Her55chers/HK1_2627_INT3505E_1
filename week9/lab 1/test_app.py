"""Practice 1 — chạy: python -m pytest -v (trong thư mục lab 1)."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app  # noqa: E402
from blueprints import users_data as data  # noqa: E402


@pytest.fixture()
def client():
    snapshot = copy.deepcopy(data.users_data)
    yield app.test_client()
    data.users_data.clear()
    data.users_data.update(snapshot)


def test_same_user_two_schemas(client):
    v1 = client.get("/v1/users/1").get_json()
    v2 = client.get("/v2/users/1").get_json()
    assert set(v1) == {"id", "full_name", "email"}
    assert set(v2) == {"id", "first_name", "last_name", "email"}
    assert v1["id"] == v2["id"] == 1


def test_v1_has_sunset_headers(client):
    res = client.get("/v1/users/1")
    assert res.headers["Sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"
    assert res.headers["Deprecation"] == "true"
    assert 'rel="successor-version"' in res.headers["Link"]


def test_v2_has_no_sunset_header(client):
    assert "Sunset" not in client.get("/v2/users/1").headers


def test_not_found_both_versions(client):
    assert client.get("/v1/users/999").status_code == 404
    assert client.get("/v2/users/999").status_code == 404


def test_post_v2_creates_user_readable_by_both_versions(client):
    res = client.post("/v2/users", json={"first_name": "Dung", "last_name": "Pham",
                                         "email": "dung.pham@example.com"})
    assert res.status_code == 201
    body = res.get_json()
    assert res.headers["Location"] == f"/v2/users/{body['id']}"
    assert client.get(f"/v2/users/{body['id']}").get_json()["first_name"] == "Dung"
    assert client.get(f"/v1/users/{body['id']}").get_json()["full_name"] == "Pham Dung"


@pytest.mark.parametrize("payload", [
    {"first_name": "A", "email": "a@example.com"},
    {"first_name": "A", "last_name": " ", "email": "a@example.com"},
    {"first_name": "A", "last_name": "B", "email": "not-an-email"},
])
def test_post_v2_validation(client, payload):
    assert client.post("/v2/users", json=payload).status_code == 400


def test_post_not_available_on_v1(client):
    assert client.post("/v1/users", json={}).status_code in (404, 405)
