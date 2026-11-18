# Runbook trình diễn và bàn giao — TASK-012

## Phạm vi và nguồn

SRS mục9,12,13,15; [setup](techs/setup.md), [simulation](techs/simulation.md), [backend](techs/backend.md), [dashboard](techs/dashboard.md), [thực nghiệm](techs/experiments.md). Đây là hướng dẫn vận hành mô hình ba phiên Wokwi local. Kết quả diễn tập thực tế phải có hồ sơ riêng; tệp hướng dẫn không chứng minh đã chạy thành công trên máy khác.

Ba repo đặt cạnh nhau: `DoAn/firmware`, `DoAn/backend`, `DoAn/dashboard`. Giữ PlatformIO/Arduino, board esp32dev, source chung, pin map và dependency đã pin. Không đổi API/schema hoặc nâng toolchain trong buổi bảo vệ. Không dùng fixture khi thiếu dữ liệu thật.

## Trước khi bắt đầu

1. Xác nhận VS Code, PlatformIO, Wokwi4.1.0 và Live Server đã cài; license Wokwi/gateway sử dụng được. Không sao chép credential vào backup.
2. Kiểm tra cổng1883, API8000 (hoặc8001 của QA),5500 và Serial4000/4001/4002. Nếu cổng thuộc dịch vụ khác, xác minh và chọn cấu hình QA rõ ràng; không dừng process không sở hữu.
3. Kiểm tra source/artifact hash theo manifest bàn giao. Nếu source đổi, build lại đúng environment và tạo manifest mới; không dùng binary cũ như bằng chứng source mới.
4. Mỗi đợt thực nghiệm dùng QA root và SQLite riêng. Không xóa DB người dùng hoặc nhập dữ liệu tổng hợp để làm đủ mẫu.
5. Dữ liệu mô phỏng và model power được ghi rõ trên dashboard, báo cáo và phần thuyết minh. Hai thành viên cần tự luyện thao tác và trả lời câu hỏi; agent không tự nghiệm thu khả năng này.

## Khởi động từ trạng thái dịch vụ đã dừng

### 1. Broker local

Dùng cấu hình Mosquitto của dự án theo setup.md, listener loopback1883. Khởi động bằng Docker Compose nếu Docker daemon hoạt động. Đợt QA TASK-012 dùng Mosquitto native trong QA root do Docker daemon không hoạt động; nguồn/version/hash ở `broker-build.json`. Không khởi động đồng thời cả hai broker trên cùng cổng.

### 2. Firmware và ba Wokwi

Tại firmware, nếu cần build từ source:

```bash
pio run -e esp32dev -e node_02 -e node_03
python3 scripts/prepare-simulation.py --node all
```

Mở riêng `simulations/node_01`, `node_02`, `node_03` trong ba cửa sổ VS Code. Dùng **Wokwi: Start Simulator** ở từng cửa sổ. Xác nhận banner đúng node và boot, AUTO, Wi-Fi/MQTT; không chỉ kiểm nhãn trong sơ đồ. RFC2217 lần lượt4000/4001/4002. Source không nhân bản theo node.

Đợt QA dùng cap4MHz đã chốt trong diagram, không suy ra hiệu năng MCU thật. Chu kỳ/timeout của controller là thời gian mô phỏng. Độ trễ dashboard và cửa sổ ổn định30 phút được đo bằng thời gian máy.

### 3. Backend một worker

Tại repo backend trên Linux, sau khi cài đúng requirements vào venv theo README:

```bash
SMARTLIGHT_DB=/absolute/path/to/demo.db .venv/bin/python -m uvicorn smartlight.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Trên PowerShell đặt `$env:SMARTLIGHT_DB` và dùng `.venv/Scripts/python.exe`. Đường dẫn DB phải là ổ local. `.env.example` không tự được nạp. Không chạy init_db khi backend đang hoạt động; không bật nhiều worker hoặc collector thứ hai trên cùng DB.

Kiểm `GET /api/health` trả200 với database/broker/queue=true, dropped_events=0. `GET /api/nodes` phải có đủ3 node ONLINE/FRESH sau telemetry mới. Retained ONLINE hoặc lịch sử cũ chưa đủ để cấp quyền gửi lệnh.

### 4. Dashboard qua Live Server

Mở riêng repo dashboard trong VS Code, nhấp phải `index.html` → **Open with Live Server**. Truy cập `http://127.0.0.1:5500/`; không dùng file://. `config.js` mặc định API8000; nếu đợt QA dùng8001, bản QA phải trỏ8001 và ghi cấu hình. Không sửa source bàn giao chỉ để khớp cổng tạm.

Xác nhận health, ba card node, ADC/môi trường/motion, target/applied và thời điểm nhận mới. Dữ liệu lịch sử hoặc cảnh báo đã kết thúc không được diễn giải như lỗi đang hoạt động.

## Kịch bản trình diễn ngắn

