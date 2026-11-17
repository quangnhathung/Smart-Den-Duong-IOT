# Chạy Wokwi — cập nhật A3 và lịch sử P2/P1

## TASK-011 — Chuẩn bị và chạy ba cấu hình

Tại gốc firmware: `pio run -e esp32dev -e node_02 -e node_03`, sau đó `python3 scripts/prepare-simulation.py --node all`. Có thể chọn `--node node_01|node_02|node_03`; bỏ tham số giữ node_01. Mỗi BIN/ELF lấy từ environment tương ứng; prepare kiểm tồn tại/độ mới/SHA256 và ghi manifest vào build/ đang được Git ignore. Manifest ghi định danh dự kiến, không thay xác nhận Serial/MQTT live.

Cả ba ESP32 trong diagram.json dùng `cpuFrequency: "4"`: giới hạn tốc độ thực thi lệnh của bộ mô phỏng, không đổi clock ngoại vi hoặc các timer firmware. Wokwi mặc định auto cap khoảng 8 MHz; mức cap thấp hơn giảm tải máy khi chạy ba phiên. Đây không phải tần số MCU thật hoặc chứng cứ hiệu năng phần cứng. Xem [CPU frequency limit của Wokwi](https://docs.wokwi.com/guides/esp32#cpu-frequency-limit). Những sơ đồ cũ không có thuộc tính này vẫn giữ trong hồ sơ lịch sử; biến thể timeout riêng không thuộc ba node chạy đồng thời.

Mở riêng `simulations/node_01`, `simulations/node_02`, `simulations/node_03` trong ba cửa sổ VS Code rồi Wokwi: Start Simulator. Sơ đồ phần cứng giống nhau, source C++ dùng chung; cổng RFC2217 lần lượt 4000/4001/4002. Tại gốc firmware cũng có thể dùng Wokwi: Select Config File để chọn đúng toml trong từng cửa sổ. Không sửa launch.json do PlatformIO sinh. Giữ biến thể timeout node_01 làm hồi quy riêng.

Bảo đảm broker QA mà node truy cập được qua host.wokwi.internal:1883, backend một worker/SQLite riêng và Dashboard Live Server5500. Không chiếm cổng hoặc dừng dịch vụ không thuộc QA. Máy cần đủ tài nguyên cho ba mô phỏng; kiểm tốc độ mô phỏng và thời gian nhận thực, không sửa ngưỡng 3s để làm kiểm thử đạt. [Đặc tả được giao](../reports/evidence/task-011/run-20261117-135233/task-011-accepted.md); kết quả live/giới hạn chốt trong báo cáo lượt này. Tham chiếu SRS P6/A6, TC17/21–25.


## TASK-010 — môi trường nghiệm thu Linux đã hoàn tất

Lượt 2026-11-17T12:05:29+07:00: dùng Wokwi VSCode4.1.0 với profile QA riêng, node_01/source/board/pin map giữ nguyên; copy BIN/ELF hiện có vào workspace QA và kiểm hash vì extension yêu cầu artifact trong workspace. Không build lại khi artifact còn fresh. CLI0.29.1 đã có nhưng token trả Unauthorized; không tự đăng ký/mua dịch vụ, dùng phương án VSCode dự phòng đã chọn.

Broker QA11884, proxy1883 cho node và11883 cho backend, backend8001/SQLite riêng, Live Server5500 trên bản dashboard QA chỉ đổi URL API. Mất/phục hồi broker được kiểm bằng dừng/start đúng container có nhãn sở hữu, không dừng broker dùng chung. LDR được tác động thật bằng phím slider Home/End; Serial RFC2217 chỉ đọc dùng cho ca AUTO offline, không dùng làm mốc t0 latency. [Runbook, bằng chứng và cleanup](../reports/evidence/task-010/completion-20261117-105535/README.md). Các công cụ as-run có đường dẫn/PID guard riêng, cần thiết lập lượt mới trước khi tái sử dụng. Không coi một node đạt là ba node30phút hoặc EX-series đạt.


TASK-007 có banner `P3/A3 lighting control`, MQTT nghiệp vụ một node và diagnostics; build/copy theo hướng dẫn bên dưới. [Bộ kiểm tra A3 đầy đủ](mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này) gồm telemetry/command/ACK/retry/reconnect/LWT và lệnh Linux/PowerShell. Chưa chạy live A3 tại máy này; P2 đã có xác nhận PASS ở máy dev kia, không yêu cầu chạy lại toàn bộ. Các quy trình P2/P1 dưới đây giữ làm lịch sử/runbook theo firmware tương ứng, không phải kết quả A3.

# Chạy Wokwi — P2/A2 hiện tại, lưu runbook P1 bên dưới

## TASK-006: kiểm tra tối thiểu sau host/build

Rà soát sau live: RFC2217/MANUAL80/timeout60s có log gốc PASS; người vận hành xác nhận các bước khác đã chạy. [Ma trận nguồn bằng chứng](../reports/evidence/task-006/acceptance-review.md) còn thiếu file AUTO/PIR/fault/timeout/reconnect; ưu tiên xuất dữ liệu đã có, không yêu cầu chạy lại các bước đã đạt. Các bước dưới đây giữ làm runbook, không phải yêu cầu lặp toàn bộ.

### Gửi MANUAL/AUTO qua RFC2217 khi Terminal không nhận input

Sơ đồ chính node_01/wokwi.toml đã thêm `rfc2217ServerPort = 4000` trong [wokwi], giữ đường dẫn artifact. Đây là [tính năng chính thức Wokwi](https://docs.wokwi.com/vscode/project-config#serial-port-forwarding); không sửa thuật toán hoặc broker. Sau thay đổi cấu hình: F1 → Stop Simulator, rồi Start Simulator đúng cấu hình chính một lần, giữ tab hiển thị. Không build lại chỉ vì thay cổng Serial.

Từ CMD ở gốc repo, dùng Python PlatformIO (đã có pyserial3.5):

```cmd
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" scripts\wokwi-serial.py PROBE
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" scripts\wokwi-serial.py MANUAL 80
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" scripts\wokwi-serial.py AUTO
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" scripts\wokwi-serial.py MANUAL 80 --check-timeout
```

PROBE chỉ mở/đóng kết nối và xác nhận thương lượng RFC2217, không gửi lệnh điều khiển. MANUAL/AUTO tự thêm LF (`\n`), đợi LOCAL accepted=1 rồi CONTROL xác nhận mode; MANUAL còn phải applied=80 trước khi báo đạt. Client đặt DTR/RTS false trước mở để không chủ động reset ESP32. Không mở nhiều client Serial TCP đồng thời. Nếu lỗi kết nối, kiểm tra port4000 và cấu hình trước, không sửa thuật toán.

Mỗi lần chạy tạo log UTF-8 tên mới `rfc2217-<mode>-<timestamp>.log` trong evidence/task-006, ghi host timestamp, TX dạng bytes và RX Serial thực. Không ghi đè. `--check-timeout` giữ kết nối đến khi nhận MANUAL/applied rồi AUTO, mqtt luôn1 trong CONTROL đã quan sát. So uptime giữa hai dòng CONTROL để xác nhận khoảng60s mô phỏng với độ phân giải log±1s; không dùng 60s thời gian thực. Giới hạn chờ mặc định300s thực, có thể tăng `--wall-timeout 600` nếu mô phỏng chậm. Không gửi AUTO hoặc lệnh khác trong lúc kiểm tra timeout. Early fallback, mất mạng, boot lại hoặc hết thời gian chờ không được báo PASS.

Script và verifier đã có 7 test offline ở `test/host/test_wokwi_serial.py` (chạy Python với -B); test giả transport không phải bằng chứng RFC2217/Wokwi thật. Tại lượt chuẩn bị chưa có listener4000 và chưa restart Wokwi, nên việc gửi/nhận lệnh live vẫn chờ người vận hành.

Artifact chuẩn bị bằng scripts/prepare-simulation.py sau build SUCCESS. Firmware hiện banner `P2/A2 lighting control`, dòng CONTROL có mode/environment/motion/target/applied/fault/mqtt; LED không còn tự cycle. Không chạy lại nghiệm thu TASK-005; các bước P1 cũ dưới đây là lịch sử của firmware trước.

1. Chạy riêng `simulations/node_01/wokwi.toml`, giữ broker hiện có. LDR lần lượt 10000/100/1 lux (xem ADC thực), đợi filter+dwell rồi dimming: DAY0, TWILIGHT50, NIGHT25; boot đầu UNKNOWN50 là bình thường. Xem filtered ADC, không giả lux bằng ADC.
2. NIGHT, PIR Simulate Motion với distance150cm rồi50cm: mục tiêu70 rồi100. Khi PIR LOW, giữ mức cao nhất5s theo uptime rồi dim về25. Khoảng cách gần mà PIR LOW không tự kích hoạt.
3. Khi mqtt=1, nhập Serial `MANUAL 80` newline: target80 cả ban ngày. Gửi `AUTO` để về mức hiện tại, không dùng hold cũ; có thể gửi MANUAL lại và giữ60s mô phỏng để kiểm tra tự hết hạn. Không dừng broker; fallback offline đã có host test nhưng chưa đo live P2.
4. MANUAL80, đợi applied ổn định; pot về0: sau stable1s và xác nhận2s xuất OPEN_LOAD, PWM vẫn80. Gửi MANUAL0: lỗi không tự xóa. Đưa pot tối đa, MANUAL80, đợi ổn định và phục hồi3s: OK.
5. Sau khi xuất Serial/ảnh chính, Stop Simulator rồi chọn riêng `simulations/node_01/timeout/wokwi.toml`. NIGHT + PIR HIGH phải distance_valid=0/NA, motion UNKNOWN/target100; PWM/heartbeat tiếp tục. Chỉ chạy một client. Không stop/start Docker để làm bước này.

Lưu một đoạn Serial/ảnh gọn trong evidence/task-006, ghi cấu hình và giờ thực. Timing điều khiển trên theo clock mô phỏng, không theo tốc độ đồng hồ Windows. Chưa có kết quả live P2: không đánh dấu PASS từ host/build. Lệnh Serial cần newline; `LOCAL command accepted=0` nếu malformed hoặc MANUAL khi MQTT chưa nối.

## Tham chiếu và điều kiện

[SRS](../srs.md) mục 4.4, 10 P1, 11 A1, 12; [pin map](hardware.md), [ma trận kiểm tra](testing.md), [setup broker P0](setup.md). Chỉ một node/client smartlight-node_01-p0. Dừng mô phỏng cũ trước để tránh trùng client ID.

Firmware và hai cấu hình đã chạy live P1; TASK-005 hoàn thành 4/4 theo [biên bản](../reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Người dùng thao tác Wokwi; agent chạy capture và một lượt stop/start riêng broker theo ủy quyền. Các bước dưới đây là runbook tái lập, không yêu cầu chạy lại ca đã PASS. Khi lựa chọn cấu hình bị nhầm, mở riêng thư mục node_01 hoặc timeout trong VS Code để bảo đảm diagram.json cạnh wokwi.toml đúng; chỉ một mô phỏng cùng client ID.

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
