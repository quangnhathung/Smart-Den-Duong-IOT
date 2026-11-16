# TASK-010 — bằng chứng live, lượt tiếp tục 2026-11-16

Trạng thái đang thực hiện. Phạm vi một node; Backend8001, Dashboard5500, MQTT127.0.0.1:1883. Không fixture, không xóa SQLite, không đổi firmware/MQTT/thuật toán. Không commit/push/merge. Thời gian UTC trong dữ liệu thu tự động; uptime là clock mô phỏng.

## Nguồn bằng chứng

1. [Xác nhận người vận hành](user-confirmation.md): Python3.12,68 Pytest/Ruff PASS, build/prepare SUCCESS, Dashboard live/MANUAL80/ACK/PWM80/tự AUTO khoảng60s. Các mốc Serial193431/194431ms do người dùng cung cấp; chưa có file Serial hoặc ảnh mới trong repo cho lượt đó. Không biến xác nhận thành log giả.
2. `snapshot-initial.jsonl` và `sqlite-initial.json`: agent trực tiếp GET API và đọc SQLite bằng mode=ro/query_only, transaction nhất quán, quick_check=ok, schema1. Hai command MANUAL80 cũ có APPLIED, ACK thật lưu trong DB;32 mẫu PWM80. Có telemetry chuyển AUTO uptime193094ms; đây là mốc telemetry, không ghi đè mốc Serial người dùng cung cấp. Không chạy lại MANUAL60s.
3. `run-command-latency.jsonl`: HTTP request/response/status và MQTT thật, timestamp UTC/perf_counter. Có5 input sai422, node_02 không dữ liệu409, command không tồn tại404. Mỗi output được tạo mới, không ghi đè lịch sử.
4. `command-latency-command-latency.json`:10 command mới luân phiên MANUAL80/AUTO để đo,10 APPLIED, ACK MQTT đối chiếu command_id. Trung vị686,217ms, max1002,001ms theo server sent_at→ack_at. Đây không phải latency cảm biến→render Dashboard. Hệ điều hành/Python trong file; tốc độ Wokwi và CPU tải chưa đo trực tiếp. Timestamp server UTC có độ phân giải cao nhưng thời gian truyền qua quan sát client được lưu riêng.
5. `reject-wire-rejects.jsonl`: command MQTT non-retained dùng UUIDv4 mới, kiểm EXPIRED/BOOT_MISMATCH/INVALID_COMMAND; cả3 PASS từ ACK firmware thật. Những probe này đi trực tiếp MQTT, không phải API command đã được Backend tiếp nhận. Không suy thành UI REJECTED đã PASS.
6. `pending-pending-guard.jsonl`: POST AUTO202/PENDING, POST thứ hai409, lệnh đầu cuối APPLIED/ACK. Không giả timeout.
7. `experiment-1-command-latency.csv`, `experiment-1-comparison-command-latency.json`: phiên thực1 đã đóng;12 mẫu, API/history/CSV cùng boot/seq/raw/quality/continuity/timestamp. Tổng0,0018346Wh, valid_uptime2,284s, covered_wall16,6180400848s, coverage92,2025129083%; baseline DAY0Wh, saving=null. MANUAL/STATE_CHANGE được loại đúng khỏi so sánh AUTO. Không phải EX-series.
8. `audit-initial.json`: tính độc lập hình thang từ CSV/uptime/công suất, mô hình12V/24W khớp;9 mẫu công suất khác0. Chưa có boundary restart trong CSV phiên1.
9. `capture-operator-tests.jsonl`: capture có giới hạn thời gian, MQTT node_01/# và health/nodes mỗi giây. Ghi thật các sự kiện người vận hành; phần chưa xuất hiện vẫn PENDING.

## Ma trận nghiệm thu hiện tại

| Nhóm/tiêu chí | Kết quả | Nguồn/giới hạn |
|---|---|---|
|1. Luồng broker/Wokwi→Backend/SQLite→Dashboard một node | PASS cơ bản | Người dùng xác nhận live; API/SQLite/MQTT/hash bổ sung. Node_02/03 UNKNOWN/không telemetry. Ảnh và bằng chứng trực tiếp về rendering/clock/fault còn thiếu |
|2. MANUAL80, ACK, PWM80 và tự AUTO60s | PASS | Xác nhận người dùng + hai command cũ/APPLIED/32 mẫu PWM80/telemetry AUTO. Không chạy lại |
|2. AUTO API mới, lệnh sai422, pending409 | PASS | run-command-latency/pending-pending-guard |
|2. Reject MQTT hết hạn/sai boot/sai brightness | PASS | reject-wire-rejects; UI REJECTED chưa kiểm trực tiếp |
|2. Retry/cache/timeout backend10s/ACK muộn, mất API/broker/reconnect/no-replay và AUTO khi mất mạng | PENDING | Chưa có bằng chứng live đủ; không lấy host test hoặc reject probe làm thay thế |
|3. History, alert OFFLINE có start/end, phiên1, CSV/stats/clock/công thức | PASS | API/SQLite + CSV + audit |
|3. OPEN_LOAD/phục hồi, restart giữ dữ liệu/phiên mở, gap không nối, rendering history/alerts/CSV | PENDING | Đang capture, cần thao tác người vận hành và đối chiếu sau restart |
|4. Command→ACK10 lượt | PASS phép đo | Median/max trên; không tự đặt ngưỡng nghiệm thu mới |
|4. Cảm biến→Dashboard10 lượt, median/max và điều kiện mô phỏng | PENDING | Chưa có timestamp thao tác cảm biến và thời điểm render; không thay bằng HTTP RTT/telemetry→API |

