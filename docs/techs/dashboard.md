# Dashboard P5/A5 — TASK-009

## TASK-011 — Dashboard ba node qua Live Server

Giữ nguyên HTML/CSS/JS và API của repo dashboard, không sửa giao diện. Bản QA đối chiếu hash source, chỉ đổi URL API sang8001; Live Server5500 dùng engine từ extension VS Code đã cài. Đã kiểm ba node tách dữ liệu và điều khiển đúng đích; broker down hiển thị Kết nối suy giảm/0 node online/giá trị cũ, phục hồi nhận dữ liệu mới. Ba mươi phép đo LDR→API→DOM sau hai rAF hợp lệ,10/node, đều dưới3s trên firmware sửa coalescing cảm biến. Cận trên lớn nhất1.272,235ms; không phải phép đo photon màn hình. Raw flags INCOMPLETE do nhãn100k lux giữ nguyên, [audit cuối](../reports/evidence/task-011/run-20261117-135233/latency-final-audit.json) kiểm đơn vị k=1000 từ chính log đã thu, không thay timestamp hoặc bỏ mẫu chậm. Cửa sổ30phút cuối chưa đóng; EX-series chưa thực hiện.


## TASK-010 — UI đã kiểm live một node, 2026-11-17T12:05:29+07:00

UI REJECTED/EXPIRED, TIMEOUT/ACK_TIMEOUT và ACK muộn giữ kết quả cuối đã quan sát trực tiếp; restart pending/open experiment, reload phiên, khóa khi broker QA ngừng và mở lại sau reconnect đều PASS. 10 mẫu LDR→DOM thật đạt3s, max cận trên2401,274ms; [ảnh/video, số liệu và phương pháp](../reports/evidence/task-010/completion-20261117-105535/README.md). Không dùng fixture hay mock response API trong các ca nghiệm thu này.

Bản chạy QA là copy source đối chiếu hash, chỉ config.js đổi API8001/Live Server5500. Repo dashboard gốc vẫn API8000, không đổi giao diện hoặc runtime. Sửa nằm ở backend Service để không bỏ retained ONLINE sau restart. Hai cửa sổ cùng hiển thị, viewport thật và LDR raw trong vùng nhìn thấy; DOM sau hai rAF là đại diện render, không phải phép đo photon màn hình. Những giới hạn fixture/PENDING cũ phía dưới là hồ sơ thời điểm TASK-009/lượt trước, không phủ định bổ sung live này.


## Đối chiếu môi trường sau pull — 2026-11-17T09:45:17+07:00

Repo dashboard local ở main `6cb402b`, sạch trước lượt rà soát; config.js dùng `http://127.0.0.1:8000`, chưa có `tests/task010-live-latency.html`. Bằng chứng TASK-010 trên Windows dùng API8001, Live Server5500 và bộ ghi trong tests/. Firmware main đã có bằng chứng mới không chứng minh repo dashboard ở máy khác đã đồng bộ source/cấu hình. Đây là khác biệt môi trường cần đối chiếu trước lượt live tiếp; chưa xác định lỗi chức năng và không tự đổi cổng hoặc pull repo khác.

[Kết quả rà soát](../reports/evidence/task-010/review-20261117-094517/README.md) giữ TASK-010 ở 2/4 nhóm. Kết quả UI fixture TASK-009 và các xác nhận Dashboard live TASK-010 có nguồn riêng; chưa chốt UI trạng thái cuối REJECTED/TIMEOUT hoặc cảm biến → dashboard đủ 10 mẫu. Lượt này chỉ cập nhật tài liệu, không sửa giao diện nên không có thiết kế hoặc kiểm thử browser mới.


## Tham chiếu SRS

SRS7.3/8/9/12, TC17–22/26 và các ca UI/clock. Người dùng chốt HTML/CSS/JavaScript thuần, VS Code Live Server, theme sáng và API read tối thiểu; thay phần React/TypeScript/Vite trong SRS theo yêu cầu mới. Không thay MQTTv1 hoặc logic điều khiển/năng lượng. Kết quả task là code/test/hướng dẫn A5; chưa nghiệm thu tích hợp live.

