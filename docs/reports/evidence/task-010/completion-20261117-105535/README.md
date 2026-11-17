# TASK-010 — Nghiệm thu hoàn tất một node live trên Linux

- Hoàn tất: **2026-11-17T12:05:29+07:00**, **4/4 nhóm nghiệm thu TASK-010**.
- Source firmware ban đầu: main `3c8fe1b`; backend base `2e6a15f`, nhánh sửa `task/task-010-restart-sync`; dashboard `6cb402b` giữ nguyên. Không commit/push/merge.
- Giữ nguyên mọi kết quả và bằng chứng Windows trước đó. [Task trước lượt hoàn thiện](task-before-completion.md), [audit nghiệm thu](acceptance-audit.json), [kiểm tra bàn giao](verification.json).

## Kết quả nghiệm thu

| Nhóm | Kết quả | Bằng chứng và giới hạn |
|---|---|---|
| 1. Tích hợp một node | PASS | ESP32 Wokwi VSCode → MQTT QA → FastAPI/SQLite → dashboard Live Server thật; boot71a86c73, node02/03 UNKNOWN. [Snapshot cuối](qa-final-snapshot.json) |
| 2. Điều khiển và độ tin cậy | PASS | MANUAL/60s và guard giữ bằng chứng cũ; thêm UI REJECTED/EXPIRED, UI TIMEOUT/ACK muộn, broker outage/reconnect/no-replay và AUTO offline trong lượt này |
| 3. Dữ liệu/restart/CSV/gap | PASS | Giữ các CSV/gap/restart đã PASS; thêm pending/open experiment qua restart, UI reload phục hồi phiên, đóng phiên và khắc phục race session |
| 4. Latency | PASS |10 mẫu sensor → dashboard mới đạt mục tiêu3s;10 mẫu command → ACK cũ giữ nguyên, không đo lại |

### UI và mạng thật

- [UI terminal](ui-terminals-v2.log): REJECTED/EXPIRED ID1aca308e…; TIMEOUT/ACK_TIMEOUT ID24f6cf3a…/attempts2, ACK thật tới muộn không đổi kết quả cuối. [Ảnh REJECTED](ui-expired-live.png), [ảnh TIMEOUT](ui-hold_ack-live.png).
- REJECTED là **fault injection có nhãn**: proxy sửa riêng deadline về0 cho command QA đã chọn, giữ UUID/boot; firmware tạo ACK thật. Frame gốc/sau sửa có hash trong [events-v2.jsonl](events-v2.jsonl). Không đưa ACK giả hoặc fixture vào broker. Ca TIMEOUT giữ/thả nguyên frame ACK thật sau12s từ lần gửi đầu.
- [Restart trên bản sửa](ui-restart-after-fix.log): PENDING → TIMEOUT/BACKEND_RESTART, UI mở khóa khi node fresh lại; phiên QA đang mở còn sau reload rồi được đóng. [Ảnh lệnh](ui-backend-restart-live.png), [ảnh phiên phục hồi](ui-open-experiment-restored-live.png).
- [Outage](ui-broker-outage-v2.log) dừng riêng broker QA khi có PENDING; UI khóa. [Audit Serial theo thứ tự nhân quả](offline-auto-causal-audit.json) chứng minh mqtt0/AUTO/NIGHT25 trước thao tác LDR và mqtt0/AUTO/DAY0 sau thao tác, trước khi broker được khởi động lại.
- [Audit reconnect](broker-recovery-audit.json): cùng boot, fresh lại; command cũ TIMEOUT/attempts1, **0 publish lại command cũ sau reconnect**, một command mới APPLIED. [Ảnh offline](ui-broker-offline-live.png), [ảnh phục hồi](ui-broker-recovered-live.png). Không suy thành bảo đảm quan sát vô hạn.

### Latency cảm biến → dashboard

**10/10 mẫu hợp lệ PASS**; không loại mẫu chậm. Median nằm trong **1417,832–1464,491ms**, max trong **2353,967–2401,274ms**, đã tính sai số clock. [Tổng hợp và đối chiếu độc lập MQTT/API/DOM](latency-summary.json), [toàn bộ12 lượt gồm2 pilot](latency-trials.json), [raw browser events](latency-events-v4.jsonl), [video hai cửa sổ](latency-side-by-side.mp4), [metadata video](video-metadata.json), [ảnh bố trí](latency-desktop-before.png).

LDR được tác động bằng **phím Home/End thật** trong UI Wokwi VSCode, tương ứng0,1/100000 lux. Đây là phương án dự phòng với hai đầu slider có bước tác động rời rạc; không đổi firmware, timer hoặc ngưỡng. Hai pilot được định trước và tách khỏi10 mẫu nghiệm thu. Các khoảng chờ giữa thao tác đã được định trước để thay đổi pha lấy mẫu. Tiến trình điều phối foreground bị kết thúc mã143 sau8 mẫu; bộ ghi vẫn giữ dữ liệu, chỉ thu tiếp mẫu9/10, không lặp hoặc bỏ mẫu.

Mốc t0 là KeyboardEvent trusted trong control LDR, t4 là DOM hiển thị đúng boot/seq/ADC sau hai requestAnimationFrame. Clock browser được chặn bằng nhiều lượt trao đổi trước/sau từng phép đo; dùng khoảng sai số, không lấy uptime node trừ thời gian host. Mỗi mẫu đối chiếu telemetry MQTT thật, API last_seen và DOM; raw ADC nằm trong vùng nhìn thấy, trang không hidden trong khoảng đo. Video30fps chỉ bổ trợ quan sát, không phải phép đo photon màn hình. Serial có thời lượng ghi giới hạn để chứng minh AUTO offline, không dùng thời điểm nhận Serial làm t0 hoặc khẳng định có Serial cho từng mẫu latency.

