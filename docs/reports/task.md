# TASK-002 — Kiểm chứng môi trường P0

- Trạng thái: Bị chặn
- Tiến độ: 1/4 mục nghiệm thu
- Cập nhật: 2026-11-15T17:55:23+07:00

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

Build mẫu và firmware mới bị chặn quyền cache ~/.platformio; chưa thể kết luận mã mới biên dịch được. Chạy build theo [setup](../techs/setup.md) trên terminal ngoài phiên, kiểm tra SUCCESS rồi chuẩn bị artifact. Chưa tự khởi động Docker hoặc Wokwi vì người dùng chọn tự chạy. Cần lưu log/ảnh theo [bằng chứng](evidence/task-002/README.md) rồi tiếp tục TASK-002 để nghiệm thu; chưa đưa vào checklist task hoàn thành.

## Phụ thuộc và điều kiện bắt đầu

Đã được người dùng giao triển khai. Phần tiếp theo cần Docker daemon khả dụng, quyền build cache và license Wokwi. Không tự tắt sandbox, sửa quyền hệ thống hay mua dịch vụ.
