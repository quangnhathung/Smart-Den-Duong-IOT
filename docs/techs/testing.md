# Kiểm tra dự án — firmware, backend và dashboard

## TASK-009 P5/A5 — dashboard và API read bổ sung

Tại DoAn/dashboard: `node --test tests/*.test.mjs` →16 PASS (Node24.17). Tại DoAn/backend: `.venv/bin/python scripts/check.py` →Ruff check/format,68 Pytest PASS/1 deprecation warning cũ. OpenAPI11 paths/12 thao tác. Không đổi firmware/toolchain nên không build lại C++/Wokwi trong task UI.

Playwright CLI với Live Server engine2.2.0 của VS Code extension5.7.10:18 kiểm tra luồng chính +8 kiểm tra bổ sung PASS; viewport375/768/1024/1440, chart/bảng/keyboard, draft, lệnh, phiên/reload/stop/CSV, mất API/recovery/no-retry, reduced motion và overflow mobile. Pha REJECTED/TIMEOUT dùng phản hồi API mock, lỗi mạng chủ động tạo console resource errors dự kiến; pha cuối trên repo bàn giao có0 console error/0 uncaught JS exception. API/SQLite thật, transport MQTT và dữ liệu giả có nhãn, không mở broker. [Bằng chứng và lệnh tái lập](../reports/evidence/task-009/README.md), [dashboard](dashboard.md).

Chưa chạy UI với broker/ESP32 thật, VS Code Go Live thao tác tay/Windows, đo latency10 lượt, ba node30phút hay EX-series. Đó là kiểm tra tích hợp tiếp theo; không ghi PASS từ fixture.

## TASK-008 P4/A4 — backend

Chạy `.venv/bin/python scripts/check.py` từ repo DoAn/backend (PowerShell dùng .venv/Scripts/python.exe).66 test collector/command/API/energy/transport, Ruff check/format PASS trên Linux; [log và giới hạn](../reports/evidence/task-008/README.md), [cách chạy](backend.md). Pytest dùng DB tạm, fake MQTT/clock, không mở broker. Không cần build firmware vì TASK-008 không sửa C++/PlatformIO. Lệnh Windows và live được bàn giao nhưng chưa chạy tại máy này.

## TASK-007 P3/A3 — bàn giao code/test/hướng dẫn

SRS6,5.7,9.1 và TC17–22/26 trong phạm vi một node/client giả. Chạy từ gốc firmware:

```bash
# Một lần sau checkout để cài đúng dependency đã pin; không nâng toolchain.
~/.platformio/penv/bin/pio pkg install
python3 scripts/check-firmware.py
python3 -B test/host/test_wokwi_serial.py
python3 -B test/host/test_mqtt_command.py
~/.platformio/penv/bin/pio run -e esp32dev
python3 scripts/prepare-simulation.py
```

check-firmware.py dùng g++/C++17 -Wall -Wextra -Werror, link ArduinoJson7.4.2 thật từ .pio/libdeps; không mock JSON. Năm suite: protocol/controller/sensors/app/mqtt. Protocol kiểm schema/type/range/UUID/boot/uint64/trailing/invalid, telemetry16 trường/current-power/null/fault, cacheFIFO32/deadline/dedup/rejected ID và mailbox queue8/backpressure. App chạy code thật tới controller/PWM stub, xác minh ACK sau nhận target, duplicate không gia hạn60s, sai boot/expired/session và Serial trước MQTT. Network kiểm CONNECT will/clean session/QoS/retain/subscriptions, telemetry200ms/2s/seq/reconnect, ACK publish fail và session flush; GPIO/network/RTOS vẫn là stub.

Bảy unittest RFC2217 giữ nguyên; bốn unittest generator kiểm input/deadline64/UUID/fixture sai và tuổi file telemetry3s. scripts/mqtt-command.py chỉ tạo JSON, không gửi dữ liệu hoặc kiểm chứng broker.

Bằng chứng mới lưu ở [TASK-007](../reports/evidence/task-007/README.md). [Ma trận/lệnh live A3](mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này) chưa chạy tại máy này. Không suy host/build thành LWT thực, timing hai core hoặc ba node30phút PASS. Các đoạn TASK-006 bên dưới là lịch sử P2 trước khi thêm A3.

## TASK-006 P2/A2

Chạy `python scripts/check-firmware.py` bằng Python PlatformIO: bốn suite controller/sensors/app/mqtt; [cách chạy Windows và giới hạn stub](../../test/host/README.md). Code/host/build được kiểm tra trong [validation.log](../reports/evidence/task-006/validation.log); không chạy lại Wokwi TASK-005 hoặc thao tác broker.

| Nhóm | Ca tự động | Trạng thái |
|---|---|---|
| AUTO/state | TC-01–11: 5 mẫu mới, boundary1200/2600, hysteresis1100/1300/2500/2700, dwell1s, motion100cm/invalid/PIR gate, hold5s/max, DAY cancel | Host PASS |
| MANUAL | TC-12/13/27: range0–100, DAY priority, refresh60s, offline/reconnect và fast-loss giữa poll, AUTO không dùng hold cũ | Host PASS |
| Dimming/fault | TC-14/15/16/28: 2điểm/20ms, target lẻ, không burst, stable1s/detect2s/recover3s, biên ADC409/410/818/819, invalid, mode/off không xóa, PWM không bị cắt | Host PASS |
| Runtime/regression | ISR ECHO/timeout30ms/late edges/micros wrap, sample timers; Serial parser/overflow/NUL; MQTT binary pong/64byte/topic/retain/backoff/resubscribe | Host PASS |
| Firmware đích | esp32dev, package pin, formatter | Xem log thực tế |
| Wokwi P2 | [Bằng chứng và ma trận hiện tại](../reports/evidence/task-006/acceptance-review.md) | MANUAL80/timeout60s có file PASS; các bài live khác người dùng xác nhận, hồ sơ file PENDING |

TC-17–20/26 JSON command/ACK, đa node/backend/dashboard và stability30phút thuộc A3 trở đi, chưa được coi PASS. Test MQTT hiện dùng stub, không thay kiểm tra broker/live. Một test tích hợp đã bắt lỗi reconnect quá nhanh che mất sự kiện offline; code có atomic loss-count và test hồi quy. Những assertion thử nghiệm thất bại trong quá trình phát triển đã được sửa rồi chạy lại; log cuối ghi kết quả thực, không tuyên bố không từng có lỗi.

## TASK-005 P1/A1 — lịch sử nghiệm thu giữ nguyên

## Kết quả nghiệm thu cuối

TASK-005 đã hoàn thành 4/4 nhóm nghiệm thu; P1-01 đến P1-08 PASS theo [biên bản và ma trận evidence](../reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Các trạng thái “Chưa chạy” trong ma trận bên dưới là trạng thái ban đầu khi lập kế hoạch, không phải kết quả cuối. P1-08 dùng bộ bằng chứng bổ sung của hai lượt recovery, ghi rõ nguồn thời gian; không tuyên bố một capture đồng bộ duy nhất. Không nghiệm thu AUTO/MANUAL hoặc mạng nghiệp vụ ở P1.

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
