# Chạy và nghiệm thu Wokwi P1/A1

## Tham chiếu và điều kiện

[SRS](../srs.md) mục 4.4, 10 P1, 11 A1, 12; [pin map](hardware.md), [ma trận kiểm tra](testing.md), [setup broker P0](setup.md). Chỉ một node/client smartlight-node_01-p0. Dừng mô phỏng cũ trước để tránh trùng client ID.

Firmware và hai cấu hình đã chuẩn bị; chưa có kết quả live P1. Người dùng vận hành Docker/Wokwi, agent không tự chạy trong TASK-005.

## 1. Chuẩn bị bằng terminal thông thường

Từ gốc firmware, build và kiểm tra SUCCESS trước khi chạy script copy:

```bash
~/.platformio/penv/bin/pio run -e esp32dev
python3 scripts/prepare-simulation.py
docker compose -f infra/compose.yaml up -d mosquitto
```

Nếu build lỗi, dừng, không lấy artifact cũ. Không bỏ pin hoặc nâng package. Chạy subscriber trước khi gửi ping, lưu vào thư mục TASK-005 mới:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_sub -h 127.0.0.1 -p 1883 -t 'huit/nhom7/smartlight/v1/node_01/diagnostics/#' -W 600 -v 2>&1 | tee -a docs/reports/evidence/task-005/mqtt-live.log
```

Terminal khác theo dõi/lưu broker nếu cần:

```bash
docker compose -f infra/compose.yaml logs -f --since 1m --no-color mosquitto 2>&1 | tee -a docs/reports/evidence/task-005/broker-live.log
```

Không ghi đè bằng chứng TASK-002. Định kỳ log bao gồm lịch sử; đánh giá theo mốc lượt thử mới.

## 2. Chạy sơ đồ chính

F1 → Wokwi: Select Config File → simulations/node_01/wokwi.toml → Wokwi: Start Simulator. Nếu chọn cấu hình không hiện, mở thư mục simulations/node_01 trong cửa sổ VS Code riêng. Build/copy vẫn chạy ở gốc firmware.

Xác nhận banner P1/A1 sensor diagnostics và Arduino 3.3.12. Serial phải có dòng SENSORS mỗi khoảng một giây; ứng dụng printf dùng CRLF để dễ đọc. Nếu vẫn hiện banner P0, kiểm tra cấu hình/đường dẫn firmware và restart sau copy. Không chạy đồng thời cấu hình chính và timeout.

- LDR: click cảm biến, đổi lux theo P1-01.
- PIR: click → Simulate Motion; có log PIR motion=1 rồi motion=0.
- Biến trở: xoay thấp/giữa/tối đa; xem current_adc, không phải mA.
- HC-SR04: đổi Distance (cm), xem distance_cm và distance_valid.
- Quan sát LED chạy vòng năm mức độc lập với cảm biến. Chưa có AUTO.

Đợi MQTT subscribed và heartbeat; terminal khác gửi ping kiểm tra hồi quy:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_pub -h 127.0.0.1 -p 1883 -t huit/nhom7/smartlight/v1/node_01/diagnostics/ping -q 1 -m task005-001
```

Subscriber phải nhận /pong task005-001, không tính dòng /ping là phản hồi. Giữ chạy 3 phút thực trong lúc đổi cảm biến, không pause; lưu cả tốc độ mô phỏng và mốc thời gian.

## 3. Timeout và broker offline

Dừng Wokwi chính; chọn simulations/node_01/timeout/wokwi.toml, khởi động riêng. Đây là sơ đồ cùng linh kiện nhưng bỏ ECHO, dùng artifact ../build. Xác nhận distance_valid=0 distance_cm=NA; Serial/PWM và heartbeat tiếp tục. Cấu hình này test không có echo từ lúc boot; kiểm thử host kiểm tra thêm chuyển từ kết quả tốt sang timeout để bảo đảm không giữ dữ liệu cũ.

Dừng bản timeout và mở lại bản chính. Stop broker theo setup, vẫn giữ Wokwi chạy; đổi LDR/biến trở, quan sát dữ liệu/PWM tiếp tục với lịch có thể chậm quanh reconnect. Start broker, đợi subscribe và kiểm tra pong mới, không restart ESP32 trong ca phục hồi. Không cần test này bằng nhiều node.

## 4. Lưu và kết thúc

Copy Serial vào docs/reports/evidence/task-005/serial-live.log, ảnh sơ đồ và điều khiển cảm biến; ghi ca nào PASS/FAIL và cấu hình chính/timeout. Không gán timestamp thực cho uptime mô phỏng. Chưa chạy thì ghi chưa chạy; dữ liệu host test không thay thế Serial thực.

Firmware chạy liên tục. Hoàn tất các ca thì Stop Simulator, dừng lệnh nghe bằng Ctrl+C rồi mới docker compose down. Không chờ Serial tự kết thúc. Nếu lỗi, giữ log và mô tả thao tác; timeout phiên dài P0 vẫn là hạn chế cần theo dõi, không sửa mạng ngoài phạm vi chỉ để ghi PASS.
