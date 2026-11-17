import copy
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError, validate

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "resources"
sys.path.insert(0, str(STARTER))

from app import create_app  # noqa: E402

SPEC = yaml.safe_load((HERE / "openapi.yaml").read_text(encoding="utf-8"))


def to_json_schema(node):
    """OpenAPI 3.0 -> JSON Schema: đổi `nullable: true` thành type [..., "null"],
    và inline các $ref tới components.schemas."""
    if isinstance(node, list):
        return [to_json_schema(n) for n in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return to_json_schema(SPEC["components"]["schemas"][name])
    out = {k: to_json_schema(v) for k, v in node.items() if k != "nullable"}
    if node.get("nullable") and "type" in out:
        out["type"] = [out["type"], "null"]
    return out


BOOK = to_json_schema(SPEC["components"]["schemas"]["Book"])
ERROR = to_json_schema(SPEC["components"]["schemas"]["Error"])


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True,
                      "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'c.db'}"})
    return app.test_client()


@pytest.fixture()
def created(client):
    res = client.post("/books", json={"title": "API Design Patterns",
                                      "author": "J.J. Geewax", "year": 2021,
                                      "isbn": "9781617295850"})
    assert res.status_code == 201
    return res.get_json()


def test_create_response_matches_book_schema(created):
    validate(created, BOOK)


def test_get_response_matches_book_schema(client, created):
    validate(client.get(f"/books/{created['id']}").get_json(), BOOK)


def test_list_response_items_match_book_schema(client, created):
    body = client.get("/books").get_json()
    validate(body, {"type": "array", "items": BOOK})


def test_year_null_is_allowed(client):
    res = client.post("/books", json={"title": "No year", "author": "x"})
    validate(res.get_json(), BOOK)


def test_error_responses_match_error_schema(client):
    validate(client.get("/books/9999").get_json(), ERROR)
    validate(client.post("/books", json={"author": "x"}).get_json(), ERROR)


@pytest.mark.parametrize("mutate", [
    lambda b: b.update(password_hash="x"),   # lộ field lạ
    lambda b: b.pop("isbn"),                 # thiếu field required
    lambda b: b.update(year="2021"),         # sai kiểu (lỗi 3 của Lab 2)
])
def test_schema_rejects_drift(created, mutate):
    """Chứng minh schema đủ chặt để bắt các kiểu 'code trả sai field'."""
    drifted = copy.deepcopy(created)
    mutate(drifted)
    with pytest.raises(ValidationError):
        validate(drifted, BOOK)
