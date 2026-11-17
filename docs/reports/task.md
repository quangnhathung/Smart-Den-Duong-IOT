# TASK-011 — Hoàn thiện ba node và nghiệm thu ổn định 30 phút

- Trạng thái: Đang thực hiện
- Tiến độ: 3/4 nhóm nghiệm thu; source/config, tích hợp và lỗi/phục hồi/latency đạt; đang chờ đủ 30 phút thực
- Cập nhật: 2026-11-17T13:19:25+07:00

## Mô tả và phạm vi

Người dùng đã chốt TASK-011 là gói tích hợp ba node đầy đủ, gồm triển khai, kiểm thử live và chạy ổn định 30 phút thực. Người dùng đã giao triển khai sau khi chốt đặc tả. Lượt hiện tại thực hiện TASK-011 theo phạm vi này. Không còn phụ thuộc “chờ đặc tả chính thức”.

Đầu ra cần đạt: `node_01`, `node_02`, `node_03` dùng chung source firmware, chạy đồng thời trong ba phiên Wokwi VS Code, truyền dữ liệu riêng biệt qua MQTT → backend/SQLite → dashboard và nhận lệnh đúng đích. Dashboard giữ HTML/CSS/JavaScript thuần, chạy bằng VS Code Live Server.

TASK-010 đã hoàn thành 4/4 nhóm nghiệm thu một node; đã lưu [task trước khi chuyển](evidence/task-011/run-20261117-135233/task-010-before.md) trước khi triển khai TASK-011. [Hồ sơ TASK-010](evidence/task-010/completion-20261117-105535/README.md) là đầu vào, không phải bằng chứng ba node. [Bản mô tả cũ](evidence/task-011/specification-20261117-131925/next-task-before.md) được lưu nguyên byte; các trạng thái cũ trong bản lưu và báo cáo lịch sử không còn là trạng thái hiện hành của TASK-011.

### Giới hạn

- Giữ PlatformIO, board `esp32dev`, Arduino, entry point `src/main.cpp`, pin map, thuật toán, timer, ngưỡng và hợp đồng MQTT v1. Không nhân bản source C++ theo node.
- Backend/dashboard đã có mô hình ba node; kế hoạch không bổ sung API, đổi schema hoặc migration. Chỉ sửa lỗi liên quan trực tiếp nếu kiểm thử phát hiện, kèm tái hiện và hồi quy; nếu phải sửa giao diện, áp dụng skill ui-ux-pro-max.
- Bảo toàn bản sửa backend, thay đổi đang có và dữ liệu/bằng chứng TASK-010. Không reset hoặc chuyển nhánh làm mất công việc.
- Không bao gồm EX-series, phân tích tiết kiệm điện đại diện, báo cáo tổng kết, video bàn giao, thiết kế lại giao diện, deploy cloud hoặc mua/đăng ký dịch vụ. Không tự commit/push/merge hoặc chạy task tiếp theo.

## Tham chiếu SRS

[SRS](../srs.md): FR-06/07/08/09/10/12; mục 2.3 về độc lập node, độ trễ dashboard và ổn định; mục 6–9 về firmware/MQTT/backend/dashboard; P6 ở mục 10.2; A6 ở mục 11.2; kiểm thử mục 12.1–12.2. Ca live trọng tâm: TC-12/13/14/16/17/21/22/23/24/25. Giữ ca chống trùng, sai boot/deadline và input lỗi trong hồi quy host; không coi kết quả một node là nghiệm thu ba node.

## Phương án thực hiện đã chốt

### Firmware và cấu hình build

- Thêm cấu hình biên dịch `SMARTLIGHT_NODE_INDEX=1|2|3`, mặc định `1`; giá trị ngoài tập hợp bị từ chối khi biên dịch. Một module định danh dùng chung tạo node ID, MQTT client ID, topic command/telemetry/ACK/availability/diagnostics và nhãn Serial từ cấu hình này.
- Topic/payload/client ID phải nhất quán. Không đổi node lúc runtime hoặc sao chép module điều khiển theo node. Boot ID vẫn tạo mỗi lần khởi động; không yêu cầu boot ID duy nhất toàn hệ thống.
- Dùng chung platform/framework/packages/dependencies đã pin; ba environment chỉ khác cấu hình node. Giữ `esp32dev` làm environment mặc định.

