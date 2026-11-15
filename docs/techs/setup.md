# Setup P0: Docker MQTT và Wokwi một node

## Tham chiếu và hiện trạng

[SRS](../srs.md) mục 3.1, 4, 10.2–10.3, 11–12. Đây là firmware chẩn đoán môi trường, chưa có cảm biến, AUTO/MANUAL, telemetry hoặc ACK nghiệp vụ. Giữ workspace firmware hiện tại; infra nằm trong workspace này, không di chuyển thư mục cha.

Đã quan sát: PlatformIO Core 6.1.19, Espressif32 8.0.0, Arduino ESP32 3.3.12 (package 4.30312.261113), ESP32 libs 3.3.12; Docker CLI 29.9.2, Compose 5.7.0, Wokwi extension 4.1.0. Build esp32dev đã PASS sau sửa lỗi min; Wokwi/MQTT live chưa được nghiệm thu. Platform chưa pin trong platformio.ini: chỉ khóa sau khi kiểm chứng build và smoke test thành công, theo SRS. PubSubClient được khai báo chính xác 2.8 cho firmware mới.

## 1. Điều kiện và broker Docker

Dùng Linux với Docker Engine/Compose hoạt động, Internet để tải image/dependency và chạy Wokwi, VS Code có PlatformIO và Wokwi. Bạn chạy các lệnh từ gốc firmware bằng terminal thông thường ngoài phiên agent. Các lệnh dưới không tự cài Docker hoặc sửa quyền hệ thống.

```bash
docker version
docker compose version
mkdir -p docs/reports/evidence/task-002
docker compose -f infra/compose.yaml config --quiet
docker compose -f infra/compose.yaml pull
docker compose -f infra/compose.yaml up -d mosquitto
docker compose -f infra/compose.yaml ps
docker compose -f infra/compose.yaml port mosquitto 1883
docker compose -f infra/compose.yaml logs --tail=50 mosquitto
```

Kỳ vọng mapping `127.0.0.1:1883`, broker không bị exit. Image cố định `eclipse-mosquitto:2.1.2-alpine`; có thể lưu image digest thực tế bằng `docker image inspect eclipse-mosquitto:2.1.2-alpine --format '{{json .RepoDigests}}'`.

Broker nghe 0.0.0.0 bên trong container, Docker chỉ publish trên 127.0.0.1 của host. Không đổi mapping thành 0.0.0.0. Anonymous chỉ dành cho demo local, persistence tắt, log stdout, restart tự động tắt. Cấu hình được mount read-only. Service mqtt-client dùng host networking Linux để kiểm tra đúng đường qua cổng host; không phải chỉ thử nội bộ mạng Compose.

## 2. Kiểm tra broker từ máy

Terminal A, chạy trước (thoát sau một bản tin hoặc timeout 15 giây):

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_sub -h 127.0.0.1 -p 1883 -t huit/nhom7/smartlight/v1/diagnostics/broker -C 1 -W 15 -v
```

Terminal B:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_pub -h 127.0.0.1 -p 1883 -t huit/nhom7/smartlight/v1/diagnostics/broker -m p0-broker-001
```

Kỳ vọng A nhận đúng `p0-broker-001`; publish thành công một mình chưa đủ kết luận. Không thêm cờ retain `-r`. Lưu đầu ra thực tế vào bằng chứng; các chuỗi trên là dữ liệu thử, không phải telemetry v1.

## 3. Build firmware mới và chuẩn bị artifact

```bash
~/.platformio/penv/bin/pio --version
~/.platformio/penv/bin/pio run -e esp32dev > docs/reports/evidence/task-002/build.log 2>&1
```

Kiểm tra exit code và cuối build.log; chỉ tiếp tục nếu SUCCESS. Có thể dùng `pio` thay đường dẫn trên nếu đã có trong PATH. Không chạy bước copy chỉ vì thấy BIN/ELF có sẵn: artifact trước task có thể là code mẫu.

```bash
python3 scripts/prepare-simulation.py
```

Script kiểm tra đủ hai artifact không rỗng, không cũ hơn source/config và so SHA-256 sau copy. Lưu hai checksum được in ra. Nó không tự build, không chứng minh build trước đó thành công; người chạy phải kiểm tra build.log trước. Đích nằm trong simulations/node_01/build và bị gitignore.

## 4. Chạy Wokwi trong VS Code

