"""Practice 4 — gateway 3 tầng: cohort header -> account allow-list -> hash bucket %."""
import hashlib
import logging

from flask import request

import config
from handlers import v1_create_order, v2_create_order

log = logging.getLogger("gateway")


def bucket(account_id):
    """Bucket 0..99 cố định theo account: cùng account luôn vào cùng version."""
    return int(hashlib.md5(account_id.encode()).hexdigest(), 16) % 100


def decide(body):
    """Trả (route_to_v2: bool, reason: str)."""
    # 1. Explicit cohort có ưu tiên cao nhất
    cohort = request.headers.get("X-Cohort", "").strip().lower()
    if cohort in config.V2_COHORTS:
        return True, f"cohort:{cohort}"
    # 2. Account nằm trong allow-list
    acct = str(body.get("account_id", ""))
    if acct in config.V2_FORCE_ACCOUNTS:
        return True, "allow-list"
    # 3. Deterministic percentage bucket
    if config.V2_PERCENT <= 0:
        return False, "percent:0"
    b = bucket(acct)
    return b < config.V2_PERCENT, f"bucket:{b}<{config.V2_PERCENT}" if b < config.V2_PERCENT \
        else f"bucket:{b}>={config.V2_PERCENT}"


def route_to_v2(body):
    return decide(body)[0]


def dispatch(body):
    to_v2, reason = decide(body)
    which = "v2" if to_v2 else "v1"
    # Log mọi quyết định để đo adoption (bao nhiêu % traffic còn ở v1)
    log.info("route account=%s handler=%s reason=%s", body.get("account_id"), which, reason)
    result = v2_create_order(body) if to_v2 else v1_create_order(body)
    return which, reason, result
