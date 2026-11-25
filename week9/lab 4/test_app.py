"""Practice 4 — test 5 case của blue-green routing.

Chạy: python -m pytest -v (trong thư mục lab 4)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from app import app  # noqa: E402
from gateway import bucket  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(config, "V2_PERCENT", 5)
    return app.test_client()


def post(client, body, **headers):
    return client.post("/orders", json=body, headers=headers)


# 1. Cohort beta -> v2 (kể cả account bình thường)
def test_case1_cohort_beta_goes_to_v2(client):
    res = post(client, {"account_id": "any"}, **{"X-Cohort": "beta"})
    assert res.status_code == 201
    assert res.headers["X-Order-Handler"] == "v2"
    assert res.headers["X-Route-Reason"] == "cohort:beta"
    assert res.get_json()["id"].startswith("ord_")


# 2. acct_42 trong allow-list -> v2
def test_case2_allow_listed_account_goes_to_v2(client):
    res = post(client, {"account_id": "acct_42"})
    assert res.headers["X-Order-Handler"] == "v2"
    assert res.headers["X-Route-Reason"] == "allow-list"


# 3. Account thường -> hash bucket quyết định, và ổn định qua nhiều lần gọi
def test_case3_bucket_decides_and_is_sticky(client):
    assert bucket("acct_101") < 5 <= bucket("acct_1")
    for _ in range(5):
        assert post(client, {"account_id": "acct_101"}).headers["X-Order-Handler"] == "v2"
        res = post(client, {"account_id": "acct_1"})
        assert res.headers["X-Order-Handler"] == "v1"
        assert res.status_code == 200
        assert set(res.get_json()) == {"order_id", "account", "status"}


def test_case3_about_5_percent_of_accounts(client):
    share = sum(bucket(f"acct_{i}") < 5 for i in range(10_000)) / 10_000
    assert 0.03 < share < 0.07


# 4. Flip V2_PERCENT = 100 -> mọi account vào v2
def test_case4_flip_to_100_percent(client, monkeypatch):
    monkeypatch.setattr(config, "V2_PERCENT", 100)
    for acct in ("acct_1", "acct_2", "acct_3", ""):
        assert post(client, {"account_id": acct}).headers["X-Order-Handler"] == "v2"


# Rollback: V2_PERCENT = 0 -> chỉ cohort/allow-list còn ở v2
# (case 5 của đề — archive v1 sau 30 ngày ở 100% — là bước vận hành, xem readme)
def test_rollback_to_zero_percent(client, monkeypatch):
    monkeypatch.setattr(config, "V2_PERCENT", 0)
    assert post(client, {"account_id": "acct_101"}).headers["X-Order-Handler"] == "v1"
    assert post(client, {"account_id": "acct_42"}).headers["X-Order-Handler"] == "v2"


def test_unknown_cohort_falls_through_to_bucket(client):
    res = post(client, {"account_id": "acct_1"}, **{"X-Cohort": "gamma"})
    assert res.headers["X-Order-Handler"] == "v1"


def test_invalid_body_is_400(client):
    assert client.post("/orders", data="nope", content_type="application/json").status_code == 400
