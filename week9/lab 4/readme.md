# Practice 4 — Blue-Green Routing: 1 URL, chọn v1 hoặc v2 theo cohort

Mọi đơn hàng đều đi qua cùng một URL `POST /orders`. Gateway quyết định gọi `v1_create_order` (blue) hay `v2_create_order` (green) theo 3 tầng ưu tiên:

1. **Cohort**: header `X-Cohort: beta` hoặc `internal` → v2.
2. **Allow-list**: `account_id` thuộc `acct_42` hoặc `acct_99` → v2.
3. **Hash bucket**: `md5(account_id) % 100 < V2_PERCENT` → v2. Cùng một account luôn rơi vào cùng bucket, nên không bị lúc v1 lúc v2.

| File | Nội dung |
|---|---|
| [config.py](config.py) | `V2_PERCENT` (mặc định 5, đổi qua biến môi trường), `V2_COHORTS`, `V2_FORCE_ACCOUNTS` |
| [gateway.py](gateway.py) | Routing 3 tầng; log mọi quyết định để đo adoption |
| [handlers.py](handlers.py) | v1 trả schema cũ + `200`, v2 trả schema mới + `201` |
| [app.py](app.py) | `POST /orders` (header `X-Order-Handler`, `X-Route-Reason`), `GET /rollout` xem cấu hình |

So với code mẫu trên slide, tôi thêm:

- Header **`X-Route-Reason`** cho biết vì sao request vào v1/v2 (`cohort:beta`, `allow-list`, `bucket:53>=5`, ...).
- **Log mỗi quyết định route**, để đếm được bao nhiêu % traffic còn ở v1 trước khi sunset.
- Body không phải JSON object → **400**. Code mẫu sẽ lỗi 500 khi `request.get_json()` trả `None`.
- `V2_PERCENT` đọc từ biến môi trường và gateway đọc config mỗi request, nên flip % chỉ cần restart chứ không cần sửa code.

## 1. Cách chạy

```powershell
cd "week9\lab 4"
..\..\.venv\Scripts\python app.py
```

Chạy test (**8 passed**):

```powershell
..\..\.venv\Scripts\python -m pytest -v
```

## 2. Test 5 case — curl và kết quả

Các lệnh dưới đây chạy được trong Git Bash; trên PowerShell hãy dùng `curl.exe`. Kết quả là output thật với `V2_PERCENT=5`.

### Case 1 — Cohort beta → v2

```bash
curl -i -X POST localhost:5000/orders -H "X-Cohort: beta" -H "Content-Type: application/json" -d '{"account_id":"any"}'
```

```http
HTTP/1.1 201 CREATED
X-Order-Handler: v2
X-Route-Reason: cohort:beta

{"account_id":"any","id":"ord_1001","items":[],"state":"created"}
```

### Case 2 — `acct_42` trong allow-list → v2

```bash
curl -i -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{"account_id":"acct_42"}'
```

```http
HTTP/1.1 201 CREATED
X-Order-Handler: v2
X-Route-Reason: allow-list

{"account_id":"acct_42","id":"ord_1002","items":[],"state":"created"}
```

### Case 3 — Account thường: bucket quyết định (5%)

`acct_1` rơi vào bucket 53, tức ≥ 5, nên vào **v1**:

```bash
curl -i -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{"account_id":"acct_1"}'
```

```http
HTTP/1.1 200 OK
X-Order-Handler: v1
X-Route-Reason: bucket:53>=5

{"account":"acct_1","order_id":1003,"status":"accepted"}
```

`acct_101` rơi vào bucket 1, tức < 5, nên vào **v2**:

```bash
curl -i -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{"account_id":"acct_101"}'
```

```http
HTTP/1.1 201 CREATED
X-Order-Handler: v2
X-Route-Reason: bucket:1<5

{"account_id":"acct_101","id":"ord_1004","items":[],"state":"created"}
```

Với 10 000 account `acct_0..acct_9999`, có **4,74%** rơi vào v2, sát với mục tiêu 5%.

### Case 4 — Flip `V2_PERCENT = 100` → mọi account vào v2

Dừng server, rồi chạy lại với 100%:

```powershell
$env:V2_PERCENT = "100"
..\..\.venv\Scripts\python app.py
```

```bash
curl localhost:5000/rollout
curl -i -X POST localhost:5000/orders -H "Content-Type: application/json" -d '{"account_id":"acct_1"}'
```

```http
{"v2_cohorts":["beta","internal"],"v2_force_accounts":["acct_42","acct_99"],"v2_percent":100}

HTTP/1.1 201 CREATED
X-Order-Handler: v2
X-Route-Reason: bucket:53<100

{"account_id":"acct_1","id":"ord_1001","items":[],"state":"created"}
```

Cùng account `acct_1`, trước đó vào v1, giờ đã chuyển sang v2. Khi xong, trả về mặc định:

```powershell
Remove-Item Env:V2_PERCENT
```

### Case 5 — Sau khi 100% ổn định: archive v1 sau 30 ngày

Đây là bước vận hành, không phải một request. Quy trình:

1. Giữ `V2_PERCENT = 100` trong 30 ngày. Theo dõi log `gateway`: số dòng `handler=v1` phải về **0**. Nếu còn, đó là client dùng cohort hoặc account bị ép về v1.
2. Nếu v2 có sự cố trong 30 ngày này, **rollback** bằng cách đặt `V2_PERCENT = 0`. Khi đó chỉ cohort beta/internal và allow-list còn ở v2. Trường hợp này được kiểm bởi `test_rollback_to_zero_percent`.
3. Hết 30 ngày: xoá nhánh v1 khỏi `dispatch`, chuyển `v1_create_order` vào archive. Theo slide, nên giữ code v1 khoảng 12 tháng để khôi phục được khi cần.

## 3. Log gateway (đo adoption)

```
INFO gateway: route account=any handler=v2 reason=cohort:beta
INFO gateway: route account=acct_42 handler=v2 reason=allow-list
INFO gateway: route account=acct_1 handler=v1 reason=bucket:53>=5
INFO gateway: route account=acct_101 handler=v2 reason=bucket:1<5
```
