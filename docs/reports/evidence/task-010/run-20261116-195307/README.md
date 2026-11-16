# TASK-010 — latency cảm biến→Dashboard và UI còn thiếu

Đang thực hiện; chưa có10 mẫu latency hoặc UI mới để đánh dấu PASS. Giữ nguyên toàn bộ bằng chứng PASS trước và SQLite, không commit/push/merge.

## Phương pháp dự kiến

Mỗi lượt cần xác định t0 là lúc tác động sensor thực trong Wokwi, t1 là snapshot sensor/Serial đầu nhận thay đổi, t2 là MQTT telemetry thật tới host, t3 là Backend/API nhận mẫu, t4 là Dashboard thật render mẫu đúng boot/seq/giá trị. Đo t4−t0 theo cùng wall clock; t4−t2 hoặc HTTP RTT chỉ là phần của đường đi, không thay thế sensor→Dashboard. Ghi độ bất định timestamp thao tác và render. Clock node chỉ đối chiếu điều khiển, không dùng để trừ wall clock.

Đọc ADC/distance/clock/seq từ telemetry thật, không phát sensor fixture hoặc gọi command là sensor. Không sửa thuật toán/threshold/chu kỳ để ép mục tiêu Dashboard≤3s đạt. Dữ liệu quá chậm hoặc vượt tiêu chí phải ghi FAIL/INCOMPLETE rõ ràng.

