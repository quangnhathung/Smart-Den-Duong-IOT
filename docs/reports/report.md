## 2026-11-16T11:28:57+07:00 - TASK-006 - Save implementation on tuan

- Work: fetched origin; verified TASK-005 PR #1 merge commit 9dbff58 preserves b24ac60; switched to tuan and fast-forwarded to origin/main without creating another merge commit. Preparing the requested TASK-006 commit; no push.
- Checks/results: backed up all 48 changed paths (46 existing files, 2 deletions), verified SHA-256 before/after branch switch. Build and host tests passed in the preceding review; this Git-only operation does not rerun Wokwi or touch the broker. Select only TASK-006 changes; leave TASK-005 evidence unchanged.
- Status: TASK-006 evidence remains PENDING as documented in acceptance-review.md. Saving implementation does not complete acceptance.
- Blockers: None for Git synchronization. Missing live evidence and its documented resolution remain unchanged; no unsupported PASS results added.

## 2026-11-16T11:21:17+07:00 — TASK-006 — Đối chiếu evidence live và kế hoạch commit tuan

- Trạng thái: Đang thực hiện4/5; toàn task PENDING hồ sơ, chưa chốt PASS.
- Đã làm: đọc log RFC2217, tìm CONTROL trên toàn repo ngoài cache/build; xác minh MANUAL80/applied80 và timeout23399→83399ms/mqtt1/RESULT PASS. Lưu trích đoạn fault/timeout do người dùng cung cấp vào báo cáo với nguồn rõ ràng, không tạo log gốc giả.
- Kiểm tra/kết quả: build esp32dev SUCCESS exit0 3.28s, RAM48028/327680, flash912763/1310720; bốn suite C++ host PASS,7 unittest RFC PASS; git diff --check đạt. Chưa thấy file live AUTO ba vùng/PIR-VEHICLE/OPEN_LOAD/timeout/reconnect ngoài lời xác nhận và trích đoạn người dùng.
- Vướng mắc/cách giải quyết: thiếu hồ sơ để đối chiếu độc lập các ca nêu trên; ưu tiên xuất dữ liệu đã có, không bắt kiểm thử lại toàn bộ hoặc thay đổi thuật toán. Giữ TASK-005/evidence cũ và Docker nguyên trạng.
- Git: đang main, local tuan và origin/tuan cùng b24ac60; chưa stage/checkout/commit/push/merge. Đề xuất switch tuan cùng base rồi commit chọn lọc, chỉ push khi được đồng ý. [Báo cáo, ma trận và kế hoạch](evidence/task-006/acceptance-review.md).

---

## 2026-11-16T11:03:41+07:00 — TASK-006 — Chuẩn bị Serial TCP RFC2217 cho MANUAL

- Đã làm: chỉ thêm rfc2217ServerPort=4000 trong cấu hình Wokwi chính; pyserial3.5 đã có trong Python PlatformIO. Tạo script gửi MANUAL/AUTO có LF, PROBE, ghi RX/TX timestamp và kiểm tra timeout60s theo uptime; không sửa thuật toán.
- Kiểm tra: 7 test Python offline PASS, gồm bytes newline và nhận xác nhận giả lập. Cấu hình hiện trước restart chưa có listener4000; chưa gửi lệnh live hoặc kết luận MANUAL PASS. Không cần build lại vì không sửa firmware.
- Vướng mắc: Terminal Wokwi không nhận input theo báo cáo người dùng; chưa xác minh nguyên nhân frontend. Giải quyết bằng RFC2217 chính thức, yêu cầu Stop/Start Wokwi đúng một lần rồi kiểm tra port/PROBE. Giữ TASK-006 Đang thực hiện4/5.
- [Lệnh CMD và tiêu chí](../techs/simulation.md). Không Docker/TASK-005/commit/push, không cài hoặc đổi dependency. Các test transport giả không phải evidence Wokwi.

---

## 2026-11-16T10:41:14+07:00 — TASK-006 — AUTO/MANUAL P2/A2, code và kiểm tra tự động

- Trạng thái: Đang thực hiện; 4/5 mục nghiệm thu, chờ Wokwi P2.

### Đã thực hiện

State machine thuần với cấu hình SRS có tên, filter LDR5 mẫu/hysteresis/dwell1s, AUTO/PIR/distance/invalid/max-hold5s, MANUAL0–100/60s/offline fallback và hủy hold cũ; dimming2điểm/20ms, OPEN_LOAD stable1s/detect2s/recover3s, fault độc lập mode/không tự cắt PWM. FirmwareApp thay EnvironmentSmokeTest, một chủ PWM. SensorReader chuyển pulseIn sang ISR ECHO/timeout hữu hạn; WiFi/PubSubClient thuộc task core0, atomic status/loss-count bảo vệ MANUAL cả khi mất/kết nối lại giữa poll. Giữ topic diagnostics, pin map, dependency và sơ đồ. MANUAL cục bộ qua API/Serial, chưa triển khai command/ACK A3.

