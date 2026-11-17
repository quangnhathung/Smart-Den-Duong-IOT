# TASK-010 — Tích hợp một node MQTT–backend–dashboard

- Trạng thái: Đang thực hiện
- Tiến độ: 2/4 nhóm nghiệm thu live; nhóm 2 và 4 còn tiêu chí PENDING
- Cập nhật: 2026-11-17T09:45:17+07:00

## Rà soát flow report sau pull — 2026-11-17T09:45:17+07:00

- Trạng thái lượt rà soát: Hoàn tất 3/3 tiêu chí tài liệu; tiếp tục hồ sơ TASK-010, không mở TASK-011.
- Phạm vi: đối chiếu bản main đã pull, số nhóm nghiệm thu, JSON/manifest bằng chứng và cấu hình repo tại máy này; cập nhật báo cáo và tài liệu tổng hợp. Tham chiếu SRS10.2/12 và quy trình development.md.
- Tiêu chí hoàn tất lượt tài liệu: (1) trạng thái có nguồn và phân biệt kiểm tra mới với live cũ; (2) report/task/checklist/next-task và techs nhất quán; (3) lịch sử report và bằng chứng cũ giữ nguyên, liên kết và diff hợp lệ.
- TASK-010 vẫn Đang thực hiện, 2/4 nhóm nghiệm thu live. Không chạy lại các ca live đã PASS, đo thêm latency hoặc thay đổi dịch vụ trong lượt này.
- Kiểm tra sau pull: firmware main `7e8f5c4` chứa PR #3; cả ba repo sạch trước lượt tài liệu. 112 tệp của 4 manifest SHA256 khớp; 70 JSON bằng chứng hợp lệ. Đây là kiểm tra mới trên file đã pull, không phải chạy lại live.
- Nguồn chốt: `run-20261116-195307/final-status.json`. Nhóm 1 và 3 PASS; nhóm 2 còn UI trạng thái lệnh cuối, broker outage/reconnect/no-replay và AUTO offline; nhóm 4 còn cảm biến → dashboard đủ 10 mẫu. Đã thử 5 lượt cảm biến nhưng 0/10 mẫu đủ điều kiện; command → ACK có đủ 10 lượt, median 686,217 ms, max 1002,001 ms.
- Dashboard local dùng API8000 và chưa có trang `tests/task010-live-latency.html`; bằng chứng Windows dùng API8001/Live Server5500. Khác biệt phiên bản/cấu hình giữa các repo cần được đối chiếu trước lượt live tiếp, chưa được xác định là lỗi production. Không tự đổi cổng hoặc pull repo khác.
- Một số ghi chú cũ mất dấu; giữ nguyên nguồn cũ, dùng bản tổng hợp có dấu và JSON để đối chiếu. [Kết quả rà soát](evidence/task-010/review-20261117-094517/README.md).


## Mô tả và phạm vi

Kiểm chứng ESP32 node_01 trong Wokwi → Mosquitto local → FastAPI một worker → SQLite → Dashboard Live Server5500. Dùng ba repo hiện có tại D:/IOT; không chạy node_02/03, không dùng fixture thay live, không đổi MQTT v1/thuật toán/ngưỡng. Nguồn yêu cầu là next-task.md trước lượt này, được giữ tại [bản giao việc](evidence/task-010/run-20261116-173103/task-010-accepted.md). TASK-009 trước chuyển được giữ nguyên tại [bản lưu](evidence/task-010/run-20261116-173103/task-009-before-task010.md).

## Tham chiếu SRS

SRS6/7/8/9/12, TC17–22/26; ma trận A3-01…08 trong techs/mqtt.md và runbook backend/dashboard. Một node đạt chưa phải nghiệm thu ba node hoặc EX-series.

## Tiêu chí hoàn thành và tiến độ

- [x] Broker/Wokwi thật, backend/SQLite một chủ ghi, dashboard Live Server; node_02/03 UNKNOWN; telemetry/target/applied/clock hiện tại đúng. API/MQTT/SQLite/hash do agent thu, hiển thị Dashboard do người dùng xác nhận. Fault tải→API/SQLite đã PASS; ảnh Serial do người dùng chụp chưa có file trong repo.
- [ ] AUTO/MANUAL80/ACK/reject/timeout/60s theo node, input sai/pending guard, mất API/broker/reconnect, không replay và AUTO tiếp tục.
- [x] Restart giữ history/alerts/experiments đã lưu; gap phía API không nối năng lượng, CSV3 phiên khớp từng byte trước/sau; stats/coverage/clock đã đối chiếu. Không có lệnh chờ/phiên mở trong ca này, không chốt các tình huống đó hoặc rendering Dashboard sau reload.
- [ ] Latency cảm biến→dashboard và command→ACK ít nhất10 lượt mỗi loại; median/max/điều kiện máy, log/hash/cấu hình và kết quả thật.

