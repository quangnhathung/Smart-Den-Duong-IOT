# TASK-010 — Tích hợp live một node MQTT–backend–dashboard

- Hoàn thành: 2026-11-17T12:05:29+07:00; **4/4 nhóm nghiệm thu**. Kết hợp PASS Windows được bảo toàn với lượt Linux bổ sung.
- [x] Broker/Wokwi/SQLite/API/dashboard thật một node; node02/03 UNKNOWN.
- [x] Giữ MANUAL/60s/guard/reject wire cũ; thêm UI REJECTED/TIMEOUT, ACK muộn, broker outage/reconnect/no-replay và Serial AUTO/PWM khi mqtt0.
- [x] Giữ history/CSV/gap cũ; thêm pending/open experiment qua restart/reload, sửa race retained ONLINE sau chờ queue;72 Pytest/Ruff PASS.
- [x]10 sensor→dashboard mới PASS3s (median1417,832–1464,491ms; max2353,967–2401,274ms),10 command→ACK cũ giữ nguyên; phương pháp/clock/video/hash có bằng chứng.

[Hồ sơ nghiệm thu](evidence/task-010/completion-20261117-105535/README.md).4 test lõi proxy PASS; dịch vụ QA đã dừng, source firmware/dashboard và dữ liệu cũ giữ nguyên. Không nghiệm thu ba node/stability30phút/EX-series/phần cứng thật, không commit/push/merge. TASK-011 chờ đặc tả. Các ghi chú checklist phía dưới giữ đúng lịch sử từng lượt.

---

Ghi chú rà soát 2026-11-17T09:45:17+07:00: TASK-010 đang thực hiện, 2/4 nhóm nghiệm thu; TASK-011 chờ đặc tả. Lượt rà soát tài liệu đã hoàn tất, không thêm TASK-010 vào danh sách task hoàn thành. [Bằng chứng rà soát](evidence/task-010/review-20261117-094517/README.md). Toàn bộ checklist lịch sử bên dưới được giữ nguyên.

---

# TASK-009 — Dashboard HTML/CSS/JS qua Live Server

- Hoàn thành đầu ra code/test/hướng dẫn:2026-11-16T14:18:00+07:00;4/4 nhóm nghiệm thu.
- [x] Dashboard sáng theo ui-ux-pro-max,5 view, native HTML/CSS/JS/SVG, responsive/keyboard/reduced motion và cấu hình Live Server5500.
- [x] Polling/stale/uint64, draft/AUTO/MANUAL/pending/ACK/reject/timeout/unknown, POST không tự retry.
- [x] History gap/continuity/charts/table, alerts, experiments/reload/CSV, API list/detail/CORS5500 giữ5173.
- [x]16 Node test,68 Pytest/Ruff,26 browser checks đạt; smoke repo bàn giao0 console error/0 uncaught exception; tài liệu/SRS/bằng chứng hoàn tất.

[Bằng chứng và manifest](evidence/task-009/README.md). API/SQLite thật nhưng MQTT/telemetry là fixture; chưa nghiệm thu MQTT/Wokwi live, latency, Windows hoặc ba node30phút. Không commit/push/deploy, không tự thực hiện TASK-010.

---

# TASK-008 — Backend, SQLite và API P4/A4

- Hoàn thành đầu ra code/test/hướng dẫn: 2026-11-16T13:17:56+07:00;4/4 nhóm nghiệm thu được giao.
- [x] Collector strict/boot/order/dedup, persistence/WAL/version/OS lock, quality/health/alerts.
- [x] API10 endpoint/typed OpenAPI, command persist-before-publish/ACK/retry/timeout/concurrency/no-replay.
- [x] Năng lượng/baseline/clock coverage/experiment/CSV dùng cùng thuật toán và kiểm thử.
- [x]66 Pytest, Ruff lint/format, pip check/init DB/OpenAPI đạt; README Linux/Windows, evidence/report/next-task cập nhật.

[Bằng chứng, manifest backend và giới hạn](evidence/task-008/README.md). Chưa nghiệm thu live A4 hoặc Windows; không suy fixture/host thành broker/ESP32 thực. Backend Git riêng chưa commit/push.

---

# TASK-007 — MQTT nghiệp vụ một node P3/A3

- Hoàn thành đầu ra bàn giao: 2026-11-16T12:02:01+07:00; 5/5 mục code/test/hướng dẫn.
- [x] Telemetry/schema/boot/seq/uptime64/current-power và giới hạn200ms/2s.
- [x] Command validation/deadline/cache32/ACK sau áp dụng; queue8 và session flush.
- [x] LWT/availability/reconnect, P2 offline và diagnostics giữ đúng trong host.
- [x] 5 suite host,11 unittest Python, formatter/build/copy/hash PASS.
- [x] Tài liệu, generator và runbook live Linux/PowerShell có tiêu chí/evidence.