Đang khảo sát browser/Windows control và Wokwi automation hiện có. Wokwi4.1.0 có UI Pause/Resume/Start/Stop; chưa thấy lệnh scenario trong command manifest của extension. [Automation scenarios](https://docs.wokwi.com/wokwi-ci/automation-scenarios) được tài liệu chính thức mô tả qua CLI; cần kiểm môi trường/token trước khi chọn, không tự tạo tài khoản hoặc đổi mô phỏng đang chạy.

Sau latency/UI mới chuẩn bị outage qua kết nối riêng/instance test cô lập; không dừng broker1883 dùng chung khi chưa được đồng ý. TASK-011 chờ đặc tả.

## Bộ ghi live và giới hạn quan sát

Trang `Dashboard/tests/task010-live-latency.html` nhúng Dashboard thật, quan sát response `/api/nodes` và DOM cùng boot/sequence/distance sau hai requestAnimationFrame. Không phát command hoặc thay dữ liệu trả về. Bộ nhận loopback18765 ghi MQTT1883, browser và Serial vào JSONL; không ghi SQLite. Cổng8765 đã có PHP ngoài dự án nên bộ nhận riêng được chuyển sang18765 trước khi đo. Không dừng PHP.

Hai lần thử điều khiển Distance bằng accessibility bị guard từ chối, không thay sensor; giữ nguyên log lỗi, không tính là lượt đo. CUA hết thời gian chờ cấp quyền; không tiếp tục thử chụp/điều khiển. Người dùng đổi Distance thủ công; bộ quan sát chỉ đọc accessibility để xác định khoảng thời điểm thay đổi. Không lấy thời điểm người dùng trả lời hoặc thời điểm nhận Serial làm t0.

Với lần đọc cuối còn giá trị cũ bắt đầu tại A và lần đọc đầu thấy giá trị mới kết thúc tại B, t0 thuộc [A,B]. Khoảng này bao gồm thời gian đọc cây accessibility; không giả định field được đọc ngay đầu/cuối lời gọi. Nếu thiếu lần đọc cũ, lượt đo thiếu mốc t0. Đồng bộ clock bằng GET /time, lưu RTT và khoảng offset; render hai requestAnimationFrame chỉ là mốc xấp xỉ frame trình duyệt, không phải đo photon màn hình.

Latency được báo bằng khoảng có tính sai số clock. Chỉ PASS ngưỡng3s khi toàn khoảng không vượt3s; FAIL khi cận dưới vượt3s; khoảng cắt ngưỡng hoặc thiếu mốc/ẩn trang là INCOMPLETE. Không giảm sai số giả tạo, đổi ngưỡng hoặc dùng MQTT→Dashboard thay sensor→Dashboard.

`ui-observation-progress.json` tổng hợp DOM thực: ONLINE/mở khóa, ONLINE/khóa khi dữ liệu quá3s, dữ liệu cũ/offline/khóa. Đây là gap telemetry tự nhiên của Wokwi đang chạy chậm; không chứng minh broker outage hoặc AUTO offline. Chưa ghi nhận UI REJECTED/TIMEOUT trong lượt này. JSONL đang ghi tiếp, chưa chốt hash.


## C?p nh?t ?o live l??t1

?? quan s?t ng??i d?ng k?o Distance100?50cm (qua c?c gi? tr? trung gian), kh?ng ph?t command. MQTT seq1138/boot3268eb79/distance50,7069 t?i13:34:34.735312Z; Dashboard ghi ??ng50,7cm sau hai rAF t?i13:34:45.1142Z. `trial-01-summary.json` gi? c?c m?c th?c. K?t qu? INCOMPLETE v? nghi?m thu latency: c? visibility hidden/visible nh?ng c?c event c? ch?a mang m? trang, kh?ng x?c ??nh ch?c trang ?o n?o b? ?n. Kho?ng m? t?12,873?13,652s ch?a c?ng sai s? clock, kh?ng ???c d?ng l?m k?t lu?n PASS/FAIL3s. Kh?ng x?a ho?c s?a log c?. B? ghi b? sung page_id/time_origin/visibility cho m?i event browser; ch? t?i l?i tr??c l??t2/150cm. Ch?a c?10 m?u h?p l?.

B?n nh?m hi?n t?i: (1) t?ch h?p m?t node PASS theo h? s? tr??c; (2) ?? tin c?y PENDING ? timeout/ACK mu?n PASS c?, UI stale/kh?a/ph?c h?i ?? quan s?t live, c?n terminal command UI/broker reconnect/AUTO offline; (3) d? li?u/phi?n/CSV/gap/restart PASS theo h? s? tr??c; (4) latency PENDING ? command?ACK10 m?u PASS c?, sensor?Dashboard ch?a ??10 m?u h?p l?. TASK-011 v?n ch? ??c t?.

Chu?n b? outage: proxy ri?ng ph?a Backend c? th? ki?m m?t/ph?c h?i k?t n?i Backend m? kh?ng d?ng Mosquitto1883 d?ng chung. N? kh?ng c?t k?t n?i Wokwi?1883, do ?? kh?ng ?? ch?ng minh AUTO offline ? node. Ch?a th?c hi?n outage trong l??t n?y; c?n ph??ng ?n c? l?p ri?ng ???ng k?t n?i node tr??c khi k?t lu?n ti?u ch? ??. Kh?ng thay c?u h?nh1883 ?ang ho?t ??ng.


## C?p nh?t l??t2 v? ph??ng ph?p kh?ng ph? thu?c native UI

Ng??i d?ng x?c nh?n trang ?? ghi l??t2. Raw accessibility cho th?y slider cu?i149cm, gi? ?n ??nh ??n khi observer d?ng; `trial-02-derived-action.json` suy ra m?c t? hai b?n ghi th?t k?m nguy?n d? li?u ngu?n, kh?ng s?a JSONL. API/MQTT/DOM c?ng boot3268eb79/seq1172/distance151,1035cm. Trang c? page_id5e90c658-15b9-4a77-87ee-0ba963c69a98; ch?nh trang n?y chuy?n hidden13:41:29.3748Z v?13:41:33.0034Z tr??c render13:41:36.0827Z. K?t lu?n INCOMPLETE, kh?ng ghi PASS3s. Kh?ng y?u c?u l?m l?i l??t2 trong b??c hi?n t?i.

Native observer ch? ??ng150cm n?n kh?ng ph?t sensor-action-observed; tool call timeout300s v? phi?n Computer Use b?o ?? k?t th?c, kh?ng g?i ti?p native UI. B? ph?n t?ch d?ng b?n suy ra t? raw cho l??t2. B? ghi m?i c? n?t B?t ??u: marker browser l? c?n d??i tr??c t?c ??ng; MQTT th?t ??u ti?n nh?n gi? tr? m?i l? c?n tr?n sau t?c ??ng. t0 ???c gi? d?ng kho?ng, kh?ng d?ng MQTT l?m timestamp t?c ??ng ch?nh x?c. Kh?ng thay firmware, schema, chu k? hay ng??ng3s. Kho?ng c?t3s v?n INCOMPLETE; kh?ng h?a ph??ng ph?p n?y cho ?? ?? ch?nh x?c trong m? ph?ng ch?m. Kh?ng c? marker th? l??t require_marker kh?ng ghi render-match. L??t3/50cm ?? chu?n b?, ch? n?p trang m?i; ch?a ??i sensor.

Ki?m tra `node --check` b? ghi JS PASS. B? ph?n t?ch hi?n0 m?u nghi?m thu h?p l?: l??t1/2 INCOMPLETE,3?10 PENDING. Hai nh?m nghi?m thu1/3 gi? PASS c?; nh?m2/4 c?n PENDING. Kh?ng ch?y l?i ca ?? PASS, kh?ng th? outage ho?c d?ng broker, kh?ng commit/push/merge. TASK-011 ch?a tri?n khai.


## L??t3: lo?i m?u tr??c marker; s?a guard b? ghi

L??t3: ng??i d?ng x?c nh?n b? ghi hi?n ?? ghi. ??i chi?u c?ng boot3268eb79/seq1210/distance50,7069cm: MQTT13:51:09.498210Z, marker13:51:16.7248Z, render13:51:17.4558Z. M?u ??n tr??c marker7,2266s n?n INCOMPLETE; kh?ng d?ng kho?ng ?m ho?c render-marker0,731s l?m sensor latency. B?ng ch?ng g?c gi? nguy?n; trial-03-summary-causal-audit.json l? k?t lu?n s?a sau ki?m tra nh?n qu?, c?n trial-03-summary.json gi? b?n ph?n t?ch ??u.

B? ghi test ???c s?a marker-baseline-v2: baseline MQTT t?i l?c b?m; t? ch?i baseline ?? ? target, ch? nh?n seq m?i c?ng boot v? API last_seen sau c?n tr?n timestamp marker ?? ??ng b?. Analyzer ?? lo?i m?u seq1210 c? b?ng causal check, assertion tr?n b?ng ch?ng th?t PASS; JS node --check PASS. Kh?ng ph?i k?t qu? nghi?m thu live c?a b? ghi m?i. Ch?a c?10 m?u latency h?p l?. L??t4/150cm chu?n b?; ch? t?i l?i tr??c t?c ??ng. Kh?ng ch?y l?i PASS c?, kh?ng ??i firmware/schema/ng??ng3s, kh?ng restart backend/broker, kh?ng commit/push/merge; TASK-011 v?n ch? ??c t?.


## L??t4 v? ??i chi?u Page Visibility

L??t4 ?? thu ???c baseline seq1239/distance69,96552cm, marker13:58:59.4735Z, MQTT/APIseq1240/distance151,1035cm13:59:04.072285Z, DOM ??ng151,1cm sau hai rAF13:59:05.5443Z. B? ghi marker-baseline-v2 ?? ch?n m?u c? th?nh c?ng. Kho?ng sensor?render1,469216?6,080600s c?t ng??ng3s, n?n INCOMPLETE. MQTT?render kho?ng1,472s ch? l? ?o?n truy?n sau MQTT, kh?ng thay sensor latency. ??ng page_id15197d89-1b03-44dd-ad2e-77abbb4505b8 b?o hidden13:59:03.2071Z?visible13:59:05.4744Z.

Ng??i d?ng x?c nh?n trang ?o lu?n nh?n th?y b?n c?nh Wokwi; l?u ri?ng trial-04-user-observation.json. Kh?ng quy nguy?n nh?n hidden cho ng??i d?ng chuy?n tab. Ch?a x?c ??nh nguy?n nh?n kh?c bi?t gi?a quan s?t ng??i d?ng v? Page Visibility. Kh?ng s?a log ho?c k?t lu?n PASS3s. trial-04-summary.json gi? ??y ?? m?c/ngu?n. B? ph?n t?ch ban ??u g?p KeyError seq v? x?t c? MQTT availability; ?? gi?i h?n ??ng topic /telemetry, ch?y l?i tr?n log hi?n c? th?nh c?ng, kh?ng ch?y l?i thao t?c sensor.

Sau khi reset kernel v? kh?i t?o m?i, Computer Use list_apps/??c accessibility kh?ng screenshot ho?t ??ng tr? l?i (<1s cho l?n ??c). M? ph?ng41:11.585, t?c ??12%; b?ng Distance hi?n ??ng. Ch? ?? ngh? m? b?ng ?? quan s?t th? ??ng v? thu h?p sai s? ? l??t k? ti?p, ch?a ch?y l??t5. Kh?ng ?i?u khi?n sensor b?ng tool, kh?ng d?ng Wokwi/Mosquitto/Backend. Hai nh?m1/3 gi? PASS c?; nh?m2/4 c?n PENDING, ch?a ??10 m?u sensor latency. Kh?ng commit/push/merge; TASK-011 ch?a tri?n khai.


## Ch?t ??t thu latency theo y?u c?u r?t ng?n

?? thao t?c5 l??t sensor, nh?ng0/10 m?u ??t ?? ?i?u ki?n nghi?m thu. L??t1 thi?u m? trang;2 browser b?o hidden;3 m?u c? tr??c marker;4 kho?ng1,469?6,081s c?t ng??ng3s, browser hidden d? ng??i d?ng x?c nh?n hai c?a s? lu?n nh?n th?y;5 ?? c? kho?ng t?c ??ng native48cm nh?ng render tr?/?i?u ki?n trang kh?ng li?n t?c, kh?ng d?ng kho?ng~203s l?m latency s?n ph?m b?nh th??ng. C?c l??t6?10 ch?a ch?y. Kh?ng th? suy ra ch? c?n5 thao t?c n?a l? ho?n t?t. B? ?o ch?a ?n ??nh ?? g?y nhi?u thao t?c cho ng??i d?ng; kh?ng y?u c?u thao t?c c?m bi?n th?m trong ??t n?y.

Ch?t4 nh?m: nh?m1 t?ch h?p m?t node PASS; nh?m2 ?? tin c?y PENDING (UI terminal command, outage/reconnect/no-replay/AUTO offline); nh?m3 d? li?u/restart/CSV/gap PASS; nh?m4 latency PENDING (10 command?ACK PASS c?; sensor ch?a ?? m?u). Kh?ng ch?y l?i PASS c?. Backend healthOK/database/broker/queue true. Gi? nguy?n SQLite v? ?ng d?ng ?ang ch?y, kh?ng command m?i. TASK-011 ch? ??c t?.

final-status.json v? snapshot latency-events-cutoff.jsonl ch?t b?ng ch?ng hi?n c?; JSONL g?c v?n ?ang ???c collector ghi. Tra c?u PID b?ng Windows CIM b? Access denied; kh?ng d?ng process ch?a x?c minh. Snapshot l? prefix ??y ?? d?ng, kh?ng ch?nh s?a d? li?u g?c. Kh?ng commit/push/merge ho?c thay schema/thu?t to?n. Chu?n b? outage ch? d?ng ? ph??ng ?n proxy ri?ng cho Backend; ch?a c? ph??ng ?n c?t ri?ng ???ng MQTT node ?? tin c?y, kh?ng d?ng Mosquitto d?ng chung.
