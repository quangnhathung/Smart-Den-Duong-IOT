# TASK-011 — Nghiệm thu ba node, hoàn thành 4/4

- Chốt hồ sơ: 2026-11-17T16:32:01+07:00.
- Môi trường: Linux, PlatformIO/Arduino `esp32dev`, ba phiên Wokwi VS Code độc lập, MQTT Mosquitto QA, backend một worker/SQLite QA/API8001, dashboard HTML/CSS/JS qua engine Live Server của extension VS Code trên cổng5500.
- Phạm vi: P6/A6, FR-06/07/08/09/10/12; TC-12/13/14/16/17/21–25 theo [SRS](../../../../srs.md). Đây là nghiệm thu mô phỏng; EX-series, báo cáo tổng kết, video bàn giao và phần cứng thật chưa thuộc kết quả này.
- [Đặc tả được giao](task-011-accepted.md), [task làm việc trước khi đóng](task-011-working.md), [TASK-010 được lưu trước khi bắt đầu](task-010-before.md). Các bản Markdown lưu nguyên byte dùng ngữ cảnh đường dẫn của tài liệu gốc; trạng thái cũ trong đó là lịch sử.

## Thay đổi thực tế

`NodeIdentity.h` chọn chỉ số1/2/3 lúc biên dịch; mặc định1, từ chối chỉ số khác. Node ID, client ID, topic nghiệp vụ/diagnostics và nhãn Serial cùng một nguồn. Ba environment `esp32dev`, `node_02`, `node_03` dùng chung source/toolchain; RFC2217 lần lượt4000/4001/4002. Công cụ prepare chọn đúng artifact, kiểm độ mới/hash và ghi manifest; công cụ command chọn node nhưng chỉ sinh JSON.

Kiểm thử live phát hiện raw cảm biến phải chờ thay đổi control hoặc periodic2s, làm một số mẫu vượt3s. Đã sửa MqttMailbox đánh dấu snapshot khi dữ liệu cảm biến thay đổi, vẫn gộp về snapshot mới nhất, giữ khoảng cách thử publish200ms/giới hạn5 lần mỗi giây và periodic2s. Không đổi controller, timer điều khiển, pin map hoặc schema. [Ca red](sensor-coalescing-red.log) là FAIL có chủ đích để tái hiện trước sửa; [ma trận green](sensor-coalescing-green.log) và [host cuối](host-checks-final.log) xác nhận sau sửa, gồm raw-only publish/gộp cập nhật và bỏ qua bộ đếm lấy mẫu.

Ba diagram dùng cap thực thi Wokwi4MHz, cấu hình mô phỏng được nêu trong [runbook](../../../../techs/simulation.md); không dùng tốc độ này làm số đo hiệu năng MCU thật. Source backend/dashboard gốc không bị sửa; bản QA dashboard chỉ đổi URL API sang8001, có [đối chiếu](dashboard-qa-source.json).

## Kiểm tra code và build

| Tầng | Kết quả | Bằng chứng |
| --- | --- | --- |
| Python | PASS20 test | [Log cuối](python-checks-final.log) |
| Host C++ | PASS11 lượt: protocol/app/MQTT ×3, controller/sensors ×1; 2 chỉ số không hợp lệ compile-fail đúng kỳ vọng | [Log cuối](host-checks-final.log) |
| Firmware | PASS cả3 environment; RAM16,4%, Flash71,2% | [Build cuối](firmware-build-final.log) |
| Format | PASS9 tệp C++ được kiểm | [Log cuối](format-check-final.log) |
| Chuẩn bị artifact | Đúng source/environment/hash; identity được kiểm tiếp qua live | [Prepare cuối](prepare-final.log), [node01](node_01-artifact-manifest-final.json), [node02](node_02-artifact-manifest-final.json), [node03](node_03-artifact-manifest-final.json) |

## Ca tích hợp và phục hồi