Chốt nhóm1 PASS cho kết nối live và trạng thái cơ bản từ xác nhận người vận hành kết hợp API/MQTT/SQLite/hash. `db-lock-check.json` xác nhận DB chỉ có một chủ ghi; listener8001 thuộc một PID. Không suy ra mọi tương tác UI đã PASS. Tổng1/4 nhóm; nhóm2–4 còn các tiêu chí PENDING như bảng trên.

## Kết quả bổ sung cuối lượt

- `cache-cached-auto-wire-int.jsonl`: PASS replay lệnh AUTO cũ sau deadline, cùng ID đổi nội dung INVALID_COMMAND, gửi lại bản gốc vẫn APPLIED; Backend giữ kết quả cuối APPLIED. `cache-cached-auto.jsonl` là lượt probe lỗi do script dùng chuỗi uint64 từ HTTP trên wire MQTT; firmware từ chối đúng. Đã sửa duy nhất script bằng chứng để chuyển deadline thành JSON integer, chạy lại với tag mới; giữ nguyên log lỗi, không sửa source ứng dụng/giao thức.
- `sqlite-before-restart.json`: baseline được chuẩn bị trước ca dự kiến. Không có restart thật trong capture; `sqlite-final.json` chỉ là snapshot cuối lượt, không được gọi là snapshot sau restart.
- `capture-operator-tests.jsonl` hoàn tất420s, không có OPEN_LOAD hoặc HTTP_UNAVAILABLE. Người vận hành chưa phản hồi ca fault; không suy việc không có sự kiện thành test PASS.
- Phiên2 đã đóng bằng `owned-experiment-stop.json`, CSV423 mẫu và API/stats khớp. Tất cả DAY/applied0, điện năng0Wh; có845,943s uptime hợp lệ và1697,82353425s wall coverage. Thời lượng này vượt capture420s vì phiên2 vẫn mở trong lúc chờ công cụ GUI. Không gọi là stability30phút/ba node.
- `audit-final.json`: kiểm độc lập cả2 CSV PASS; không có continuity boundary trong chúng, restart/gap vẫn PENDING.
- Quan sát GUI hết thời gian chờ cấp quyền (`Computer Use app approval timed out`); không có screenshot mới. Không có automatic approval review rejection, không yêu cầu lại quyền hoặc dùng cách khác để vượt giới hạn.

Các API command/experiment mới là thao tác kiểm thử đã được giao. Các command cũ, SQLite và log cũ giữ nguyên; hai phiên agent tạo đã đóng, Backend/Wokwi/Dashboard không bị dừng.

## Vấn đề thời gian quan sát

SQLite ban đầu có20 alert OFFLINE đã đóng.187 cặp telemetry có21 khoảng nhận≥10s thực, max13,83255s; trung vị tỉ số delta uptime/delta nhận≈0,436. Điều này phù hợp khả năng mô phỏng chạy chậm nhưng chưa chứng minh nguyên nhân duy nhất. Health broker vẫn OK khi đọc. Không sửa timeout/ngưỡng/schema để che trạng thái stale; cần ghi tốc độ Wokwi và kiểm kết nối/tốc độ trong ca còn lại. Không dùng tỉ số clock này làm latency cảm biến→UI.

## Tái lập và bảo toàn

`live-evidence.py` chạy bằng `.venv/Scripts/python.exe` của Backend, từ repo Backend; mọi file output exclusive-create theo tag. `snapshot` chỉ đọc DB; `capture` chỉ subscribe/poll. `run` chủ động tạo/đóng phiên của nó và gửi10 command đo latency; không chạy lại khi đã đủ bằng chứng. `reject` gửi probe command sai có ID mới/non-retained; `pending` gửi AUTO hai lần để kiểm guard. `experiment-export --experiment-id ID` chỉ so phiên đã đóng. Không chạy `init_db` khi Backend đang hoạt động.

`audit-evidence.py --tag TEN_MOI` đọc file đã thu, không đụng DB. Thêm `--after TAG` sau restart thật để đối chiếu snapshot với `sqlite-before-restart.json`; cần kèm log API mất/phục hồi/continuity, không coi việc chụp hai snapshot là đã restart.

`restart-experiment.json` ghi ID phiên2 do agent mở để quan sát fault/persistence; phiên này đã được đóng khi kết thúc lượt chờ. Không đụng phiên của người dùng. Các lỗi môi trường trước khắc phục giữ nguyên ở run-20261116-173103.
