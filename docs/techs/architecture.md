# Kiến trúc và ranh giới triển khai A0

## Tham chiếu SRS

[SRS](../srs.md) mục 2–7, 10–12, 16; [setup P0](setup.md), [MQTT v1](mqtt.md).

Tài liệu chốt thiết kế A0 cho các gói tiếp theo. Nghiệm thu môi trường xem [TASK-002](../reports/evidence/task-002/acceptance.md). Thiết kế trong tài liệu không phải bằng chứng các thành phần đã được triển khai.

## Hiện trạng đã triển khai

- Một ESP32 `esp32dev`, source dùng chung với entry point `src/main.cpp`.
- EnvironmentSmokeTest tích hợp SensorReader đọc raw cảm biến P1; LED GPIO26, năm PWM, Serial, Wi-Fi, MQTT ping/pong và heartbeat diagnostics.
- Một cấu hình Wokwi node_01, script copy artifact, Mosquitto Docker local.
- Đã có code/sơ đồ cảm biến P1 nhưng chưa nghiệm thu live. Chưa có AUTO/MANUAL, telemetry/ACK nghiệp vụ, backend, SQLite hoặc dashboard.
- Đã pin các package trong PlatformIO. PlatformIO Core 6.1.19 là phiên bản công cụ đã dùng, không được cài lại bởi tệp cấu hình dự án.

## Kiến trúc mục tiêu

```text
LDR/PIR/HC-SR04/biến trở -> ESP32 -> PWM LED
                              <-> Gateway Wokwi VS Code
                              <-> Mosquitto local
                              <-> Backend MQTT collector + FastAPI <-> SQLite
                                                                   <-> Dashboard HTTP
```

Ba node mục tiêu chạy ba phiên mô phỏng riêng, mỗi phiên một ID/client ID. Dùng chung source, build theo cấu hình riêng; không đặt nhiều ESP32 vào một sơ đồ và không nhân bản source. Hiện chỉ có node_01; cấu hình ba node sẽ được làm ở A6.

| Thành phần | Trách nhiệm và ranh giới |
|---|---|
| Firmware | Quyết định độ sáng AUTO tại biên, timer, PWM, phát hiện lỗi, lệnh và ACK |
| Broker | Chuyển tiếp MQTT; không chạy thuật toán chiếu sáng hoặc lưu lịch sử ứng dụng |
| Backend | Kiểm tra payload, trạng thái mới nhất, lưu lịch sử, gửi lệnh, theo dõi ACK, điện năng |
| SQLite | Dữ liệu bền qua restart backend; khác với persistence broker hiện đang tắt |
| Dashboard | HTTP API của backend; không tự publish MQTT hoặc coi gửi API thành node đã áp dụng |
| Wokwi | Tín hiệu/mạch mô phỏng; dòng/công suất là mô hình, không phải đo điện thật |

Node vẫn xử lý AUTO khi broker/backend dừng. MANUAL có thời hạn và fallback theo SRS 5.7. Dữ liệu cũ, offline, lỗi tải là các chiều riêng. Theo SRS, backend một worker để tránh collector trùng.

## Giao diện giữa các thành phần

- Firmware–broker–backend: [MQTT v1](mqtt.md), JSON có version và định danh phiên boot. Diagnostics P0 tách riêng.
- Dashboard–backend: endpoint và mã HTTP giữ đúng SRS 7.3. POST command trả 202 chỉ là tiếp nhận, ACK APPLIED xác nhận mục tiêu; mức PWM thật tiếp tục lấy từ telemetry.
- Backend–database: các nhóm nodes/telemetry/alerts/commands/experiments theo SRS 7.2. UTC tiếp nhận để truy vấn; uptime node để tính khoảng hoạt động.
- Firmware dự kiến tách SensorReader, LightingController, DimmingController, FaultDetector, Connectivity và Telemetry/Command theo SRS 5.1. Chưa tạo module trống trong A0.

## Hạ tầng và workspace

Broker container nghe 1883 bên trong, host chỉ publish 127.0.0.1:1883. ESP32 dùng host.wokwi.internal qua gateway VS Code; backend local dùng 127.0.0.1. Không mở cổng Internet hoặc chuyển broker public.

Giữ workspace hiện tại, infra và simulations đang nằm tại đây; không di chuyển source theo cây thư mục dự kiến trong SRS. Chỉ tạo backend/dashboard khi đến đúng gói được giao, không tạo khung trong A0.

Pin map mục tiêu giữ SRS 4.1: LDR34, PIR27, TRIG18, ECHO19, tải35, LED26. Pin map P1 đã cấu hình theo thiết kế; pin map đã nghiệm thu live P0 chỉ gồm LED26. Phải xác minh cảm biến trong A1 trước khi dùng ngưỡng trong A2.

## Thứ tự giao việc và điểm bàn giao

| Gói | Đầu vào | Đầu ra để review | Chưa làm ở gói này |
|---|---|---|---|
| A0/TASK-004 | P0 đã nghiệm thu, SRS | Kiến trúc, hợp đồng MQTT, cấu hình cố định, kiểm tra convention | Cảm biến, ứng dụng nghiệp vụ |
| A1/TASK-005 (chờ live) | Pin map, cấu hình A0 | Một mạch đủ cảm biến, Serial raw và ca PWM | AUTO/MANUAL, phân loại, fault |
| A2 | Cảm biến đã kiểm chứng | Logic ánh sáng/timer/dimming/fault, kiểm thử clock | Backend/dashboard |
| A3 | Logic và MQTT v1 | Telemetry/command/ACK/availability, reconnect | Xây giao diện web |
| A4 | Hợp đồng và fixture có nhãn | Collector/API/database/năng lượng | Tuyên bố dữ liệu fixture là live |
| A5 | API đã kiểm chứng | Dashboard và các trạng thái lỗi/lệnh | Đổi giao thức một phía |
| A6 | Một node hoàn chỉnh | Ba node định danh riêng và tích hợp | Nhân bản source |
| A7 | Bản tích hợp | Kiểm thử, thực nghiệm, runbook, tài liệu | Thêm tính năng sau đóng bản |

Mỗi gói được giao riêng, có tiêu chí nghiệm thu và nguồn bằng chứng. Không tự chạy gói kế tiếp. Thay đổi hợp đồng phải đồng bộ SRS/tài liệu liên quan và các phía, không sửa SRS để hợp thức hóa mã lệch yêu cầu.

## Kiểm tra và giới hạn

A0 kiểm tra convention, cấu hình, ví dụ JSON và đối chiếu SRS; không tính là kiểm thử mạng nghiệp vụ. Kết quả ở [bằng chứng TASK-004](../reports/evidence/task-004/convention-checks.md).

P0 đạt các ca smoke tối thiểu và phục hồi broker theo xác nhận người dùng. Timeout ở một số cuối phiên dài còn trong log, nguyên nhân chưa được xác nhận; phải theo dõi lại khi làm A3. Không suy từ P0 ra độ ổn định ba node/30 phút của P6. Không có giới hạn A0 nào được giải quyết bằng cách bỏ timeout hoặc nâng toolchain.
