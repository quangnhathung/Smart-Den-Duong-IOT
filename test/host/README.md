# Host checks firmware

Từ gốc repository trên Windows CMD:

```cmd
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" scripts\check-firmware.py
```

Script dùng g++ trong PATH, C++17 với -Wall -Wextra -Werror; build executable trong thư mục tạm rồi dọn khi kết thúc. Không cài tool/dependency, không gọi Docker/PlatformIO/Wokwi.

- LightingControllerChecks: filter5 mẫu, hysteresis/dwell, AUTO/hold/motion/invalid, MANUAL/60s/offline, dimming, fault và rollover.
- SensorReaderChecks: biên dịch SensorReader thật với stub cạnh GPIO19/micros, kiểm tra TRIG12us tổng, timeout30ms, cạnh muộn/không đủ cạnh, invalidation/recovery2/100/400cm, timer tràn. pulseIn stub assert nếu bị gọi.
- FirmwareAppChecks: code app thật, stub sensor/connectivity/PWM/Serial; một chủ PWM, không cycle diagnostic, parser/overflow/NUL, AUTO/MANUAL và mất mạng nhanh giữa hai poll.
- ConnectivityChecks: compile implementation Connectivity.cpp trong cùng TU để điều khiển networkStep với WiFi/PubSubClient/RTOS giả. Kiểm tra binary ping/pong, giới hạn64byte, heartbeat/topic/retain/QoS, backoff và resubscribe. Không chạy TCP/broker thật.

Arduino.h và runtime/ chỉ dùng host, không phải include firmware. Chưa chứng minh ISR điện thực, RTOS scheduling, PWM vật lý hoặc Wokwi live. Các test/evidence TASK-005 cũ giữ lịch sử; SensorReaderChecks hiện kiểm tra triển khai async P2, không chạy lại nghiệm thu P1.
