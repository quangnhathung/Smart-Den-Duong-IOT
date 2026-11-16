# Hợp đồng MQTT v1 — chốt A0

TASK-006/A2 giữ nguyên diagnostics ping/pong/heartbeat, chuyển network sang FreeRTOS task riêng và dùng atomic trạng thái/mất kết nối để điều khiển fallback. Không subscribe command v1 hoặc phát telemetry/ACK trong A2. `AUTO` / `MANUAL <0..100>` trên Serial là giao diện thử cục bộ, không phải MQTT schema; command/ACK/deadline/cache thuộc A3.

## Tham chiếu và trạng thái

[SRS](../srs.md) mục 5–7, 11–12, 16; [kiến trúc](architecture.md); [diagnostics P0 đang chạy](setup.md).

Đây là hợp đồng cho A3/A4 và các gói sau. Firmware hiện chỉ chạy diagnostics; telemetry/command/ACK/availability dưới đây chưa được triển khai. TASK-004 được giao chốt các tên `deadline_uptime_ms`, `result`, `reason`, `status`; đây là chi tiết wire của yêu cầu SRS, không thêm chức năng.

## Topic, QoS và nhận dạng

Prefix: `huit/nhom7/smartlight/v1`. Chỉ nhận `node_01`, `node_02`, `node_03`; ID trong payload phải khớp topic. Một client ID riêng cho mỗi node; backend có ID riêng. Clean session, không hàng đợi lệnh offline.

| Hậu tố sau node_id | Chiều | QoS publish | Retain | Ghi chú |
|---|---|---:|---|---|
| telemetry | Node → backend | 0 | Không | Định kỳ 2 giây và khi đổi trạng thái, tối đa 5 bản tin/giây |
| availability | Node → backend | 0 | Có | ONLINE khi nối, OFFLINE khi ngắt chủ động; LWT OFFLINE QoS 0 |
| command | Backend → node | 1 | Không | Node subscribe QoS 1; không phát lại cho node offline |
| ack | Node → backend | 0 | Không | Có retry tầng ứng dụng, không coi ACK được đảm bảo QoS 1 |

PubSubClient 2.8.0 chỉ publish QoS 0; buffer dự kiến 2048 byte bao gồm topic/header/payload. Kiểm tra độ dài trước serialize/publish, kiểm tra kết quả publish; không cắt JSON để vừa buffer. ArduinoJson 7 là phụ thuộc dự kiến khi làm A3, chưa thêm hoặc khóa một bản chưa sử dụng trong A0.

JSON UTF-8, số hữu hạn; các trường bắt buộc phải đúng kiểu (boolean không thay số nguyên). Node bỏ qua bản tin không parse được và ghi log; không tạo dữ liệu 0 giả. Trường chưa thuộc schema v1 bị từ chối để phát hiện lệch hợp đồng. Mọi ví dụ là fixture thiết kế, không phải kết quả live.

## Telemetry

Giữ đầy đủ trường SRS 6.2. `schema_version` bằng 1; `node_id` string như trên; `boot_id` string hex 8 ký tự mới mỗi boot; `seq` số nguyên không âm tăng theo lần phát trong cùng boot; `uptime_ms` số nguyên unsigned 64 bit, đơn điệu theo boot. Phía JavaScript phải giữ chính xác số nguyên khi xử lý uptime 64 bit, không âm thầm làm tròn giá trị vượt phạm vi Number an toàn.

| Trường | Kiểu/phạm vi |
|---|---|
| mode | AUTO hoặc MANUAL |
| environment | UNKNOWN, DAY, TWILIGHT, NIGHT |
| ldr_adc, current_adc | Số nguyên 0–4095 |
| motion | NONE, PEDESTRIAN, VEHICLE, UNKNOWN |
| distance_cm | Số dương hữu hạn hoặc null khi đo lỗi |
| brightness_target, brightness_applied | Số nguyên 0–100 |
| current_ma_sim, power_sim_w | Số hữu hạn không âm; đơn vị mA và W, mô hình |
| faults | Mảng không trùng phần tử; [] hoặc ["OPEN_LOAD"] trong v1 |

Ví dụ tải bình thường:

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","seq":120,"uptime_ms":240000,"mode":"AUTO","environment":"NIGHT","ldr_adc":3100,"motion":"VEHICLE","distance_cm":60.0,"brightness_target":100,"brightness_applied":100,"current_adc":4095,"current_ma_sim":2000.0,"power_sim_w":24.0,"faults":[]}
```

Ví dụ đo khoảng cách lỗi và hở mạch mô phỏng:

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","seq":121,"uptime_ms":242000,"mode":"AUTO","environment":"NIGHT","ldr_adc":3100,"motion":"UNKNOWN","distance_cm":null,"brightness_target":100,"brightness_applied":100,"current_adc":0,"current_ma_sim":0.0,"power_sim_w":0.0,"faults":["OPEN_LOAD"]}
```

Backend thêm received_at UTC. Không lưu/tính điện năng hai lần cho cùng node/boot/seq. Mẫu cũ không ghi đè trạng thái mới, không tích phân mẫu sai thứ tự hoặc xuyên boot/gap theo SRS 9.1. Không suy ra boot mới từ việc seq giảm: phải có boot_id mới và thông tin kết nối/availability mới; bản tin boot cũ đến trễ không được giành trạng thái hiện tại. Backend restart chờ telemetry mới.

## Availability và LWT

Payload gồm schema_version, node_id, boot_id và status ONLINE/OFFLINE. LWT dùng boot_id của phiên đang nối, chuẩn bị trước CONNECT; không chứa timestamp/uptime được giả là thời điểm mất kết nối.

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","status":"ONLINE"}
```

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","status":"OFFLINE"}
```