## Vướng mắc và cách giải quyết

Người dùng xác nhận đã khắc phục môi trường: Python3.12,68 Pytest/Ruff PASS, SQLite, build P3/A3/prepare SUCCESS; Wokwi→MQTT→API→Dashboard live, MANUAL80/ACK/PWM80 và tự AUTO sau khoảng60s mô phỏng đã PASS. Đây là xác nhận người vận hành, tách khỏi log/ảnh trong repo. Log lỗi run-20261116-173103 là lịch sử trước khắc phục, giữ nguyên.

Lượt tiếp tục [run-20261116-180648](evidence/task-010/run-20261116-180648/README.md): API health OK, node_01 ONLINE/FRESH AUTO DAY target/applied0, node_02/03 UNKNOWN; hash BIN/ELF build/mô phỏng khớp, SQLite quick_check OK và singleton DB lock PASS. Không chạy lại pytest/build/MANUAL60s đã được xác nhận. API8001 do người dùng chọn, Dashboard5500. Không commit/push/merge.

## Kết quả tiêu chí con

Lượt hoàn thiện tiếp: ưu tiên10 lượt sensor→Dashboard live có timestamp thao tác/cảm biến/MQTT/API/render, không thay bằng command latency hoặc HTTP RTT. Giữ các PASS trước, không chạy lại. Đang kiểm khả năng quan sát/điều khiển browser/Wokwi và chuẩn bị instrumentation ngoài luồng sản phẩm; ghi mọi giới hạn phương pháp. Broker outage chỉ chuẩn bị phương án cô lập, không dừng Mosquitto dùng chung hoặc đổi ngưỡng/schema. Một bước thủ công mỗi lần nếu cần.

PASS [lượt proxy live](evidence/task-010/run-20261116-193157/README.md): preflight2 telemetry seq932/933 qua Backend1884, healthOK. Đúng một POST AUTO/command0d8f20f5-4700-4be4-b5cc-37b555396adc; Backend retry đúng1 lần sau2,041s, TIMEOUT quan sát10,089s. Hai ACK thật giữ/thả ở mốc12s từ lệnh đầu, raw hash khớp; DB lưu LATE_OR_DUPLICATE, API/SQLite cuối vẫn TIMEOUT/ACK_TIMEOUT/attempts2. Không thêm command hoặc replay sau khôi phục. Backend đã về1883/PID14144/API8001/workers1, healthOK; proxy/recorder dừng. Người dùng xác nhận Dashboard ONLINE/AUTO NIGHT25/LDR3917/dữ liệu mới19:44:21/boot3268eb79/seq963→969. SQLite/log/PASS cũ giữ nguyên, không init_db, không Pause Wokwi hoặc dừng broker.

PASS restart theo [đối chiếu mới](evidence/task-010/run-20261116-190549/README.md): người dùng xác nhận PID18828→43632/API8001/workers1, không init_db/xóa SQLite, giữ Wokwi/Mosquitto. Listener43632/start19:03:07+07, Backend run ID đã đổi, firmware boot3268eb79 giữ nguyên. Bảo toàn760 mẫu telemetry cũ,13 command,20 ACK,106 alert,3 phiên; CSV3 phiên tải lại giống từng byte. Row765→766 khác continuity, API stats không nối năng lượng qua gap. Capture mới chỉ thu sau restart, không dựng lại API outage hoặc STALE lúc khởi động.

PASS OPEN_LOAD/phục hồi theo [đối chiếu mới](evidence/task-010/run-20261116-184903/README.md):16 mẫu quanh hai đợt đều AUTO/NIGHT/NONE/target25/applied25, cùng boot. Alert30/33 đã đóng; đợt cuối seq683/uptime1323338ms/current_adc0 bắt đầu lỗi, seq692/uptime1340238ms/current_adc4095 hết lỗi và đóng alert33. Giữ riêng mốc Serial1340431ms/duty64/mqtt1 do người dùng xác nhận; ảnh chưa có trong repo. Không chạy lại OPEN_LOAD. Capture cũ kết thúc trước thao tác; chứng cứ quá khứ là telemetry lưu SQLite/API, không phải raw MQTT capture.

