# MQTT v1 — hợp đồng A0 và triển khai TASK-007/A3

## TASK-011 — Định danh và công cụ theo node

Một `NodeIdentity` cấp node ID, client ID và topic cho cả nghiệp vụ/diagnostics theo `SMARTLIGHT_NODE_INDEX=1|2|3`; không đổi prefix hoặc schema MQTT v1. Boot ID vẫn thuộc mỗi lần khởi động, không yêu cầu duy nhất toàn hệ thống. Client ID riêng ngăn ba node đá kết nối lẫn nhau; host checks xác minh từng định danh và đích topic/payload sai bị loại.

`scripts/mqtt-command.py --node node_02 --telemetry <file> --mode MANUAL --brightness 80` tạo JSON cho node_02; tương tự node_01/03, mặc định node_01. Telemetry phải đúng node/schema/boot/uptime64 và file trong 3s hiện có. Ca wrong-node chọn node kế tiếp trong tập ba node. Script không publish; khi gửi kiểm thử cần chọn đúng topic và giữ command không retained. Tham chiếu SRS6, FR08, TC17–20/P6.


TASK-006/A2 giữ nguyên diagnostics ping/pong/heartbeat, chuyển network sang FreeRTOS task riêng và dùng atomic trạng thái/mất kết nối để điều khiển fallback. Không subscribe command v1 hoặc phát telemetry/ACK trong A2. `AUTO` / `MANUAL <0..100>` trên Serial là giao diện thử cục bộ, không phải MQTT schema; command/ACK/deadline/cache thuộc A3.

## Tham chiếu và trạng thái

[SRS](../srs.md) mục 5–7, 11–12, 16; [kiến trúc](architecture.md); [diagnostics P0 đang chạy](setup.md).

Hợp đồng A0 dưới đây đã được triển khai ở firmware một node trong TASK-007; TASK-008 bổ sung [backend/API A4](backend.md), chưa nghiệm thu tích hợp live. Kết quả live A3 chưa chạy tại máy này; hướng dẫn ở cuối trang. TASK-004 được giao chốt các tên `deadline_uptime_ms`, `result`, `reason`, `status`; đây là chi tiết wire của yêu cầu SRS, không thêm chức năng.

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

Các topic diagnostics/ping, pong và heartbeat chỉ dùng setup. Heartbeat hiện gửi uptime_ms 32 bit, không có boot_id/schema_version; không được đọc nó như telemetry v1 unsigned 64 bit. Hợp đồng nghiệp vụ đã có code firmware TASK-007 và backend TASK-008; các ví dụ A0 trước đây được kiểm tra tĩnh tại [TASK-004](../reports/evidence/task-004/convention-checks.md), không phải test MQTT nghiệp vụ.

Timeout phiên dài P0 vẫn cần theo dõi ở A3. Không tự đổi keepalive, broker, QoS hoặc bỏ deadline nhằm làm ca thử đạt. Khi sửa giao thức, cập nhật các phía và tài liệu đồng bộ trước khi công bố phiên bản mới.


## Triển khai TASK-007/A3

Tham chiếu SRS6,5.7,9.1,TC17–22/26. `MqttProtocol` dùng ArduinoJson **7.4.2** đã smoke host/build rồi pin; PubSubClient2.8.0 và framework giữ nguyên. Bộ mã reason/schema/QoS/retain không đổi. Prefix/node hiện cố định node_01; chưa build ba environment.

