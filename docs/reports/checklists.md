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
