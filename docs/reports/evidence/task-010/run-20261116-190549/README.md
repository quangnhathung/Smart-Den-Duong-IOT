# TASK-010 — đối chiếu restart Backend thật

## Xác nhận người vận hành và quan sát tiến trình

Người dùng xác nhận: Backend cũ PID18828 đã dừng, Backend mới PID43632 chạy127.0.0.1:8001/workers1; không chạy init_db hoặc xóa/thay SQLite, giữ Wokwi và Mosquitto. Agent thấy listener8001 thuộc43632, tiến trình Python khởi động19:03:07+07:00, không còn PID18828. `backend-process.json` và `backend-listener.log` ghi trực tiếp các quan sát này. Không suy rằng đã capture API outage đúng lúc dừng: recorder lượt trước kết thúc trước thao tác restart.

## Kết quả thực tế — PASS

`sqlite-after-restart.json`/`snapshot-after-restart.jsonl` là dữ liệu thu trực tiếp bằng DB mode=ro/query_only và HTTP thật. `restart-audit.py` kiểm snapshot gần nhất trước restart từ run-20261116-184903/sqlite-final.json; kết quả và response API nằm ở `restart-audit.json`.

| Dữ liệu | Trước → sau | Đối chiếu |
|---|---|---|
| Telemetry |760→781 | Không thiếu bản ghi cũ, giữ nguyên từng trường |
| Commands |13→13 | ID/payload/result/sent/retry/ACK/attempts không đổi |
| ACK events |20→20 | Từng bản ghi cũ nguyên vẹn |
| Alerts |106→122 | ID/kind/node/start còn; alert đã đóng giữ nguyên end, alert mở được phép đóng theo dữ liệu mới |
| Experiments |3→3 | Cấu hình/notes/start/end của3 phiên đã đóng khớp API trước restart |
| Availability |1→2 | Bản cũ còn; có thông tin retained ONLINE qua session Backend mới |

SQLite quick_check=ok, schema1 và cùng đường dẫn data/smartlight.db. Health OK, database/broker/queue true, dropped_events0. Node_01 cùng boot3268eb79, tiếp tục AUTO/NIGHT target25/applied25/6W; node_02/03 không có telemetry.

Backend run ID đổi từ26989c18-61ec-478e-95cf-82f310ba944b sang44cc197e-d126-41d2-8cdb-a050afcf1a4c. Ranh giới thật là row765/seq764/uptime1484617ms → row766/seq770/uptime1496643ms. Hai đầu mút cùng boot nhưng khác continuity; API history giữ ranh giới và API stats cửa sổ hai đầu mút trả0 năng lượng/0 valid_uptime, có lý do DISCONTINUITY. Không nối điện năng qua thời gian collector ngừng; khoảng thiếu mẫu không được lấp giả.

Tải lại CSV phiên1/2/3 sau restart khớp **từng byte/SHA256** với file đã lưu trước restart. Các bản sau restart ở `experiment-1-after-restart.csv` đến `experiment-3-after-restart.csv`; không tạo lại phiên hoặc sửa metadata hồi tố. OPEN_LOAD alert30/33 vẫn đóng đúng timestamp cũ. Những kết quả này xác nhận dữ liệu đã lưu được giữ qua restart, không có nghĩa không thiếu telemetry lúc collector dừng.

`capture-after-restart.jsonl` chỉ ghi75s tiếp diễn sau restart, không tạo packet/ACK giả hoặc gửi lệnh. `live-evidence.py` là bản sao harness của lượt trước, dùng snapshot/capture. Không có phiên đo mới do agent mở trong lượt này.

## Giới hạn và các ca chưa PASS

- Không capture đúng thời điểm API ngừng hoặc trạng thái STALE đầu tiên ngay khi Backend khởi động; không dùng dữ liệu hiện tại để tái tạo log đó.
- Không có command PENDING hoặc phiên đo mở lúc restart; chưa chốt timeout/no-replay cho lệnh đang chờ hoặc phục hồi phiên mở.
- API/SQLite/CSV và gap phía server đã kiểm; rendering Dashboard sau reload và các trạng thái UI terminal chưa có bằng chứng trực tiếp mới.
- Nhóm3 PASS theo tiêu chí đã giao về history/alerts/experiments đã lưu, gap, CSV/stats/coverage/clock. Nhóm1 đã PASS; nhóm2 và4 vẫn PENDING, tổng2/4 nhóm. Không chạy lại OPEN_LOAD/MANUAL60s/build/68 Pytest đã đủ chứng cứ.

## Ca TIMEOUT/ACK muộn chuẩn bị cho người vận hành

`timeout-check.py` đã được người vận hành chạy; giữ nguyên source và file `timeout-20261116-191322-428249.jsonl`/`timeout-20261116-191322-428249-summary.json`. Lệnh7aa224a2-5738-42ad-8b13-cf857629a670 có kết quả INCOMPLETE cho ca TIMEOUT; không tự retry. Không tiếp tục dùng quy trình Pause trong2s này.

