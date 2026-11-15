# Firmware đèn đường thông minh

ESP32 esp32dev, Arduino trên PlatformIO. Hiện là firmware kiểm chứng P0 (Serial, PWM, MQTT ping/pong), chưa phải ứng dụng điều khiển hoàn chỉnh.

- [Setup Docker Compose và Wokwi](docs/techs/setup.md)
- [Yêu cầu và kế hoạch SRS](docs/srs.md)
- [Kiến trúc A0](docs/techs/architecture.md)
- [Hợp đồng MQTT v1](docs/techs/mqtt.md)
- [Convention agent](AGENTS.md)
- [Task hiện tại](docs/reports/task.md)

Môi trường đã quan sát: PlatformIO Core 6.1.19, Espressif32 8.0.0, Arduino ESP32 3.3.12 (package 4.30312.261113), ESP32 libs 3.3.12. PubSubClient 2.8.0, Mosquitto image 2.1.2-alpine. P0 đạt các ca smoke test; platform/framework và PubSubClient đã pin. Xem [biên bản](docs/reports/evidence/task-002/acceptance.md) để biết nguồn bằng chứng và giới hạn timeout phiên dài. Chưa nghiệm thu cảm biến hoặc toàn hệ thống. Xem setup để biết lệnh build và các giới hạn quyền của phiên agent.
