# TASK-025 — Khởi động hệ thống local

Hoàn thành 2026-11-19T07:28:45+07:00, 4/4 mục nghiệm thu vận hành.

- [Artifact](artifacts.json): current source và BIN/ELF của3 node khớp manifest. Không build lại hoặc copy đầu ra .pio/build cũ.
- [Runtime cuối](runtime.json): node01/02/03 ONLINE/FRESH, age cuối dưới0,4s; subscriber độc lập nhận3/2/2 telemetry. Health OK/database/broker/queue=true/dropped_events=0. Live Server HTTP200/HTML, MQTT1883, API8000, RFC22174000/4001/4002.
- [Lần kiểm đầu chưa đủ](runtime-initial-incomplete.json): node03 chưa có MQTT; không bỏ bằng chứng lỗi. Sau đó node03 kết nối mà không đổi cấu hình/source. Đọc Serial bổ sung cho thấy CONTROL AUTO/DAY/mqtt=1 và HEARTBEAT published=1.
- [Sở hữu runtime](startup.json): backend một worker PID10442/start ticks/boot ID mới, giữ DB backend/data/smartlight.db. Broker smartlight-p0-mosquitto-1. [Helper khởi động](start-as-run.py), [probe chỉ đọc](verify-as-run.py). Launcher tạm chỉ gọi command của Wokwi/Live Server đã cài qua VS Code API; bốn thư mục launcher riêng, không cài extension vào profile hoặc sửa source sản phẩm. Kết quả command ở bốn tệp *-launcher.json.

Dịch vụ giữ chạy để người dùng thao tác. Dashboard http://127.0.0.1:5500/; API http://127.0.0.1:8000/docs; MQTT127.0.0.1:1883. Live Server extension5.7.10 thực tế listen0.0.0.0:5500 dù URL/config dùng127.0.0.1; không sửa extension ngoài phạm vi. RFC2217 do extension mở trên wildcard như cấu hình sẵn. Cần đối chiếu PID/start ticks của lượt này khi dừng, không dùng PID ngày18.

Vướng mắc còn lại về khởi động: Không có. Docker thiếu socket ở kiểm đầu, kiểm lại daemon đã chạy; không tự bật autostart. Chưa kiểm DOM/render do CUA apps/browsers rỗng, chưa chạy lại toàn bộ FR, command ACK, build/tests hay30 phút ổn định. Giữ nguyên DB/source và thay đổi Git có sẵn.
