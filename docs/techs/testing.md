# Kiểm tra TASK-005 P1/A1

## Tham chiếu SRS

[SRS](../srs.md) mục 4.1, 5.3, 10 P1, 11 A1, 12. Các TC AUTO/MANUAL/fault trong SRS thuộc A2 trở đi, chưa nghiệm thu tại P1. [Firmware](firmware.md), [cách chạy Wokwi](simulation.md), [bằng chứng](../reports/evidence/task-005/README.md).

## Kiểm tra đã thực hiện

- Host: test/host/SensorReaderChecks.cpp biên dịch cùng SensorReader.cpp thật; Arduino.h trong test/host là stub chỉ dùng cho compiler host. Kiểm tra pin/ADC, lịch 20/100/200 ms, xung TRIG, timeout 30000 µs, xóa distance cũ khi timeout, phục hồi 2/100/400 cm và timer qua tràn uint32. Không thêm native environment hoặc dependency vào PlatformIO.
- Build đích esp32dev với platform/package đã pin; formatter, sơ đồ JSON/TOML, dây nguồn/GND và script copy/checksum.
- Các phép kiểm tra trên không chứng minh Wokwi, điện áp thật, khoảng thời gian mạng hoặc GPIO thực hoạt động.

Lệnh tái lập host (tại gốc firmware):

```bash
g++ -std=c++17 -Wall -Wextra -Werror -Itest/host -Isrc src/SensorReader.cpp test/host/SensorReaderChecks.cpp -o /tmp/task005-sensor-checks
/tmp/task005-sensor-checks
```

## Ma trận live cần người vận hành thực hiện

| Mã | Cấu hình và thao tác | Kỳ vọng | Trạng thái ban đầu |
|---|---|---|---|
| P1-01 | Chính, LDR 1/100/10000 lux | ADC 0–4095, giảm khi lux tăng | Chưa chạy |
| P1-02 | Chính, biến trở thấp/giữa/tối đa | ADC tăng theo vị trí, đúng nhãn raw | Chưa chạy |
| P1-03 | Chính, PIR Simulate Motion | LOW → HIGH → LOW; log sự kiện | Chưa chạy |
| P1-04 | Chính, HC-SR04 2/100/400 cm | Sai số ≤ max(2 cm, 5% giá trị đặt) | Chưa chạy |
| P1-05 | Timeout, ECHO bị bỏ dây | distance_valid=0, NA; không treo vòng điều phối | Chưa chạy |
| P1-06 | Chính, quan sát đủ một vòng | PWM 0/25/50/70/100, duty 0/64/128/179/255, ready=1 | Chưa chạy |
| P1-07 | Chính, MQTT nối và đổi cảm biến 3 phút thực | Heartbeat, pong task005-001; không có lỗi mạng mới trong khoảng kiểm tra | Chưa chạy |
| P1-08 | Chính, broker stop/start | Raw Serial/PWM tiếp tục, reconnect và pong mới không reset ESP32 | Chưa chạy |

Ghi cho từng ca: thời gian thực, bản firmware/checksum, cấu hình, thao tác, kỳ vọng, thực tế, PASS/FAIL và đường dẫn log/ảnh. Tốc độ mô phỏng hoặc reconnect có thể làm chu kỳ thực dài hơn lịch; ghi hiện tượng thay vì đổi ngưỡng để làm test đạt. LDR/pot có giới hạn mô phỏng analog; kiểm tra monotonic/range, không giả định giá trị khớp một bảng ADC Arduino Uno.

## Điều kiện hoàn tất

Giữ bốn nhóm nghiệm thu TASK-005: mạch, raw cảm biến, build/live PWM-cảm biến, tài liệu. Sơ đồ kiểm tra tĩnh không được báo như đã xác minh live. Chỉ chốt toàn task sau khi đủ P1-01 đến P1-08 và không có lỗi chặn liên quan. Nếu chờ người vận hành, giữ task Bị chặn, không thêm vào checklist task hoàn thành. Không tự chạy A2/TASK-006.