| Ca live | Kết quả | Bằng chứng |
| --- | --- | --- |
| AUTO/MANUAL/ACK/PWM đúng đích, hai node còn lại không đổi | PASS30 lệnh,10/node | [Command và MQTT ACK](command-isolation-latency.json) |
| MANUAL tự về AUTO | PASS; mốc wire MANUAL→AUTO59991/59999/60003ms theo clock node | [Timeout wire](manual-timeout-wire-final.json), [snapshot](manual-timeout.json) |
| Thay LDR từng node | PASS, API/DOM/ADC/PWM không lẫn | [Sensor isolation](sensor-isolation.json) |
| OPEN_LOAD node02 và phục hồi | PASS, không lan cảnh báo | [Fault](open-load-isolation.json) |
| Dừng node02, hai node khác tiếp tục; khởi động lại đúng boot mới | PASS | [Node stop](node-stop-isolation.json) |
| Broker outage: AUTO/NIGHT/PWM25 khi mqtt0 trên cả3 | PASS, Serial chỉ đọc | [Serial offline](auto-offline-serial.json), [Dashboard suy giảm](broker-offline-dashboard.json) |
| Broker reconnect, không phát lại command cũ, lệnh mới APPLIED | PASS; dùng cả checkpoint log broker để đóng khoảng mù reconnect của recorder ban đầu | [Recovery](broker-outage-recovery.json), [No replay](broker-reconnect-no-replay-checkpoint.json) |
| Restart backend | PASS; giữ hash các telemetry cũ, cả3 boot không đổi | [Restart](backend-restart.json) |

Command→ACK tính theo thời điểm MQTT command và ACK tới recorder cùng clock, không thay cho sensor→dashboard; không đặt thêm ngưỡng mới:

| Node | Kết quả | Median ms | Max ms |
| --- | --- | ---: | ---: |
| `node_01` | 10/10 APPLIED | 230.559 | 377.106 |
| `node_02` | 10/10 APPLIED | 286.947 | 383.384 |
| `node_03` | 10/10 APPLIED | 250.896 | 347.404 |

## Sensor→dashboard: 30/30 mẫu dưới3 giây thực

Đúng10 mẫu chính/node trên firmware cuối sau mốc bắt đầu stability-02; mỗi node có1 pilot định trước, tách riêng. T0 là phím trusted Home/End trên slider LDR Wokwi. API và DOM đối chiếu node/boot/seq mới/ADC; t1 là DOM sau hai rAF. Clock được chặn sai số bằng các mốc trước/sau. Kiểm visibility lúc tác động/render và ADC trong viewport; đây là proxy render DOM, không đo photon màn hình hay chứng minh che khuất vật lý liên tục.

| Node | Mẫu chính | Khoảng median ms | Khoảng max ms |
| --- | ---: | ---: | ---: |
| node01 | 10/10 | 1133,608–1199,445 | 1216,230–1272,235 |
| node02 | 10/10 | 1005,903–1063,666 | 1155,032–1192,405 |
| node03 | 10/10 | 814,538–872,738 | 1064,496–1144,163 |

[Raw trials](latency-trials.json) giữ cả FAIL hợp lệ của firmware cũ và INCOMPLETE. Parser online đã đọc nhãn `100k lux` thành100 thay vì100000, khiến riêng các mẫu End bị gắn INCOMPLETE. [Audit độc lập](latency-final-audit.json) đọc SI k=1000 từ nhãn đã ghi, kiểm lại hành động/boot/seq/ADC/clock/visibility và chỉ gỡ lỗi xác nhận nhãn đó. Không đổi thời gian hoặc sửa raw status; SHA256 raw được chốt trong audit. Không loại mẫu chậm hợp lệ để chọn kết quả đẹp. Source audit ở [tools-as-run](tools-as-run/task011-latency-audit.py).

## Ổn định: một cửa sổ1800 giây monotonic đồng thời

Cửa sổ cố định từ **2026-11-17T15:36:05+07:00 đến16:06:05+07:00**; mốc monotonic chính xác trong [start](stability-02/start.json) và [wire audit](stability-02/wire-audit.json). Chạy LDR latency ở đầu cửa sổ rồi đưa cả3 về AUTO/NIGHT25; không có command, restart hoặc outage chủ động trong cửa sổ. [Workload](stability-workload.json), [về steady AUTO](postflight-steady-auto.json).

