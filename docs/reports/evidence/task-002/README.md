# Bằng chứng TASK-002

baseline-build.log và smoke-build.log: build đã thử trong phiên agent, thất bại do quyền cache PlatformIO. Không phải lỗi biên dịch đã xác nhận.

Khi chạy ngoài phiên, thêm build.log (build mới), broker.log, serial.log, mqtt.log, ảnh LED. Mỗi ca ghi thời gian, phiên bản, checksum BIN/ELF, kỳ vọng, thực tế và PASS/FAIL. Đã có build.log FAIL do lỗi min; chưa có bằng chứng Wokwi/MQTT live.

| Ca | Trạng thái hiện tại |
| --- | --- |
| Build mẫu | Log cũ bị chặn quyền cache |
| Firmware sau sửa min | PASS: build-min-fix.log; chưa có smoke live |
| Wokwi, Serial và năm mức PWM | Chưa chạy |
| Broker publish/subscribe qua host | Chưa chạy |
| Ba ping/pong và mất/khôi phục broker | Chưa chạy |

## Lượt sửa min — 2026-11-15T18:10:41+07:00

Giữ nguyên build.log lỗi biên dịch gốc. build-min-fix.log là build mới sau sửa std::min<uint32_t>, exit 0, SUCCESS 10.19 giây. clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp: PASS. Core dir tạm /tmp/iot-pio-check-de41spu8 dùng lại package/platform đã cài; không sửa quyền/toolchain. BIN/ELF mới đã tạo trong .pio/build/esp32dev; chưa copy sang mô phỏng, chưa chạy Wokwi/MQTT.