- Boot ID dùng esp_random, 8 hex; giữ qua reconnect. Uptime64 lấy esp_timer_get_time()/1000, independent với timer32 của P2. seq bắt đầu0, tăng sau publish telemetry thành công; lần publish thất bại có thể retry cùng seq để phía nhận chống trùng.
- Snapshot sensor/control/uptime được copy trong critical section ngắn. Network core0 là chủ MQTT; core1 sở hữu controller/cache và PWM. Không parse/serialize/network trong critical section. Network stack8192 byte; queue lệnh8 và kết quả8 phần tử, cấp phát tĩnh.
- Command callback parse bằng độ dài, sao chép các trường sang kiểu riêng, không giữ pointer vào buffer PubSubClient. JSON hỏng, embedded NUL/trailing garbage hoặc command_id không phải UUIDv4 thì chỉ log/drop; topic khác chỉ drop. Payload có ID hợp lệ nhưng schema/node/range sai trả INVALID_COMMAND. UUID/boot hex được chuẩn hóa chữ thường. Không phát ACK khi chưa nhận diện được ID.
- Core1 lấy tối đa1 lệnh/vòng khi result queue còn chỗ, kiểm tra phiên/loss-count và deadline64 tại lúc xử lý. Serial xử lý trước MQTT nếu cùng vòng. Sau requestAuto/requestManual và controller.update mới đưa kết quả sang task mạng. APPLIED không đo PWM hay xác nhận đã dimming xong.
- Cache FIFO32 ở core1 giữ nội dung chuẩn hóa và reason, không refresh vị trí khi retry. Retry sau deadline vẫn nhận kết quả cũ; nội dung khác cùng ID bị từ chối, không sửa cache gốc. Kết quả invalid có ID hợp lệ cũng chiếm cache để tránh tái dùng ID đó thành lệnh khác. Sai boot được kiểm tra trước cache. Cache reset khi boot, giữ qua reconnect.
- Callback gặp command queue đầy thì log/drop, không áp dụng hoặc thêm mã reason mới. Result queue đầy ngăn lấy lệnh mới. ACK publish thất bại giữ đầu queue để thử lại lúc network tick, không áp dụng lại controller; client còn có retry cùng ID. Session mất thì flush command/result đang chờ, giữ cache; result của lệnh đã lấy ở phiên cũ bị loại.
- Snapshot mới nhất thay thế snapshot cũ, không có history offline. Từ TASK-011, mode/environment/motion/target/applied/fault và dữ liệu cảm biến (LDR/current ADC, khoảng cách hợp lệ hoặc null và PIR đầu vào của motion) đều làm bẩn snapshot để gửi sớm. analogSequence, uptime và thay đổi giá trị khoảng cách vẫn cùng biểu diễn null không làm bẩn snapshot. Sửa này tránh raw mới phải chờ control hoặc periodic, không thêm trường JSON hoặc đổi timer điều khiển. Telemetry định kỳ2s, thay đổi được gộp với khoảng cách tối thiểu200ms giữa mọi lần thử publish (kể cả thất bại/reconnect), tối đa5/s. Không phát lại các bước dimming đã bị gộp.
- Current mô phỏng =2000mA×applied/100×current_adc/4095, power=12×current_mA/1000. distance invalid/nonfinite/nonpositive là null, ADC ngoài range không phát bản tin giả. Buffer2048 gồm MQTT header/topic; kiểm tra measureJson/overflow/serialize/publish.
- CONNECT clean session, LWT OFFLINE retain/QoS0 được chuẩn bị trước; subscribe diagnostics/ping và command QoS1. Sau subscribe gửi ONLINE retain rồi snapshot telemetry mới nhất ở network tick tiếp. ONLINE publish fail sẽ thử lại trước telemetry. Ngắt chủ động khi transport còn dùng được phải publish OFFLINE trước DISCONNECT; transport mất/ghi lỗi thì đóng TCP, giữ will để broker phát. Broker chết không tự phát LWT tới client khác; backend tương lai phải dựa mất kết nối/stale.
- PubSubClient callback không cung cấp retained flag: việc command không retained là yêu cầu publisher; không tuyên bố node nhận diện/reject retained command. Môi trường demo phải dùng broker sạch retained command; tuyệt đối không thêm -r cho command.

Host stubs không chứng minh contention hai core, timing Serial/ISR, broker thực nhận hay LWT thực tế. [Log TASK-007](../reports/evidence/task-007/host-checks.log). Hạn chế timeout phiên dài còn cần theo dõi live; không tăng keepalive hoặc che lỗi để làm PASS.

## Bộ kiểm tra live A3 trên máy dev (chưa chạy tại máy này)

### Chuẩn bị

Build/copy theo simulation.md; chỉ1 phiên Wokwi cấu hình node_01. Broker local theo setup.md do người vận hành khởi động. Lưu hash BIN/ELF, phiên bản dependency, giờ bắt đầu thực và toàn Serial. Artifact/clock của lượt này phải tách TASK-005/006; không dùng uptime làm giờ thực.

Trong terminal A tại gốc firmware, nghe trước khi gửi lệnh (Linux bash):

```bash
mkdir -p docs/reports/evidence/task-007/live
# Lưu thời điểm bắt đầu riêng, không sửa log cũ.
date --iso-8601=seconds > docs/reports/evidence/task-007/live/start-time.log
docker compose -f infra/compose.yaml --profile tools run --rm -T mqtt-client mosquitto_sub -h 127.0.0.1 -t 'huit/nhom7/smartlight/v1/node_01/#' -v -W 600 | tee docs/reports/evidence/task-007/live/mqtt.log
```

### Lệnh mới từ telemetry thật

Terminal B: mỗi lệnh mới cần capture mới; không gõ boot_id/deadline từ ví dụ cố định. Script dưới **chỉ tạo JSON**, không publish, chỉ đọc telemetry capture không quá3s (mtime dùng cho độ mới file đầu vào, không dùng làm timestamp nghiệm thu).

```bash
docker compose -f infra/compose.yaml --profile tools run --rm -T mqtt-client mosquitto_sub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/telemetry -C 1 -W 15 > /tmp/task007-telemetry.json
if python3 scripts/mqtt-command.py --telemetry /tmp/task007-telemetry.json --mode MANUAL --brightness 80 > /tmp/task007-command.json; then
  cat /tmp/task007-command.json | docker compose -f infra/compose.yaml --profile tools run --rm -T mqtt-client mosquitto_pub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/command -q 1 -s
fi
```