| Node | Boot giữ nguyên | Telemetry được nhận | Seq đầu→cuối | Max khoảng nhận thực ms |
| --- | --- | ---: | --- | ---: |
| node01 | d6fe6a8a | 1561 | 949→2509 | 4997,526 |
| node02 | 33ec5fdb | 2216 | 512→2727 | 4188,564 |
| node03 | 9fbc1fc2 | 1583 | 1638→3220 | 5323,374 |

**PASS1800s** theo [summary](stability-02/summary.json) và [audit](stability-02/wire-audit.json):5360 bản tin có sequence liên tục, boot/uptime đúng, được raw recorder bao phủ cả hai biên và khớp nguyên payload với SQLite `ACCEPTED`; cùng continuity, backend giữ PID/start ticks, không reconnect recorder/OFFLINE/command trong cửa sổ, health cuối không mất sự kiện, SQLite quick_check=ok. Khoảng nhận periodic theo clock mô phỏng có thể vượt3s thực khi VM chạy chậm; không đồng nhất với độ trễ nhân quả sensor→DOM được đo riêng ở trên.

**Giới hạn giám sát:** [HTTP/resource probe](stability-02/api-probe-status.json) là **INCOMPLETE**, nhận SIGTERM/exit143 tại1346,506s,672 mẫu; nguyên nhân chính xác chưa xác định. Không tuyên bố900 mẫu API hoặc giám sát HTTP/tài nguyên đủ30 phút. Recorder MQTT và backend độc lập tiếp tục; audit dùng toàn bộ cửa sổ đã định trước, không ghép đoạn hoặc đổi mốc để bù. API/dashboard có quan sát trước, các mẫu probe đã thu và snapshot sau; không có chứng cứ liên tục từng frame dashboard trong phần probe thiếu.

[stability-01](stability-01/summary.json) là **INCOMPLETE**, dừng trước sửa firmware, góp0 giây vào nghiệm thu cuối. Các lỗi công cụ và cách giải quyết giữ tại [qa-issues.json](qa-issues.json).

## Dữ liệu, ảnh và tái lập

- [Ảnh và metadata](screenshots.json): [3 node cuối](screenshots/three-nodes-steady-end.png), [broker offline](screenshots/broker-offline-dashboard.png), [mạch Wokwi](screenshots/wokwi-node_03-fit.png).
- [Archives](archives.json) ghi raw SHA256/size và gzip SHA256.10 stream/log được nén lossless sau cleanup; nguyên byte còn tại `/tmp/task011-20261117-135233/raw-logs/`. Giải nén bản sao trước khi chạy lại reader; không sửa hồ sơ này.
- SQLite backup ngoài Git: `/tmp/task011-20261117-135233/qa-final.db`; [hash/counts/quick_check](database-final.json). DB16101 telemetry của toàn lượt QA, gồm cả setup/lượt cũ; không nhầm5360 bản tin của cửa sổ cuối. Pending command0, phiên thực nghiệm mở0.
- [Tools as-run](tools-as-run/README.md) có đường dẫn/cổng/PID guard của lượt này. Tạo QA root mới và xác minh sở hữu khi tái lập; không chạy setup/cleanup mù quáng trên dữ liệu cũ. Build thường ngày và chuẩn bị ba node theo [simulation](../../../../techs/simulation.md).
- [Cleanup](cleanup.json) PASS: tất cả cổng QA đóng; broker QA giữ ở trạng thái stopped. Lần cleanup đầu thiếu listener18773 được giữ [riêng](cleanup-initial.json), sau đó xác minh đúng PID/argv rồi dừng. Dữ liệu/dịch vụ người dùng được giữ.
- [Bảo toàn source và lịch sử](source-preservation-final.json), [manifest](manifest.json), [kiểm tra hồ sơ](verification.json). Chỉ số PASS trong kiểm tra hồ sơ xác nhận tính toàn vẹn, không thay các kiểm thử chức năng đã chạy.

Không còn vướng mắc chặn TASK-011. Giới hạn còn lại: môi trường mô phỏng/cấu hình máy cụ thể, phần probe thiếu nêu trên, chưa có EX-series/so sánh điện năng đại diện/bàn giao cuối/phần cứng thật. TASK-012 mới là đề xuất, chưa triển khai.
