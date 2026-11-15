# TASK-005 — Mạch và đọc cảm biến một node P1/A1

- Trạng thái: Bị chặn
- Tiến độ: 2/4 nhóm nghiệm thu (chờ Wokwi live)
- Cập nhật: 2026-11-15T19:29:24+07:00

## Mô tả và phạm vi

Đã bổ sung mạch đầy đủ, SensorReader đọc raw, banner/Serial P1, bản sao ECHO timeout, kiểm thử host và artifact mới. Giữ MQTT/PWM diagnostics P0 và package pin. Chưa có AUTO/MANUAL, phân loại, fault, telemetry nghiệp vụ hoặc nhiều node. Chưa chạy Docker/Wokwi live P1.

## Tham chiếu SRS

[SRS](../srs.md) 4.1/4.4, 5.1/5.3, 10 P1, 11 A1, 12; [kiến trúc](../techs/architecture.md), [hợp đồng MQTT](../techs/mqtt.md).

## Tiêu chí hoàn thành và tiến độ

- [x] Sơ đồ đủ LDR34, PIR27, TRIG18/ECHO19, biến trở35, LED26/220 Ω; nguồn/GND và bản timeout đạt kiểm tra tĩnh, chưa xác minh điện/tín hiệu live.
- [ ] Raw ADC12 bit, PIR/distance và Serial: code/host checks đạt; còn chờ kiểm chứng chiều ADC và từng cảm biến trong Wokwi.
- [ ] Build esp32dev đã PASS, artifact mới đã chuẩn bị; còn chờ live đủ năm PWM/cảm biến và hồi quy MQTT.
- [x] Đã cập nhật tài liệu hardware/firmware/simulation/testing, hồ sơ và giới hạn đúng kết quả thật.

## Vướng mắc và cách giải quyết

Chờ người vận hành chạy P1-01 đến P1-08 theo [testing](../techs/testing.md); không dùng log P0 làm bằng chứng P1. Script copy từng từ chối artifact cũ sau sửa comment vì SCons không relink; đã clean build thật và copy lại đạt, giữ log từ chối. Không sửa timestamp hoặc bỏ kiểm tra freshness. Timeout phiên dài P0 vẫn là giới hạn cần theo dõi, chưa kết luận nguyên nhân.

## Phụ thuộc và điều kiện bắt đầu

Người dùng đã giao triển khai TASK-005. [Simulation](../techs/simulation.md) hướng dẫn chạy cấu hình chính/timeout và lưu log/ảnh. Agent chưa tự chạy Docker/Wokwi theo lựa chọn vận hành trước đó. Không tự triển khai TASK-006.

## Checklist triển khai

- [x] Module riêng, timer 20/100/200 ms, timeout 30 ms, invalid distance/NA, PIR edge log, CRLF.
- [x] Giữ PWM 0/25/50/70/100 và heartbeat/ping-pong, không điều khiển LED theo cảm biến.
- [x] Host checks, formatter, kiểm tra diagram, build và copy artifact.
- [x] Tài liệu và báo cáo có bằng chứng, lịch sử được giữ.
- [ ] Nghiệm thu Wokwi live và chốt hai nhóm còn lại.