| Node | Environment PlatformIO dự kiến | Thư mục mô phỏng dự kiến | Cổng RFC2217 |
| --- | --- | --- | ---: |
| `node_01` | `esp32dev` — mặc định | `simulations/node_01` | 4000 |
| `node_02` | `node_02` | `simulations/node_02` | 4001 |
| `node_03` | `node_03` | `simulations/node_03` | 4002 |

### Mô phỏng và công cụ

- Thêm hai cấu hình mô phỏng với phần cứng/pin map giống node_01; kiểm sơ đồ không lệch ngoài khác biệt định danh/cổng được phép. Giữ cấu hình timeout node_01 làm hồi quy riêng, không tính thành node thứ tư.
- Mở rộng `scripts/prepare-simulation.py` với `--node node_01|node_02|node_03|all`, mặc định node_01; ánh xạ cố định node → environment. Kiểm artifact tồn tại, không rỗng, đủ mới so với source/config và SHA256 khớp sau sao chép. Manifest ghi node/environment/đường dẫn/hash BIN/ELF và đầu vào; xác nhận định danh thực qua Serial/MQTT khi chạy.
- Mở rộng `scripts/mqtt-command.py` với `--node`, mặc định node_01; telemetry đúng node/schema/boot và đủ mới theo chính sách hiện có. Giữ deadline uptime 64 bit; ca sai node chọn một node khác trong ba node. Công cụ chỉ tạo JSON, không publish.
- Công cụ Serial tiếp tục chọn qua `--port` 4000/4001/4002; bỏ thông báo gán cứng node_01 khi dùng cổng khác. Không sửa thủ công launch.json do PlatformIO sinh.

### Môi trường live

- Ba phiên Wokwi VS Code độc lập trên Linux hiện tại, mỗi phiên đúng cấu hình/artifact/node. Preflight xác nhận chạy đồng thời, client ID riêng và cổng Serial không xung đột. Dùng workspace/profile QA riêng khi cần, chỉ sao chép cấu hình/artifact, không tạo ba bộ source phát triển.
- Broker QA riêng để node truy cập qua `host.wokwi.internal:1883`; backend một worker, SQLite QA riêng/API8001; dashboard QA chạy Live Server5500. Nếu đổi URL API, chỉ đổi trong bản QA có đối chiếu source, không ghi đè cấu hình dashboard gốc.
- Kiểm quyền sở hữu tiến trình/container và cổng trước thao tác. Không giành cổng hoặc dừng dịch vụ dùng chung. Nếu chưa đáp ứng, ghi phụ thuộc và tiếp tục phần độc lập.
- Wokwi CLI trước đó Unauthorized; mặc định dùng VS Code, không yêu cầu token mới hoặc mua gói để vượt lỗi. Khả năng chạy ba phiên là điều kiện cần kiểm chứng, chưa được ghi PASS.

## Trình tự thực hiện và kiểm tra

