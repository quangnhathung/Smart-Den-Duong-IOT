# TASK-005 — Kiểm tra tĩnh và convention

## Kết quả đã chạy

| Nhóm | Kết quả | Phạm vi và bằng chứng |
|---|---|---|
| Định dạng C++ | PASS | clang-format --dry-run --Werror trên 7 source/header trong src, include và test/host; cấu hình tại gốc dự án |
| Logic SensorReader | PASS | Code thật biên dịch với g++ -std=c++17 -Wall -Wextra -Werror và stub Arduino; [host-checks.log](host-checks.log) |
| Build firmware | PASS | esp32dev, Arduino/package giữ nguyên; [build-fresh.log](build-fresh.log), SUCCESS 9.06 giây; RAM 47388/327680 byte, flash 908071/1310720 byte |
| Artifact | PASS | BIN/ELF có nội dung, mới hơn đầu vào build; hash bản nguồn/copy khớp [prepare-final.log](prepare-final.log); cả hai cấu hình Wokwi trỏ tới artifact hiện hữu |
| Sơ đồ | PASS tĩnh | 7 ID duy nhất, loại linh kiện/default đúng, pin tín hiệu/nguồn/GND, LED 220 Ω và Serial; bản timeout chỉ bỏ dây ECHO |
| Cấu hình và tài liệu | PASS | JSON/TOML hợp lệ, Python parse được, liên kết file Markdown tồn tại, UTF-8/LF/newline; git diff --check đạt |
| Compose | PASS cấu hình | docker compose -f infra/compose.yaml config --quiet, exit 0; không khởi chạy container |
| Bảo toàn phạm vi | PASS | main.cpp, platformio.ini, SRS và checklist hoàn thành khớp byte trước task; toàn bộ report cũ còn nguyên ở cuối; ví dụ JSON MQTT parse được, giao thức nghiệp vụ chưa triển khai |

Host checks xác nhận lịch 20/100/200 ms, xung TRIG, tham số timeout 30000 µs, xóa distance cũ, phục hồi khoảng cách và timer qua tràn uint32. Stub không đo thời gian chặn thực, điện áp hoặc chất lượng ADC. Đây không phải kết quả Wokwi.

## Lệnh tái lập chính

Chạy tại gốc firmware:

```bash
clang-format --dry-run --Werror src/*.cpp src/*.h test/host/*.cpp test/host/*.h
g++ -std=c++17 -Wall -Wextra -Werror -Itest/host -Isrc src/SensorReader.cpp test/host/SensorReaderChecks.cpp -o /tmp/task005-sensor-checks
/tmp/task005-sensor-checks
docker compose -f infra/compose.yaml config --quiet
git diff --check
```

Build trong lượt này dùng PLATFORMIO_CORE_DIR=/tmp/iot-pio-check-de41spu8 vì package đã pin có sẵn tại đó. [Clean log](clean.log) và build-fresh.log ghi lượt build sạch; không thay cấu hình package của dự án.

## Giới hạn và việc còn lại

Script từng [từ chối artifact cũ](prepare-rejected.log) sau sửa comment vì SCons không relink. Đã clean/build lại rồi copy đạt; không bỏ kiểm tra freshness.

Chưa chạy Wokwi live P1-01 đến P1-08, chưa xác nhận chiều ADC/cảm biến thực, MQTT hồi quy hoặc broker recovery khi có cảm biến. Không mở phiên model khác để kiểm tra nạp convention runtime. TASK-005 giữ 2/4 nhóm nghiệm thu; [phần live tiếp theo](../../next-task.md) vẫn chờ người vận hành.
