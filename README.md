# Firmware đèn đường thông minh

ESP32 esp32dev, Arduino trên PlatformIO. Firmware hiện P2/A2 có AUTO/MANUAL cục bộ, hold/dimming/fault, đọc raw LDR/PIR/HC-SR04/biến trở và MQTT diagnostics. Host checks/build đã chạy, Wokwi P2 còn chờ; chưa có MQTT command/ACK nghiệp vụ hoặc ứng dụng điều khiển hoàn chỉnh.

- [Chạy Wokwi P1/A1 và nghiệm thu cảm biến](docs/techs/simulation.md)
- [Pin map mô phỏng](docs/techs/hardware.md)
- [Module và lịch đọc cảm biến](docs/techs/firmware.md)
- [Kiểm tra P1/A1](docs/techs/testing.md)
- [Điều khiển P2/A2 và lệnh Serial AUTO/MANUAL](docs/techs/firmware.md)
- [Setup Docker Compose và Wokwi P0](docs/techs/setup.md)
- [Yêu cầu và kế hoạch SRS](docs/srs.md)
- [Kiến trúc A0](docs/techs/architecture.md)
- [Hợp đồng MQTT v1](docs/techs/mqtt.md)
- [Convention agent](AGENTS.md)
- [Task hiện tại](docs/reports/task.md)

Môi trường đã quan sát: PlatformIO Core 6.1.19 ở hồ sơ ban đầu và 6.2.0 trên Windows, Espressif32 8.0.0, Arduino ESP32 3.3.12 (package 4.30312.261113), ESP32 libs 3.3.12. PubSubClient 2.8.0, Mosquitto image 2.1.2-alpine. Platform/framework và PubSubClient đã pin. P0 đạt smoke test theo [biên bản](docs/reports/evidence/task-002/acceptance.md); P1/A1 đã nghiệm thu TASK-005 4/4, P1-01 đến P1-08 theo [bằng chứng cuối](docs/reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Giữ giới hạn timeout phiên dài, metadata và phạm vi mô phỏng đã ghi trong biên bản; chưa nghiệm thu toàn hệ thống. TASK-006 AUTO/MANUAL đã triển khai code và host checks, còn chờ Wokwi P2; chưa chốt toàn task. Xem setup/simulation để biết cách chạy và điều kiện môi trường.