Điều kiện: một node, Wokwi hiển thị xấp xỉ99–100% tại các mốc quan sát; hai cửa sổ960x1040 cạnh nhau, dashboard viewport thật. [Phiên bản](versions.json) được lấy sau đo, không phải log tải CPU liên tục. Command → ACK cũ:10 lượt, median686,217ms/max1002,001ms, xem [nguồn cũ](../run-20261116-180648/command-latency-command-latency.json).

## Lỗi backend phát hiện và đã sửa

Sau restart backend, telemetry mới liên tục UNCONFIRMED_BOOT dù node vẫn cùng boot. Actor đã kiểm readiness trước khi chờ queue; availability ONLINE retained tới trong lúc chờ bị xử lý với session cũ. [Bằng chứng trước sửa](restart-regression-before-fix.json).

Service hiện đồng bộ connected/session ngay sau dequeue, trước dispatch, và vẫn đồng bộ khi idle/tick. Không đổi MQTT/HTTP API, schema SQLite hoặc điều khiển. Bốn trường hợp hồi quy kiểm session mới/cũ khi khởi động/reconnect: **trước sửa2 FAIL/2 PASS**, [log tái hiện](backend-regression-red.log); **sau sửa72 Pytest/Ruff PASS**, [log](backend-fix-checks.log). Warning TestClient/HTTPX cũ giữ nguyên. [Publication/hash](backend-fix-publication.json), [fresh cùng boot sau sửa](restart-after-fix-nodes.json). Đã tạo nhánh backend trước khi sửa, không commit.

Lượt UI đầu dùng nhầm hậu tố HTTP `/commands` cho proxy MQTT nên chỉ tạo AUTO/APPLIED; sửa riêng công cụ về topic thật `/command`, giữ log thất bại và chạy lại hai tiêu chí UI còn thiếu. Một locator phiên đo cần khớp ID thay vì tên hiển thị kèm timestamp; các log chờ thất bại được giữ, không coi đó là lỗi sản phẩm. [Proxy4 test](proxy-checks.log) kiểm framing/QoS/stream chia nhỏ/giữ-thả ACK/scope.

## Môi trường QA và cách đối chiếu

```text
Wokwi node_01 → host.wokwi.internal:1883 → proxy1883 → Mosquitto QA11884
Backend/API8001 → proxy11883 → cùng Mosquitto QA11884
Observer → Mosquitto QA11884
Live Server5500 → bản dashboard QA cấu hình API8001
```

Chỉ các cổng loopback. Broker dùng image eclipse-mosquitto:2.1.2-alpine có sẵn, container có nhãn sở hữu riêng; SQLite `/tmp/task010-completion/qa.db`. Bản dashboard QA chỉ đổi config.js sang8001; các tệp ứng dụng đối chiếu [manifest nguồn](dashboard-qa-source.json). Source dashboard thật vẫn API8000 và không sửa. Không chuyển broker public hoặc dừng dịch vụ dùng chung.

CLI0.29.1 tìm thấy token trong .bashrc nhưng máy chủ trả **Unauthorized** khi bắt đầu mô phỏng; [preflight](preflight.json), [log có redaction](events.jsonl). Không suy nguyên nhân token và không đăng ký/mua dịch vụ. Dùng Wokwi VSCode4.1.0 theo phương án dự phòng đã chọn; artifact hiện có fresh/hash khớp nên không build lại.

Để tái kiểm hồi quy backend, chạy `.venv/bin/python scripts/check.py` tại repo backend. Để kiểm lõi proxy chuẩn thư viện: `python3 -B tools-as-run/test_proxy.py` từ thư mục hồ sơ này. [Công cụ đã dùng](tools-as-run/) được lưu đúng source của lượt Linux, gồm đường dẫn SDK/cache, PID guard và cấu hình cụ thể; chúng là hồ sơ phương pháp, **không chạy runner/cleanup mù quáng trên máy khác**. Khi tái lập live phải tạo lượt QA mới, xác minh cổng/quyền sở hữu, chọn source/SDK hiện tại và giữ nguyên mọi file bằng chứng cũ. Không khởi động lại toàn bộ ca đã PASS chỉ để tạo thêm log.

## Khôi phục, bảo toàn và phần ngoài phạm vi

[Cleanup](cleanup.json): cửa sổ/profile VSCode QA, Chrome đo, backend, Live Server, proxy/collector và container QA đã dừng; không còn listener trên các cổng QA. Kiểm bind ngay sau stop từng có TIME_WAIT; đối chiếu LISTEN và connect_ex=111 để xác minh đã dừng, không force-kill process chưa rõ. QA DB giữ tại /tmp, các phiên QA đã đóng, không còn command PENDING trong snapshot cuối. Video được chốt hợp lệ và bao phủ cả10 mẫu. Preview ban đầu có nền cửa sổ trong suốt được loại khỏi hồ sơ; chỉ video sau khi đặt hai cửa sổ opaque được dùng, raw timing không đổi.

Bảo toàn report cũ từng byte và toàn bộ bằng chứng trước lượt này; kết quả kiểm tra trong verification.json và manifest. Không sửa firmware/pin map/toolchain/SRS; backend chỉ sửa race và thêm test/tài liệu; source dashboard giữ nguyên.

Đây là nghiệm thu **một node trong Wokwi**, không phải phần cứng thật, ba node/stability30phút, EX-series hoặc toàn đồ án. TASK-011 tiếp tục chờ đặc tả chính thức; không tự triển khai bước tiếp theo.
