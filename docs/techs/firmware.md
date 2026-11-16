# Firmware P1/A1 — SensorReader và chẩn đoán

## Tham chiếu SRS

[SRS](../srs.md) mục 4.1, 5.1/5.3, 10–12; [pin map](hardware.md), [MQTT v1 chưa triển khai](mqtt.md). Hiện có đọc raw và diagnostics, chưa có thuật toán chiếu sáng AUTO/MANUAL.

## Module và giao diện

SensorReader.h/.cpp cung cấp:

- setupSensors(): đặt chân ADC/PIR/TRIG/ECHO, ADC12 bit, attenuation ADC_11db trên GPIO34/35; đọc analog/PIR lần đầu, đặt distanceValid=false.
- updateSensors(uint32_t nowMs): lấy mẫu theo lịch; đo siêu âm ngay ở lần update đầu, sau đó mỗi 200 ms.
- getSensorSnapshot(): const reference dữ liệu mới nhất. SensorSnapshot gồm uint16_t ldrAdc/currentAdc, bool pirMotion, float distanceCm và bool distanceValid. distanceCm chỉ có nghĩa khi distanceValid=true.

Module không chứa Wi-Fi, MQTT hoặc Serial, không lọc ADC, không chuyển sang lux/mA/W và không phân loại người/xe. EnvironmentSmokeTest gọi setup sau Serial.begin, update mỗi vòng và in kết quả. main.cpp giữ setup()/loop() như trước.

| Việc | Lịch |
|---|---:|
| PIR | 20 ms |
| LDR/biến trở | 100 ms |
| HC-SR04 | 200 ms |
| Serial tổng hợp | 1 giây |
| PWM diagnostics | Đổi mức mỗi 2 giây |
| Heartbeat MQTT | 2 giây |

Dùng phép trừ unsigned chịu tràn millis. TRIG LOW 2 µs, HIGH 10 µs rồi LOW; pulseIn(ECHO,HIGH,30000), khoảng cách duration/58.0 cm. Timeout trả distanceValid=false, xóa giá trị cũ về 0 nội bộ, Serial hiển thị NA. Không coi 0 là khoảng cách hợp lệ.

PIR đổi mức được log riêng ngay khi update phát hiện. Dòng tổng hợp: SENSORS uptime_ms=... ldr_adc=... pir=0/1 current_adc=... distance_valid=0/1 distance_cm=.../NA. Banner P1/A1 sensor diagnostics giúp phân biệt firmware mới. Các printf của ứng dụng dùng CRLF; log boot/ESP-IDF do framework quyết định cách xuống dòng.

## Hồi quy P0 và giới hạn

Giữ nghỉ 10 ms, LEDC 5 kHz/8 bit, vòng PWM 0/25/50/70/100%, MQTT host.wokwi.internal:1883, keepalive 15 giây, buffer 2048, ping/pong tối đa 64 byte, heartbeat và retry P0. Dữ liệu cảm biến chưa được gửi vào heartbeat/telemetry. LED không phản ứng theo cảm biến trong P1.

Lịch lấy mẫu là mục tiêu trong một vòng điều phối: pulseIn có thể chặn đến 30 ms, MQTT connect có timeout P0 1 giây mỗi bước. Không cam kết thời gian thực cứng 20 ms; xung PIR ngắn có thể bị bỏ lỡ trong khoảng mạng đang chặn. Kiểm tra PIR ở kết nối ổn định; kiểm tra offline xác nhận vòng xử lý tiếp tục, không khẳng định bắt mọi xung. Timer/dimming nghiệp vụ sẽ được đánh giá ở A2/A3.

Build, host checks và Wokwi live P1 đã nghiệm thu; xem [biên bản TASK-005](../reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Raw/PWM tiếp tục trong đoạn broker offline, retry/reconnect và heartbeat/pong có bằng chứng bổ sung. Không dùng bằng chứng P0 làm kết quả cảm biến hoặc suy thành timing cứng/mạng nghiệp vụ đạt.
