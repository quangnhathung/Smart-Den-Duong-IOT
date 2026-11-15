# TASK-005 — Mạch và đọc cảm biến một node P1/A1

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 mục nghiệm thu
- Cập nhật: 2026-11-15T19:15:52+07:00

## Mô tả và phạm vi

Đề xuất dựng một node Wokwi đầy đủ cảm biến, đọc/in raw Serial và giữ ca kiểm tra PWM. Giữ source dùng chung và entry main, không di chuyển workspace. Chưa triển khai AUTO/MANUAL, phân loại người/xe, fault, telemetry/ACK nghiệp vụ hoặc nhiều node.

## Tham chiếu SRS

[SRS](../srs.md) mục 4.1, 4.4, 5.1, 10.2 P1, 11 A1, 12; [kiến trúc](../techs/architecture.md), [MQTT đã chốt](../techs/mqtt.md).

## Tiêu chí hoàn thành và tiến độ

- [ ] Mạch đủ LDR34, PIR27, HC-SR04 TRIG18/ECHO19, biến trở35, LED26 với điện trở 220 Ω; đúng nguồn/GND.
- [ ] Đọc raw ADC12 bit, PIR và distance có timeout; Serial rõ đơn vị, kiểm chứng chiều ánh sáng/ADC và tín hiệu từng linh kiện.
- [ ] Build esp32dev với package đã pin; xác nhận PWM 0/25/50/70/100 và cảm biến trên Wokwi có log/ảnh.
- [ ] Cập nhật hardware/simulation/testing hoặc setup phù hợp; hồ sơ đủ kết quả thực tế và giới hạn giả lập.

## Vướng mắc và cách giải quyết

Chưa bắt đầu nên chưa có lỗi triển khai được xác nhận. Giữ diagnostics P0 tách khỏi hợp đồng nghiệp vụ, không coi raw sensor là telemetry v1. Không bỏ package pin để xử lý lỗi.

## Phụ thuộc và điều kiện bắt đầu

TASK-004 đã hoàn thành A0. Cần người dùng giao TASK-005; vận hành Wokwi theo phương thức đã thống nhất. Không tự thực hiện đề xuất này.