1. Mở workspace firmware. F1 → Wokwi: Request a New License nếu chưa kích hoạt; hoàn tất xác nhận qua trình duyệt/VS Code. Không lưu license/token trong tài liệu hoặc source.
2. F1 → Wokwi: Select Config File, chọn simulations/node_01/wokwi.toml. Nếu extension không liệt kê cấu hình, mở thư mục simulations/node_01 trong một cửa sổ VS Code rồi chạy mô phỏng ở đó; build vẫn thực hiện tại gốc firmware.
3. F1 → Wokwi: Start Simulator. Cấu hình version 1 trỏ tương đối tới build/firmware.bin và build/firmware.elf. Mỗi lần đổi code: build, copy lại artifact rồi restart mô phỏng.
4. Quan sát Serial 115200: banner `P0 smoke node_01 Arduino=...`, `ready=1`, và các mức 0/25/50/70/100% lặp mỗi 2 giây. Duty tương ứng 0/64/128/179/255. Lưu log và ảnh LED.
5. Chờ `MQTT connected; ping subscribed`. Nếu không xuất hiện, xem wifi/status và cách xử lý bên dưới. Chỉ có banner không chứng minh đã kết nối MQTT.

Pin map kiểm chứng: ESP32 board-esp32-devkit-c-v4, GPIO26 → điện trở 220 Ω → LED vàng A; LED C → GND. Không có sensor trong sơ đồ P0. PWM LEDC Core 3.x ở 5 kHz, 8 bit.

## 5. MQTT hai chiều qua Wokwi

Node dùng Wi-Fi Wokwi-GUEST không mật khẩu, channel 6, broker host.wokwi.internal:1883 qua gateway VS Code. Host dùng 127.0.0.1:1883. Client ID `smartlight-node_01-p0`: chỉ chạy một phiên node này để tránh đá kết nối nhau.

Topic nhận: `huit/nhom7/smartlight/v1/node_01/diagnostics/ping`; topic trả: cùng prefix, hậu tố `diagnostics/pong`. Payload tối đa 64 byte, trả nguyên byte; quá dài chỉ ghi từ chối. Không retained; node subscribe QoS 1, publish pong QoS 0. Không gửi bản tin này vào telemetry/command/ack nghiệp vụ.

Terminal A, chạy trước khi gửi ping:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_sub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/diagnostics/pong -C 3 -W 60 -v
```

Terminal B, sau khi node đã subscribe:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_pub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/diagnostics/ping -q 1 -m p0-001
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_pub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/diagnostics/ping -q 1 -m p0-002
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_pub -h 127.0.0.1 -t huit/nhom7/smartlight/v1/node_01/diagnostics/ping -q 1 -m p0-003
```

A phải nhận đúng ba payload; Serial node ghi nhận ping/publish. Không lấy log publish trên host làm bằng chứng pong. PubSubClient publish dùng chung buffer: firmware đã copy payload sang buffer riêng trước khi trả lời để tránh ghi đè payload nhận.

## 6. Mất broker và khôi phục

```bash
docker compose -f infra/compose.yaml stop mosquitto
```

Giữ mô phỏng chạy ít nhất 20 giây: Serial/PWM tiếp tục, node báo mất kết nối và thử lại theo backoff 1/2/4/8/10 giây. TCP connect và chờ MQTT có timeout 1 giây mỗi bước; không phải mạng bất đồng bộ hoàn toàn, PWM có thể chậm quanh lần connect. Chưa tuyên bố đạt timing điều khiển 20 ms của firmware nghiệp vụ.

```bash
docker compose -f infra/compose.yaml start mosquitto
```

Chờ node báo subscribe lại, mở subscriber pong mới rồi gửi `p0-004` theo lệnh mục 5 (đổi -C thành 1). Cần nhận đúng pong mới mà không restart ESP32. Có thể thử payload 65 byte: kỳ vọng log rejected và không có pong tương ứng. Không sửa dữ liệu cũ để làm ca thử đạt.

## 7. Bằng chứng, nghiệm thu và dừng

Lưu build.log, broker.log, serial.log, mqtt.log, ảnh LED và kết quả từng ca trong [thư mục bằng chứng](../reports/evidence/task-002/README.md). Ghi phiên bản, checksum artifact, thời gian, thao tác, kỳ vọng và thực tế. Chưa chạy thì ghi chưa chạy. Bốn nhóm nghiệm thu TASK-002: build, Wokwi/PWM, MQTT/live, tài liệu. Chỉ đánh dấu toàn task hoàn thành khi đủ bằng chứng; sau đó khóa platform/framework đã chạy thành công và cập nhật README.

