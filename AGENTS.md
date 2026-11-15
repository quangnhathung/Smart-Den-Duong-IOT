# Convention cho agent — firmware đèn đường thông minh

Áp dụng cho toàn bộ thư mục `firmware/`. Đọc [quy trình và mẫu tài liệu](docs/techs/development.md) trước khi thực hiện task.

Đây là nguồn convention chung cho Codex, Claude Code và OpenCode. Codex/OpenCode nạp tệp này trực tiếp; [CLAUDE.md](CLAUDE.md) import tệp này cho Claude Code. Sửa quy tắc chung tại đây và tài liệu development, không sao chép thành bộ quy tắc riêng cho từng công cụ. Khởi động công cụ tại gốc `firmware/` để nạp đúng hướng dẫn dự án.

## Bắt đầu task

1. Luôn đọc [SRS](docs/srs.md), [task hiện tại](docs/reports/task.md), [task tiếp theo](docs/reports/next-task.md) và tài liệu trong `docs/techs/` liên quan đến yêu cầu. Không coi nội dung dự kiến trong SRS là chức năng đã triển khai.
2. Mỗi yêu cầu có đầu ra riêng là một task. Tiếp tục cùng mã nếu đang làm tiếp task cũ; task mới dùng mã `TASK-NNN` tăng tuần tự theo lịch sử.
3. Xác định phạm vi, mục SRS, tiêu chí hoàn thành và checklist; cập nhật `task.md` trước khi sửa. Nếu chỉ được lập kế hoạch, không ghi tệp; trình bày các cập nhật dự kiến.
4. Giữ stack, pin map, schema và phạm vi đã chốt trong SRS. Yêu cầu mới rõ ràng của người dùng được ưu tiên; nếu còn mâu thuẫn chưa giải quyết, ghi bằng chứng, tác động và phương án, tiếp tục phần độc lập. Không tự sửa SRS để hợp thức hóa triển khai lệch yêu cầu.

## Triển khai và tài liệu

- Giữ PlatformIO, board `esp32dev`, framework Arduino và entry point `src/main.cpp` với `setup()`/`loop()`. Không nhân bản source cho từng node, không di chuyển dự án để phù hợp cấu trúc dự kiến trong SRS.
- Tuân thủ [quy tắc Arduino của dự án](docs/techs/development.md#arduino-và-c): thụt 2 dấu cách, hàm/biến `camelCase`, kiểu/module `PascalCase`, hằng `UPPER_SNAKE_CASE`; giữ nguyên tên trong hợp đồng MQTT/JSON. Dùng `.clang-format` và `.editorconfig` ở gốc dự án.
- Không chờ kết nối vô hạn hoặc dùng `delay()` dài trong vòng điều khiển. Kiểm tra timeout, tràn bộ đếm thời gian và kết quả thao tác phần cứng/mạng.
- Cập nhật `docs/techs/<danh-muc>.md` tương ứng ngay trong task: mô tả cách triển khai thực tế, cấu hình, kiểm tra, giới hạn và mục SRS liên quan. Tái sử dụng tài liệu cùng chủ đề; chỉ tạo danh mục khi có nội dung thực tế.
- Chỉ sửa phần liên quan; không tự nâng toolchain, thêm tính năng, chạy gói tiếp theo, deploy cloud hay mua/đăng ký dịch vụ ngoài yêu cầu.

## Kiểm tra và kết thúc task

1. Chạy kiểm tra phù hợp thay đổi. Phân biệt kiểm tra logic, build firmware, Wokwi và tích hợp; build đạt không chứng minh mô phỏng đạt. Không ghi PASS khi chưa chạy; ghi rõ FAIL/chưa chạy, nguyên nhân và bước xử lý.
2. Cập nhật tiến độ và trạng thái trong `docs/reports/task.md`, kể cả khi bị chặn. Task hoàn thành vẫn ở đây đến khi bắt đầu task mới.
3. Thêm một báo cáo mới **lên đầu** `docs/reports/report.md`, giữ nguyên mọi byte nội dung cũ bên dưới. Bắt buộc có: đã làm gì, kiểm tra/kết quả, vướng mắc và cách giải quyết. Không có vướng mắc thì ghi “Không có”.
4. Cập nhật `docs/reports/checklists.md` với các task đã hoàn thành và bằng chứng. Không xóa lịch sử, không đánh dấu hoàn thành công việc còn thiếu kiểm chứng theo tiêu chí task.
5. Cập nhật `docs/reports/next-task.md` với đề xuất tiếp theo, phụ thuộc và điều kiện bắt đầu; không tự thực hiện đề xuất đó.
6. Trả kết quả ngắn gọn: thay đổi, kiểm tra, giới hạn và vướng mắc còn lại. Bảo toàn công việc đã có của người dùng.
