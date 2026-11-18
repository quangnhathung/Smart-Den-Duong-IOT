# Thực nghiệm và bàn giao TASK-012

## Phạm vi và trạng thái

Tham chiếu SRS9.1–9.3,12,15, P7/A7. Công cụ TASK-012 chạy từ repo firmware, dùng backend/API/SQLite và dashboard hiện có. Không đổi hợp đồng MQTT/HTTP, schema hoặc thuật toán. [Task hiện tại](../reports/task.md) là nguồn trạng thái nghiệm thu; công cụ và fixture đạt không chứng minh EX-series đã chạy.

## Môi trường

Mỗi lượt QA có runtime.json, SQLite và log mới dưới output/task-012/run-TIMESTAMP/ (Git ignore). Ghi baseline/hash ba repo, sơ đồ/artifact, phiên bản runtime, PID/start ticks và cổng trước khi chạy. Không dùng lại PID hoặc DB trong /tmp của TASK-011. API QA8001, Live Server5500, broker1883, Serial4000/4001/4002; tránh dịch vụ người dùng trên API8000 và các cổng khác. Chỉ dừng tiến trình có metadata sở hữu khớp PID/start ticks/argv.

Lượt Linux hiện tại Docker daemon không chạy sau reboot. Dùng Mosquitto2.1.2 build từ [source chính thức](https://mosquitto.org/download/) và cJSON1.7.19 trong QA, listener127.0.0.1:1883, không bật dịch vụ hệ thống. Ghi nguồn/hash/build flags; không đổi infra Docker của sản phẩm. Ba Wokwi dùng artifact đã nghiệm thu TASK-011 và cap4MHz hiện có; xác nhận lại source/target hash, không build lại khi không cần.

## Công cụ và cách chạy

- scripts/experiments.py: `plan`, `preflight`, `run`, `summarize`, `verify`. Đọc cấu hình lượt bằng `--run-dir`; `run --scenario PILOT` tách pilot khỏi dữ liệu chính, `run --all` chạy15 lượt và dừng ngay khi lượt không đạt. Không tự bỏ mẫu/lượt hoặc nối tiếp một cửa sổ bị ngắt.
- scripts/experiment-ui.cjs: Playwright/CDP trên ba profile VS Code QA; chọn đúng Wokwi iframe/workbench. Chỉ dùng click/phím/slider thật, đọc DOM để kiểm giá trị; không gán trạng thái cảm biến hoặc inject telemetry. Fit/pan chỉ chỉnh viewport. Đóng popup che khuất trước thao tác; chuẩn bị popup trước mốc thay đổi không làm đổi cảm biến.
- scripts/experiment-collector.py: bộ ghi độc lập MQTT/Serial/API; DTR/RTS false trước mở RFC2217, không gửi lệnh Serial. Ghi JSONL theo dòng, heartbeat và lỗi nguồn, giữ nguyên boot/seq/uptime64. Probe2s, không gọi HTTP503 là health thành công.
- scripts/experiment_tools: recipe cố định, lịch theo từng node và phép tính năng lượng độc lập từ SQLite; không import thuật toán reporting của backend để đối chiếu với chính nó.

```bash
python3 -B scripts/experiments.py plan --scenario EX-05 --repeat 1
python3 -B scripts/experiments.py preflight --run-dir output/task-012/run-TIMESTAMP
python3 -B scripts/experiments.py run --run-dir output/task-012/run-TIMESTAMP --scenario PILOT
python3 -B scripts/experiments.py run --run-dir output/task-012/run-TIMESTAMP --all
python3 -B scripts/experiments.py summarize --run-dir output/task-012/run-TIMESTAMP
python3 -B scripts/experiments.py verify --run-dir output/task-012/run-TIMESTAMP
```

Ví dụ TIMESTAMP là đường dẫn cần thay bằng lượt mới thực tế; không trỏ producer/setup/cleanup vào dữ liệu cũ. Collector dùng Python backend/Paho và pyserial đã cài, bridge dùng Playwright đã có. Tách dependencies QA khỏi toolchain/venv sản phẩm.

## Đồng hồ và lịch tác động

Theo lựa chọn người dùng, phiên5/10/15 phút và chu kỳ PIR30s tính theo uptime riêng mỗi node. UTC nhận dùng chọn cửa sổ và độ phủ; monotonic máy dùng kiểm tiến trình/thời gian thực. Không cộng ba uptime hoặc chia thời gian mô phỏng cho thời gian thực để tính coverage.

Node nhanh hoàn tất sớm giữ trạng thái cuối và vẫn được quan sát đến khi cả3 xong. Chọn hai đầu bằng mẫu SQLite ACCEPTED của đúng node/boot, lưu seq/uptime và UTC. Khi serialize query UTC, bao hai đầu2microsecond để tránh làm tròn timestamp vào trong rồi mất mẫu; công bố biên này trong kết quả. Phần chạy thêm của node nhanh không vào bảng so sánh chính.

Đặt PIR ở15s rồi mỗi30s trong pha có chuyển động; distance150cm cho người và50cm cho xe (giá trị UI, đồng thời giữ distance_cm thực thu). EX01 DAY thay chuyển động; EX02 NIGHT yên tĩnh; EX03/04 NIGHT người/xe. EX05 có3 pha300s:

| Pha | node01 | node02 | node03 |
| --- | --- | --- | --- |
| 0–300s | DAY | NIGHT yên tĩnh | NIGHT người |
| 300–600s | TWILIGHT | NIGHT người | NIGHT xe |
| 600–900s | NIGHT xe | DAY | NIGHT yên tĩnh |

EX06 node02 tải0 ở60s, phục hồi180s. EX07 dừng broker60s, phục hồi120s theo node02; đổi LDR node01 DAY ở75s, NIGHT ở90s và dùng Serial chứng minh AUTO tiếp tục. Các node khác vẫn quan sát độc lập.

Độ trễ tác động vật lý tối đa2s mô phỏng. Predictor lịch chỉ nội suy tối đa1s từ Serial/tốc độ đo được; không thay clock trong dữ liệu. Audit giữ mốc Serial trước/sau và sai số. Mở sẵn bảng cảm biến là thao tác chuẩn bị, không đổi lịch cảm biến. Trễ, mất nguồn giám sát, reset, queue drop hoặc thiếu kết quả vật lý ngoài kịch bản làm lượt INCOMPLETE/FAIL; giữ bằng chứng và chạy lại trọn lượt liên quan.

EX05/R1 attempt01 giữ INCOMPLETE do đổi đồng thời LDR/khoảng cách node01 tại600s có cận trễ2257ms. Các thử tối ưu click ban đầu vẫn chưa đạt ổn định, được giữ cùng hồ sơ. Bridge hiện chuẩn bị bảng và tọa độ điều khiển ở290/590s, không thay cảm biến; tại300/600s mới gửi chuột/phím thật, kiểm giá trị UI và đối chiếu raw cảm biến. Chuẩn bị sớm10s thay5s chỉ áp dụng UI của EX05; toàn bộ tác động vật lý, thời lượng, clock và giới hạn2000ms giữ nguyên. Đã so cấu hình của10 lượt chính PASS không đổi;18 lần diễn tập đổi hai đầu vào ngoài phiên đo PASS, cận lớn nhất1475ms;34 Python test PASS. Không dùng diễn tập thay kết quả EX05 chạy lại. Xem [bằng chứng](../reports/evidence/task-012/run-20261117-200024/recovery-20261118-091409/ex05-timing/).

## Năng lượng và kiểm chứng

Một phiên API chung chứa dữ liệu cả3; phân tích chính dùng cửa sổ riêng từng node với from/to/experiment_id rõ ràng. Tính độc lập hình thang theo Δuptime, cùng boot/order/continuity và0<Δt≤6s; không nối qua restart, offline, invalid hoặc queue loss. So sánh AUTO loại MANUAL/UNKNOWN/fault/verification/recovery/low-load<0,95/đổi trạng thái theo SRS. Giữ tổng năng lượng riêng, baseline DAY0W và TWILIGHT/NIGHT24W trên cùng đoạn hợp lệ; baseline0 thì saving=null.

Đối chiếu SQLite độc lập, API và CSV trong1e-9Wh; bỏ phần năng lượng của hàng đầu tại biên riêng vì không có cặp trước trong cửa sổ. Báo số mẫu, thời gian mô phỏng hợp lệ, thời gian nhận có/thiếu dữ liệu, lý do loại và coverage. EX02–05 có từng lượt, trung bình/min–max và công suất trung bình khi thời lượng hợp lệ lệch nhau. Không đặt tỷ lệ tiết kiệm mục tiêu; số75% trong fixture chỉ kiểm công thức6W so24W, không phải thành tích live.

## Kiểm tra và giới hạn hiện tại

34 Python test đã PASS:20 test cũ,12 ca recipe/clock/số học và2 ca hồi quy clock qua reboot/toàn vẹn CSV. PILOT-r01-a04 PASS đầy đủ90s/node, người/xe, fault/phục hồi và đối chiếu API/CSV. Ba pilot trước giữ INCOMPLETE (hai lượt vượt biên trễ2s, một lượt timeout chuẩn bị), không nới giới hạn. EX-01-r01-a01 đã PASS; các lượt khác đang chạy, chưa đủ điều kiện công bố15 lượt chính. Xem hồ sơ/task để biết kết quả cập nhật.

Người dùng đã cài bộ docx/pptx/pdf Anthropic trong TASK-013 và yêu cầu kiểm tra để tiếp tục; đã đọc các hướng dẫn. DOCX dùng npm docx, PPTX dùng pptxgenjs; WPS Page.SaveAsPNG/Slide.Export PNG render trực tiếp để kiểm ảnh, không cần PDF. Runtime riêng trong QA, không sửa plugin OpenAI hoặc venv sản phẩm. Đã có bản nháp Word23 trang và PPTX12 slide kiểm cấu trúc/ảnh; chưa chốt bản cuối hoặc video. Tiêu chí hai thành viên tự chạy/giải thích cần xác nhận trực tiếp, không tự ghi PASS.

## Điều chỉnh đầu ra tài liệu

Ngày 2026-11-17T21:52:03+07:00, người dùng yêu cầu nhận bản Word và tự xuất PDF bằng WPS. DOCX/PPTX là tệp bàn giao chỉnh sửa được; PDF không còn là đầu ra bắt buộc của TASK-012. WPS đã mở được mẫu DOCX/PPTX; đường RPC xuất PDF trả 0x80010105, giữ bằng chứng và không tiếp tục cài renderer chỉ để xuất PDF. Kiểm tra cấu trúc và giao diện WPS theo khả năng thực tế, không ghi đã kiểm mọi trang khi chưa làm.

## Tiếp tục qua lần khởi động máy

Lượt bị ngắt giữ INCOMPLETE và được chạy lại trọn lượt; --resume chỉ tái dùng PASS cùng recipe. Từ lần tiếp tục18/11, collector ghi host_boot_id của máy vào MQTT/Serial/probe và runner ghi cùng giá trị vào result. Audit chỉ so monotonic trong đúng cohort; bản ghi cũ chưa có tag được giữ riêng với các result cũ chưa có tag. Không đổi timestamp/raw lịch sử hoặc thuật toán sản phẩm. Hồi quy33 Python test PASS, gồm ca cố ý trùng giá trị monotonic qua ba cohort.

WPS Writer Page.SaveAsPNG đã xuất22 trang bản nháp; Presentation Slide.Export PNG xuất12 slide. Đã rà hết bản nháp và sửa tràn chữ slide9 trong generator; bản cập nhật cần render lại trước chốt. Không cần PDF để kiểm ảnh; PDF vẫn do người dùng tự xuất.

Sau khôi phục cửa sổ, EX02/R3 attempt02 INCOMPLETE ngay bước chuẩn bị do LDR bị toolbar che. Đã kéo vùng nền trống để đưa cảm biến vào viewport, không di chuyển linh kiện. Bridge chỉ gửi Home/End cho biến trở khi giá trị UI thực khác giá trị yêu cầu; bỏ thao tác vô ích khi đã1023 để tránh browser focus tự cuộn mạch. Không bỏ tác động tải0/phục hồi của EX06, không sửa recipe hoặc firmware. Các lượt bị lỗi được giữ nguyên.

Audit cuối có thêm đối chiếu toàn bộ trường payload CSV với SQLite, số mẫu/quality/continuity và tổng ba cột năng lượng sau biên đầu. Seq/uptime so bằng int, không qua float. Fixture thiếu hàng/sai công suất/NaN bị phát hiện;34 Python test PASS. Audit3 lượt cũ với raw/SQL/API/CSV đều không sai lệch; chưa coi các lượt thiếu là đã đạt.

## Công cụ phân tích và bàn giao

- `scripts/audit-experiments.py`: đọc raw MQTT, SQLite và attempt đã PASS; kiểm recipe, thời lượng, payload/seq, API đã lưu, CSV và quick_check. `--require-complete` trả lỗi nếu thiếu lượt. Không sửa attempt hoặc tạo PASS từ dữ liệu tổng hợp. Lưu hash prefix raw đã đọc; prefix có thể tăng khi collector tiếp tục ghi.
- `scripts/plot-experiments.py`: CSV45 quan sát node–lượt khi đủ15 lượt; bảng số liệu từng lần lặp và biểu đồ PNG. Trung bình/min–max tính giữa các lần lặp sau khi tổng hợp đúng thời lượng hợp lệ của ba node. Baseline EX05 tính từ năng lượng baseline/thời gian hợp lệ, không mặc định24W cho cả pha DAY.
- `scripts/build-experiment-report.cjs`, `build-experiment-slides.cjs`: dùng audit làm nguồn; Word sáu chương và12 slide16:9 với bảng/chart native. Tệp đang thiếu lượt mang nhãn đang hoàn thiện. Mỗi lần build tạo version mới, giữ tệp người dùng đã nhận. Biểu đồ Word chỉ được nhúng khi plot-source.json khớp SHA256 audit.
- `scripts/record-experiment-demo.cjs`: chỉ cho chạy sau15 lượt và audit PASS. Quay riêng workbench Wokwi qua CDP và dashboard QA qua Playwright; không chụp desktop cá nhân. Tác động UI thật, xác nhận telemetry/ACK/fault, đối chiếu CSV tải từ dashboard; MP4 khoảng7 phút1080p có phụ đề Việt, không microphone. Chưa coi RECORDED là đã QA video.
- `scripts/backup-experiments.py`: yêu cầu15 lượt audit, output mới không ghi đè; SQLite backup API/quick_check, source ba repo có trạng thái HEAD+working tree, raw gzip kiểm byte, toàn bộ attempt kể cả lỗi, cấu hình/artifact và deliverables; SHA256 và đọc lại archive để kiểm toàn vẹn. Không đóng gói profile/license/credential hoặc cache/venv/node_modules.

Runbook vận hành ở [docs/demo-runbook.md](../demo-runbook.md). Helper khôi phục/render/cold-start trong QA root có đường dẫn/PID guard của đúng máy; lưu as-run khi đóng hồ sơ. Không chạy mù helper cũ trên máy hoặc PID khác. Runtime tài liệu: docx9.15.4, pptxgenjs4.0.1, Python3.12 và WPS11.1.0.11723; log phụ thuộc/lockfile ở QA runtime/office/. WPS RPC có lỗi destructor ở teardown; helper render ghi đủ ảnh, kiểm source không đổi và chỉ dừng instance QA mới đã đóng hết tài liệu trước khi thoát.

Quay dashboard dùng context mới, được tạo và điều khiển qua cùng kết nối BrowserServer; context của kết nối khác không xuất hiện trong danh sách context hiện tại. Playwright cần FFmpeg v1013 riêng; FFmpeg hệ thống dùng cho encode/decode sau đó. Với kết nối từ xa, lưu Video bằng `saveAs()` sau khi đóng context; `path()` không được hỗ trợ. Quay thử 3 giây thực đã đạt 1920×1080/90 frame, decode thành công và mở trong Chrome. Giữ hai lần thử lỗi trong bằng chứng; thử runtime này không thay cho video demo cuối hoặc kiểm phát đầy đủ.
