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

Build mới trong phiên agent đã PASS với core dir tạm trong /tmp, dùng platform/package có sẵn; xem cập nhật bên dưới. Chưa chạy Docker/Wokwi live. Không có kết quả nghiệm thu giả lập hoặc cảm biến. Tài liệu firmware/mạch/MQTT thử nghiệm được gộp trong trang setup này để tránh lặp giữa các trang khi mới có một kịch bản P0.

## Cập nhật TASK-002: sửa lỗi kiểu min

Log gốc [build.log](../reports/evidence/task-002/build.log) đã chạy compiler và FAIL tại EnvironmentSmokeTest.cpp do hai đối số min khác kiểu unsigned long/unsigned int. Đã thêm <algorithm>, dùng std::min<uint32_t> để thống nhất kiểu; giữ nguyên backoff tăng gấp đôi và trần 10000 ms.

Formatter PASS. Build esp32dev PASS, exit 0, 10.19 giây; RAM 47276/327680 byte, flash 896199/1310720 byte. [Log sau sửa](../reports/evidence/task-002/build-min-fix.log). Lệnh kiểm chứng trong phiên này:

```bash
clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp
PLATFORMIO_CORE_DIR=/tmp/iot-pio-check-de41spu8 PLATFORMIO_SETTING_ENABLE_TELEMETRY=no /home/quangnhathung/.platformio/penv/bin/pio run -e esp32dev
```

Core dir trên là thư mục tạm đã có, tham chiếu package/platform cài cục bộ; không phải cấu hình cần sao chép sang máy khác. Terminal thông thường vẫn dùng lệnh build ở mục 3. Không nâng phiên bản hoặc sửa quyền hệ thống. Chưa chạy copy artifact, Docker hoặc Wokwi; chưa khóa phiên bản vì còn chờ smoke test live. Giữ các log thất bại trước đó làm lịch sử, không dùng chúng để phủ nhận kết quả build mới.