`timeout-diagnosis.json` đối chiếu SQLite/API và log thật: sent_at12:13:36.973317Z, ACK APPLIED được Backend chấp nhận12:13:37.996447Z, sau1,0231297s; attempts1/retry_atnull, ACK event21 có disposition ACCEPTED. Backend kết thúc lệnh trước10s đúng thiết kế. `observed_timeout_wall_s≈1,297` trong summary là thời gian script quan sát đến khi phát hiện APPLIED, không phải timer timeout của Backend. Không có timestamp Pause hoặc bằng chứng MCU thực sự đã halt; chưa thể phân biệt Pause muộn với mô phỏng/transport còn xử lý. Cửa sổ2s và thiếu interlock xác nhận Pause là hạn chế của quy trình test, không phải bằng chứng lỗi timeout Backend.

## Thay thế bằng giữ trễ ACK thật — đã chuẩn bị, chưa chạy live với Backend

`ack-delay-proxy.py` là proxy TCP/MQTT chỉ bind127.0.0.1:1884, nối broker1883. Khi `ack-delay-check.py` arm đúng một lệnh AUTO, proxy giữ nguyên raw frame ACK thật tới12s tính từ lệnh đầu, vẫn chuyển telemetry/PUBACK/PING và lệnh retry. Retry không gia hạn mốc release. Không phát ACK giả, không sửa payload/QoS/schema, ACL/firewall hoặc DB. Driver gửi một AUTO ngay sau telemetry mới, không yêu cầu Pause/Resume và không tự POST lại.

Đã kiểm **offline** CONNECT/framing, ACK đi trễ giữ nguyên bytes, frame thường vẫn đi qua khi ACK bị giữ và cleanup; ghi rõ không phải test MQTT nghiệp vụ live. Đã chạy roundtrip **diagnostics thật** qua proxy với broker local, không publish telemetry/ACK nghiệp vụ; kết quả ở `ack-delay-proxy-offline-check.json` và `ack-delay-proxy-smoke.json`. Proxy smoke20s đã dừng, Backend hiện tại không bị chuyển cổng hoặc restart bởi agent. Các kiểm này xác nhận công cụ sẵn sàng cho phép thử, chưa chốt TIMEOUT/late-ACK PASS.

Quy trình vận hành không có cửa sổ thao tác2s; từ repo Backend:

1. Terminal riêng chạy `.venv/Scripts/python.exe ../Smart-Den-Duong-IOT/docs/reports/evidence/task-010/run-20261116-190549/ack-delay-proxy.py`.
2. Terminal Backend: Ctrl+C, đặt `$env:SMARTLIGHT_MQTT_PORT='1884'`, chạy lại `.venv/Scripts/python.exe -m uvicorn smartlight.api:app --host 127.0.0.1 --port 8001 --workers 1`. Giữ nguyên SQLite, không init_db, Wokwi/Mosquitto vẫn RUNNING trên1883.
3. Terminal kiểm tra chạy `.venv/Scripts/python.exe ../Smart-Den-Duong-IOT/docs/reports/evidence/task-010/run-20261116-190549/ack-delay-check.py`. Driver từ chối gửi command nếu không thấy đúng một client Backend đi qua proxy, status proxy cũ hoặc node chưa commandable. Không thao tác Pause.
4. Sau kết quả, Ctrl+C Backend, đặt `$env:SMARTLIGHT_MQTT_PORT='1883'`, chạy lại đúng lệnh một worker ở bước2; đợi healthOK rồi mới Ctrl+C proxy. Biến môi trường chỉ đổi ở terminal này, không sửa cấu hình toàn hệ thống hoặc source.

Chỉ PASS khi có202, TIMEOUT/ACK_TIMEOUT khoảng10s thực, ACK thật cùng ID/boot bị proxy giữ/release nguyên hash, DB ghi LATE_OR_DUPLICATE và GET command vẫn TIMEOUT. ACK có thể đến broker sớm nhưng tới Backend muộn do **fault injection có ghi nhãn**, không gọi là lỗi mạng tự nhiên. Lệnh AUTO giữ chế độ vốn đang chạy, không tái kiểm tải. Retry2s chỉ được chốt nếu raw command/attempts thật chứng minh có retry; UI TIMEOUT là tiêu chí riêng. Agent chưa chuyển Backend hiện tại qua proxy hoặc yêu cầu người dùng lặp lại bài Pause.

Các hạng mục khác: mất broker/reconnect/no-replay/AUTO offline, trạng thái UI và cảm biến→Dashboard10 lượt vẫn cần phối hợp. TASK-011 chờ đặc tả. Không commit/push/merge hoặc xóa SQLite/log.