## Triển khai và cấu hình

Repo Git riêng `DoAn/dashboard/`, nhánh main; không remote/commit/push trong task. [README dashboard](../../../dashboard/README.md) hướng dẫn Linux/PowerShell và Live Server. Mở riêng folder dashboard trong VS Code, Open with Live Server tại index.html → http://127.0.0.1:5500/. Không cần npm/build/framework/CDN; không dùng file://. API mặc định http://127.0.0.1:8000 trong config.js, timeout4s. Backend cần một worker theo [backend.md](backend.md).

`.vscode/settings.json` đặt host127.0.0.1, port5500, root `/`, không useLocalIp. Bỏ theo dõi `.git`, output, `.playwright-cli`, tests, Markdown để log/ảnh kiểm tra không gây reload. CORS backend thêm localhost/127.0.0.1:5500, giữ5173; đổi origin phải cấu hình SMARTLIGHT_ORIGINS tương ứng. Không mở Internet/deploy.

| Tệp/module | Trách nhiệm thực tế |
|---|---|
| index.html, css/styles.css | Năm view semantic, sidebar/menu mobile, card/tables/forms, responsive và reduced motion |
| config.js, js/api.js | URL/timeout, fetch JSON/CSV, AbortController, lỗi HTTP, polling không chồng request |
| js/core.js | UTC/giờ Việt Nam, decimal uint64/BigInt, validate lệnh, trạng thái lệnh, nối mẫu |
| js/charts.js | SVG brightness bậc thang/power đường, nhãn và chấm cho mẫu đơn |
| js/app.js | Hash route, state/draft, tải/hiển thị dữ liệu, form/pagination, export |
| design-system/MASTER.md | Theme sáng Data-Dense Dashboard theo skill ui-ux-pro-max |
| tests/*.test.mjs | Node built-in test; không phải dependency runtime |

Hash routes `#overview`, `#nodes/node_01` (đổi node trong view), `#history`, `#alerts`, `#experiments`. Tổng quan gồm health,4 KPI, tuyến đèn SVG và ba card; node chưa có telemetry không bịa số. Chi tiết có ADC/môi trường/motion/distance/target/applied/current/power/fault/last_seen/uptime/boot. Lịch sử có bộ lọc node/khoảng giờ/phiên, chart, thống kê backend và bảng raw. Alerts phân trang/lọc node. Phiên có list/detail/create/stop/CSV, đọc lại server sau reload và chỉ một phiên mở.

## Polling, điều khiển và lỗi

Health/nodes/kết quả command mỗi1s; stats/alerts/list phiên đang xem mỗi5s. Poller không chồng request cùng nhịp; refresh khi đang chạy được xếp tải lại ngay sau đó. Đổi bộ lọc/ngữ cảnh hủy request cũ, detail phiên có số thứ tự để bỏ response cũ. Tab ẩn tạm dừng/hủy GET, hiện lại đồng bộ và khóa thao tác trước khi có trạng thái mới. Request POST không tự retry.

Chỉ nút Áp dụng gửi lệnh: AUTO bỏ brightness, MANUAL nguyên0–100. Khóa ngay khi submit/pending, API lỗi, node không can_command, stale/offline hoặc đang đồng bộ. Form draft tách telemetry và giữ qua polling. 202 chưa là APPLIED; trạng thái cuối lấy GET command. APPLIED chỉ xác nhận chế độ/mục tiêu, PWM thực có thể đang dim và vẫn hiển thị từ telemetry. MANUAL60s theo clock node, UI giải thích thay vì đếm theo wall clock.

Mất phản hồi POST tạo UNCERTAIN, không tự báo thành công/timeout. Poll nodes đối chiếu pending_command_id: nếu có thì tiếp tục GET command, nếu trạng thái fresh và không pending thì cho phép người dùng chủ động gửi mới với thông báo vẫn chưa xác định kết quả cũ. Kết quả GET lỗi không ghi đè lệnh mới. Mất API giữ snapshot và nhãn cũ, khóa nút; phục hồi không tự replay POST. Fault tải tách khỏi offline và không tự xóa khi mất kết nối.

## Lịch sử, thời gian và API bổ sung

- Query from/to UTC, UI nhập/hiển thị giờ Việt Nam UTC+7. Kiểm tra round-trip lịch để từ chối ngày không hợp lệ. seq/uptime/deadline HTTP giữ chuỗi thập phân, chênh lệch dùng BigInt; không ép uint64 sang Number.
- History tải tối đa1000 mẫu/trang, bảng100 mẫu/lần trong trang; chart chỉ phản ánh trang đã chọn, có nhãn số lượng. Ngắt đường khi quality không ACCEPTED, đổi boot/continuity, seq/uptime/received_at không tăng hoặc Δuptime>6s. Mẫu đơn hiển thị chấm. Range điều hướng mẫu bằng bàn phím; bảng raw để đọc chính xác.
- Stats năng lượng/baseline/coverage/clock_basis lấy nguyên thuật toán backend, không tính lại điện năng trên trình duyệt. Node thiếu vẫn góp khoảng thiếu theo API; không lấp gap bằng fixture.
- GET experiments list/detail bổ sung để phục hồi phiên sau reload; list mặc định100/max1000, offset không âm, thứ tự started_at DESC/id DESC. Trả config/notes/start/end; detail thiếu404. History thêm continuity từ dữ liệu đã có; không đổi SQLite schema/MQTT.
- Export fetch→kiểm status/content-type→blob/download; phản hồi JSON lỗi không được lưu thành CSV. Tên phiên/metadata được escape khi đưa vào HTML.

## Thiết kế và khả năng truy cập

Nền slate sáng/card trắng, chữ tương phản, xanh lục hành động/online, amber cảnh báo, đỏ lỗi; mọi trạng thái có chữ. Font hệ thống/SVG nội bộ; focus rõ, input có label, heading/landmarks, phản hồi aria-live, chart có nhãn và bảng thay thế. Mobile menu xếp dòng, bảng có vùng cuộn riêng; hỗ trợ prefers-reduced-motion. [Ảnh desktop](../reports/evidence/task-009/overview-desktop-fixture.png), [ảnh mobile](../reports/evidence/task-009/overview-mobile-fixture.png) có banner dữ liệu giả lập do test thêm vào DOM, không phải demo fallback trong ứng dụng.

## Kiểm tra

16 Node test,68 Pytest/Ruff,18 kiểm tra browser chính +8 bổ sung PASS. Browser dùng Playwright CLI, engine Live Server2.2.0 từ VS Code extension5.7.10 trên Linux, API/SQLite thật và transport MQTT giả; REJECTED/TIMEOUT ở pha bổ sung dùng phản hồi mock. Viewport375/768/1024/1440, thao tác bàn phím/range, draft, lệnh/no retry, chart/alerts, phiên/reload/CSV, stale/recovery/reduced motion. Lượt cuối tại repo bàn giao0 console error/0 uncaught JS exception. [Log, scripts QA và manifest](../reports/evidence/task-009/README.md).

## Giới hạn và vấn đề còn lại

Không có lỗi chặn trong phạm vi UI/host đã kiểm. Một warning TestClient/HTTPX cũ của backend còn nguyên, không nâng dependency để che warning. Chưa thao tác Go Live qua UI VS Code/Windows; đã dùng đúng engine của extension và lưu cấu hình. Chưa chạy MQTT/Paho/socket/Wokwi thật, đo latency10 lượt, ba node30phút hay EX-series. Các kết quả fixture không chứng minh TC tích hợp PASS. Các dịch vụ QA tạm được dừng sau kiểm tra; chạy môi trường thật theo README khi được giao tích hợp.