- PASS: hai command MANUAL80 cũ APPLIED/ACK lưu trong SQLite,32 mẫu PWM80; telemetry tự AUTO uptime193094ms. Giữ riêng mốc Serial193431/194431ms do người dùng xác nhận.
- PASS:5 input sai422, node_02 không dữ liệu409, command không tồn tại404; AUTO202/PENDING và lệnh kế tiếp409, cuối APPLIED.
- PASS: ACK thật REJECTED/EXPIRED, BOOT_MISMATCH, INVALID_COMMAND qua MQTT. Retry nguyên lệnh AUTO đã quá deadline trả ACK cũ; ID trùng đổi nội dung bị từ chối, cache gốc còn nguyên. Đây là wire probe, chưa chứng minh UI REJECTED.
- PASS:10/10 command→ACK, median686,217ms/max1002,001ms; lưu cả timestamp server và ACK MQTT. Không suy thành latency cảm biến→Dashboard.
- PASS: phiên thực1/2 đã đóng, CSV12/423 mẫu khớp API/history/stats; tính độc lập công thức điện năng, quality/clock/coverage. Phiên1 tổng0,0018346Wh/coverage92,2025%; phiên2 toàn DAY0W, không phải EX-series.
- PASS: phiên3 NIGHT25/6W đã đóng,50 mẫu CSV khớp API/stats;48 continuity gap đều không nối năng lượng. Coverage chỉ1,534987%, valid_uptime2,005s/tổng0,0033416667Wh; saving75% chỉ thuộc tập mẫu hợp lệ nhỏ, không đại diện toàn khoảng. Serial sau phục hồi có19 CONTROL giữ AUTO25/duty64/faultOK/mqtt1.
- PASS: TIMEOUT10s/ACK muộn/retry1 lần và khôi phục API/MQTT/Dashboard qua một lượt proxy thật như trên. Bài Pause2s trước đó giữ nguyên INCOMPLETE; không sửa kết quả cũ thành PASS hoặc chạy lại.
- PENDING: UI REJECTED/TIMEOUT (chưa quan sát trực tiếp), broker outage/reconnect/no-replay cho lệnh đang chờ/AUTO offline, lệnh chờ/phiên mở qua restart (không có trong ca đã chạy), latency cảm biến→Dashboard10 lượt. API mất/kết nối lại khi chuyển Backend đã được capture, không suy thành broker outage PASS.

GUI lượt trước hết thời gian chờ cấp quyền quan sát; người dùng đã phản hồi OPEN_LOAD và ảnh Serial. Không dừng cưỡng bức Backend do người dùng khởi chạy. Capture600s cũ kết thúc trước restart; giữ kết luận cũ như lịch sử, dùng snapshot/process/run ID/CSV mới để xác nhận restart thật. Phiên1/2/3 đã đóng, lượt mới không mở phiên đo. Serial sau phục hồi đo node/wall≈0,1603, telemetry thực trung vị12,70s/max15,62s dù mqtt1; cần đánh giá tốc độ mô phỏng trước ca latency, không sửa ngưỡng.

## Phụ thuộc và điều kiện bắt đầu

Người dùng đã giao TASK-010→011. Chỉ triển khai TASK-011 khi có đặc tả rõ; hiện chưa tìm thấy trong tài liệu. Giữ DB/log và lịch sử; không push/merge/reset. Nếu cần sửa tính năng backend/dashboard phải tạo nhánh công việc trước.


C?p nh?t ?o live: run-20261116-195307/trial-01-summary.json ghi INCOMPLETE do ch?a ph?n bi?t c?c trang browser/visibility; sensor50cm, MQTTseq1138 v? DOM50,7cm ?? thu th?t. B? ghi th?m page_id; ch? t?i l?i tr??c l??t2. UI stale/kh?a/kh?i ph?c ?? c? DOM th?t; c?c nh?m nghi?m thu v?n2/4, kh?ng t?nh l??t1 th?nh PASS latency.

L??t2 ?? kh?i ph?c m?c slider149cm t? raw accessibility nh?ng INCOMPLETE do ??ng page_id b? ?n tr??c render. Native observer timeout/k?t th?c phi?n; chu?n b? marker th? c?ng tr?n trang ?o v? t0 d?ng kho?ng [marker, MQTT m?i ??u ti?n] (Serial n?u c?) ?? kh?ng ph? thu?c native UI. Kh?ng l?y MQTT l?m th?i ?i?m t?c ??ng ch?nh x?c; gi? ng??ng3s v? ghi sai s?.

L??t3 nh?n renderseq1210 nh?ng MQTT50,7069cm c? tr??c marker~7,2s; INCOMPLETE, kh?ng ch?p nh?n latency?m. S?a b? ghi test ?? ch?p baseline l?c b?m, t? ch?i baseline ?? ? target, y?u c?u seq m?i sau marker v? APIreceived_at sau marker; kh?ng s?a Dashboard production/Backend/firmware. B? sung causal check tr?n d? li?u th?t ?? thu tr??c khi h??ng d?n l??t4.

L??t4 INCOMPLETE: bounded sensor latency1,469?6,081s; MQTT/API/DOMseq1240 kh?p, browser b?o hidden nh?ng ng??i d?ng x?c nh?n lu?n nh?n th?y c?nh Wokwi. Kh?ng quy l?i thao t?c. Native read-only ?? ph?c h?i sau reset kernel, ch? m? l?i Distance ?? thu h?p t0 cho l??t5. Xem trial-04-summary.json v? trial-04-user-observation.json.