```bash
docker compose -f infra/compose.yaml logs --no-color mosquitto > docs/reports/evidence/task-002/broker.log
docker compose -f infra/compose.yaml stop mosquitto
docker compose -f infra/compose.yaml down
```

Không cần xóa volume hệ thống; không dùng docker system prune. Stop Wokwi bằng lệnh Wokwi: Stop Simulator.

## Xử lý vướng mắc

| Hiện tượng | Cách xử lý và xác nhận |
| --- | --- |
| Docker permission denied/không thấy daemon | Kiểm tra docker version trên terminal máy; khởi động Engine hoặc dùng context được phép. Agent không tự chmod socket hay thêm group. |
| Cổng 1883 bị chiếm | Kiểm tra dịch vụ đang dùng cổng; người vận hành quyết định dừng dịch vụ đó. Không tự đổi cổng lệch tài liệu. |
| PlatformIO HomeDirPermissionsError | Build bằng terminal VS Code ngoài phiên agent với cache có quyền phù hợp. Không xóa cache hoặc nâng toolchain để che lỗi quyền. |
| Copy báo artifact cũ/thiếu | Xem build.log, build thành công lại trước khi copy; không dùng artifact code mẫu. |
| Wokwi lỗi license | Xác nhận quyền tài khoản qua extension; không tự mua dịch vụ. |
| Broker local chạy nhưng node không nối | Kiểm tra cấu hình Wokwi đang chọn, gateway, hostname host.wokwi.internal và port mapping loopback; không chuyển broker public hay mở cổng Internet. |
| Không có pong | Mở subscriber trước, chờ log subscribed, kiểm tra topic, payload và tránh nhiều phiên trùng client ID. |

## Nguồn và giới hạn

