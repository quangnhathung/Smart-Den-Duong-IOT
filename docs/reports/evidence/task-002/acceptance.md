# TASK-002 — Nghiệm thu smoke test môi trường P0

- Chốt: 2026-11-15T19:12:53+07:00.
- Trạng thái: Hoàn thành 4/4 nhóm nghiệm thu môi trường; không phải nghiệm thu toàn đồ án.

| Nhóm | Kết quả và nguồn |
|---|---|
| Build và khóa phiên bản | PASS: platform 8.0.0, Arduino package 4.30312.261113 (Core 3.3.12), ESP32 libs 3.3.12, PubSubClient 2.8.0. [Build sau pin](build-pinned-retry.log): SUCCESS 8.37 giây; [copy/checksum](prepare-pinned.log) |
| Wokwi/Serial/PWM | PASS: [ảnh license/khởi chạy](wokwi-first-run.png); Serial do người dùng dán trong hội thoại chứa đủ 0/25/50/70/100%, duty 0/64/128/179/255, ready=1 và heartbeat. Chưa có serial.log thô đầy đủ trên đĩa |
| Broker và MQTT hai chiều/phục hồi | PASS phép thử: host pub/sub theo terminal người dùng; [MQTT](mqtt-heartbeat-live.log) có đủ pong p0-001/002/003/004; [broker](broker-heartbeat-live.log) dừng 19:01:33, chạy lại 19:02:25, node kết nối 19:02:27 (+07:00). Người dùng xác nhận “Không restart ESP32” trong lượt chốt kế hoạch |
| Mã/cấu hình/tài liệu | PASS: firmware P0 đã build, cấu hình Compose/JSON/TOML, script copy, setup và hồ sơ có bằng chứng |

## Cách đối chiếu và giới hạn

Agent đọc file và đối chiếu artifact; không tự vận hành Docker/Wokwi live. Kết quả live là kết hợp file log, Serial trong hội thoại và xác nhận người vận hành, không giả tạo một file Serial đầy đủ. Heartbeat đầu tiên ghi uptime 5889 đến 551587 ms, 273 mẫu; khoảng cách lớn nhất 2009 ms theo đồng hồ mô phỏng. Broker đã có phiên hoạt động vượt 3 phút thực và ba pong trong phiên thử. Không đồng nhất thời gian mô phỏng với thời gian thực.

Log có cả các lần timeout lịch sử và timeout cuối phiên dài; không tuyên bố đã xác định nguyên nhân hay bảo đảm kết nối mọi thời lượng. Nghiệm thu ở đây là các ca smoke/PWM/ping-pong/recovery đã chốt. Lưu vấn đề timeout phiên dài để theo dõi khi tích hợp mạng nghiệp vụ; không xóa các dòng FAIL cũ. Chưa có thử độ ổn định ba node/30 phút theo P6.

Lần build-pinned.log đầu lỗi HTTPClientError khi PlatformIO chuẩn hóa yêu cầu PubSubClient 2.8 thành 2.8.0. Đối chiếu lại package cục bộ thấy đúng 2.8.0; lần thử lại build-pinned-retry.log PASS. Không nâng package, thay quyền hệ thống hoặc xóa cache để làm kiểm tra đạt. Build dùng PLATFORMIO_CORE_DIR=/tmp/iot-pio-check-de41spu8, các package/platform cục bộ đã cài.

Source ứng dụng giữ nguyên sau pin; chỉ cấu hình dependency được cố định. Build/copy sau pin không phải lượt live mới. Phiên bản runtime trong log trước tương ứng đúng package được khóa.