[Bằng chứng và giới hạn](evidence/task-007/README.md). **Chưa nghiệm thu live A3 tại máy này**; đây là hoàn thành phạm vi code/test/hướng dẫn người dùng đã chọn. Không nâng trạng thái TASK-006 hoặc toàn đồ án từ kết quả này.

---

# Cập nhật nghiệm thu TASK-005

## TASK-005 — Mạch và đọc cảm biến một node P1/A1

- Hoàn thành: 2026-11-16T02:56:10+07:00
- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu

- [x] Mạch/pin map chính và timeout, Wokwi thực tế.
- [x] Raw cảm biến P1-01 đến P1-05, có Serial/ảnh/xác nhận giá trị đặt theo biên bản.
- [x] Build/artifact/hash, PWM P1-06, MQTT P1-07 và recovery P1-08.
- [x] Tài liệu/hồ sơ và đề xuất TASK-006; chưa triển khai tính năng tiếp theo.

[Bằng chứng, nguồn xác nhận và giới hạn](evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Chỉ nghiệm thu raw sensor/diagnostics một node, không phải AUTO/MANUAL hoặc toàn đồ án.

---

# Các task đã hoàn thành

## TASK-004 — Hoàn thiện kiến trúc và giao thức A0

- Hoàn thành: 2026-11-15T19:15:52+07:00
- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu

- [x] Kiến trúc và điểm bàn giao, tách hiện trạng khỏi thiết kế.
- [x] MQTT v1 giữ SRS, chốt trường wire và ví dụ, tách diagnostics.
- [x] Convention/cấu hình/JSON được kiểm tra; báo cáo và checklist giữ lịch sử.

Bằng chứng: [kiểm tra A0](evidence/task-004/convention-checks.md), [kiến trúc](../techs/architecture.md), [MQTT](../techs/mqtt.md). Chưa triển khai runtime nghiệp vụ hoặc P1.

## TASK-002 — Kiểm chứng môi trường P0

- Hoàn thành: 2026-11-15T19:12:53+07:00
- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu môi trường

- [x] Build/pin đúng package và copy checksum.
- [x] License/Serial/năm PWM theo ảnh và hội thoại.
- [x] Broker host pub/sub, đủ bốn pong, phục hồi không reset ESP32 theo xác nhận người dùng.
- [x] Hoàn thiện hồ sơ; bảo toàn log và giới hạn timeout phiên dài.

Bằng chứng: [nghiệm thu](evidence/task-002/acceptance.md), [task đã chốt](evidence/task-002/accepted-task.md), [báo cáo](report.md). Chỉ nghiệm thu môi trường P0, chưa có cảm biến hoặc ba node.

## TASK-003 — Dùng chung convention cho ba công cụ

- Hoàn thành: 2026-11-15T17:41:58+07:00
- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

- [x] Giữ AGENTS.md làm nguồn chung cho Codex/OpenCode và thêm CLAUDE.md import cho Claude Code.
- [x] Cập nhật development.md: cơ chế nạp, cách xác nhận và giới hạn kiểm chứng.
- [x] Kiểm tra import/liên kết, bảo toàn lịch sử và dữ liệu dự án; hoàn thiện hồ sơ task.

Bằng chứng: [báo cáo TASK-003](report.md), [hướng dẫn dùng chung](../techs/development.md). Chưa chạy phiên model mới để xác minh context thực tế.

## TASK-001 — Thiết lập convention agent

- Hoàn thành: 2026-11-15T17:37:41+07:00
- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu

- [x] Tạo [AGENTS.md](../../AGENTS.md) và [quy trình phát triển](../techs/development.md): tham chiếu SRS mỗi task, cập nhật techs, vòng đời và mẫu báo cáo.
- [x] Thêm [.clang-format](../../.clang-format), [.editorconfig](../../.editorconfig) cho Arduino C/C++, giữ source hiện tại.
- [x] Kiểm tra liên kết, formatter và bảo toàn dữ liệu; hoàn thiện bốn tệp báo cáo và đề xuất task kế tiếp.

Bằng chứng: [báo cáo TASK-001](report.md), [task hiện tại](task.md). Task tiếp theo nằm ở [next-task.md](next-task.md), chưa được thực hiện và không thuộc checklist hoàn thành này.
