# Kiểm tra tĩnh TASK-002

- PASS: docker compose -f infra/compose.yaml config --quiet.
- PASS: clang-format --dry-run --Werror cho ba tệp C/C++ thay đổi.
- PASS: đọc diagram.json bằng json, wokwi.toml bằng tomllib; kiểm tra đích liên kết tài liệu.
- PASS: script artifact thử trên fixture tạm: từ chối thiếu file, từ chối file cũ, copy đủ BIN/ELF và checksum khớp.
- EXPECTED FAILURE: chạy script trên dự án thật báo thiếu artifact sau build không thành công; không xuất firmware cũ cho Wokwi.
- Build firmware: bị chặn cache, xem baseline-build.log và smoke-build.log. Các kiểm tra tĩnh không thay thế biên dịch hoặc mô phỏng live.