1. **Bắt đầu:** đọc source/config và hồ sơ TASK-010, ghi trạng thái Git/hash ba repo. Lưu task hiện tại trước khi chuyển đặc tả TASK-011 sang task.md và đặt `Đang thực hiện — 0/4`. Chỉ làm khi được giao triển khai.
2. **Code/build:** tham số hóa định danh, thêm cấu hình/công cụ; chạy protocol/app/MQTT host checks cho từng chỉ số 1/2/3, controller/sensors một lượt. Kiểm client ID/topic/subscription/LWT riêng, từ chối command sai node và compile-fail khi chỉ số không hợp lệ. Kiểm prepare/generator: ánh xạ ba node, artifact thiếu/cũ/sai nguồn, mặc định tương thích, wrong-node và deadline 64 bit; giữ hồi quy Serial. Build đủ ba environment, đối chiếu manifest và xác nhận Serial/MQTT đúng node. Chạy kiểm backend/dashboard tương ứng nếu sửa các thành phần đó.
3. **Tích hợp:** cả ba ONLINE/FRESH, MQTT/API/dashboard đúng từng cảm biến. Tác động cảm biến từng node trong khi giữ đầu vào hai node kia ổn định để kiểm dữ liệu không lẫn. Gửi AUTO/MANUAL lần lượt tới cả ba; đối chiếu command ID, node/boot, ACK, PWM và dashboard; hai node còn lại không đổi vì lệnh đó. Kiểm tự về AUTO sau 60 giây mô phỏng theo hợp đồng hiện có.
4. **Lỗi/phục hồi:** tạo OPEN_LOAD node_02 rồi phục hồi, cảnh báo không lan sang node khác. Tắt node_02, hai node còn lại tiếp tục cập nhật/nhận lệnh; khởi động lại node_02, xác nhận boot mới đúng đích. Dừng/phục hồi broker QA: cả ba tiếp tục AUTO theo cảm biến khi offline, reconnect/subscribe/telemetry mới và không phát lại command cũ. Restart backend: dữ liệu cả ba còn, online xác nhận lại từ dữ liệu mới. Các ca gián đoạn thực hiện ngoài cửa sổ ổn định.
5. **Latency khi ba node cùng chạy:** thu 10 mẫu sensor→dashboard và 10 lệnh→ACK mỗi node bằng dữ liệu live; ghi node/boot/seq hoặc command ID, timestamp, điều kiện quan sát và sai số. Sensor→dashboard không quá 3 giây thực; dùng phương pháp TASK-010 với mốc tác động và render rõ, không thay bằng HTTP RTT/ACK. Command→ACK báo median/max và kết quả theo timeout hiện có, không đặt ngưỡng mới. Mẫu thiếu bằng chứng là INCOMPLETE, giữ log và thu bổ sung; không bỏ mẫu chậm hợp lệ để chọn kết quả đẹp.
6. **Ổn định:** sau ca gián đoạn, đưa ba node về AUTO, chờ ONLINE/FRESH rồi chạy đồng thời một cửa sổ liên tục ít nhất 1.800 giây theo clock monotonic máy. Không cộng ba lượt 10 phút hoặc dùng uptime mô phỏng thay thời gian thực. Thu boot/seq/uptime, khoảng cách telemetry, trạng thái MQTT/API/dashboard, sức khỏe collector, lỗi/drop hàng đợi và tài nguyên máy. Không chủ động restart/outage trong cửa sổ. Reset bất thường, collector dừng, mất dữ liệu do hàng đợi hoặc offline ngoài dự kiến làm lượt FAIL; giữ bằng chứng, xử lý rồi chạy lại đủ 30 phút, không ghép các đoạn đạt.
7. **Đóng task:** đối chiếu dữ liệu SQLite/tính toàn vẹn, tổng hợp evidence/manifest; cập nhật techs/report/checklist/task theo quy trình. Chỉ dừng tài nguyên QA do lượt này tạo, giữ dữ liệu cũ. Đề xuất TASK-012 sau đó, không tự thực hiện.

## Tiêu chí hoàn thành và tiến độ

- [x] **Nhóm 1 — Source/config/công cụ:** một source, ba environment và ba cấu hình mô phỏng, định danh nhất quán; host/Python checks liên quan và build cả ba đạt, artifact được kiểm hash và định danh live.
- [x] **Nhóm 2 — Tích hợp đúng đích:** ba node chạy đồng thời; MQTT/API/dashboard tách dữ liệu; AUTO/MANUAL/ACK/PWM và cảm biến đúng node, không tác động chéo.
- [x] **Nhóm 3 — Lỗi/phục hồi/latency:** OPEN_LOAD, tắt riêng node, broker outage/reconnect/no-replay, backend restart đạt với bằng chứng ba node; đủ 10 mẫu sensor→dashboard đạt mục tiêu 3 giây thực và 10 lệnh→ACK mỗi node có kết quả đúng hợp đồng.
- [ ] **Nhóm 4 — Ổn định và bàn giao:** một cửa sổ ba node liên tục đủ 30 phút thực đạt; collector/dữ liệu ổn định, hồ sơ tái lập và tài liệu hoàn tất, cleanup tài nguyên QA được kiểm chứng.

Chỉ ghi Hoàn thành khi đủ 4/4. Build/host/fixture không thay Wokwi live; PASS một node trước đây không tự nâng tiến độ ba node. Mỗi nhóm có bằng chứng riêng; FAIL/INCOMPLETE/chưa chạy phải ghi đúng và nêu bước xử lý.

## Đầu ra và bằng chứng bắt buộc