File code: src/ControlConfig.h, ControlTypes.h, LightingController.h/.cpp, DimmingController.h/.cpp, FaultDetector.h/.cpp, FirmwareApp.h/.cpp, Connectivity.h/.cpp, LocalControlCommand.h/.cpp; sửa SensorReader.h/.cpp và main.cpp, bỏ EnvironmentSmokeTest.h/.cpp. Test: test/host/LightingControllerChecks.cpp, SensorReaderChecks.cpp, FirmwareAppChecks.cpp, ConnectivityChecks.cpp, Arduino.h/runtime stubs, README; scripts/check-firmware.py. Tài liệu: README, architecture/development/firmware/mqtt/simulation/testing, task/next-task/report. Evidence TASK-005 và checklists lịch sử không đổi.

### Kiểm tra và kết quả

PASS bốn suite host g++ C++17 -Wall -Wextra -Werror, formatter clang-format17.0.3 đọc cấu hình dự án; build cuối esp32dev SUCCESS exit0, 58.48s, RAM48028/327680 (14.7%), flash912763/1310720 (69.6%). Script prepare freshness/copy/hash PASS. [Log thực tế](evidence/task-006/validation.log). Test chạy code thật với GPIO/ADC/RTOS/network stub, không phải mạng thật hoặc Wokwi; không kiểm thử lại nghiệm thu TASK-005. Không chạy hoặc thao tác container.

### Vướng mắc và cách giải quyết

Đã sửa lỗi phát hiện qua test/code review: mất MQTT quá nhanh che fallback MANUAL (thêm loss-count); cạnh ECHO sau deadline và dao động PWM giữa kỳ fault (bổ sung test). Những test cuối đều PASS. Chưa xác minh live ISR/task hai core, timing và Serial/Wokwi sau thay đổi kiến trúc. Chưa coi task PASS hoặc thêm vào checklist hoàn thành. Không nâng toolchain/thêm thư viện hoặc sửa SRS để hợp thức hóa.

### Bước tiếp theo

[5 bước Wokwi P2](../techs/simulation.md): môi trường, PIR/hold, MANUAL/AUTO/60s, fault/recovery, timeout-ECHO. Artifact đã chuẩn bị. Tiếp tục cùng TASK-006 sau khi có Serial/ảnh; không tự chạy A3. Không commit/push. Lịch sử report cũ bảo toàn nguyên byte.

---

## 2026-11-16T03:04:48+07:00 — TASK-005 — Kiểm tra trước commit/push main

- Đã làm: rà 51 file TASK-005 (8 tài liệu, 43 evidence), không có file ngoài phạm vi; origin/main ngang main sau fetch. Người dùng cho phép commit/push trực tiếp main, không tạo nhánh/PR.
- Kiểm tra/kết quả: build esp32dev SUCCESS exit 0 (4.52 giây), RAM 47388 byte, flash 908071 byte; host g++ C++17 với -Wall -Wextra -Werror PASS lịch cảm biến, timeout/invalidation/recovery và tràn uint32. Rà credential/token theo mẫu không có phát hiện; liên kết Markdown nội bộ hợp lệ. Không stage .pio/BIN/ELF/.env; giữ log/ảnh nghiệm thu đã rà soát.
- Vướng mắc: Không có. Giữ nguyên giới hạn host test không thay Wokwi; không chạy lại Wokwi hoặc dừng broker. Không sửa firmware hoặc triển khai TASK-006.
- Cách xử lý: stage đúng tập file đã rà, commit theo thông điệp người dùng, push thường lên origin/main; nếu remote đổi hoặc lỗi/conflict thì dừng, không force push. Kết quả push và commit hash báo trực tiếp sau thao tác, không ghi PASS trước khi chạy.

---

## 2026-11-16T02:56:10+07:00 — TASK-005 — Nghiệm thu cuối P1/A1

