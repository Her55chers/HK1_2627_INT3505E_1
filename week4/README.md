# Quyết định thiết kế và các đánh đổi trong dự án

## 1. Chia nhỏ spec thành nhiều file và quản lý tham chiếu `$ref` chéo

**Bối cảnh và thách thức**

Năm thành viên cùng làm việc song song trên một bộ đặc tả API. Nếu dồn tất cả vào một file `openapi.yaml`, nhóm sẽ thường xuyên gặp xung đột khi merge trên Git. Vì vậy nhóm tách spec thành cấu trúc nhiều tầng: file gốc `openAPI.yaml`, các file endpoint trong `paths/*.yaml`, và các thành phần dùng chung trong `components/schemas.yaml` và `responses.yaml`.

Cách tách này giải quyết được vấn đề cộng tác, nhưng đặt ra bài toán về khả năng tương thích của các công cụ phân giải tham chiếu (resolver):

* Theo chuẩn OpenAPI 3.0.3, đường dẫn tương đối giữa các file con (ví dụ từ `paths/books.yaml` trỏ sang `../components/schemas.yaml`) rất dễ bị sai khi nạp qua các công cụ khác nhau như Swagger UI, Redocly, Prism Mock Server hay Swagger Editor.
* Ở file gốc `openAPI.yaml`, nhóm còn chọn cách đưa toàn bộ `schemas` vào bằng một tham chiếu duy nhất: `$ref: "./components/schemas.yaml"`, buộc parser phải dereference đầy đủ theo JSON Pointer, nếu không các schema con sẽ không được phân giải.

**Giá trị mang lại**

Ranh giới trách nhiệm rõ ràng: mỗi thành viên phụ trách một module, có thể phát triển và kiểm thử độc lập mà không ảnh hưởng đến người khác.

## 2. Tách DTO cho request và response, chuẩn hóa lỗi và phân trang dùng chung

**Bối cảnh và thách thức**

Với các thực thể chính (`Book`, `Author`, `BorrowRecord`), nhóm phải chọn giữa việc dùng chung một schema hay tách thành các DTO chuyên biệt. Mỗi thao tác có yêu cầu khác nhau:

* Khi tạo mới (`POST`), client không được gửi `id`, `created_at`, `updated_at`.
* Khi cập nhật (`PUT`/`PATCH`), một số trường là tùy chọn hoặc chỉ được sửa một phần (ví dụ trạng thái của phiếu mượn).
* Khi trả về, phản hồi cần đủ các trường kiểm toán (audit) và các quan hệ liên kết, chẳng hạn thông tin tác giả hoặc sách đi kèm phiếu mượn.

Nhóm chọn tách rõ ràng: `Book` cho dữ liệu đầu ra, `BookCreateInput` và `BookUpdateInput` cho dữ liệu đầu vào, `BookListResponse` để bọc danh sách cùng `PaginationMeta`.

Song song đó, nhóm đặt ra một hợp đồng chung về bảo mật và xử lý lỗi:

* `BearerAuth` được áp dụng mặc định ở cấp gốc, riêng các endpoint xác thực tắt đi bằng `security: []`.
* Mọi API đều phải trả lỗi theo cùng một định dạng `ErrorResponse` gồm `code`, `message`, `timestamp` và `details`.

**Giá trị mang lại**

Hệ thống nhất quán dù do năm người khác nhau viết.