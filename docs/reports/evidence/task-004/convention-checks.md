# TASK-004 — Kiểm tra convention và hợp đồng A0

- Kiểm tra: 2026-11-15T19:15:52+07:00 (+07:00).
- Kết quả: PASS các nhóm kiểm tra tĩnh dưới đây, không phải toàn bộ FR/TC nghiệp vụ.

| Nhóm | Cách kiểm tra thực tế | Kết quả |
|---|---|---|
| C/C++ | clang-format --dry-run --Werror trên ba tệp .cpp/.h hiện hữu trong src | PASS |
| Docker | docker compose -f infra/compose.yaml config --quiet; không khởi động daemon/container | PASS |
| Tài liệu | Đọc UTF-8, LF/newline, giải đường dẫn Markdown ngoài code fence; vòng đầu 99 liên kết file hợp lệ sau sửa | PASS |
| Convention entry | CLAUDE.md đúng một import @AGENTS.md; không có override tại gốc | PASS cấu trúc, không thử phiên model mới |
| Cấu hình/script | json.loads cho diagram.json; tomllib cho wokwi.toml; ast.parse script Python | PASS |
| Hợp đồng | Parse 8 JSON trong mqtt.md; kiểm tra tập trường, version/ID, enum availability, AUTO không brightness, MANUAL 80, ACK tương ứng, null/fault; so tập telemetry với SRS | PASS kiểm tra tĩnh |
| Build/pin/artifact | Kiểm tra phiên bản đã pin, SUCCESS trong log build và checksum/freshness BIN/ELF nguồn/copy | PASS |
| Bảo toàn | Source ứng dụng và infra byte-identical với bản trước; SRS chỉ đổi đúng hai liên kết; report cũ giữ nguyên ở đuôi, mục checklist cũ giữ nguyên | PASS |

Lệnh formatter thực tế: `clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp src/EnvironmentSmokeTest.h src/main.cpp`. Kiểm tra Python chạy bằng script tạm `/tmp/a0-check.py`, gồm giải liên kết và parse/đối chiếu nêu trên. Sau khi đóng báo cáo chạy lại cùng bộ kiểm tra; số liên kết có thể tăng khi thêm báo cáo cuối. Không coi kiểm tra file đích là kiểm tra nội dung trang web hoặc tất cả anchor ngoài dự án.

Build sau pin: [SUCCESS 8.37 giây](../task-002/build-pinned-retry.log), [checksum](../task-002/prepare-pinned.log). Lần đầu [HTTPClientError](../task-002/build-pinned.log) được giữ; sau khi đối chiếu lại package cục bộ đúng 2.8.0, lần build lại đạt. Không nâng phiên bản hoặc thay quyền hệ thống.

Nguồn live P0 ở [nghiệm thu TASK-002](../task-002/acceptance.md); bao gồm xác nhận người dùng không reset ESP32. Chưa chạy MQTT v1 nghiệp vụ, backend, dashboard, cảm biến, ba node hoặc P6; không ghi PASS cho các phần chưa tồn tại. Timeout phiên dài P0 là giới hạn theo dõi đã ghi, không bị xóa để làm checklist đạt.

Vòng kiểm tra sau khi đóng hồ sơ: PASS đủ tám nhóm, 115 liên kết file nội bộ hợp lệ. Task hiện tại TASK-004 hoàn thành 3/3; TASK-005 chưa bắt đầu 0/4. Lịch sử TASK-002/001/003 giữ nguyên và không có triển khai P1.