- Trạng thái: Hoàn thành; 4/4 nhóm nghiệm thu, P1-01 đến P1-08 PASS trong phạm vi raw sensor/diagnostics một node.
- Đã làm: đọc toàn bộ Serial recovery mới 159 dòng, đối chiếu lịch sử MQTT recovery đã PASS; cập nhật biên bản, task/checklist/next-task và tài liệu. Không chạy lại test hoặc thao tác broker/firmware.
- Kiểm tra/kết quả: 14 mẫu SENSORS trong đoạn offline, năm mức PWM/duty/ready=1, retry và reconnect 120163 ms, heartbeat từ 122171 ms; uptime tăng, không banner boot. P1-02 đã đủ 4095/2122/0 và xác nhận vị trí núm. MQTT/pong sau recovery có bằng chứng lượt 02:29, Serial bổ sung từ lượt 02:50; ghi rõ hai lượt và nguồn xác nhận mốc thời gian.
- Vướng mắc: Không còn vướng mắc chặn TASK-005. Giữ giới hạn metadata/ảnh và timeout phiên dài chưa rõ nguyên nhân, không tuyên bố nghiệm thu toàn hệ thống.
- Cách giải quyết: nhận log bổ sung, đối chiếu dữ liệu thực; giữ các báo cáo PARTIAL cũ như lịch sử, không giả log/ảnh hoặc gộp sai timestamp.
- [Biên bản và ma trận bằng chứng](evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Đủ điều kiện đề xuất TASK-006 P2/A2, chưa triển khai. Không commit/push.

---

## 2026-11-16T02:36:12+07:00 — TASK-005 — Chốt P1-02, rà Serial offline P1-08

- Đã làm: đọc nguyên log biến trở cuối, xác nhận đủ 4095/2122/0 tại đúng uptime; vị trí tối đa/giữa/thấp nhất do người dùng xác nhận. P1-02 PASS, không thử lại.
- Kiểm tra/kết quả: TASK-005 3/4 nhóm nghiệm thu, P1-08 recovery MQTT đã PASS nhưng toàn ca vẫn PARTIAL. Tìm log đã lưu chưa có Serial offline/retry. Cửa sổ Wokwi còn mở, đọc terminal/screenshot qua UI bị timeout nên chưa xác định buffer còn hay mất.
- Vướng mắc/cách giải quyết: chỉ cần xuất đoạn Serial đang có của lượt 02:29:15–02:29:46 để chứng minh raw/PWM/retry và không boot lại; nếu không còn bằng chứng thì giữ PARTIAL, không tự tạo log hoặc ngắt broker.
- [Báo cáo chi tiết](evidence/task-005/windows-live-20261116-003644/p102-final-and-p108-gap-20261116.md). Không sửa firmware, build, commit/push, đóng TASK-005 hoặc triển khai TASK-006.

---

## 2026-11-16T02:32:06+07:00 — TASK-005 — Kiểm thử recovery P1-08 trên Windows

- Trạng thái: Bị chặn; 2/4 nhóm nghiệm thu, còn đối chiếu hồ sơ.
- Đã làm: xác minh đúng project/service/config/container Mosquitto; capture timestamp; stop riêng mosquitto, giữ offline 20 giây, start lại trong finally. Không tác động PostgreSQL/Redis hoặc source.
- Kiểm tra: PASS recovery MQTT thực tế: broker start 02:29:36, node reconnect 02:29:46, heartbeat tiếp tục, pong khớp payload lúc 02:30:19. P1-07 đã PASS với 184 giây thực và 40 heartbeat khớp Serial boot thứ hai.
- Vướng mắc: thiếu Serial chứng minh raw/PWM/retry và không reset trong khoảng offline để chốt P1-08; người dùng xác nhận ADC 4095/2122/0 nhưng chưa thấy mẫu 2122 trong log hiện có.
- Cách giải quyết: xuất đoạn Serial đang có, không thử lại các ca PASS hoặc ngắt broker thêm lần nữa. Giữ TASK-005 chưa hoàn thành; chưa triển khai TASK-006.
- Bằng chứng: [tổng hợp và timeline/MQTT/broker](evidence/task-005/windows-live-20261116-003644/p108-20261116-022831-review.md). Broker đã khôi phục, đang chạy. Không commit/push. Toàn bộ byte báo cáo cũ được giữ bên dưới.

---

## 2026-11-15T19:29:24+07:00 — TASK-005 — Triển khai mạch và raw sensor P1/A1

- Trạng thái: Bị chặn
- Tiến độ: 2/4 nhóm nghiệm thu

### Đã thực hiện

Thêm SensorReader setup/update/snapshot, raw ADC12 bit, PIR20 ms, ADC100 ms, siêu âm200 ms timeout30000 µs; timeout xóa distance cũ/cờ invalid. Tích hợp vào EnvironmentSmokeTest, banner P1/A1, log SENSORS mỗi giây, PIR đổi mức, CRLF; giữ P0 PWM/MQTT. Mở rộng sơ đồ một node, thêm cấu hình timeout ECHO dùng cùng artifact. Thêm host checks cho code SensorReader thật. Cập nhật hardware/firmware/simulation/testing, README, architecture, development và hồ sơ. Giữ main, SRS, package pin và hợp đồng MQTT.

### Kiểm tra và kết quả

PASS host pin/lịch lấy mẫu, xung trigger, giới hạn timeout, invalidation/recovery và tràn uint32; đây là stub GPIO/ADC, không phải live. Formatter và wiring/JSON/TOML/tài liệu kiểm tra tĩnh PASS. Build sạch cuối SUCCESS 9.06 giây, RAM 47388 byte, flash 908071 byte; artifact copy/hash khớp. [Bằng chứng](evidence/task-005/README.md), [host](evidence/task-005/host-checks.log), [build](evidence/task-005/build-fresh.log), [checksum](evidence/task-005/prepare-final.log). Không chạy Docker/Wokwi hoặc ca P1 live; các ca đó chưa PASS.

### Vướng mắc

Script copy từ chối artifact cũ sau lần sửa comment: build SUCCESS nhưng SCons không relink. Đã clean/rebuild thật và copy đạt; giữ log từ chối, không bỏ freshness. Còn thiếu nghiệm thu live LDR/PIR/pot/distance/PWM/MQTT và timeout. Giới hạn timeout phiên dài P0 chưa được khẳng định đã giải quyết.

### Cách giải quyết

Người dùng chạy P1-01 đến P1-08 theo simulation/testing, lưu Serial/ảnh/log đúng task. Cấu hình timeout riêng chỉ bỏ ECHO; không thay sơ đồ chính. Theo dõi polling có thể chậm quanh pulseIn/MQTT connect, không khẳng định hard realtime. Không coi lịch sử P0 là nghiệm thu P1.

### Tài liệu và bước tiếp theo

TASK-005 tiếp tục phần live, chưa vào checklist task hoàn thành; checklist các task cũ giữ nguyên. Chưa triển khai TASK-006/P2/A2. Toàn bộ byte report cũ giữ nguyên phía sau.

---

## 2026-11-15T19:15:52+07:00 — TASK-004 — Chốt kiến trúc và giao thức A0

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu

### Đã thực hiện

Tạo architecture.md về trách nhiệm, luồng, trạng thái hiện tại/mục tiêu và điểm bàn giao. Tạo mqtt.md theo SRS với topic/QoS/retain, telemetry, availability/LWT, command/ACK, deadline_uptime_ms, result/reason/status, retry/cache và tám JSON. Cập nhật README và development theo source P0 thực tế. Hoàn tất TASK-004, đề xuất TASK-005/P1-A1; không tự triển khai.

### Kiểm tra và kết quả

PASS tám nhóm kiểm tra: formatter ba source/header, Compose config, liên kết file/UTF-8/LF, import convention, JSON/TOML/Python, tám JSON hợp đồng và đối chiếu SRS, build/pin/checksum, bảo toàn source/infra/lịch sử. [Chi tiết](evidence/task-004/convention-checks.md). Không tạo model session mới để kiểm tra convention runtime. Không chạy Wokwi/Docker live hoặc MQTT v1 nghiệp vụ trong A0.

### Vướng mắc

Không có vướng mắc A0 còn chặn. Timeout phiên dài P0 là giới hạn đã ghi tại [nghiệm thu](evidence/task-002/acceptance.md), chưa kết luận nguyên nhân. Không coi ví dụ hợp đồng là code đã triển khai.

### Cách giải quyết

Giữ hạn chế trong tài liệu và theo dõi ở A3; các gói triển khai dùng hợp đồng A0 và bổ sung kiểm thử thực tế. Không ghi PASS cho phần chưa chạy hoặc thay SRS để hợp thức hóa lỗi.

### Tài liệu và bước tiếp theo

SRS 3–7, 10–12, 16. [Task hiện tại](task.md) hoàn thành và giữ nguyên tới lần giao việc mới. [TASK-005](next-task.md) chưa bắt đầu. Giữ nguyên mọi byte báo cáo cũ phía sau.

---

## 2026-11-15T19:12:53+07:00 — TASK-002 — Chốt smoke P0 và phiên bản kiểm chứng

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu môi trường

### Đã thực hiện

Khóa platform/framework/libs/PubSubClient; sửa đúng hai đường dẫn đề cương trong SRS, không đổi yêu cầu; cập nhật README/setup/bằng chứng. Lưu [task đã nghiệm thu](evidence/task-002/accepted-task.md), [biên bản](evidence/task-002/acceptance.md). Source ứng dụng không đổi.

### Kiểm tra và kết quả

PASS formatter, Compose config và các kiểm tra tĩnh trước đó. Lần build sau pin đầu lỗi tải registry; retry với package cục bộ đã hiện hữu PASS 8.37 giây, RAM 47276 byte, flash 897039 byte. Copy/checksum PASS. File MQTT xác nhận đủ pong 001–004, broker restart 19:02:25 và node trở lại 19:02:27; Serial hội thoại đủ năm PWM. Người dùng xác nhận không restart ESP32. Không tự chạy Docker/Wokwi live.

### Vướng mắc

Đã xử lý trở ngại build qua retry, giữ cả log lỗi và log đạt. Timeout cuối phiên dài chưa được kết luận nguyên nhân; đây là giới hạn theo dõi, không được xóa hoặc diễn giải thành ổn định tuyệt đối. Chưa có serial.log thô đầy đủ; nguồn Serial là hội thoại.

### Cách giải quyết

Nghiệm thu các ca smoke đã thỏa; giữ hạn chế trong biên bản và theo dõi ở mạng nghiệp vụ. Không cần nâng toolchain. Build/copy sau pin không được tính là lượt live mới.

### Tài liệu và bước tiếp theo

Đã ghi checklist TASK-002; người dùng giao tiếp TASK-004 để hoàn thiện A0. Giữ nguyên toàn bộ báo cáo cũ phía sau.

---

## 2026-11-15T18:32:51+07:00 — TASK-002 — Firmware chẩn đoán timeout MQTT

- Trạng thái: Bị chặn (chờ live bản mới)
- Tiến độ: 1/4 nhóm nghiệm thu; triển khai lượt heartbeat hoàn tất

### Đã thực hiện

Thêm nghỉ 10 ms đầu loopSmokeTest, heartbeat mỗi 2 giây theo millis không retained trên diagnostics/heartbeat, payload uptime_ms, kiểm tra độ dài/publish; reset timer sau subscribe. Giữ keepalive 15 giây, broker/pin/topic ping-pong. Thêm log uptime cho chuyển kết nối, connect failed, loop failed, Wi-Fi reconnect và heartbeat. Build/copy artifact mới; cập nhật setup, task, next-task và README bằng chứng. Không chạy Docker/Wokwi, không mở rộng cảm biến/AUTO hoặc nhiều node.

### Kiểm tra và kết quả

Formatter ban đầu phát hiện xuống dòng; đã format đúng file thay đổi, dry-run PASS. Build cuối esp32dev exit 0, SUCCESS 4.89 giây, RAM 47276/327680 byte, flash 897039/1310720 byte: [log](evidence/task-002/build-heartbeat.log). Build dùng core dir tạm /tmp/iot-pio-check-de41spu8 và package/platform cục bộ. Script prepare-simulation PASS; [checksum](evidence/task-002/prepare-heartbeat.log). Kiểm tra liên kết mới, artifact khớp checksum, lịch sử report và tệp ngoài phạm vi được giữ nguyên.

### Vướng mắc

Chưa có live cho bản mới. Bằng chứng cũ cho thấy timeout 22–23 giây; tốc độ mô phỏng chậm là giả thuyết. Người dùng xác nhận từng thấy dòng subscribe; chưa đủ chứng minh kết nối ổn định. Không đánh dấu fix runtime/P0 PASS từ build.

### Cách giải quyết

Người dùng restart Wokwi với artifact mới, mở subscriber diagnostics/# trước khi gửi ping, xác nhận heartbeat và ba pong, giữ 3 phút thực, đủ năm PWM, rồi thử stop/start broker và pong p0-004 không reset ESP32. Nếu còn lỗi thu Serial/PCAP. Không chỉ tăng keepalive để che lỗi.

### Tài liệu và bước tiếp theo

Setup mô tả bản P0 hiện tại và lệnh nhận heartbeat/pong. Giữ TASK-002, chưa khóa toolchain hoặc thêm vào danh sách task hoàn thành; checklists.md giữ nguyên. Tham chiếu SRS 4.3–4.5, 10–12. Giữ toàn bộ lịch sử report và log trước.

---

## 2026-11-15T18:19:35+07:00 — TASK-002 — Cập nhật tiến độ theo bằng chứng live

- Trạng thái: Bị chặn
- Tiến độ: 1/4 nhóm nghiệm thu gốc; đã đạt thêm nhiều bước con

### Đã thực hiện

Cập nhật task/next-task, setup và README bằng chứng; thêm [tổng hợp live](evidence/task-002/live-progress.md) và bản sao nguyên ảnh Wokwi người dùng. Giữ nguyên firmware, cấu hình, SRS, log và checklist các task hoàn thành. Không tự chạy Docker/Wokwi hoặc gói kế tiếp.

### Kiểm tra và kết quả

Build.log hiện tại SUCCESS 7.31 giây. Đã đối chiếu checksum BIN/ELF nguồn và copy khớp nhau/khớp đầu ra người dùng. Ảnh xác nhận Wokwi/Serial, ready=1 và PWM 0%/25%; chưa đủ năm mức. Host pub/sub PASS theo terminal người dùng; chưa có mqtt.log thô riêng. Broker.log có ESP32 kết nối ba lần, timeout 22–23 giây. Chưa xác nhận ba pong, SUBACK hay phục hồi sau restart.

Kiểm tra tài liệu: liên kết mới, bảo toàn ảnh/checksum, lịch sử report và các tệp ngoài phạm vi. Không build lại vì chỉ cập nhật hồ sơ dựa trên bằng chứng đã có.

### Vướng mắc

MQTT chưa ổn định, thiếu Serial đầy đủ và pong. Mô phỏng chậm là giả thuyết, chưa kết luận nguyên nhân. Build.log lỗi cũ đã được người dùng thay bằng log SUCCESS; không phục dựng hoặc giả tạo log cũ.

### Cách giải quyết

Lần thử tiếp khởi động lại broker sau compose down, giữ Wokwi chạy, thu Serial và kiểm tra heartbeat; nghiệm thu đủ PWM và ping/pong trước/sau restart. Chỉ khóa toolchain sau khi smoke live đạt. Giữ 1/4 vì tiêu chí build còn gộp khóa phiên bản, PWM thiếu mức, MQTT chưa đạt; không ghi phần trăm tùy ý.

### Tài liệu và bước tiếp theo

Setup cập nhật theo SRS 4.3–4.5, 10–12. Next-task giữ TASK-002, chưa triển khai đề xuất sửa timeout. Không thêm task chưa hoàn thành vào checklists.md. Lịch sử report cũ giữ nguyên toàn bộ phía sau.

---

## 2026-11-15T18:10:41+07:00 — TASK-002 — Sửa lỗi biên dịch min

- Trạng thái: Bị chặn (còn chờ nghiệm thu live)
- Tiến độ: 1/4 mục nghiệm thu tổng; lượt sửa lỗi hoàn tất

### Đã thực hiện

Thêm <algorithm>, đổi min thành std::min<uint32_t> trong EnvironmentSmokeTest.cpp để xử lý xung đột unsigned long/unsigned int; không đổi thuật toán hoặc mức trần backoff. Cập nhật task, next-task, setup và README bằng chứng. Giữ nguyên build.log và các log cũ.

### Kiểm tra và kết quả

PASS: clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp. PASS: build esp32dev, exit 0, SUCCESS 10.19 giây, RAM 47276/327680 byte, flash 896199/1310720 byte. Xem [log mới](evidence/task-002/build-min-fix.log). Dùng core dir tạm /tmp/iot-pio-check-de41spu8 với package/platform cục bộ; không nâng toolchain hoặc sửa quyền hệ thống.

### Vướng mắc

Lỗi biên dịch đã xử lý. Wokwi/Serial/PWM, broker và ping/pong/reconnect live chưa chạy. Tiêu chí đầu tiên còn gộp build và khóa phiên bản sau smoke live nên chưa đánh dấu đạt toàn mục.

### Cách giải quyết

Người vận hành tiếp tục chuẩn bị artifact và nghiệm thu live theo setup; sau khi đạt mới khóa platform/framework. Không tự chạy Docker/Wokwi trong lượt sửa này.

### Tài liệu và bước tiếp theo

Tham chiếu SRS 4.3–4.5, 10–12. Giữ TASK-002 chờ kiểm chứng; không đánh dấu task hoàn thành hoặc thêm mục hoàn thành vào checklists.md. Lịch sử checklist giữ nguyên. Toàn bộ nội dung report cũ giữ nguyên ở phía sau.

---

## 2026-11-15T17:55:23+07:00 — TASK-002 — Chuẩn bị môi trường P0

- Trạng thái: Bị chặn
- Tiến độ: 1/4 mục nghiệm thu

### Đã thực hiện

- Tạo Docker Compose Mosquitto 2.1.2-alpine và service MQTT client profile tools trên host networking Linux; broker chỉ publish 127.0.0.1:1883, cấu hình read-only, anonymous local, không persistence.
- Thay code mẫu bằng main điều phối EnvironmentSmokeTest: Serial, LEDC 5 kHz/8 bit, năm mức PWM, Wi-Fi/MQTT với retry hữu hạn, ping/pong tối đa 64 byte, không retained. Thêm PubSubClient 2.8; chưa pin platform/framework vì chưa build/smoke đạt.
- Tạo sơ đồ và cấu hình Wokwi node_01, script chuẩn bị BIN/ELF kiểm tra freshness/checksum và gitignore artifact.
- Tạo [setup](../techs/setup.md), README, cập nhật development và [bằng chứng](evidence/task-002/README.md). Giữ nguyên SRS và lịch sử checklist; chưa có task hoàn thành mới.

### Kiểm tra và kết quả

PASS: Compose config, clang-format, JSON/TOML, liên kết tài liệu; thử script với fixture tạm gồm thiếu file, artifact cũ và copy checksum. Chi tiết tại [kiểm tra tĩnh](evidence/task-002/static-checks.md).

Build code mẫu và code mới: bị chặn quyền cache PlatformIO, xem baseline-build.log/smoke-build.log trong thư mục bằng chứng. Chưa xác nhận biên dịch mã mới. Chuẩn bị artifact thật từ chối vì thiếu BIN/ELF; không xuất artifact cũ.

Docker runtime, license Wokwi, Serial/PWM live, broker host và ping/pong/reconnect: chưa chạy. Không coi kiểm tra tĩnh là kết quả nghiệm thu mô phỏng.

### Vướng mắc

PlatformIO không ghi được cache/lock trong ~/.platformio ở sandbox. Người dùng chọn tự chạy Docker Compose và Wokwi; chưa có log live.

### Cách giải quyết

Chạy theo setup từ terminal ngoài phiên: khởi động broker, xác nhận host pub/sub, build SUCCESS, copy artifact, chọn cấu hình và chạy Wokwi, thử ba ping/pong rồi stop/start broker. Lưu log và ảnh vào evidence/task-002. Sau khi có bằng chứng đạt, tiếp tục cùng TASK-002 để khóa toolchain đã kiểm chứng và nghiệm thu. Không cần thay quyền hệ thống hoặc xóa cache từ agent.

### Tài liệu và bước tiếp theo

[SRS](../srs.md) mục 3, 4, 10–12; setup là tài liệu chính cho firmware/mạch/MQTT thử P0. [Task tiếp theo](next-task.md) là phần kiểm chứng còn lại của TASK-002; TASK-004 chỉ được đề xuất khi P0 môi trường đạt. Chưa tự triển khai A0/P1.

---

## 2026-11-15T17:41:58+07:00 — TASK-003 — Dùng chung convention cho Codex, Claude Code và OpenCode

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

### Đã thực hiện

- Giữ [AGENTS.md](../../AGENTS.md) làm nguồn convention chung, bổ sung chỉ dẫn đồng bộ và khởi động tại gốc firmware.
- Thêm [CLAUDE.md](../../CLAUDE.md) với import @AGENTS.md theo cơ chế chính thức của Claude Code. Codex/OpenCode sử dụng AGENTS.md trực tiếp, không nhân bản convention hoặc thêm cấu hình nạp trùng.
- Cập nhật [development.md](../techs/development.md) với tài liệu nguồn, cách kiểm tra trên phiên mới và giới hạn xác minh.
- Cập nhật task hiện tại và checklist. TASK-002 vẫn là đề xuất P0 chưa bắt đầu; mã TASK-003 dùng cho yêu cầu mới vì TASK-002 đã được dành trong next-task.md.

### Kiểm tra và kết quả

- PASS: đối chiếu tài liệu chính thức Codex AGENTS.md, Claude Code memory/imports và OpenCode instructions; liên kết nguồn trong development.md.
- PASS: CLAUDE.md có đúng một import trỏ tới AGENTS.md hiện hữu; không có vòng import hoặc AGENTS.override.md tại gốc.
- PASS: kiểm tra 31 đường dẫn Markdown nội bộ trước khi đóng hồ sơ; tệp đọc được UTF-8/LF, có newline cuối.
- PASS: SHA-256 của SRS, src/main.cpp, platformio.ini, .clang-format, .editorconfig và next-task.md giữ nguyên.
- PASS: giữ nguyên lịch sử report/checklists trước khi ghi; thêm mục report mới lên đầu và xác nhận toàn bộ nội dung cũ giữ nguyên ở cuối.
- PASS: lệnh opencode --version với XDG_DATA_HOME/XDG_STATE_HOME/XDG_CACHE_HOME trỏ thư mục tạm cho kết quả v2.0.26.
- Chưa kiểm chứng bằng phiên model mới: không gọi Codex/Claude/OpenCode để thực hiện prompt hoặc phát sinh phiên agent khác. Không chạy build firmware vì chỉ sửa hướng dẫn.

### Vướng mắc

Claude CLI không có trong PATH của môi trường kiểm tra. OpenCode --version với vị trí dữ liệu mặc định lỗi EROFS khi mở log trong ~/.local/share/opencode/log/opencode.log. Điều này giới hạn kiểm tra runtime, không ngăn tạo các entry point hướng dẫn tại dự án.

### Cách giải quyết

Đã dùng các thư mục XDG tạm trong /tmp để đọc phiên bản OpenCode, không sửa cấu hình global. Để xác nhận context thực tế, mở phiên mới tại firmware bằng từng công cụ; với Claude Code kiểm tra /context all, rồi dùng prompt chỉ đọc trong development.md để xác nhận quy định SRS/techs/báo cáo/task/checklist/Arduino. Cần môi trường có Claude Code khả dụng nếu muốn chạy kiểm chứng Claude CLI.

### Tài liệu và bước tiếp theo

Tham chiếu [SRS](../srs.md) mục 11, 16. Tài liệu development đã cập nhật. Giữ [đề xuất P0](next-task.md), chưa thực hiện. Cấu trúc nhận convention đã được thiết lập; việc model tuân thủ không được cưỡng chế bằng tệp Markdown.

---

## 2026-11-15T17:37:41+07:00 — TASK-001 — Thiết lập convention agent

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

### Đã thực hiện

- Tạo [AGENTS.md](../../AGENTS.md) tại gốc firmware: đọc SRS mỗi task, xác định phạm vi, cập nhật tài liệu kỹ thuật và báo cáo trước khi kết thúc.
- Tạo [development.md](../techs/development.md) với vòng đời task, trạng thái, mẫu task/báo cáo, danh mục techs, cách thêm báo cáo lên đầu và giữ lịch sử.
- Thêm [.clang-format](../../.clang-format) và [.editorconfig](../../.editorconfig): định dạng C/C++ Arduino, UTF-8/LF; giữ khoảng trắng Markdown có chủ đích. Không format lại source mẫu.
- Khởi tạo [task hiện tại](task.md), [checklist hoàn thành](checklists.md) và [đề xuất TASK-002](next-task.md). Chưa thực hiện P0, chưa nghiệm thu chức năng firmware.

### Kiểm tra và kết quả

- PASS: kiểm tra các đường dẫn Markdown nội bộ trong AGENTS, development và các tệp task đang có tại thời điểm kiểm tra, không có đích thiếu.
- PASS: chạy clang-format 23.1.4 với `--style=file --assume-filename=src/main.cpp` trên mẫu Arduino qua stdin. Cấu hình thật được đọc; thụt 2 dấu cách, chèn ngoặc nhánh if, format hai lần cho cùng kết quả; `--dry-run --Werror` đạt với mẫu đã định dạng.
- PASS: các tệp mới có nội dung đọc được UTF-8, dùng LF và có newline cuối tệp.
- PASS: đối chiếu SHA-256 trước/sau, SRS, src/main.cpp và platformio.ini giữ nguyên.
- PASS: đã đọc báo cáo cũ trước khi thêm mục mới. Tệp ban đầu trống (0 byte); kiểm tra thêm khối mới giữ nguyên lịch sử không rỗng bằng mẫu trong bộ nhớ. Thao tác ghi báo cáo thật cũng nối nguyên nội dung cũ ở phía sau.
- Đã rà văn phong bằng vi_scan.py và đọc lại các cảnh báo: chủ yếu là dấu câu, khoảng mục SRS và thuật ngữ trong tài liệu kỹ thuật; giữ các cấu trúc cần thiết.
- Chưa chạy build firmware, Wokwi hoặc MQTT: ngoài phạm vi task thuần tài liệu/cấu hình định dạng. Không coi formatter đạt là chức năng firmware đạt.

### Vướng mắc

Không có vướng mắc chặn task. Git CLI không nhận diện thư mục hiện tại là repository trong môi trường này, nên không dùng git diff để xác minh thay đổi.

### Cách giải quyết

Đã đối chiếu nội dung và SHA-256 của SRS, source cùng cấu hình build thay cho git diff. Không cần hành động bổ sung để hoàn thành task convention. Khi làm P0, cần kiểm tra quyền build cache, Wokwi và kết nối MQTT theo task kế tiếp.

### Tài liệu và bước tiếp theo

Tham chiếu [SRS](../srs.md) mục 3–6, 10–12 và 16. Quy trình và convention đã ghi ở development.md. Đề xuất TASK-002 kiểm chứng môi trường P0, chỉ bắt đầu khi người dùng giao việc; không tự chuyển task.
