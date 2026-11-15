# TASK-002 — Kiểm chứng môi trường P0

- Trạng thái: Bị chặn
- Tiến độ: 1/4 mục nghiệm thu
- Cập nhật: 2026-11-15T18:10:41+07:00

## Mô tả và phạm vi

Đã chuẩn bị firmware Serial/PWM/MQTT chẩn đoán, Docker Compose và Wokwi một node theo kế hoạch. Người dùng tự chạy Docker và Wokwi; chưa có bằng chứng live. Chưa triển khai cảm biến hoặc AUTO/MANUAL, chưa hoàn tất toàn bộ P0/A0.

## Tham chiếu SRS

[SRS](../srs.md) mục 3.1, 4.3–4.5, 10.2–10.3, 11–12.

## Tiêu chí hoàn thành và tiến độ

- [ ] Build mới esp32dev thành công và khóa phiên bản platform/framework sau smoke test đạt.
- [ ] License Wokwi, Serial và năm mức PWM được xác nhận bằng log/ảnh.
- [ ] Broker qua host, ba ping/pong và mất/khôi phục broker đạt bằng chứng live.
- [x] Chuẩn bị mã/cấu hình, tài liệu setup và hồ sơ kiểm tra; ghi rõ phần chưa xác minh.

## Vướng mắc và cách giải quyết

Đã sửa lỗi min(unsigned long, unsigned int) bằng std::min<uint32_t> và include <algorithm>. Build esp32dev PASS (exit 0, 10.19 giây), formatter PASS. Dùng PLATFORMIO_CORE_DIR=/tmp/iot-pio-check-de41spu8 với package/platform cục bộ có sẵn; không đổi toolchain hoặc quyền hệ thống. Log mới: [build-min-fix.log](evidence/task-002/build-min-fix.log). Giữ nguyên build.log ghi lỗi gốc và baseline-build.log/smoke-build.log ghi lỗi cache trước đó. Wokwi/Serial/PWM và MQTT live chưa chạy; người dùng tiếp tục theo setup. Chưa khóa platform/framework vì còn chờ smoke test live theo tiêu chí SRS; TASK-002 vẫn 1/4, chưa hoàn thành.

## Phụ thuộc và điều kiện bắt đầu

Đã được người dùng giao triển khai. Phần tiếp theo cần Docker daemon khả dụng, quyền build cache và license Wokwi. Không tự tắt sandbox, sửa quyền hệ thống hay mua dịch vụ.

## Lượt sửa lỗi biên dịch

Tiếp tục TASK-002: sửa xung đột kiểu trong min tại EnvironmentSmokeTest.cpp, kiểm tra formatter và build esp32dev; giữ nguyên thuật toán backoff, không chạy Docker/Wokwi hoặc gói tiếp theo. Log build.log hiện có ghi FAIL do unsigned long/unsigned int, khác lỗi cache trong các log trước.

- [x] Sửa kiểu đối số min một cách tường minh.
- [x] Kiểm tra định dạng và build PASS; lưu kết quả thật.
- [x] Cập nhật setup và hồ sơ bằng chứng, giữ nguyên log lỗi gốc.
