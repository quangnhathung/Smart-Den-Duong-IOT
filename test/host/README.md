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


## TASK-007/A3

Sau `pio pkg install`, script check-firmware.py tìm header ArduinoJson7.4.2 ở .pio/libdeps/esp32dev/ArduinoJson/src. Có thêm suite MqttProtocolChecks (parse/serialize/cache32/mailbox8); app/network suite mở rộng cho lệnh MQTT/ACK và reconnect/telemetry/LWT stub. Tổng5 suite. Chạy thêm `python -B test/host/test_mqtt_command.py` (4 unittest generator), giữ7 test RFC2217. Không cần broker/giấy phép Wokwi cho host checks; không cài dependency tự động từ script kiểm tra.

## TASK-011: ba định danh và coalescing cảm biến

Runner chạy protocol/app/MQTT cho chỉ số 1/2/3, controller/sensors một lượt; tổng 11 lượt và hai ca compile-fail chỉ số 0/4. Các fixture chọn đúng node đang biên dịch, sai node/topic được từ chối, stub kiểm client ID/subscription/LWT riêng. Mailbox kiểm cảm biến raw kích gửi sớm, bỏ qua analogSequence và invalid distance cùng biểu diễn null; giới hạn thử publish 200ms và định kỳ 2s giữ nguyên. Các checks này không thay thế Wokwi hoặc đo clock thực.

Unittest Python kiểm generator ba node, prepare artifact đúng environment/hash/freshness và ba diagram/cổng Serial/cap CPU; tổng 20 test cùng hồi quy Serial cũ. Test prepare dùng dummy artifact có nhãn, không gọi đó là firmware build thật.
