# Backend/API P4/A4 — TASK-008 và bổ sung TASK-009

## TASK-010 — sửa race khi nhận availability sau restart/reconnect

Hoàn tất 2026-11-17T12:05:29+07:00. Service đồng bộ transport connected/session ngay sau Queue.get và trước dispatch, bổ sung kiểm ở đầu vòng hiện có. Nếu readiness đổi khi actor đang chờ queue, retained ONLINE đầu tiên được xử lý theo session mới; event session cũ vẫn bị loại. Không thay schema/MQTT/API hoặc khôi phục freshness từ dữ liệu cũ. Cần telemetry mới hợp lệ trước khi can_command=true.

Lỗi được phát hiện live: node cùng boot vẫn gửi nhưng latest bị kẹt UNCONFIRMED_BOOT sau restart. Hồi quy4 ca có2 FAIL trước sửa; sau sửa72 Pytest/Ruff PASS/1 warning TestClient cũ. Live sau sửa: pending→TIMEOUT/BACKEND_RESTART, node fresh cùng boot, phiên mở phục hồi sau reload; broker outage/reconnect/no-replay cũng đạt. Nhánh backend `task/task-010-restart-sync`, không commit/push. [Bằng chứng và giới hạn](../reports/evidence/task-010/completion-20261117-105535/README.md).


TASK-010 trên máy Windows hiện dùng API127.0.0.1:8001 theo lựa chọn người dùng; không đổi cấu hình mặc định8000 của Backend. Dashboard nhánh task/010-live-integration gọi8001. [Bằng chứng một node live](../reports/evidence/task-010/run-20261116-180648/README.md) đã có API/MQTT/SQLite/command/CSV/stats; [restart giữ dữ liệu và gap](../reports/evidence/task-010/run-20261116-190549/README.md) đã đối chiếu PASS sau PID18828→43632. Timeout/no-replay cho lệnh đang chờ, phiên mở và các phần còn thiếu ghi riêng PENDING. Không chạy init_db khi Backend đang hoạt động, không xóa SQLite để restart.

Bổ sung [TIMEOUT/ACK muộn qua proxy local](../reports/evidence/task-010/run-20261116-193157/README.md) đã PASS với ACK firmware thật, không sửa schema/thuật toán; một retry dự kiến/attempts2, ACK muộn không đổi TIMEOUT. Backend tạm32248 dùng1884, sau test đã khôi phục14144 dùng1883/8001/một worker, proxy dừng; không giữ biến hệ thống hoặc .env thay đổi. Broker outage/no-replay cho lệnh chờ và phiên mở vẫn cần ca riêng.

## Tham chiếu và phạm vi

SRS6/7/9/12, FR06/08/09/10/11, TC17–22/24/26 và ca năng lượng. [MQTT v1](mqtt.md) giữ nguyên; [README backend](../../../backend/README.md) có lệnh Linux/PowerShell và bộ kiểm live. Đầu ra TASK-008 là code/test/OpenAPI/hướng dẫn, không phải nghiệm thu broker/Wokwi/ba node thật. Dashboard TASK-009 đã có ở repo cùng cấp; [tài liệu](dashboard.md).

## Vị trí và cấu hình

Backend ở `DoAn/backend/`, cùng cấp firmware, là Git repo riêng nhánh main. TASK-009 giữ nguyên lịch sử commit đã có, không commit/push hoặc đổi remote. Firmware/infra/source giữ nguyên; task/report/checklist và tài liệu dùng nguồn chung ở repo firmware. AGENTS backend trỏ nguồn convention thay vì sao chép. Khi chuyển máy cần đặt hai repo cạnh nhau để các liên kết tài liệu hoạt động.

Python3.12, FastAPI0.163.1, Pydantic2.14.3, Paho2.2.0, Uvicorn0.54.0, SQLite của Python (máy kiểm tra3.54.1), Pytest9.2.0, HTTPX0.28.1 và Ruff0.17.5. Runtime/test/transitive dependencies pin trong requirements.txt sau smoke test. `.venv` riêng ở backend. Không nâng PlatformIO/toolchain; frontend là repo riêng.

Mặc định API127.0.0.1:8000/workers1; broker127.0.0.1:1883; SQLite data/smartlight.db trên ổ local. SMARTLIGHT_DB, SMARTLIGHT_MQTT_HOST, SMARTLIGHT_MQTT_PORT, SMARTLIGHT_ORIGINS đọc từ environment. .env.example chỉ mô tả, không tự load; không có tài khoản/cloud. CORS mặc định localhost/127.0.0.1 cổng5500 (Live Server); giữ5173 để tương thích cấu hình cũ. .env.example được cập nhật, không dùng wildcard.

## Lifecycle, database và collector

