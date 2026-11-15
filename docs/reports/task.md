# TASK-004 — Hoàn thiện kiến trúc và giao thức A0

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu
- Cập nhật: 2026-11-15T19:15:52+07:00

## Mô tả và phạm vi

Đã chốt kiến trúc, hợp đồng MQTT v1, quy tắc bàn giao và kiểm tra convention theo SRS. Tài liệu phân biệt P0 đã triển khai và phần thiết kế chưa chạy. Không thêm cảm biến, logic nghiệp vụ, backend/dashboard hoặc nhiều node.

## Tham chiếu SRS

[SRS](../srs.md) mục 3–7, 10–12, 16; A0. P0 đóng ở [TASK-002](evidence/task-002/accepted-task.md).

## Tiêu chí hoàn thành và tiến độ

- [x] [Kiến trúc](../techs/architecture.md) giữ workspace, pin map và trách nhiệm từng thành phần; có điểm bàn giao.
- [x] [MQTT v1](../techs/mqtt.md) có topic/QoS/retain, kiểu trường, deadline_uptime_ms, result/reason, status, retry/cache/LWT và tám ví dụ.
- [x] [Kiểm tra convention](evidence/task-004/convention-checks.md) PASS; hồ sơ và lịch sử được bảo toàn.

## Vướng mắc và cách giải quyết

Không có vướng mắc A0 còn chặn. Lần build pin đầu lỗi registry, retry package cục bộ đã PASS; cả hai log được giữ. Giới hạn timeout phiên dài P0 được ghi riêng trong biên bản và tiếp tục theo dõi ở A3, chưa tuyên bố đã giải quyết nguyên nhân. Chưa có kiểm thử runtime MQTT nghiệp vụ vì chưa triển khai.

## Phụ thuộc và điều kiện bắt đầu

TASK-002 đạt smoke P0; người dùng đã giao TASK-004. TASK-005 chỉ là đề xuất, không tự triển khai.
