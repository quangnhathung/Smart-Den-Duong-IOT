# TASK-007 — MQTT nghiệp vụ một node P3/A3

- Trạng thái: Hoàn thành
- Tiến độ: 5/5 mục nghiệm thu bàn giao code
- Cập nhật: 2026-11-16T12:02:01+07:00

## Mô tả và phạm vi

Telemetry/command/ACK/availability/LWT/reconnect một node theo SRS6 và mqtt.md. Giữ P2, pin map, source chung và toolchain. Đầu ra được giao: code, host test/build và hướng dẫn live trên máy dev; không tự chạy Wokwi/broker, backend/dashboard hoặc commit/push.

## Tham chiếu SRS

SRS5.7,6,9.1,10P3,11A3,12TC17–22/26; hợp đồng MQTT v1. TC17 chỉ kiểm tra đúng đích một node; TC26 mô phỏng client retry, chưa nghiệm thu backend.

## Tiêu chí hoàn thành và tiến độ

- [x] Telemetry/schema/boot/seq/uptime64/công suất/rate limit đúng hợp đồng.
- [x] Command strict validation/cache32/ACK sau áp dụng, hàng đợi hữu hạn và chống lệnh phiên cũ.
- [x] LWT/availability/reconnect và P2 offline giữ đúng; diagnostics không đổi.
- [x] Host hồi quy/protocol/tích hợp, RFC tests, formatter/build/copy/hash đạt.
- [x] Tài liệu và bộ lệnh live có tiêu chí/evidence; report/checklist/next-task cập nhật.

## Vướng mắc và cách giải quyết

Không có vướng mắc chặn bàn giao. Live A3 chưa chạy tại máy này; chỉ chốt đầu ra code/test/hướng dẫn, không suy thành nghiệm thu live.

## Phụ thuộc và điều kiện bắt đầu

Người dùng giao triển khai kế hoạch TASK-007. Người dùng xác nhận P2 PASS ở máy dev khác; giữ nguyên hồ sơ cũ trong evidence TASK-006 và bản task trước chuyển ở evidence/task-007/task-006-before-task007.md. Không tự nâng trạng thái nghiệm thu P2.

## Kết quả và giới hạn

Năm suite C++,11 unittest Python, formatter/build/copy/hash PASS. [Bằng chứng](evidence/task-007/README.md). Đây là hoàn thành code/test/hướng dẫn theo phạm vi đã chọn, không phải live A3 PASS. Giữ nguyên hồ sơ P2 đã xác nhận tại máy dev kia.
