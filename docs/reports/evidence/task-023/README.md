# TASK-023 — Khởi động hệ thống local

Hoàn thành 2026-11-18T20:05:42+07:00, 4/4 mục nghiệm thu vận hành.

- [Artifact](artifacts.json): hash source và BIN/ELF đã chuẩn bị khớp cả ba manifest; .pio/build không còn đầu ra, không chạy build mới hoặc copy artifact.
- [Runtime](runtime.json): health OK, database/broker/queue=true, dropped_events=0; ba node ONLINE/FRESH, age cuối dưới1s. Subscriber MQTT độc lập nhận2 telemetry/node. Các cổng1883/8000/5500/4000/4001/4002 có listener; Live Server trả HTTP200 với HTML dashboard.
- [Sở hữu tiến trình](startup.json): backend một worker PID58865/start ticks, DB hiện có backend/data/smartlight.db; broker smartlight-p0-mosquitto-1. Ba cửa sổ Wokwi và dashboard đã mở, lệnh Start Simulator/Live Server đã gửi qua command palette.
- Giữ hệ thống chạy. Dashboard http://127.0.0.1:5500/; API http://127.0.0.1:8000/docs; MQTT127.0.0.1:1883.

Vướng mắc khởi động còn lại: Không có. Sandbox cần quyền vận hành đã cấp. Hai helper trả lỗi thiếu Pillow ở bước chụp ảnh sau khi đã gửi lệnh Wokwi; bỏ ảnh tùy chọn, dùng telemetry broker/API xác minh thực. CUA không có trình duyệt kết nối nên chưa kiểm DOM/render. Không kiểm lại toàn bộ FR, command ACK, build, host tests hay30 phút ổn định trong lượt này; không có thay đổi source/chức năng/toolchain.
