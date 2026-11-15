# TASK-003 — Dùng chung convention cho Codex, Claude Code và OpenCode

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục
- Cập nhật: 2026-11-15T17:41:58+07:00

## Mô tả và phạm vi

Bảo đảm ba công cụ có entry point nạp convention chung từ AGENTS.md tại gốc firmware. Thêm import cho Claude Code, ghi cách khởi động và kiểm tra, không thay cấu hình global hoặc chức năng firmware.

## Tham chiếu SRS

[SRS](../srs.md), mục 11 và 16: hướng dẫn agent và quản lý thay đổi. Task hỗ trợ phát triển, không nghiệm thu FR. TASK-002 đã được dành cho đề xuất P0 trong next-task.md nên yêu cầu mới này dùng TASK-003.

## Tiêu chí hoàn thành và tiến độ

- [x] Đối chiếu cơ chế nạp hướng dẫn chính thức của ba công cụ; thiết lập entry point tương ứng.
- [x] Cập nhật tài liệu development với cách dùng, kiểm tra và giới hạn xác minh.
- [x] Kiểm tra import/liên kết, bảo toàn lịch sử và dữ liệu; hoàn thiện hồ sơ task.

Bằng chứng: [báo cáo TASK-003](report.md). Kiểm tra cấu trúc/import đạt; chưa xác minh context bằng phiên model mới.

## Vướng mắc và cách giải quyết

Claude CLI không có trong PATH của phiên. OpenCode cần ghi log ngoài vùng được phép; dùng thư mục dữ liệu/cache/state tạm trong /tmp để đọc phiên bản. Không dùng phiên gọi model để kiểm thử trong task này; ghi rõ giới hạn xác minh ở báo cáo.

## Phụ thuộc và điều kiện bắt đầu

Người dùng đã yêu cầu đồng bộ convention. Giữ đề xuất TASK-002 kiểm chứng P0, không tự triển khai.
