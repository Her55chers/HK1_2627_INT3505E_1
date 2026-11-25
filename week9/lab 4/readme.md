# Practice 4 — Blue-Green Routing: 1 URL, chọn v1 hoặc v2 theo cohort

Mọi đơn hàng đi qua `POST /orders`. Gateway chọn v1 (blue) hay v2 (green) theo 3 tầng ưu tiên:

1. **Cohort**: header `X-Cohort: beta` hoặc `internal` → v2.
2. **Allow-list**: `account_id` là `acct_42` hoặc `acct_99` → v2.
3. **Hash bucket**: `md5(account_id) % 100 < V2_PERCENT` → v2 (mặc định 5%).

v1 trả schema cũ (`order_id`, `status`) với `200`; v2 trả schema mới (`id`, `state`, `items`) với `201`.

## Cách chạy

Terminal 1 (server, mặc định 5%):

```powershell
cd "C:\Users\vulin\Documents\github\HK1_2627_INT3505E_1\week9\lab 4"; ..\..\.venv\Scripts\python app.py
```

Chạy test (8 passed):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## Kết quả

Chạy các lệnh dưới trong terminal 2 (PowerShell).

**curl 1:** cohort `beta` → v2, `201`

```powershell
curl.exe -X POST localhost:5000/orders -H "X-Cohort: beta" -H "Content-Type: application/json" -d '{\"account_id\":\"any\"}'
```

```json
{
  "account_id": "any",
  "id": "ord_1001",
  "items": [],
  "state": "created"
}
```

**curl 2:** `acct_42` trong allow-list → v2, `201`

```powershell
curl.exe -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{\"account_id\":\"acct_42\"}'
```

```json
{
  "account_id": "acct_42",
  "id": "ord_1002",
  "items": [],
  "state": "created"
}
```

**curl 3:** `acct_1` rơi vào bucket 53 (≥ 5) → v1, `200`

```powershell
curl.exe -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{\"account_id\":\"acct_1\"}'
```

```json
{
  "account": "acct_1",
  "order_id": 1003,
  "status": "accepted"
}
```

**curl 4:** `acct_101` rơi vào bucket 1 (< 5) → v2, `201`

```powershell
curl.exe -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{\"account_id\":\"acct_101\"}'
```

```json
{
  "account_id": "acct_101",
  "id": "ord_1004",
  "items": [],
  "state": "created"
}
```

Trước curl 5: bấm `Ctrl+C` ở terminal 1, rồi chạy lại server với `V2_PERCENT = 100`:

```powershell
$env:V2_PERCENT = "100"; ..\..\.venv\Scripts\python app.py
```

**curl 5:** xem cấu hình rollout → `200`

```powershell
curl.exe localhost:5000/rollout
```

```json
{
  "v2_cohorts": [
    "beta",
    "internal"
  ],
  "v2_force_accounts": [
    "acct_42",
    "acct_99"
  ],
  "v2_percent": 100
}
```

**curl 6:** gửi lại `acct_1`, lần này vào v2 → `201` (id bắt đầu lại từ `ord_1001` vì server vừa restart)

```powershell
curl.exe -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{\"account_id\":\"acct_1\"}'
```

```json
{
  "account_id": "acct_1",
  "id": "ord_1001",
  "items": [],
  "state": "created"
}
```

Xong thì trả về mặc định (ở terminal 1): `Remove-Item Env:V2_PERCENT`.

## Case 5 — archive v1 sau 30 ngày ở 100%

Đây là bước vận hành, không phải request:

1. Giữ 100% trong 30 ngày, theo dõi log `gateway` đến khi không còn dòng `handler=v1`.
2. Nếu v2 lỗi: rollback bằng `V2_PERCENT = 0` (test `test_rollback_to_zero_percent`).
3. Hết 30 ngày: bỏ nhánh v1 khỏi `dispatch`, chuyển `v1_create_order` vào archive (giữ khoảng 12 tháng).
