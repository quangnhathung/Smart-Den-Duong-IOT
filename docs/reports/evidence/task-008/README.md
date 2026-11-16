# TASK-008 — Backend/API A4: bàn giao code/test/hướng dẫn

- Cập nhật: 2026-11-16T13:17:56+07:00
- Trạng thái: Hoàn thành4/4 nhóm đầu ra code/test/OpenAPI/hướng dẫn. **Chưa nghiệm thu live broker/ESP32 tại máy này.**
- Source: [DoAn/backend](../../../../../backend/README.md), Git repo riêng nhánh main, chưa commit/remote/push. Firmware base giữ nguyên; chỉ thay task/docs. [Manifest 25 file](backend-source-sha256.json).

## Đã thực hiện

FastAPI/Pydantic/Paho/SQLite WAL: collector strict, dedup/order/boot/quality, DB persistence/health, fault/offline alerts, lệnh persist-before-publish/retry2s/TIMEOUT10s/ACK cuối, không replay qua session/restart. Paho instance mới mỗi TCP session, một worker sở hữu DB, queue1024/OS lock tránh collector trùng.10 endpoint SRS7.3 có request/response models/OpenAPI. Uptime/seq/deadline giữ uint64 bằng decimal TEXT trong SQLite và string HTTP; MQTT vẫn number.

Năng lượng hình thang theo uptime cùng boot/continuity, baseline trên cùng đoạn AUTO hợp lệ; raw/quality/reasons được giữ. CSV/API dùng cùng thuật toán, chỉ2 đầu mút trong phiên; coverage UTC công bố riêng với uptime. Phiên start/stop có cấu hình và stop idempotent. Backend README có lệnh Linux/Windows, init DB, vận hành và6 bước live, không có dashboard.

## Kiểm tra đã chạy tại thư mục bàn giao

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| backend/.venv/bin/python scripts/check.py | PASS exit0: Ruff lint, format21 file;66 pytest,0.99s | [Log thực](backend-checks.log) |
| pip check | PASS: No broken requirements found | Đã chạy bằng .venv backend trong lượt bàn giao; [phiên bản](versions.log) |
| python -B -m smartlight.init_db --db /tmp/task008-init-smoke.db (2 lần) | PASS exit0 cả2 lần, schema v1, không xóa dữ liệu | Kết quả CLI đã đối chiếu trong lượt bàn giao; Pytest còn kiểm restart/persistence/lock |
| API startup/lifespan | PASS với TestClient và transport giả;10 paths và schema NodeResponse/HttpTelemetry | [OpenAPI](openapi.json), [test log](backend-checks.log) |
| Live broker/Wokwi/Paho socket, Windows | Chưa chạy | [README và hướng dẫn live](../../../../../backend/README.md) |

Test dùng SQLite tạm và MQTT/clock giả, không chạy broker hoặc giả kết quả sensor thật. Bao gồm concurrency202/409, sai schema/node/boot, duplicate/retired boot, lỗi DB read-only/closed và worker còn sống, timeout đúng10s, ACK muộn, Paho client mới/no-replay, singleton DB, config/CORS, energy0.4/0.1Wh, gap/invalid/restart, clock mô phỏng khác thực, CSV/API/ràng buộc phiên dài>1h.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn chặn đầu ra được giao. Cài pip lần đầu bị sandbox chặn DNS; chạy lại theo quyền mạng được cấp, tạo backend/venv/Git ngoài workspace theo quyền đã cấp. Không thay package hoặc nguồn firmware. Có1 Starlette TestClient deprecation warning khuyến nghị HTTPX2, test vẫn PASS trên stack HTTPX đã chốt; không suppress hoặc coi warning là live PASS. Lệnh Windows chưa chạy trên Windows.

Khi review đã thêm guard ACK đúng deadline, DB lỗi không làm chết worker, không retry command chưa ghi đủ bookkeeping, kiểm ISO8601 UTC và khóa singleton DB. Không ghi PASS cho tầng chưa chạy. Không có mã nguồn frontend; chưa dùng ui-ux-pro-max ở task backend/API tự sinh này.

## Bảo toàn và bước tiếp theo

[Bản task TASK-007 trước chuyển](task-007-before-task008.md) giữ nguyên byte (link bên trong dùng gốc docs/reports ban đầu). Evidence TASK-005/006/007 giữ nguyên. Report cũ SHA256 `b069eb8f43f7fcf1dbb118b20638012d5694ff6ababc049fec5c9161d0aa1f36` được giữ nguyên làm phần đuôi. Git backend mới không có commit/remote; task chưa commit/push tại cả hai repo.

[Tài liệu backend](../../../techs/backend.md) mô tả triển khai/config/HTTP/schema/clock/giới hạn. Đề xuất TASK-009 dashboard React/TypeScript/Vite, áp dụng skill ui-ux-pro-max khi được giao; chưa tự triển khai. Tích hợp live cần người vận hành máy dev làm runbook A3/A4 và lưu kết quả riêng.
