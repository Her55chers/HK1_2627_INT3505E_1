# Security Audit: Social Network API

**Phạm vi:** `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`, theo `openapi.yaml` v1.0.0.

| # | Điểm có thể lộ | Endpoint | Mức độ | OWASP API 2023 |
|---|---|---|---|---|
| 1 | Đọc bài riêng tư của người khác (BOLA) | `GET /posts/{id}` | Nghiêm trọng | API1 |
| 2 | Refresh token bị đánh cắp và dùng lại | `POST /auth/refresh` | Cao | API2 |
| 3 | Dò mật khẩu, credential stuffing | `POST /auth/login` | Cao | API2, API4 |
| 4 | JWT bị giả mạo do xác minh yếu | `GET /posts/{id}` | Cao | API2 |
| 5 | Dò tài khoản qua phản hồi và thời gian xử lý | `POST /auth/login` | Trung bình | API2 |
| 6 | Trả thừa dữ liệu trong bài viết | `GET /posts/{id}` | Trung bình | API3 |
| 7 | Token lộ qua log, cache hoặc URL | Cả 3 endpoint | Trung bình | API8 |
| 8 | Access token còn hiệu lực sau khi bị thu hồi quyền | `GET /posts/{id}` | Trung bình | API2 |

## Chi tiết

### 1. Đọc bài riêng tư của người khác (BOLA)

- **Rủi ro:** scope `posts:read` chỉ cho biết token được phép đọc bài viết nói chung. Nếu server chỉ kiểm tra scope, bất kỳ ai đăng nhập cũng có thể đổi `{id}` để đọc bài `private` hoặc `followers`.
- **Khắc phục:** kiểm tra quyền trên từng bài ở tầng truy vấn dữ liệu, gồm chủ bài, quan hệ theo dõi và trạng thái chặn. Trả 404 khi không có quyền. Dùng UUID ngẫu nhiên để giảm việc dò ID, nhưng không coi đó là biện pháp phân quyền.

### 2. Refresh token bị đánh cắp và dùng lại

- **Rủi ro:** refresh token sống 30 ngày. Nếu bị lộ, kẻ tấn công có thể duy trì quyền truy cập rất lâu.
- **Khắc phục:** xoay vòng token sau mỗi lần dùng. Khi phát hiện token cũ bị gửi lại, thu hồi cả họ token. Chỉ lưu hash của token trong database. Trên web, lưu token trong cookie `HttpOnly`, `Secure`, `SameSite`; nếu đổi sang cookie thì phải cập nhật spec và thêm chống CSRF.

### 3. Dò mật khẩu, credential stuffing

- **Rủi ro:** endpoint public là mục tiêu tấn công tự động. Băm mật khẩu cũng tốn CPU, nên request hàng loạt có thể gây quá tải.
- **Khắc phục:** giới hạn tần suất theo cả IP và tài khoản, trả 429 kèm `Retry-After`. Băm bằng Argon2id. Giới hạn mật khẩu 128 ký tự như trong spec. Hỗ trợ MFA, cảnh báo đăng nhập bất thường và đối chiếu danh sách mật khẩu đã lộ.

### 4. JWT bị giả mạo do xác minh yếu

- **Rủi ro:** thư viện hoặc cấu hình sai có thể chấp nhận `alg: none`, nhầm thuật toán RS256/HS256, hoặc bỏ qua `iss`, `aud`, `exp`.
- **Khắc phục:** chỉ chấp nhận một thuật toán bất đối xứng cố định như ES256 hoặc RS256. Luôn kiểm tra `iss`, `aud`, `exp`. Không lấy khóa từ header `jku` hoặc `x5u` do client gửi. Xoay khóa định kỳ qua `kid`.

### 5. Dò tài khoản qua phản hồi và thời gian xử lý

- **Rủi ro:** spec đã thống nhất phản hồi 401, nhưng thời gian xử lý vẫn có thể lộ thông tin nếu server bỏ qua bước băm khi email không tồn tại. Lỗi 403 cũng chỉ an toàn khi được trả sau bước kiểm tra mật khẩu.
- **Khắc phục:** vẫn chạy so sánh với một hash giả khi không tìm thấy email. Kiểm tra trạng thái tài khoản sau khi mật khẩu đúng.

### 6. Trả thừa dữ liệu trong bài viết

- **Rủi ro:** serialize trực tiếp từ model database có thể làm lộ email tác giả, IP, cờ kiểm duyệt hoặc dữ liệu nội bộ.
- **Khắc phục:** dùng DTO theo danh sách trường được phép, khớp với schema `Post` và `Author`. Đưa kiểm tra response theo spec vào CI để phát hiện trường ngoài schema.

### 7. Token lộ qua log, cache hoặc URL

- **Rủi ro:** mật khẩu và token có thể lọt vào log ứng dụng, APM, reverse proxy hoặc cache. Bài riêng tư cũng có thể bị proxy dùng chung lưu lại.
- **Khắc phục:** không đưa token vào URL. Che các trường `password`, `refresh_token`, `access_token` và header `Authorization` trong log. Dùng `Cache-Control: no-store` cho phản hồi cấp token và `private` cho bài viết. Bắt buộc HTTPS kèm HSTS.

### 8. Access token còn hiệu lực sau khi bị thu hồi quyền

- **Rủi ro:** JWT được xác minh không cần gọi database, nên sau khi đăng xuất hoặc bị khóa tài khoản, token cũ vẫn dùng được tối đa 15 phút.
- **Khắc phục:** giữ thời gian sống ngắn. Với tài khoản bị khóa do sự cố bảo mật, dùng danh sách chặn theo `jti` hoặc số phiên bản token của người dùng. Phân quyền theo bài (mục 1) luôn đọc dữ liệu mới, nên thay đổi quan hệ theo dõi và chế độ riêng tư có hiệu lực ngay.