| Bước | Thao tác thực | Kỳ vọng / bằng chứng |
|---|---|---|
| 1 | Chỉ tổng quan và ba mạch/Serial | Đủ3 định danh, ONLINE/FRESH; không dùng ảnh giả thay live |
| 2 | Đổi LDR node01 DAY→TWILIGHT→NIGHT | Mức nền0/50/25 sau lọc/xác nhận/dimming; hai node khác giữ độc l  ập |
| 3 | NIGHT, distance150cm rồi kích PIR | PEDESTRIAN/target70; sau hold giảm về25 |
| 4 | NIGHT, distance50cm rồi kích PIR | VEHICLE/target100; giải thích đây là quy ước |
| 5 | Gửi MANUAL80 trên dashboard, rồi AUTO | 202/PENDING→ACK APPLIED; applied tiến dần đến mục tiêu |
| 6 | Node02 tải0, sau đó khôi phục tối đa | OPEN_LOAD sau điều kiện xác nhận; alert phục hồi sau3s hợp lệ |
| 7 | Dừng riêng broker QA rồi đổi LDR node01 | UI suy giảm/khóa lệnh; Serial cho thấy AUTO vẫn phản ứng |
| 8 | Khởi động lại broker QA | Telemetry mới, ONLINE/FRESH; không phát lại command cũ |
| 9 | Xem phiên đo đã đóng, lịch sử và CSV | ID/config/biên thời gian rõ; không dùng tổng1h làm số riêng một phiên |

Giữ đủ thời gian quan sát theo clock phù hợp; không nói “đã xảy ra” trước khi đọc telemetry/ACK/Serial. Khi API lỗi, giữ nhãn dữ liệu cũ và trình bày lỗi, không chuyển sang dữ liệu giả.

## Thực nghiệm EX-series

Xem recipe/clock ở experiments.md. Chuỗi15 lượt chính phải đủ từng cửa sổ node; pilot ngoài dữ liệu chính. Tạo QA runtime có quyền sở hữu process, collector độc lập và heartbeat trước khi chạy công cụ.

```bash
python3 scripts/experiments.py plan --all
python3 scripts/experiments.py preflight --run-dir /absolute/path/to/QA_ROOT
python3 scripts/experiments.py run --run-dir /absolute/path/to/QA_ROOT --all --resume
python3 scripts/audit-experiments.py --run-dir /absolute/path/to/QA_ROOT --output /absolute/path/to/analysis-final.json --require-complete
```

`--resume` chỉ bỏ qua lượt PASS cùng recipe; không tiếp tục giữa lượt bị ngắt. FAIL/INCOMPLETE giữ nguyên, chạy lại toàn lượt bị ảnh hưởng. Không chọn phần trăm đẹp hoặc ghép các đoạn để tạo đủ thời lượng. Công cụ UI CDP là QA riêng trên profile sở hữu, không dùng trình duyệt/cửa sổ cá nhân.

## Khi có lỗi

| Dấu hiệu | Kiểm tra và xử lý |
|---|---|
| Chưa có telemetry | License/gateway, đúng binary/hash, broker loopback, node ID và topic; xem Serial trước khi sửa code |
| Health503 | Phân biệt broker/database/queue; kiểm log, quyềnDB, OS lock; không xóa dữ liệu để che lỗi |
| ONLINE nhưng stale | Cần telemetry mới đúng boot/session; không dùng retained ONLINE làm bằng chứng fresh |
| Command chưa rõ kết quả | Đọc command_id/pending_command_id; không tự gửi lại POST hoặc coi202 làAPPLIED |
| Fault không đóng | Khôi phục tải đủ điều kiện; mất broker không phải phục hồi tải |
| Lượt bị trễ/mất giám sát | Giữ nguyên raw/result, đánh dấu lỗi; sửa công cụ có bằng chứng rồi chạy lại trọn lượt |
| WPS/PDF | Bàn giao DOCX/PPTX; người dùng tự xuất PDF bằng WPS theo yêu cầu. Không coi lỗi xuấtPDF của RPC là lỗi dữ liệu thực nghiệm |

## Dừng, backup và khôi phục

1. Dừng nhận thao tác mới; đóng phiên đo bằng API và lưu CSV. Kiểm không còn phiên mở/PENDING cần giải thích.
2. Backup SQLite bằng `sqlite3.Connection.backup()` để có snapshot nhất quán khi WAL đang chạy; không chỉ copy riêng file.db đang ghi. Kiểm `PRAGMA quick_check` trên bản backup, số dòng và SHA256.
3. Lưu source ba repo, trạng thái Git, artifact, diagram/wokwi.toml, cấu hình broker/backend/dashboard, raw MQTT/Serial/probes, toàn bộ attempts kể cả lỗi, ảnh, audit, báo cáo, slide và video. Loại credential, cache, node_modules/venv khỏi gói source; runtime QA có manifest riêng.
4. Tạo manifest SHA256/size/relative path cho các tệp trong backup và kiểm lại sau khi copy/nén. Giải nén vào thư mục mới để thử toàn vẹn; không ghi đè workspace hiện tại.
5. Dừng dashboard/Live Server, backend, broker, collector và Wokwi QA theo PID/start ticks đã ghi. Chỉ dừng process thuộc đợt QA; xác minh cổng đã nhả. Giữ dịch vụ/cửa sổ của người dùng.
6. Khôi phục bằng source/config/artifact đã hash, DB backup mới được kiểm; khởi động theo đúng thứ tự ở trên. Xác nhận lịch sử còn và telemetry mới cấp freshness, rồi kiểm một lệnh AUTO có ACK. Không mở lại phiên đo cũ hoặc replay command cũ.

## Tình trạng diễn tập và bàn giao

Kết quả cold-start, video, backup/integrity và cleanup được ghi tại hồ sơ TASK-012; chỉ đánh dấu đạt sau khi chạy thật. Báo cáo DOCX/PPTX có thể mở/chỉnh trong WPS, PDF do người dùng tự xuất. Yêu cầu hai thành viên tự chạy/giải thích còn cần xác nhận trực tiếp.