- Source/config/công cụ đúng phạm vi; hướng dẫn build/chạy/đo tái lập; phiên bản, hash source/artifact và cấu hình thực chạy.
- Log kiểm thử/build, Serial/MQTT/API, ảnh dashboard, snapshot dữ liệu QA; bảng latency từng mẫu, phân biệt clock mô phỏng/thời gian thực.
- Log cửa sổ ổn định có mốc monotonic bắt đầu/kết thúc, thời lượng và diễn biến từng node/collector; giữ cả lượt lỗi và cách xử lý.
- Báo cáo và manifest dưới `docs/reports/evidence/task-011/`. Không đưa secret, SQLite hoặc artifact build vào Git; ghi nơi lưu/hash dữ liệu QA và version hóa báo cáo/trích xuất cần thiết theo quy ước repo.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn lại về phạm vi. Khả năng chạy ba phiên Wokwi đồng thời và mức tải máy chưa được kiểm chứng; đây là phụ thuộc preflight, chưa phải bằng chứng task bị chặn. Nếu lỗi thực tế xuất hiện, ghi nguyên nhân/log/tác động, tiếp tục code/host/build độc lập và không hạ tiêu chí live. Wokwi CLI Unauthorized có phương án VS Code nêu trên.

## Phụ thuộc và điều kiện bắt đầu

- TASK-010 hoàn thành 4/4, giữ hồ sơ và bản sửa backend session sync; đối chiếu source ba repo trên máy này trước khi chạy.
- Người dùng đã giao triển khai TASK-011 trong lượt hiện tại.
- Có môi trường build đã pin, Wokwi VS Code/gateway, ba cổng Serial, broker QA, backend một worker/SQLite QA và VS Code Live Server. Truy cập/sửa repo anh em tuân theo quyền được cấp.
- Khi triển khai, cập nhật techs firmware/simulation/testing và phần MQTT/backend/dashboard thực sự bị ảnh hưởng. Lượt đặc tả không sửa mô tả triển khai thực tế trong techs, SRS, task.md hoặc checklist task hoàn thành.

## Nhật ký triển khai hiện tại

- 2026-11-17T13:52:33+07:00: lưu baseline ba repo, lưu task trước và đặc tả được giao; bắt đầu triển khai. Host/build/live chưa chạy.

- Cập nhật triển khai: 20 Python test, 11 lượt host + 2 compile-fail, ba build PASS. Cả ba MQTT/API/dashboard live, 30 command đúng đích, cảm biến cách ly và MANUAL timeout theo clock node đạt. CPU mô phỏng giới hạn 4 MHz theo tài liệu Wokwi để giảm tải, không đổi timer ngoại vi; đang kiểm lại live trên cấu hình này. Giữ các mẫu latency FAIL/INCOMPLETE trước khi chốt cấu hình.

- Live đã PASS: cảm biến/PWM riêng từng node; OPEN_LOAD/phục hồi node_02; TC23 tắt node_02, node_01/03 vẫn nhận lệnh; broker outage AUTO/PWM25 mqtt0 cả ba, reconnect/no-replay kiểm cả raw MQTT và log broker; restart backend giữ hash toàn bộ telemetry cũ, ba boot không đổi. Còn chốt đủ mẫu latency trên CPU4 và cửa sổ ổn định 30 phút.

## Bổ sung sửa lỗi trễ dữ liệu cảm biến

Bằng chứng node_03-sample-79 trong latency-trials.json vẫn vượt 3s trên runtime CPU4. MqttMailbox chỉ tăng generation khi controlChanged, bỏ qua thay đổi trường cảm biến đã nằm trong telemetry; raw chỉ được gửi cùng control hoặc đợi periodic 2s mô phỏng. Bổ sung so sánh trường cảm biến trên wire để kích gửi sớm, bỏ qua analogSequence/uptime và giá trị distance không hợp lệ cùng biểu diễn null. Giữ nguyên timer điều khiển, schema, heartbeat định kỳ 2s và rate-limit 200ms (tối đa 5/s). Đây là sửa FR06/SRS2.3 trong TASK-011, không thêm thuật toán chiếu sáng hoặc trường dữ liệu mới. Thêm ca red/green và kiểm lại ba build/live; stability-01 kết thúc INCOMPLETE, phải chạy cửa sổ mới đủ 1.800s sau bản sửa.

- Lượt cuối: 30/30 sensor→dashboard hợp lệ theo latency-final-audit.json, đúng 10 mẫu/node trên firmware sửa coalescing; max cận trên 1272,235ms. Giữ nguyên raw trials INCOMPLETE do parser nhãn 100k và mọi FAIL trước sửa; audit sửa riêng đơn vị k=1000, không đổi clock/loại mẫu. stability-02 bắt đầu 2026-11-17T15:36:05+07:00, chưa đủ 1.800s nên nhóm 4 chưa đạt.
