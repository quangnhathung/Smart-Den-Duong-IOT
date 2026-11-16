# Firmware đèn đường thông minh

ESP32 esp32dev, Arduino trên PlatformIO. Firmware hiện có controller P2 và MQTT nghiệp vụ A3 một node: telemetry, command AUTO/MANUAL, ACK/cache, availability/LWT và reconnect; giữ cảm biến, hold/dimming/fault, Serial và diagnostics. TASK-007 bàn giao code/test/build/hướng dẫn live; chưa chạy live A3 tại máy này, backend/API A4 đã có ở repo cùng cấp; dashboard HTML/CSS/JS A5 đã có ở repo cùng cấp, chạy qua VS Code Live Server; tích hợp MQTT/Wokwi còn chờ kiểm chứng.

- [Chạy Wokwi và hướng dẫn A3](docs/techs/simulation.md)
- [Pin map mô phỏng](docs/techs/hardware.md)
- [Module và lịch đọc cảm biến](docs/techs/firmware.md)
- [Kiểm tra host và ma trận live](docs/techs/testing.md)
- [Điều khiển P2/A2 và lệnh Serial AUTO/MANUAL](docs/techs/firmware.md)
- [Setup Docker Compose và Wokwi P0](docs/techs/setup.md)
- [Yêu cầu và kế hoạch SRS](docs/srs.md)
- [Kiến trúc A0](docs/techs/architecture.md)
- [Hợp đồng MQTT v1](docs/techs/mqtt.md)
- [Convention agent](AGENTS.md)
- [Backend/API A4](../backend/README.md)
- [Dashboard — chạy bằng Live Server](../dashboard/README.md)
- [Thiết kế và hành vi dashboard A5](docs/techs/dashboard.md)
- [Task hiện tại](docs/reports/task.md)

Môi trường đã quan sát: PlatformIO Core 6.1.19 ở hồ sơ ban đầu và 6.2.0 trên Windows, Espressif32 8.0.0, Arduino ESP32 3.3.12 (package 4.30312.261113), ESP32 libs 3.3.12. PubSubClient 2.8.0, ArduinoJson 7.4.2, Mosquitto image 2.1.2-alpine. Platform/framework, PubSubClient và ArduinoJson đã pin. P0 đạt smoke test theo [biên bản](docs/reports/evidence/task-002/acceptance.md); P1/A1 đã nghiệm thu TASK-005 4/4, P1-01 đến P1-08 theo [bằng chứng cuối](docs/reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Giữ giới hạn timeout phiên dài, metadata và phạm vi mô phỏng đã ghi trong biên bản; chưa nghiệm thu toàn hệ thống. P2 đã được người dùng xác nhận PASS tại máy dev kia, giữ nguyên hồ sơ TASK-006. TASK-007 đạt5/5 đầu ra code/test/hướng dẫn; xem [bằng chứng](docs/reports/evidence/task-007/README.md) và [lệnh kiểm tra live A3](docs/techs/mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này). Xem setup/simulation để biết cách chạy và điều kiện môi trường.