FastAPI lifespan tạo Service/worker rồi transport. MQTT callback chỉ đưa bytes/topic/timestamp/session vào queue1024; không ghi SQLite. Actor xử lý toàn bộ truy vấn/ghi database, tick50ms, HTTP future có deadline3s. Nếu queue đầy trả503 hoặc drop event kèm dropped_events/generation; worker đánh dấu gap và reset freshness, không nội suy qua mất mẫu. Callback lưu tối đa2049 byte để từ chối payload quá2048, không giữ queue các payload vô hạn.

Một OS lock trên file `.db.lock` ngăn hai collector dùng cùng DB (fcntl trên Linux, msvcrt trên Windows). Lock tự nhả khi process chết; không cần xóa file sót. SQLite WAL/foreign_keys/busy_timeout1000ms, schema version1. Init script idempotent không xóa dữ liệu và không đổi lệnh đang chờ; Engine startup chuyển PENDING còn sót thành TIMEOUT/BACKEND_RESTART, không resend. Version lạ bị từ chối, không tự reset database.

Bảng nodes/boots/telemetry/availability/alerts/commands/ack_events/experiments/ingest_errors, index node/time và unique(node,boot,seq). seq/uptime là TEXT decimal chuẩn để không tràn signed64 SQLite; payload JSON giữ Python int đầy đủ. Trạng thái/telemetry/alert ghi transaction phù hợp, runtime chỉ cập nhật sau commit. Health thử một write không thay dòng để nhận diện DB read-only; DB lỗi ngăn nhận lệnh chưa ghi đủ.

Collector chỉ subscribe telemetry/availability/ack, không nhận diagnostics làm dữ liệu nghiệp vụ. Pydantic strict/reject extra/type/range/nonfinite, UTF8/JSON/duplicate keys/topic/payload phải hợp lệ. Invalid giữ payload đầu vào (tối đa2049B) và lý do trong ingest_errors; telemetry invalid tạo barrier năng lượng, không tạo mẫu0 giả.

Node_01/02/03 được đăng ký sẵn. ONLINE retained chỉ tạo candidate boot, chưa có fresh telemetry thì UNKNOWN/STALE. Đổi boot cần availability phù hợp và telemetry mới; boot đã nghỉ lưu trong boots, không được giành lại trạng thái. Duplicate không thêm mẫu, mẫu cũ/unconfirmed/retired giữ quality và không ghi đè latest. Sau restart latest cũ đọc được nhưng stale; duplicate cũ không làm fresh. LWT, mất broker hoặc10s không có telemetry mới làm offline/stale, tách fault cuối. OPEN_LOAD chỉ mở một alert, chỉ fresh telemetry xác nhận hết fault mới đóng; mất broker không coi là phục hồi.

## Lệnh, ACK và transport

API request AUTO không có brightness; MANUAL bắt buộc int0–100, không bool/float/trường lạ. Mỗi node một PENDING (kiểm worker + unique partial index). Chỉ nhận khi broker/DB/queue tốt, node fresh và age≤3s. UUIDv4, boot đích, deadline=latest uptime+5000; lưu DB trước publishQoS1/non-retain. 202 là tiếp nhận, không phải APPLIED/PUBACK. Nếu publish fail sau khi đã ghi nhận, vẫn pending và không báo thành công giả.

Retry quyết định một lần sau2s theo monotonic, chỉ nếu còn cùng session/boot và dữ liệu fresh; không kéo dài deadline. Timeout10s là cuối; ACK đến đúng hoặc sau10s cũng không thắng timer bằng thứ tự xử lý. Chỉ ACK đúng node/ID/boot kết thúc lệnh; ngoại lệ REJECTED/BOOT_MISMATCH cho phép boot thực đã đổi. ACK sai/muộn/duplicate lưu chẩn đoán, không sửa trạng thái cuối. Nếu HTTP503 do worker deadline, client cần kiểm pending_command_id trước khi retry vì thao tác đã bắt đầu có thể vừa được lưu.

Transport dùng Paho callback API VERSION2/MQTT3.1.1, connect timeout2s và hạn chờ subscription3s, loop timeout0.1s, backoff1/2/4/8/10s. Chỉ ready sau SUBACK; buffer tối đa64 message đến sớm, queue outgoing giới hạn8. Sau mất TCP, bỏ hẳn instance Paho cũ, tạo client ID/session mới và subscribe lại; không dùng Paho auto reconnect hoặc mang outgoing QoS1 cũ sang phiên mới. Worker hủy quyền retry command cũ. Test transport giả kiểm sự thay instance/không replay; chưa chứng minh hành vi socket/broker thật.

## HTTP API và kiểu dữ liệu

12 thao tác HTTP trên11 đường dẫn theo SRS7.3 sau TASK-009; request/response schemas tại /docs và /openapi.json. [Snapshot hiện tại](../reports/evidence/task-009/openapi.json), [snapshot TASK-008 giữ nguyên](../reports/evidence/task-008/openapi.json).

