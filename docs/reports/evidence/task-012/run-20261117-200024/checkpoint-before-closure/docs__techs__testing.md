# Kiểm tra dự án — firmware, backend và dashboard

## TASK-012 — Công cụ thực nghiệm đang kiểm chứng

34 test Python PASS, gồm20 ca cũ,12 ca recipe/clock/độc lập năng lượng và2 ca hồi quy tách clock qua reboot/toàn vẹn CSV. Fixture kiểm15 lượt/150 phút mô phỏng, PIR15+30k, EX05 lặp cùng lịch, chuẩn bị popup không đổi mốc tác động, predictor bị chặn1s, hai clock tách biệt, baseline null và không nối qua boot/gap/session/quality. Đây là kiểm công cụ, chưa phải15 lượt live đạt. Xem [phương pháp và trạng thái](experiments.md), [task](../reports/task.md). Không chạy lại host/build/30 phút TASK-011 khi source/artifact giữ nguyên.

## TASK-011 — Ma trận ba định danh

`python3 -B scripts/check-firmware.py`: protocol/app/MQTT cho cả 3 chỉ số; controller/sensors chạy một lượt, tổng 11 lượt; chỉ số 0 và 4 phải compile-fail. Stub lưu client ID thực; kiểm topic/LWT/subscription và payload đúng node, diagnostics, từ chối sai topic/node; giữ hồi quy controller/queue/deadline/session.

`python3 -B -m unittest discover -s test/host -p 'test_*.py'`: 20 test PASS ở lượt kiểm cuối, gồm generator ba node, freshness/deadline64, routing/default/thiếu/cũ/rỗng artifact, manifest/hash cấu hình/pin map/cap CPU của ba sơ đồ và 7 test Serial cũ. Ba environment build PASS. Các test prepare dùng dummy artifact có nhãn, không giả làm firmware thật.

Live cuối trên firmware sửa coalescing đã PASS 30 lệnh đúng đích, cảm biến/fault/tắt node/outage/restart; 30 sensor→dashboard (10/node) đạt dưới3s theo latency-final-audit.json. Các FAIL >3s và INCOMPLETE trong lượt trước vẫn giữ nguyên; bản sửa có ca red trước/green sau. TASK-011 hoàn thành4/4: stability-02 đủ1800s monotonic đồng thời với5360 bản tin raw khớp SQLite ACCEPTED, boot/seq/continuity/PID backend giữ nguyên và dropped_events0. Probe HTTP/resource bị SIGTERM143 sau1346,506s/672 mẫu vẫn INCOMPLETE; audit độc lập dùng toàn bộ cửa sổ đã định trước, không coi probe là đầy đủ. stability-01 INCOMPLETE góp0 giây. Giữ FAIL/INCOMPLETE cùng lượt mới; host/build hoặc bản một node không thay live. [Hồ sơ và phương pháp](../reports/evidence/task-011/run-20261117-135233/README.md), [host cuối](../reports/evidence/task-011/run-20261117-135233/host-checks-final.log), [build cuối](../reports/evidence/task-011/run-20261117-135233/firmware-build-final.log).


## TASK-010 — nghiệm thu hoàn tất một node, 2026-11-17T12:05:29+07:00

4/4 nhóm PASS theo [audit và hồ sơ](../reports/evidence/task-010/completion-20261117-105535/README.md). Bổ sung UI REJECTED/TIMEOUT bằng ACK thật, pending/phiên mở qua restart, broker QA outage/reconnect/no-replay và Serial AUTO/PWM khi mqtt0. Sửa race actor nhận retained ONLINE sau chờ queue;72 Pytest/Ruff PASS,4 test lõi proxy PASS. Các PASS Windows trước giữ nguyên, các đoạn PENDING phía dưới là lịch sử tại thời điểm từng lượt.

