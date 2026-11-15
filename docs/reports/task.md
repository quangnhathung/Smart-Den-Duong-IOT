# TASK-005 — Mạch và đọc cảm biến một node P1/A1

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu
- Cập nhật: 2026-11-16T02:56:10+07:00

## Mô tả và phạm vi

Một ESP32 esp32dev/Arduino, SensorReader raw LDR/PIR/HC-SR04/biến trở, năm mức PWM và MQTT diagnostics. Build/copy/hash đã PASS; Wokwi chính và timeout đã nghiệm thu P1-01 đến P1-08. Không triển khai AUTO/MANUAL, telemetry nghiệp vụ, backend hoặc nhiều node.

## Tham chiếu SRS

SRS 4.1/4.4, 5.1/5.3, 10 P1, 11 A1, 12. [Biên bản nghiệm thu cuối](evidence/task-005/windows-live-20261116-003644/acceptance-final.md).

## Tiêu chí hoàn thành và tiến độ

- [x] Mạch/pin map chính và timeout, kiểm tra tĩnh và chạy thực trong Wokwi.
- [x] Raw ADC/PIR/distance và Serial, P1-01/02/03/04/05 đạt; nhãn giá trị đặt do người vận hành xác nhận.
- [x] Build esp32dev, artifact/checksum, năm PWM, MQTT 184 giây thực và offline/recovery P1-06/07/08 đạt theo bộ bằng chứng.
- [x] Tài liệu kỹ thuật, report/checklist/next-task và hồ sơ bằng chứng cập nhật; lịch sử được giữ.

## Vướng mắc và cách giải quyết

Không còn vướng mắc chặn TASK-005. P1-08 được chốt bằng Serial offline bổ sung lượt 02:50 (mốc stop/start do người dùng xác nhận) cùng MQTT/broker/pong lượt 02:29; không gán thành một capture duy nhất. Các nhận định PARTIAL trước đây giữ trong evidence theo lịch sử. Giữ giới hạn metadata/ảnh, polling và timeout phiên dài đã ghi trong biên bản; không tuyên bố đã sửa nguyên nhân timeout dài hạn.

## Phụ thuộc và điều kiện bắt đầu

TASK-005 được giữ tại đây sau hoàn thành. Đủ điều kiện giao TASK-006/P2-A2 theo next-task.md; chưa triển khai. Không build/test lại hoặc đụng broker trong lượt chốt hồ sơ.