Chỉ gửi khi script exit0 và file command không rỗng; gửi ngay sau tạo, không chờ quá deadline. Nếu script báo telemetry cũ/không có telemetry thì dừng, capture mới trước khi thử lại; không bỏ kiểm tra độ mới. Lưu command JSON vào evidence/live cùng capture tương ứng sau khi gửi.

Windows PowerShell tương đương (Python PlatformIO hoặc python có sẵn, không cài thư viện thêm):

```powershell
docker compose -f infra/compose.yaml --profile tools run --rm -T mqtt-client mosquitto_sub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/telemetry -C 1 -W 15 | Set-Content -Encoding utf8 "$env:TEMP/task007-telemetry.json"
python scripts/mqtt-command.py --telemetry "$env:TEMP/task007-telemetry.json" --mode MANUAL --brightness 80 | Set-Content -Encoding utf8 "$env:TEMP/task007-command.json"
if ($LASTEXITCODE -eq 0) { Get-Content -Raw "$env:TEMP/task007-command.json" | docker compose -f infra/compose.yaml --profile tools run --rm -T mqtt-client mosquitto_pub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/command -q 1 -s }
```

### Ma trận và kỳ vọng

| Ca | Thao tác | Bằng chứng đạt |
|---|---|---|
| A3-01 Telemetry | Đổi LDR/PIR/distance/tải, nghe3 phút thực | Đủ16 trường, target/applied đúng CONTROL; seq tăng, boot không đổi, null khi timeout; current/power theo mô hình, không quá5 bản tin/s theo uptime. Lưu tốc độ mô phỏng và broker/log lỗi |
| A3-02 MANUAL/AUTO | MANUAL80; lệnh mới --mode AUTO (không brightness) | ACK đúng command_id/boot APPLIED/reason null; target80 rồi applied80; AUTO trở mức nền. MANUAL60s tự fallback theo uptime |
| A3-03 Retry | Gửi lại nguyên command JSON sau2s, không sinh UUID/deadline mới | ACK kết quả cũ, không refresh timer60s. Gửi lại sau deadline cũng trả ACK cũ nếu ID còn cache. Hai lần gửi không phải hai lần áp dụng |
| A3-04 Reject | Capture mới mỗi ca; thêm --case expired/wrong-boot/invalid-brightness/wrong-node | EXPIRED/BOOT_MISMATCH/INVALID_COMMAND đúng; controller không đổi. Sửa brightness cùng ID đã xử lý phải INVALID_COMMAND, cache gốc không đổi |
| A3-05 JSON hỏng/đúng đích | Gửi `{` hoặc payload >buffer; publish command vào topic node_02 | Không crash/ACK giả, node_01 không đổi. Chưa nghiệm thu ba node từ phép thử này |
| A3-06 Mất/phục hồi broker | Người vận hành stop riêng mosquitto, giữ Wokwi và đổi cảm biến, start lại | AUTO/raw/PWM tiếp tục, MANUAL cũ hủy; subscribe lại, ONLINE + telemetry mới, cùng boot/seq tiếp tục; gửi lệnh mới sau reconnect có ACK |
| A3-07 LWT | Broker vẫn chạy, dừng riêng phiên Wokwi không gửi clean DISCONNECT | Subscriber nhận OFFLINE retained khi broker phát hiện mất session; subscriber mới cũng nhận OFFLINE. Khởi động lại có boot mới/ONLINE/telemetry; lệnh boot cũ BOOT_MISMATCH |
| A3-08 Mất ACK mô phỏng | Bỏ qua ACK lần đầu ở test client; sau2s replay cùng JSON một lần | Cache không áp dụng/gia hạn lần hai; nếu bỏ qua cả ACK thì client ghi TIMEOUT sau10s, không báo thành công. Đây là mô phỏng client, không phải backend đã triển khai |

Với stop/start broker, chỉ người vận hành chạy `docker compose -f infra/compose.yaml stop mosquitto` rồi `start mosquitto`; không dùng down/prune/dừng service khác. Subscriber có thể thoát khi broker dừng: khởi động lại subscriber để capture recovery. Nếu Wokwi không chạy hoặc thiếu giấy phép, ghi chưa chạy, không đổi sang broker public.

Mỗi ca ghi PASS/FAIL/chưa chạy, command/payload, Serial + MQTT/broker nhận, hash/config và nguồn thời gian. published=1 trên Serial không đủ chứng minh broker nhận; APPLIED không đủ chứng minh PWM vật lý. Ba node30phút/backend/UI ngoài phạm vi. Chưa có kết quả live A3 trong TASK-007 bàn giao code.


## Backend TASK-008/A4

Collector/API theo [backend.md](backend.md), giữ schema v1. Không lấy diagnostics làm telemetry; strict validation, boot/seq/order/dedup, lỗi cũ và offline tách riêng. HTTP đổi uint64 thành decimal string để JS không mất chính xác, MQTT vẫn number. Command có persist-before-publish/QoS1/non-retain/retry2s/TIMEOUT10s; Paho client mới sau disconnect để không mang outgoing cũ qua session. Code/API test fixture đã có, chưa nghiệm thu broker/Wokwi/ba node thực.
