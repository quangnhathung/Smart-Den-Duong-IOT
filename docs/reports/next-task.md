# TASK-002 — Kiểm chứng môi trường P0

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 mục
- Cập nhật: 2026-11-15T17:36:07+07:00

## Mô tả và phạm vi

Đề xuất kiểm chứng môi trường build, Wokwi, gateway và MQTT local trước khi triển khai chức năng đèn. Đây là task tiếp theo được đề xuất, chưa được tự động bắt đầu.

## Tham chiếu SRS

[SRS](../srs.md): mục 3.1, 4.3–4.5, 10.2–10.3 (P0), 11.2 (đầu vào cho A0), 12. Chỉ là bước kiểm chứng môi trường, không đồng nghĩa hoàn thành mọi đầu ra kiến trúc/giao thức của P0/A0.

## Tiêu chí hoàn thành và tiến độ

- [ ] Xác nhận phiên bản PlatformIO/platform/framework, build esp32dev và ghi log/kết quả thực tế.
- [ ] Xác nhận quyền Wokwi và chạy một ESP32 với Serial/PWM có bằng chứng.
- [ ] Xác nhận Mosquitto local, gateway và publish/subscribe từ mô phỏng, ghi cấu hình và kết quả.
- [ ] Cập nhật techs liên quan cùng báo cáo; ghi rõ kiểm tra đạt, lỗi và phần còn lại của P0.

## Vướng mắc và cách giải quyết

Chưa kiểm tra trong task này. SRS ghi nhận lần build trước bị chặn ghi khóa trong ~/.platformio; cần xác minh lại bằng môi trường có quyền phù hợp. License Wokwi và MQTT local chưa được xác nhận; cần kiểm tra quyền tài khoản và kết nối thật, không suy ra từ việc có extension hoặc artifact.

## Phụ thuộc và điều kiện bắt đầu

Chỉ bắt đầu khi người dùng giao task này. Cần PlatformIO khả dụng, quyền ghi cache build, VS Code/Wokwi có quyền sử dụng và Mosquitto local. Không tự mua license, mở broker ra Internet hoặc tắt sandbox để vượt giới hạn phiên.
