# TASK-015 — Hướng dẫn cài đặt và vận hành toàn dự án

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu
- Cập nhật: 2026-11-18T15:50:12+07:00

## Mô tả và phạm vi

Người dùng yêu cầu một tài liệu chi tiết, toàn diện về setup, khởi tạo, chạy và thao tác toàn bộ dự án. Tạo Word chỉnh sửa được và bản Markdown đồng nội dung, hướng dẫn Linux/Windows, ba repo, MQTT/Docker, PlatformIO, ba Wokwi, backend/SQLite, dashboard Live Server, API, thực nghiệm, backup/restore và xử lý lỗi. Đối chiếu source thực tế; giữ source sản phẩm, pin map/schema/toolchain và mọi dữ liệu cũ. Không chạy lại chiến dịch TASK-012, không commit/push/cloud.

Đây là yêu cầu mới, dùng TASK-015; TASK-014 đã là mã đề xuất diễn tập con người, chưa triển khai. [TASK-012 hoàn thành trước đó](evidence/task-015/task.md-before.md) được bảo toàn.

## Tham chiếu SRS

SRS mục3–9,12–15, hỗ trợ vận hành và bàn giao; không triển khai tính năng mới hoặc coi thiết kế SRS là bằng chứng chức năng.

## Tiêu chí hoàn thành và tiến độ

- [x] Đối chiếu cấu hình/lệnh/source ba repo, phân biệt chạy mặc định và QA; ghi nguồn và giới hạn kiểm chứng.
- [x] Soạn hướng dẫn đầu-cuối: cài, khởi tạo, khởi động, năm màn hình, demo/API, dữ liệu, thử nghiệm, dừng/khôi phục và lỗi thường gặp.
- [x] Tạo DOCX chỉnh sửa được, kiểm cấu trúc và render/kiểm trực quan mọi trang bằng WPS; giữ Markdown đồng nội dung.
- [x] Kiểm các lệnh đọc/khởi tạo an toàn trên dữ liệu tạm phù hợp, liên kết và bảo toàn source/lịch sử; cập nhật techs/task/report/checklist/đề xuất tiếp theo.

## Vướng mắc và cách giải quyết

Đã giải quyết: lệnh đối chiếu ban đầu gọi Python hệ thống thiếu lxml; chuyển đúng runtime Office QA riêng đã có, không cài vào venv sản phẩm. Native WPS đã render/kiểm đủ34 trang; schema,695 dòng nội dung và heading/table/ảnh/numbering đạt. PDF không bắt buộc; người dùng tự xuất WPS. Không xác nhận đã cài/chạy toàn stack trên Windows hoặc máy mới nếu chưa làm thực tế.

## Phụ thuộc và điều kiện bắt đầu

Đã được người dùng giao. Đọc source/docs tại ba repo cùng cấp, runtime DOCX và WPS có sẵn. Chỉ thao tác tài liệu, công cụ xuất và SQLite tạm; không tự khởi động mô phỏng hoặc thay DB người dùng.

## Kết quả bàn giao

Word output/task-015/Huong-dan-cai-dat-va-van-hanh-toan-du-an-Nhom7-v01.docx và Markdown đồng nội dung docs/project-guide.md. [QA từng trang](evidence/task-015/document-qa.json), [kiểm lệnh/dữ liệu tạm](evidence/task-015/command-checks.json). Không chạy lại firmware/build/live hoặc xác nhận Windows toàn stack; các kết quả TASK-011/012 được dẫn nguồn riêng. Đề xuất diễn tập kế tiếp TASK-016, chưa thực hiện; đề xuất TASK-014 cũ được bảo toàn trong hồ sơ.
