# TASK-024 — Kiểm tra thao tác dashboard khi được yêu cầu

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/3 mục
- Cập nhật: 2026-11-18T20:05:42+07:00

## Mô tả và phạm vi

Đề xuất kiểm hiển thị dữ liệu thật ba node trên dashboard, điều khiển AUTO/MANUAL có ACK và trạng thái lỗi. Chưa tự thực hiện; hệ thống TASK-023 đang chạy theo yêu cầu.

## Tham chiếu SRS

SRS8/12–13, FR07–08; không thay thế diễn tập con người đã đề xuất trước đây.

## Tiêu chí hoàn thành và tiến độ

- [ ] Xác minh DOM/render ba node với dữ liệu live.
- [ ] Kiểm lệnh đúng đích và ACK.
- [ ] Ghi bằng chứng và giới hạn.

## Vướng mắc và cách giải quyết

Công cụ CUA hiện không có trình duyệt kết nối; cần kênh kiểm giao diện phù hợp khi được giao.

## Phụ thuộc và điều kiện bắt đầu

Chỉ bắt đầu khi người dùng giao yêu cầu mới; kiểm lại telemetry và tiến trình thực tế, không dùng snapshot cũ làm bằng chứng mới.