[Wokwi PlatformIO](https://docs.wokwi.com/vscode/platformio), [Wokwi config](https://docs.wokwi.com/vscode/project-config), [Wokwi license](https://docs.wokwi.com/vscode/getting-started), [Mosquitto config](https://mosquitto.org/man/mosquitto-conf-5.html).

Build mới trong phiên agent đã PASS với core dir tạm trong /tmp, dùng platform/package có sẵn; xem cập nhật bên dưới. Người dùng đã chạy Docker/Wokwi; xem kết quả đối chiếu mới nhất bên dưới. Chưa nghiệm thu đủ PWM/MQTT live; chưa triển khai cảm biến. Tài liệu firmware/mạch/MQTT thử nghiệm được gộp trong trang setup này để tránh lặp giữa các trang khi mới có một kịch bản P0.

## Cập nhật TASK-002: sửa lỗi kiểu min

Ở lượt sửa min, build.log khi đó đã chạy compiler và FAIL tại EnvironmentSmokeTest.cpp do hai đối số min khác kiểu unsigned long/unsigned int. Đã thêm <algorithm>, dùng std::min<uint32_t> để thống nhất kiểu; giữ nguyên backoff tăng gấp đôi và trần 10000 ms.

Formatter PASS. Build esp32dev PASS, exit 0, 10.19 giây; RAM 47276/327680 byte, flash 896199/1310720 byte. [Log sau sửa](../reports/evidence/task-002/build-min-fix.log). Lệnh kiểm chứng trong phiên này:

```bash
clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp
PLATFORMIO_CORE_DIR=/tmp/iot-pio-check-de41spu8 PLATFORMIO_SETTING_ENABLE_TELEMETRY=no /home/quangnhathung/.platformio/penv/bin/pio run -e esp32dev
```

Core dir trên là thư mục tạm đã có, tham chiếu package/platform cài cục bộ; không phải cấu hình cần sao chép sang máy khác. Terminal thông thường vẫn dùng lệnh build ở mục 3. Không nâng phiên bản hoặc sửa quyền hệ thống. Tại lượt sửa min chưa chạy copy artifact, Docker hoặc Wokwi. Sau đó người dùng đã chạy các bước này; xem cập nhật mới bên dưới. Chưa khóa phiên bản vì còn chờ smoke test live. Giữ các log thất bại trước đó làm lịch sử, không dùng chúng để phủ nhận kết quả build mới.

## Cập nhật bằng chứng live — 2026-11-15T18:19:35+07:00

Xem [kết quả chi tiết](../reports/evidence/task-002/live-progress.md). Build mới SUCCESS 7.31 giây, BIN/ELF copy khớp checksum; Wokwi/Serial đã chạy, mới xác nhận PWM 0%/25%. Host subscriber nhận p0-broker-001 theo terminal người dùng. Broker nhận smartlight-node_01-p0 ba lần nhưng ngắt do timeout sau 22–23 giây (k15); chưa có ba pong hoặc phục hồi sau restart.

Ảnh có tốc độ mô phỏng 39%: lệch clock là giả thuyết cần kiểm chứng bằng Serial/packet capture, không phải nguyên nhân đã xác nhận. Không cần thay cấu hình broker/hostname dựa trên bằng chứng hiện có. Sau compose down phải up -d lại trước khi thử. Mở subscriber trước, đợi node subscribe rồi gửi ping; lưu đủ Serial/PWM và pong trước/sau restart. Lượt cập nhật chỉ sửa tài liệu, không chạy dịch vụ hoặc sửa firmware.

## Firmware P0 có heartbeat (lượt xử lý timeout)

EnvironmentSmokeTest hiện nghỉ 10 ms ở đầu mỗi vòng, giữ MQTT keepalive 15 giây và gọi mqtt.loop khi kết nối. Khi loop thành công, gửi heartbeat không retained mỗi 2000 ms theo millis(), payload JSON chỉ có uptime_ms, topic huit/nhom7/smartlight/v1/node_01/diagnostics/heartbeat. Timer dùng phép trừ unsigned để chịu tràn; sau mỗi lần subscribe thành công bắt đầu chu kỳ heartbeat mới. Kiểm tra buffer/kết quả publish và log HEARTBEAT published=0/1. Đây là chẩn đoán P0, không phải telemetry v1 nghiệp vụ.

Thêm log có uptime cho connect attempt/failed, thay đổi connected/disconnected, mqtt.loop lỗi và Wi-Fi reconnect. Giữ hostname, port, timeout socket 1 giây, ping/pong và retry 1/2/4/8/10 giây. Nghỉ 10 ms chỉ dành cho firmware thử P0; chưa tuyên bố đạt timing nghiệp vụ. Khoảng nghỉ giúp giảm vòng lặp bận; heartbeat cung cấp gói MQTT định kỳ. Chưa có bằng chứng live xác nhận nguyên nhân cũ hoặc hết timeout.

Build cuối sau formatter PASS (4.89 giây), xem [build-heartbeat.log](../reports/evidence/task-002/build-heartbeat.log). Script chuẩn bị artifact PASS, xem [prepare-heartbeat.log](../reports/evidence/task-002/prepare-heartbeat.log). Core dir kiểm tra tạm /tmp/iot-pio-check-de41spu8 dùng package/platform cục bộ có sẵn; không nâng toolchain. Chưa chạy Docker/Wokwi bản mới.

### Kiểm chứng bản mới

Artifact đã được chuẩn bị trong simulations/node_01/build. Khởi động broker theo mục 1, restart Wokwi để nạp bản mới. Giữ mô phỏng hiển thị, không pause. Mở terminal nhận toàn bộ topic chẩn đoán trước khi gửi ping:

```bash
docker compose -f infra/compose.yaml --profile tools run --rm mqtt-client mosquitto_sub -h 127.0.0.1 -t 'huit/nhom7/smartlight/v1/node_01/diagnostics/#' -W 240 -v | tee docs/reports/evidence/task-002/mqtt-heartbeat-live.log
```

Đợi Serial báo MQTT connected; ping subscribed và HEARTBEAT published=1. Terminal khác gửi ba ping theo mục 5. Phải thấy các dòng topic kết thúc /pong có đủ p0-001/002/003; dòng /ping không phải phản hồi. Quan sát /heartbeat và broker ít nhất 3 phút thực, không có exceeded timeout ngoài lần cố ý stop broker. Serial có đủ PWM 0/25/50/70/100. Lưu Serial thành serial-heartbeat-live.log và broker thành broker-heartbeat-live.log, không ghi đè bằng chứng cũ.

Sau đó thử stop/start broker theo mục 6, mở subscriber mới nếu cửa sổ nghe đã hết hạn hoặc bị ngắt; đợi node subscribe lại và gửi p0-004, phải có pong mà không reset ESP32. Nếu vẫn lỗi, giữ log đầy đủ và thu PCAP; chưa thay broker/hostname hoặc tăng timeout để bỏ qua lỗi. Chỉ khóa toolchain và nghiệm thu khi live đạt. PubSubClient subscribe trả true chỉ xác nhận gửi yêu cầu, pong nhận được mới xác nhận luồng hai chiều.