Ch?t ??t thu latency: ?? thao t?c5 l??t sensor, nh?ng0/10 m?u ??t ?? ?i?u ki?n nghi?m thu. L??t1 thi?u m? trang;2 browser b?o hidden;3 m?u c? tr??c marker;4 kho?ng1,469?6,081s c?t ng??ng3s, browser hidden d? ng??i d?ng x?c nh?n hai c?a s? lu?n nh?n th?y;5 ?? c? kho?ng t?c ??ng native48cm nh?ng render tr?/?i?u ki?n trang kh?ng li?n t?c, kh?ng d?ng kho?ng~203s l?m latency s?n ph?m b?nh th??ng. C?c l??t6?10 ch?a ch?y. Kh?ng th? suy ra ch? c?n5 thao t?c n?a l? ho?n t?t. B? ?o ch?a ?n ??nh ?? g?y nhi?u thao t?c cho ng??i d?ng; kh?ng y?u c?u thao t?c c?m bi?n th?m trong ??t n?y.

Ch?t4 nh?m: nh?m1 t?ch h?p m?t node PASS; nh?m2 ?? tin c?y PENDING (UI terminal command, outage/reconnect/no-replay/AUTO offline); nh?m3 d? li?u/restart/CSV/gap PASS; nh?m4 latency PENDING (10 command?ACK PASS c?; sensor ch?a ?? m?u). Kh?ng ch?y l?i PASS c?. Backend healthOK/database/broker/queue true. Gi? nguy?n SQLite v? ?ng d?ng ?ang ch?y, kh?ng command m?i. TASK-011 ch? ??c t?.

final-status.json v? snapshot latency-events-cutoff.jsonl ch?t b?ng ch?ng hi?n c?; JSONL g?c v?n ?ang ???c collector ghi. Tra c?u PID b?ng Windows CIM b? Access denied; kh?ng d?ng process ch?a x?c minh. Snapshot l? prefix ??y ?? d?ng, kh?ng ch?nh s?a d? li?u g?c. Kh?ng commit/push/merge ho?c thay schema/thu?t to?n. Chu?n b? outage ch? d?ng ? ph??ng ?n proxy ri?ng cho Backend; ch?a c? ph??ng ?n c?t ri?ng ???ng MQTT node ?? tin c?y, kh?ng d?ng Mosquitto d?ng chung.


# TASK-010 — Trạng thái khi bàn giao để mở PR

Người dùng đã cho phép add, commit và push nhánh `tuan` ở các repository có thay đổi. Người dùng sẽ tự tạo PR vào `main`; không merge hoặc force push.

TASK-010 đang thực hiện, đạt 2/4 nhóm nghiệm thu. Tích hợp một node và lưu trữ/lịch sử/phiên đo/CSV/gap/restart đã PASS theo bằng chứng trước. TIMEOUT/ACK muộn qua proxy và khôi phục MQTT1883 đã PASS. Backend dùng API8001, Dashboard5500; không đổi thuật toán hoặc MQTT schema.

Còn PENDING: UI trạng thái lệnh cuối, broker outage/reconnect/no-replay/AUTO offline và latency cảm biến đến Dashboard. Đã thao tác 5 lượt cảm biến nhưng chưa có đủ mẫu đạt điều kiện nghiệm thu; không khẳng định đã hoàn thành 10 lượt. Xem `run-20261116-195307/final-status.json`, `trial-05-summary.json` và `latency-events-cutoff.jsonl`. Xác nhận người dùng được phân biệt với dữ liệu máy thu trực tiếp. TASK-011 vẫn chờ đặc tả chính thức.

Dashboard chỉ đổi địa chỉ API sang8001 và bổ sung bộ ghi thử nghiệm live trong `tests/`. Bộ ghi còn giới hạn về timestamp/visibility và không phải tính năng production đã nghiệm thu. Backend không có thay đổi mã nguồn nên không tạo commit riêng.

Giữ SQLite và toàn bộ log tại máy. Hai stream đang ghi tiếp được loại khỏi Git bằng đường dẫn cụ thể trong `.gitignore`; các bản chụp bằng chứng đã chốt vẫn được commit. Không đưa `.env`, SQLite, môi trường Python hoặc firmware build vào commit. Kiểm tra cú pháp JavaScript, Python AST và `git diff --check`; không chạy lại kiểm thử live đã PASS.

Một số ghi chú trong đợt đo trước bị mất dấu khi truyền qua PowerShell. Dùng bản tổng hợp này và JSON gốc để đối chiếu; không sửa dữ liệu bằng chứng gốc hoặc xóa nhật ký cũ.