ONLINE retained chỉ là thông tin kết nối, không đủ xác nhận dữ liệu mới. Cần telemetry hợp lệ trong 10 giây để báo online; LWT báo offline sớm. Broker mất kết nối: trạng thái hiển thị suy giảm/cũ. Khi reconnect, đăng ký lại subscription rồi gửi availability và telemetry mới. Không phục hồi MANUAL từ lệnh cũ.

## Command

Backend chỉ gửi khi broker nối và telemetry mới không quá 3 giây. Các trường chung: schema_version, node_id, boot_id, command_id, deadline_uptime_ms, mode. command_id là UUID v4 do backend tạo; deadline_uptime_ms = uptime mới nhất + 5000, tính theo boot đích, không dùng UTC node.

AUTO không có brightness. MANUAL bắt buộc brightness nguyên 0–100. Điều này áp dụng cho cả wire, đồng bộ với đầu vào API SRS 7.3.

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","command_id":"4113a6c8-27a4-4b2d-a37c-2a7956d673aa","deadline_uptime_ms":245000,"mode":"AUTO"}
```

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","command_id":"f11cf3d4-71de-46d5-a31a-42c3346c669c","deadline_uptime_ms":245000,"mode":"MANUAL","brightness":80}
```

Một lệnh chờ/node. Retry tối đa một lần sau 2 giây chưa ACK, cùng command_id và cùng nội dung; hết 10 giây backend TIMEOUT. Deadline là giới hạn chấp nhận tại node (quá khi uptime hiện tại > deadline), khác với hạn MANUAL 60 giây bắt đầu từ lúc áp dụng theo SRS 5.7.

Node kiểm tra topic, định dạng và boot trước; sau đó đối chiếu cache 32 command ID của boot hiện tại. ID đã xử lý cùng nội dung trả lại ACK cũ, kể cả deadline hiện đã qua, không áp dụng/gia hạn MANUAL lần hai. ID trùng khác nội dung bị từ chối, không thay kết quả cache cũ. Lệnh mới kiểm tra deadline rồi áp dụng hoặc từ chối. Cache mất khi boot, vì vậy lệnh boot cũ bị từ chối.

## ACK và kết quả lệnh

Trường bắt buộc: schema_version, node_id, boot_id, command_id, result, reason. boot_id trong ACK là phiên node đang xử lý; command_id tham chiếu lệnh. APPLIED có reason null; REJECTED có mã lý do. Bộ mã v1: INVALID_COMMAND (schema/range/topic/trường thừa/ID tái dùng khác nội dung), BOOT_MISMATCH, EXPIRED. Nếu JSON/ID không đọc được hoặc topic không dành cho node, chỉ log/bỏ qua; không giả tạo ACK với ID không biết.

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","command_id":"f11cf3d4-71de-46d5-a31a-42c3346c669c","result":"APPLIED","reason":null}
```

```json
{"schema_version":1,"node_id":"node_01","boot_id":"b7e28a10","command_id":"4113a6c8-27a4-4b2d-a37c-2a7956d673aa","result":"REJECTED","reason":"EXPIRED"}
```

APPLIED xác nhận chế độ/mục tiêu, không xác nhận PWM đã dimming xong. Mức sáng áp dụng lấy từ telemetry. Backend chỉ nhận ACK đúng node/command đang chờ; APPLIED phải khớp boot đích. REJECTED/BOOT_MISMATCH được ghi nhận là từ chối kể cả boot thực của node đã đổi, không áp dụng lại lệnh cho boot mới. APPLIED/REJECTED/TIMEOUT là trạng thái cuối; ACK đến muộn sau TIMEOUT chỉ lưu chẩn đoán, không biến kết quả thành thành công.

## Tình huống đối chiếu khi triển khai A3/A4

| Đầu vào/tình huống | Kỳ vọng |
|---|---|
| AUTO kèm brightness hoặc MANUAL thiếu brightness | INVALID_COMMAND |
| brightness -1, 101, 80.5 hoặc true | INVALID_COMMAND |
| Boot cũ | BOOT_MISMATCH nếu đọc được ID hợp lệ |
| Lệnh mới quá deadline | EXPIRED |
| Retry ID/nội dung cũ đã APPLIED | Lặp ACK cũ, không gia hạn MANUAL |
| ACK rơi trên QoS 0 | Backend retry một lần; không coi publish là ACK |
| MQTT ngắt/hết 60 giây MANUAL | Node trở AUTO theo SRS |
| Retained ONLINE nhưng telemetry cũ | Không xác nhận online/dữ liệu mới |
| Telemetry lặp/đến muộn | Không ghi đè hoặc tính điện năng hai lần |

## Diagnostics P0 và giới hạn

Các topic diagnostics/ping, pong và heartbeat chỉ dùng setup. Heartbeat hiện gửi uptime_ms 32 bit, không có boot_id/schema_version; không được đọc nó như telemetry v1 unsigned 64 bit. Hợp đồng nghiệp vụ trên chưa triển khai ở firmware hoặc backend; ví dụ được kiểm tra tĩnh tại [TASK-004](../reports/evidence/task-004/convention-checks.md), không phải test MQTT nghiệp vụ.

Timeout phiên dài P0 vẫn cần theo dõi ở A3. Không tự đổi keepalive, broker, QoS hoặc bỏ deadline nhằm làm ca thử đạt. Khi sửa giao thức, cập nhật các phía và tài liệu đồng bộ trước khi công bố phiên bản mới.
