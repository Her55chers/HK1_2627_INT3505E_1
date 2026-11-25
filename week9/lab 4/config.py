"""Practice 4 — cấu hình rollout (giả lập "flip qua dashboard" bằng biến môi trường).

PowerShell:  $env:V2_PERCENT = "100"; python app.py
"""
import os

# % account (theo hash bucket) được route sang v2. Rollout: 5 -> 25 -> 50 -> 100.
V2_PERCENT = int(os.environ.get("V2_PERCENT", "5"))
# Cohort luôn vào v2 (header X-Cohort)
V2_COHORTS = {"beta", "internal"}
# Account luôn vào v2 (allow-list)
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}