| Nhóm | Endpoint | Dữ liệu/chính sách |
|---|---|---|
| Health/nodes | GET /api/health, /api/nodes | Health200/503; nodes có connection/freshness/last_seen/age/telemetry/faults/pending_command_id/can_command |
| History | GET /api/nodes/{node_id}/history | from/to UTC, mặc định1h; limit100/max1000, offset0; items/total/limit/offset, quality, continuity và mẫu gốc |
| Command | POST /api/nodes/{node_id}/commands; GET /api/commands/{command_id} |202/PENDING, sau đó APPLIED/REJECTED/TIMEOUT; payload, sent/retry/ACK timestamps, attempts/reason |
| Alert/stats | GET /api/alerts; GET /api/stats | Alerts có pagination/node filter; stats theo node/from/to/experiment_id |
| Phiên đo | GET /api/experiments; GET /api/experiments/{id}; POST /api/experiments; POST /api/experiments/{id}/stop; GET /api/experiments/{id}/export.csv |List có items/total/limit/offset (100/max1000), mới nhất trước theo started_at/id; detail404 nếu thiếu; start201, một phiên mở; stop idempotent, config/notes được lưu, CSV cùng thuật toán stats |

HTTP giữ404/409/422/503 theo SRS. Timestamp trả UTC ISO8601; from/to bắt buộc ISO8601 có UTC timezone (Z/+00:00), không nhận timestamp số. HTTP seq/uptime/deadline trả chuỗi decimal; MQTT vẫn JSON number, không đổi schema v1. Api health không yêu cầu tất cả node online; ba node chưa chạy không được bịa telemetry.

## Năng lượng, baseline và CSV

Một thuật toán segments dùng chung stats/export. Chỉ lấy cặp cùng node/boot, seq/uptime tăng,0<Δuptime≤6s, quality ACCEPTED, cùng run/session/barrier/generation và thời gian nhận tăng. Không nối qua backend restart, disconnect, invalid hoặc queue-loss. Không lấy mẫu ngoài from/to/ranh giới phiên để nội suy; experiment mặc định dùng toàn phiên kể cả dài>1h, còn query không chọn phiên mặc định1h.

Tổng năng lượng hình thang dùng power_sim_w và Δuptime, tách khỏi AUTO. AUTO loại MANUAL/UNKNOWN/fault/low-load<0.95/đổi environment-mode-fault ở bất kỳ đầu mút. Low-load loại cả lúc xác minh trước khi có OPEN_LOAD; fault đầu mút loại lúc phục hồi. Baseline DAY0W, TWILIGHT/NIGHT24W trên cùng đoạn hợp lệ; saving=null nếu baseline0. Đó là mô hình điện năng, không phải đo phần cứng.

valid_uptime_s và auto_valid_uptime_s là thời gian mô phỏng; covered_wall_s/missing_wall_s/coverage_percent là khoảng UTC nhận giữa các cặp hợp lệ trong cửa sổ. Tổng coverage chia tổng khoảng của các node được chọn, không chia uptime cho walltime. FIRST_SAMPLE khởi tạo chưa có đoạn. API công bố clock_basis, sample_count và excluded_intervals; dữ liệu bị loại vẫn giữ raw/quality/reason. CSV có raw fields, metadata và segment energy/reasons để đối chiếu cùng API. Tên/notes kiểu công thức spreadsheet được escape trong CSV, raw DB vẫn nguyên.

## Kiểm tra và giới hạn

Chạy `.venv/bin/python scripts/check.py` tại backend: Ruff check/format và Pytest. [Bằng chứng TASK-008](../reports/evidence/task-008/README.md).66 test dùng DB tạm, MQTT/clock giả; TestClient chạy lifespan thật nhưng transport giả, không mở broker. OpenAPI đủ10 endpoint và script init DB chạy2 lần không xóa dữ liệu; pip check đạt.

Có1 deprecation warning từ Starlette1.10.0 TestClient khuyến nghị HTTPX2, bộ test vẫn PASS với HTTPX0.28.1 theo stack đã chốt; không suppress warning. Windows code/lệnh được chuẩn bị, chưa chạy trên Windows. Chưa chạy Wokwi/broker/socket/Paho thật, ba node30phút hay EX-series; kiểm chứng live theo README backend và mqtt.md. TASK-009 bổ sung hai GET, trả history.continuity từ giá trị đã lưu và thêm CORS5500, không migration hoặc sửa MQTT/thuật toán. Bộ hồi quy hiện68 Pytest, Ruff check/format PASS trên repo bàn giao; [log TASK-009](../reports/evidence/task-009/backend-checks.log). Dashboard đã dùng ui-ux-pro-max, kiểm browser với API thật/transport giả; chưa thay nghiệm thu live.