10/10 mẫu sensor→dashboard mới PASS3s, median theo khoảng1417,832–1464,491ms, max2353,967–2401,274ms. T0 là phím LDR trusted trên Wokwi VSCode, DOM sau hai rAF, clock có chặn sai số trước/sau; MQTT/API/DOM cùng boot/seq/ADC, không hidden, giá trị nhìn thấy; video30fps bổ trợ. Hai pilot tách riêng; điều phối bị kết thúc143 sau8 mẫu nhưng bộ ghi giữ nguyên, chỉ thu tiếp9/10. Không dùng Serial receive/HTTP RTT/command ACK thay sensor latency. Giữ10 command→ACK cũ (median686,217ms/max1002,001ms), không chạy lại.

LDR fallback dùng Home/End0,1/100000lux thay mức100/1000 dự kiến để có hành động UI rời rạc; không đổi ngưỡng/chu kỳ. CLI token bị Unauthorized, đã dùng VSCode theo phương án được chọn. Artifact fresh/hash khớp nên không build lại firmware. Không nghiệm thu ba node/stability30phút/EX-series hoặc phần cứng thật. Dịch vụ QA đã dừng, DB người dùng không bị sửa.


## Rà soát hồ sơ sau pull — 2026-11-17T09:45:17+07:00

Đối chiếu main firmware `7e8f5c4` (PR #3) với file chốt TASK-010: nhóm 1 và 3 PASS, nhóm 2 và 4 PENDING, tổng 2/4 nhóm nghiệm thu. Kiểm tra mới tại máy Linux: 112/112 tệp trong 4 manifest SHA256 khớp, 70/70 JSON bằng chứng đọc hợp lệ. Không mở DB hoặc kết nối MQTT/API, không chạy lại build/host/pytest/Node/live đã được xác nhận trước đó. [Kết quả và phạm vi kiểm tra](../reports/evidence/task-010/review-20261117-094517/README.md).

Command → ACK: 10 lượt cũ, median 686,217 ms/max 1002,001 ms. Cảm biến → dashboard: 5 lượt đã thử, 0/10 mẫu đủ điều kiện; các lượt 1–5 INCOMPLETE và 6–10 chưa chạy. Không tính MQTT → render, HTTP RTT hoặc command → ACK thay cho cảm biến → render. Không dùng độ trễ khoảng 203s ở lượt 5 để kết luận latency sản phẩm bình thường vì điều kiện đo bị nhiễu.

Còn kiểm UI REJECTED/TIMEOUT, broker outage/reconnect/no-replay/AUTO offline và latency cảm biến → dashboard. Những kết quả TIMEOUT/ACK muộn, OPEN_LOAD, restart/gap đã PASS ở các lượt bổ sung được giữ; các đoạn PENDING cũ bên dưới là lịch sử tại thời điểm từng lượt, không phủ định kết quả bổ sung. Một số ghi chú bị mất dấu, đối chiếu bản tổng hợp có dấu và JSON gốc, không viết lại bằng chứng.


## TASK-010 — kết quả live một node trên Windows

[Lượt proxy ACK thật run-20261116-193157](../reports/evidence/task-010/run-20261116-193157/README.md) PASS: một POST AUTO, command0d8f20f5…, đúng1 retry2,041s; TIMEOUT quan sát10,089s;2 ACK thả ở mốc12s nguyên bytes và lưu LATE_OR_DUPLICATE, API/DB cuối vẫn TIMEOUT/attempts2. Preflight2 telemetry qua1884 và không replay sau khôi phục PASS. Backend đã vềMQTT1883/API8001/PID14144/một worker, healthOK, người dùng xác nhận Dashboard ONLINE/NIGHT25/dữ liệu mới19:44:21. Proxy/recorder dừng, DB/PASS cũ giữ nguyên. Nhóm2 vẫn còn broker outage/reconnect/lệnh chờ/AUTO offline/UI terminal, nhóm4 còn sensor→Dashboard10 lượt; không chạy lại bài đã PASS.

Bổ sung restart thật: [run-20261116-190549](../reports/evidence/task-010/run-20261116-190549/README.md) PASS giữ dữ liệu đã lưu sau PID18828→43632 và run ID đổi; firmware boot giữ nguyên.760 telemetry/13 command/20 ACK/106 alert/3 phiên cũ còn,3 CSV tải lại giống từng byte. Ranh giới row765→766 khác continuity, history/stats không nối năng lượng qua gap. Không capture đúng API outage/STALE ban đầu, không có lệnh chờ/phiên mở lúc restart; các tình huống đó chưa được chốt. TASK-010 hiện2/4 nhóm, nhóm2/4 còn PENDING. Bài Pause2s đã INCOMPLETE do ACK APPLIED/ACCEPTED tới sau1,023s, trước timeout10s; mốc Pause không được ghi nên chưa xác định được thao tác muộn hay MCU còn xử lý. Quy trình thay thế dùng proxy giữ nguyên ACK thật12s, đã kiểm công cụ offline/diagnostics, chưa chạy TIMEOUT live qua proxy. Không tự gửi lại lệnh hoặc nâng PENDING thành PASS.

Bổ sung OPEN_LOAD: [đối chiếu lượt run-20261116-184903](../reports/evidence/task-010/run-20261116-184903/README.md) PASS từ telemetry SQLite/API, alert30/33 đóng và16 mẫu giữ AUTO/NIGHT25. Telemetry hết lỗi tại1340238ms; Serial1340431ms/duty64/mqtt1 và ảnh do người dùng xác nhận, không đồng nhất hai timestamp. Không chạy lại fault. Capture Serial mới sau phục hồi có19 dòng CONTROL AUTO25/duty64/faultOK/mqtt1; đồng hồ node/wall trung vị≈0,1603, khoảng telemetry thực trung vị≈12,70s/max15,62s trong phần quan sát. Trạng thái offline vì telemetry quá10s thực cần tách khỏi MQTT ngắt; không sửa ngưỡng. Latency cảm biến→render vẫn cần bằng chứng riêng.

Phiên3 NIGHT6W đã đóng:50 mẫu CSV/API/stats khớp,48 gap không nối năng lượng PASS. Coverage chỉ1,534987%, valid_uptime2,005s; không khái quát saving75% của tập mẫu hợp lệ nhỏ ra toàn khoảng. Capture600s lượt đó không ghi API outage/run ID không đổi nên khi ấy restart PENDING; sau đó người dùng thực hiện và lượt mới đối chiếu PASS như trên. Không còn phiên đo agent mở.

[Hồ sơ live và ma trận PASS/PENDING](../reports/evidence/task-010/run-20261116-180648/README.md). Backend dùng cổng8001 theo lựa chọn người dùng để giữ nguyên dịch vụ khác ở8000; Dashboard5500, broker1883. Người dùng xác nhận Python3.12/build P3/A3/prepare/68 Pytest/Ruff, Dashboard live/MANUAL80/PWM80/tự AUTO60s; agent không chạy lại các bài đã đủ xác nhận. SQLite/API bổ sung command ID/ACK cũ và mẫu PWM80. Không có ảnh/Serial mới cho lượt xác nhận; phân biệt với dữ liệu MQTT/API/SQLite agent thu trực tiếp.

PASS live: health/nodes, singleton DB lock/quick_check/hash;422/409/404/pending guard;3 reject wire; cache replay sau deadline/ID trùng khác nội dung; command→ACK10 lượt median686,217ms/max1002,001ms;phiên thực/CSV/stats/clock và phép tính điện năng độc lập; OPEN_LOAD/phục hồi, restart giữ dữ liệu/gap, TIMEOUT/ACK muộn/retry và khôi phục Dashboard theo bổ sung trên. PENDING: UI terminal states, broker outage/reconnect/no-replay cho lệnh chờ/AUTO offline, tình huống lệnh chờ/phiên mở qua restart và cảm biến→Dashboard10 lượt. GUI observation timeout nên chưa có ảnh mới trong repo; khôi phục Dashboard được người dùng xác nhận. Không đổi schema/thuật toán/ngưỡng, không lấy thời gian node chia lẫn wall clock, không nghiệm thu ba node hoặc EX-series. Tài liệu TASK-007/008/009 bên dưới giữ kết quả lịch sử ở thời điểm bàn giao.

## TASK-009 P5/A5 — dashboard và API read bổ sung

Tại DoAn/dashboard: `node --test tests/*.test.mjs` →16 PASS (Node24.17). Tại DoAn/backend: `.venv/bin/python scripts/check.py` →Ruff check/format,68 Pytest PASS/1 deprecation warning cũ. OpenAPI11 paths/12 thao tác. Không đổi firmware/toolchain nên không build lại C++/Wokwi trong task UI.

Playwright CLI với Live Server engine2.2.0 của VS Code extension5.7.10:18 kiểm tra luồng chính +8 kiểm tra bổ sung PASS; viewport375/768/1024/1440, chart/bảng/keyboard, draft, lệnh, phiên/reload/stop/CSV, mất API/recovery/no-retry, reduced motion và overflow mobile. Pha REJECTED/TIMEOUT dùng phản hồi API mock, lỗi mạng chủ động tạo console resource errors dự kiến; pha cuối trên repo bàn giao có0 console error/0 uncaught JS exception. API/SQLite thật, transport MQTT và dữ liệu giả có nhãn, không mở broker. [Bằng chứng và lệnh tái lập](../reports/evidence/task-009/README.md), [dashboard](dashboard.md).

Chưa chạy UI với broker/ESP32 thật, VS Code Go Live thao tác tay/Windows, đo latency10 lượt, ba node30phút hay EX-series. Đó là kiểm tra tích hợp tiếp theo; không ghi PASS từ fixture.

## TASK-008 P4/A4 — backend

Chạy `.venv/bin/python scripts/check.py` từ repo DoAn/backend (PowerShell dùng .venv/Scripts/python.exe).66 test collector/command/API/energy/transport, Ruff check/format PASS trên Linux; [log và giới hạn](../reports/evidence/task-008/README.md), [cách chạy](backend.md). Pytest dùng DB tạm, fake MQTT/clock, không mở broker. Không cần build firmware vì TASK-008 không sửa C++/PlatformIO. Lệnh Windows và live được bàn giao nhưng chưa chạy tại máy này.

## TASK-007 P3/A3 — bàn giao code/test/hướng dẫn

SRS6,5.7,9.1 và TC17–22/26 trong phạm vi một node/client giả. Chạy từ gốc firmware:

```bash
# Một lần sau checkout để cài đúng dependency đã pin; không nâng toolchain.
~/.platformio/penv/bin/pio pkg install
python3 scripts/check-firmware.py
python3 -B test/host/test_wokwi_serial.py
python3 -B test/host/test_mqtt_command.py
~/.platformio/penv/bin/pio run -e esp32dev
python3 scripts/prepare-simulation.py
```

check-firmware.py dùng g++/C++17 -Wall -Wextra -Werror, link ArduinoJson7.4.2 thật từ .pio/libdeps; không mock JSON. Năm suite: protocol/controller/sensors/app/mqtt. Protocol kiểm schema/type/range/UUID/boot/uint64/trailing/invalid, telemetry16 trường/current-power/null/fault, cacheFIFO32/deadline/dedup/rejected ID và mailbox queue8/backpressure. App chạy code thật tới controller/PWM stub, xác minh ACK sau nhận target, duplicate không gia hạn60s, sai boot/expired/session và Serial trước MQTT. Network kiểm CONNECT will/clean session/QoS/retain/subscriptions, telemetry200ms/2s/seq/reconnect, ACK publish fail và session flush; GPIO/network/RTOS vẫn là stub.

Bảy unittest RFC2217 giữ nguyên; bốn unittest generator kiểm input/deadline64/UUID/fixture sai và tuổi file telemetry3s. scripts/mqtt-command.py chỉ tạo JSON, không gửi dữ liệu hoặc kiểm chứng broker.

Bằng chứng mới lưu ở [TASK-007](../reports/evidence/task-007/README.md). [Ma trận/lệnh live A3](mqtt.md#bộ-kiểm-tra-live-a3-trên-máy-dev-chưa-chạy-tại-máy-này) chưa chạy tại máy này. Không suy host/build thành LWT thực, timing hai core hoặc ba node30phút PASS. Các đoạn TASK-006 bên dưới là lịch sử P2 trước khi thêm A3.

## TASK-006 P2/A2

Chạy `python scripts/check-firmware.py` bằng Python PlatformIO: bốn suite controller/sensors/app/mqtt; [cách chạy Windows và giới hạn stub](../../test/host/README.md). Code/host/build được kiểm tra trong [validation.log](../reports/evidence/task-006/validation.log); không chạy lại Wokwi TASK-005 hoặc thao tác broker.

| Nhóm | Ca tự động | Trạng thái |
|---|---|---|
| AUTO/state | TC-01–11: 5 mẫu mới, boundary1200/2600, hysteresis1100/1300/2500/2700, dwell1s, motion100cm/invalid/PIR gate, hold5s/max, DAY cancel | Host PASS |
| MANUAL | TC-12/13/27: range0–100, DAY priority, refresh60s, offline/reconnect và fast-loss giữa poll, AUTO không dùng hold cũ | Host PASS |
| Dimming/fault | TC-14/15/16/28: 2điểm/20ms, target lẻ, không burst, stable1s/detect2s/recover3s, biên ADC409/410/818/819, invalid, mode/off không xóa, PWM không bị cắt | Host PASS |
| Runtime/regression | ISR ECHO/timeout30ms/late edges/micros wrap, sample timers; Serial parser/overflow/NUL; MQTT binary pong/64byte/topic/retain/backoff/resubscribe | Host PASS |
| Firmware đích | esp32dev, package pin, formatter | Xem log thực tế |
| Wokwi P2 | [Bằng chứng và ma trận hiện tại](../reports/evidence/task-006/acceptance-review.md) | MANUAL80/timeout60s có file PASS; các bài live khác người dùng xác nhận, hồ sơ file PENDING |

TC-17–20/26 JSON command/ACK, đa node/backend/dashboard và stability30phút thuộc A3 trở đi, chưa được coi PASS. Test MQTT hiện dùng stub, không thay kiểm tra broker/live. Một test tích hợp đã bắt lỗi reconnect quá nhanh che mất sự kiện offline; code có atomic loss-count và test hồi quy. Những assertion thử nghiệm thất bại trong quá trình phát triển đã được sửa rồi chạy lại; log cuối ghi kết quả thực, không tuyên bố không từng có lỗi.

## TASK-005 P1/A1 — lịch sử nghiệm thu giữ nguyên

## Kết quả nghiệm thu cuối

TASK-005 đã hoàn thành 4/4 nhóm nghiệm thu; P1-01 đến P1-08 PASS theo [biên bản và ma trận evidence](../reports/evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Các trạng thái “Chưa chạy” trong ma trận bên dưới là trạng thái ban đầu khi lập kế hoạch, không phải kết quả cuối. P1-08 dùng bộ bằng chứng bổ sung của hai lượt recovery, ghi rõ nguồn thời gian; không tuyên bố một capture đồng bộ duy nhất. Không nghiệm thu AUTO/MANUAL hoặc mạng nghiệp vụ ở P1.

## Tham chiếu SRS

[SRS](../srs.md) mục 4.1, 5.3, 10 P1, 11 A1, 12. Các TC AUTO/MANUAL/fault trong SRS thuộc A2 trở đi, chưa nghiệm thu tại P1. [Firmware](firmware.md), [cách chạy Wokwi](simulation.md), [bằng chứng](../reports/evidence/task-005/README.md).

## Kiểm tra đã thực hiện

- Host: test/host/SensorReaderChecks.cpp biên dịch cùng SensorReader.cpp thật; Arduino.h trong test/host là stub chỉ dùng cho compiler host. Kiểm tra pin/ADC, lịch 20/100/200 ms, xung TRIG, timeout 30000 µs, xóa distance cũ khi timeout, phục hồi 2/100/400 cm và timer qua tràn uint32. Không thêm native environment hoặc dependency vào PlatformIO.
- Build đích esp32dev với platform/package đã pin; formatter, sơ đồ JSON/TOML, dây nguồn/GND và script copy/checksum.
- Các phép kiểm tra trên không chứng minh Wokwi, điện áp thật, khoảng thời gian mạng hoặc GPIO thực hoạt động.

Lệnh tái lập host (tại gốc firmware):

```bash
g++ -std=c++17 -Wall -Wextra -Werror -Itest/host -Isrc src/SensorReader.cpp test/host/SensorReaderChecks.cpp -o /tmp/task005-sensor-checks
/tmp/task005-sensor-checks
```

## Ma trận live cần người vận hành thực hiện

| Mã | Cấu hình và thao tác | Kỳ vọng | Trạng thái ban đầu |
|---|---|---|---|
| P1-01 | Chính, LDR 1/100/10000 lux | ADC 0–4095, giảm khi lux tăng | Chưa chạy |
| P1-02 | Chính, biến trở thấp/giữa/tối đa | ADC tăng theo vị trí, đúng nhãn raw | Chưa chạy |
| P1-03 | Chính, PIR Simulate Motion | LOW → HIGH → LOW; log sự kiện | Chưa chạy |
| P1-04 | Chính, HC-SR04 2/100/400 cm | Sai số ≤ max(2 cm, 5% giá trị đặt) | Chưa chạy |
| P1-05 | Timeout, ECHO bị bỏ dây | distance_valid=0, NA; không treo vòng điều phối | Chưa chạy |
| P1-06 | Chính, quan sát đủ một vòng | PWM 0/25/50/70/100, duty 0/64/128/179/255, ready=1 | Chưa chạy |
| P1-07 | Chính, MQTT nối và đổi cảm biến 3 phút thực | Heartbeat, pong task005-001; không có lỗi mạng mới trong khoảng kiểm tra | Chưa chạy |
| P1-08 | Chính, broker stop/start | Raw Serial/PWM tiếp tục, reconnect và pong mới không reset ESP32 | Chưa chạy |

Ghi cho từng ca: thời gian thực, bản firmware/checksum, cấu hình, thao tác, kỳ vọng, thực tế, PASS/FAIL và đường dẫn log/ảnh. Tốc độ mô phỏng hoặc reconnect có thể làm chu kỳ thực dài hơn lịch; ghi hiện tượng thay vì đổi ngưỡng để làm test đạt. LDR/pot có giới hạn mô phỏng analog; kiểm tra monotonic/range, không giả định giá trị khớp một bảng ADC Arduino Uno.

## Điều kiện hoàn tất

Giữ bốn nhóm nghiệm thu TASK-005: mạch, raw cảm biến, build/live PWM-cảm biến, tài liệu. Sơ đồ kiểm tra tĩnh không được báo như đã xác minh live. Chỉ chốt toàn task sau khi đủ P1-01 đến P1-08 và không có lỗi chặn liên quan. Nếu chờ người vận hành, giữ task Bị chặn, không thêm vào checklist task hoàn thành. Không tự chạy A2/TASK-006.


TASK-010: b? ghi quan s?t Dashboard th?t/MQTT/Serial qua loopback18765; t0 l? kho?ng accessibility th?y sensor ??i, hai rAF c?ng boot/seq/distance l? m?c render x?p x?. Event browser m?i c? page_id/time_origin/visibility; ph?i lo?i l??t kh?ng x?c minh ???c tr?ng th?i trang. Xem evidence/task-010/run-20261116-195307/README.md; ch?a ??10 m?u sensor?Dashboard.

TASK-010 marker-baseline-v2: kh?ng ch?p nh?n sensor ?? ? target tr??c marker; ph?i c? seq m?i c?ng boot v? API last_seen sau c?n tr?n marker ?? ??ng b? clock. Ph?n t?ch ph?i lo?i m?u MQTT ?? nh?n tr??c marker. B?n ghi ?? ghi ch? x?c nh?n capture, ch?a ph?i PASS latency. Xem trial-03-summary-causal-audit.json.
