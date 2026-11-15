# TASK-005 — Tiếp tục nghiệm thu live P1/A1

- Trạng thái: Chưa bắt đầu
- Tiến độ: 2/4 nhóm nghiệm thu TASK-005
- Cập nhật: 2026-11-15T19:29:24+07:00

## Mô tả và phạm vi

Code/mạch đã chuẩn bị, chưa chốt task vì thiếu Wokwi live. Người vận hành chạy các ca chính và timeout, giữ một ESP32, lưu log/ảnh trong evidence/task-005. Không bắt đầu P2 trước nghiệm thu cảm biến.

## Tham chiếu SRS

[SRS](../srs.md) 4.1/4.4, 5.3, 10 P1, 11 A1, 12; [cách chạy](../techs/simulation.md), [ma trận](../techs/testing.md).

## Tiêu chí hoàn thành và tiến độ

- [x] Mạch kiểm tra tĩnh và tài liệu/hồ sơ đã có.
- [ ] P1-01 đến P1-05: LDR/pot/PIR/distance và timeout có Serial/ảnh thực.
- [ ] P1-06 đến P1-08: năm PWM, heartbeat/pong và broker offline/recovery có bằng chứng, không reset node trong ca phục hồi.
- [ ] Đối chiếu live rồi chốt TASK-005 4/4, thêm checklist hoàn thành.

## Vướng mắc và cách giải quyết

Không tự đánh dấu live PASS từ host test/build. Nếu còn lỗi, giữ cùng TASK-005 và log thật; sửa trong phạm vi được giao. Theo dõi giới hạn timeout P0, không tự nâng toolchain.

## Phụ thuộc và điều kiện bắt đầu

Firmware mới đã copy; cần Docker/broker và Wokwi license trên máy người dùng. Dừng phiên cũ trước khi mở cấu hình mới. Sau TASK-005 đạt mới đề xuất TASK-006 — thuật toán chiếu sáng P2/A2; chưa thực hiện TASK-006.
