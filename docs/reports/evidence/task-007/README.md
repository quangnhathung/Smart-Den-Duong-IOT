# TASK-007 — Bàn giao code MQTT A3 một node

- Cập nhật: 2026-11-16T12:02:01+07:00
- Trạng thái: Hoàn thành **5/5 đầu ra code/test/hướng dẫn** theo phạm vi người dùng chọn. **Live A3 chưa chạy tại máy này**, không nghiệm thu toàn P3/hệ thống.
- Base: main 0c058bb (PR #2). Không commit/push, Wokwi hoặc thao tác broker.

## Đã thực hiện

MqttProtocol encode/parse JSON v1 bằng ArduinoJson7.4.2 pin sau smoke/build; uptime64, boot_id/seq, telemetry16 trường/current/power/null/fault. CommandProcessor/cacheFIFO32 chống trùng, sai boot/deadline, cùng ID khác nội dung; retry không gia hạn MANUAL.

Connectivity sở hữu MQTT core0; MqttMailbox queue8 lệnh/8 kết quả + latest snapshot dưới critical section ngắn. FirmwareApp/core1 là chủ controller/PWM, xử lý Serial rồi tối đa1 remote command/vòng và trả kết quả sau controller.update. Giữ timer/thuật toán P2, async ECHO, pin map/framework/PubSubClient và diagnostics.

Thêm telemetry2s/event coalescing200ms (≤5/s), command subscribeQoS1, ACKQoS0 không retained, availability ONLINE/OFFLINE retained và LWT/clean session. Session loss flush pending, giữ cache trong cùng boot, AUTO tiếp tục; reconnect subscribe lại và gửi trạng thái mới. Không thêm lịch sử offline hoặc backend.

Công cụ scripts/mqtt-command.py chỉ tạo JSON từ capture telemetry mới≤3s, có fixture sai boot/expired/node/range; không tự publish. [Bộ kiểm tra live Linux/PowerShell](../../../techs/mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này).

## Kiểm tra thực tế lượt cuối

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| python3 scripts/check-firmware.py | PASS exit0, 5 suite C++17 -Wall -Wextra -Werror | [host](host-checks.log) |
| python3 -B -m unittest discover -s test/host -p 'test_*.py' -v | PASS exit0, 11 test =7 RFC2217 +4 generator | [Python](python-tests.log) |
| clang-format --dry-run --Werror trên14 file C++ sửa/thêm | PASS exit0, log rỗng | [formatter](format.log) |
| pio run -e esp32dev | SUCCESS exit0/6.73s, RAM53644/327680 (16.4%), flash933143/1310720 (71.2%) | [build](build.log) |
| python3 scripts/prepare-simulation.py | PASS exit0, freshness/copy/SHA256 BIN/ELF khớp | [hash](prepare.log) |
| Liên kết/cấu hình/bảo toàn | PASS 148 liên kết file, Python/INI/JSON, report/evidence/P2, git diff --check | [kiểm tra tĩnh](static-checks.log) |
| Wokwi/TCP/MQTT broker/LWT thực | Chưa chạy tại máy này | [ma trận A3-01…08](../../../techs/mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này) |

Host protocol dùng ArduinoJson thật; hardware/network/RTOS và clock đều stub. App test chạy FirmwareApp/controller thật, gồm ACK sau target acceptance, dimming tách riêng, retry quá deadline không gia hạn60s, cùng ID khác nội dung, expired/boot/session và thứ tự Serial/MQTT. Network kiểm publish failure giữ ACK, queue flush, seq/boot qua reconnect, rate200ms/period2s và diagnostics.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn chặn bàn giao code. Trong phát triển sửa API ArduinoJson từ isBound sang isUnbound; sửa assertion fixture đếm16 trường telemetry và quan sát snapshot qua tick đúng60s. Những lần kiểm tra cuối ở trên đều PASS; không coi assertion thử nghiệm ban đầu là kết quả cuối. Các lỗi đọc JSON prefix/NUL, tái dùng ID đã bị từ chối và lệnh phiên cũ được xử lý bằng validation/cache/session và test.

Giữ giới hạn: chưa kiểm timing hai core/GPIO/ISR/broker thật, timeout phiên dài lịch sử chưa chứng minh đã hết. PubSubClient callback không có retained flag nên publisher phải gửi command non-retained; không tuyên bố node nhận diện được flag này. Queue đầy log/drop hoặc backpressure, không thêm reason ngoài schema và không áp dụng khi hết chỗ kết quả.

## Bảo toàn hồ sơ

[TASK-006 trước chuyển](task-006-before-task007.md) giữ nguyên byte; các liên kết tương đối bên trong bản sao lưu này có gốc là docs/reports ban đầu. Evidence TASK-005/006 và checklist cũ không sửa. Người dùng xác nhận P2 PASS máy dev kia; không thay nội dung nghiệm thu cũ hoặc chạy lại toàn bộ P2. SHA256 report cũ `08dc05da571ee4166877ca1075ee3bdb8386fd3f2cab7734a434f46cd0b24429` được bảo toàn làm phần đuôi report mới.

Chỉ hoàn thành đầu ra bàn giao được giao; live A3 cần người vận hành theo hướng dẫn, đánh dấu riêng PASS/FAIL/chưa chạy. Backend/A4 là đề xuất kế tiếp, chưa thực hiện.
