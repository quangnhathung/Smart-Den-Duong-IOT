# TASK-009 — Dashboard HTML/CSS/JS và API đọc bổ sung

Hoàn thành phạm vi code/test/hướng dẫn P5/A5 ngày2026-11-16. Ba repo cạnh nhau: firmware (tài liệu chung), backend (giữ lịch sử Git có sẵn), dashboard (Git main riêng mới, chưa commit/remote). Không commit/push/deploy; không sửa source firmware/toolchain/MQTT.

## Thay đổi

- Dashboard năm view sáng/responsive theo ui-ux-pro-max, JS ES modules/CSS/SVG nội bộ, không framework/build/CDN. Chạy http://127.0.0.1:5500 bằng VS Code Live Server. [Hướng dẫn](../../../../../dashboard/README.md), [thiết kế và hành vi](../../../techs/dashboard.md).
- Backend thêm GET list/detail experiments, history.continuity, CORS5500 giữ5173; không migration hoặc đổi thuật toán.12 HTTP operations/11 OpenAPI paths. [OpenAPI](openapi.json).
- [Manifest source](source-manifest.json): SHA256 của15 tệp dashboard và7 tệp backend thay đổi, kiểm lại tại repo bàn giao. Bản task cũ giữ nguyên tại [task-008-before-task009.md](task-008-before-task009.md).

## Kết quả thực tế

| Tầng | Kết quả và bằng chứng | Giới hạn |
|---|---|---|
| JavaScript |16/16 PASS, [javascript-checks.log](javascript-checks.log), Node24.17 | Logic/HTTP giả, không firmware thật |
| Backend |68/68 Pytest PASS; Ruff check/format PASS, [backend-checks.log](backend-checks.log) | Python3.12/DB tạm/clock và MQTT giả;1 warning TestClient/HTTPX có sẵn |
| Browser chính |18 mục PASS, [browser-checks.log](browser-checks.log) | Live Server engine/API/SQLite thật, telemetry/ACK là fixture |
| Browser bổ sung |8 mục PASS, [browser-negative.log](browser-negative.log) | REJECTED/TIMEOUT được mock; POST bị chặn có chủ đích |
| Bản bàn giao | Health/command APPLIED/history/experiments đạt,0 console error/0 uncaught JS exception, [browser-final.log](browser-final.log) | API thực từ repo backend với transport giả |
| Định dạng | Prettier check: All matched files use Prettier code style | Công cụ dev một lần, không dependency runtime |
| Live MQTT/Wokwi/Windows | Chưa chạy | Không coi fixture là nghiệm thu live |

Browser chính kiểm: ba node gồm một unknown; MANUAL chỉ một POST và ACK tách PWM; draft giữ qua polling; SVG/chart/range bàn phím; alerts; phiên cũ/CSV/start/reload/stop; viewport375/768/1024/1440 không tràn; reduced motion; mất API khóa điều khiển; phục hồi không replay. Browser bổ sung kiểm từ chối/timeout/lý do, mất phản hồi POST không retry, cả4 màn hình còn lại không tràn375px và không uncaught exception. Mất API chủ động tạo resource errors trong console là kỳ vọng; không gộp chúng thành lỗi ứng dụng hoặc tuyên bố toàn phiên không có resource error.

## Ảnh và dữ liệu kiểm tra có nhãn

- [Desktop tổng quan](overview-desktop-fixture.png), [mobile375](overview-mobile-fixture.png).
- [Chi tiết node](node-desktop-fixture.png), [lịch sử](history-desktop-fixture.png).
- [CSV fixture](experiment-fixture.csv): chỉ mẫu tổng hợp, không dùng làm kết quả EX-series.

Banner “BỘ KIỂM TRA GIAO DIỆN · DỮ LIỆU GIẢ LẬP” do script kiểm thêm vào DOM trước ảnh. Source dashboard không có fallback demo khi API lỗi. Fixture có node_01 bình thường, node_02 OPEN_LOAD, node_03 chưa telemetry, phiên có tên nguồn giả lập.

## Tái lập

1. Từ backend: `.venv/bin/python scripts/check.py`; từ dashboard: `node --test tests/*.test.mjs`.
2. Mở folder dashboard riêng trong VS Code → Open with Live Server. Backend thật chạy theo README để kiểm hệ thống thực. Dừng dịch vụ của mình trước khi chuyển sang QA fixture, tránh đụng cổng/dữ liệu người dùng.
3. Nếu cần tái lập QA: từ backend, dùng `.venv/bin/python ../firmware/docs/reports/evidence/task-009/qa-fixture.py`. Script chỉ dùng transport giả, DB mới `/tmp/task009-browser-fixture-*.db`, không dùng DB production hoặc broker. Bản script lưu đã thay đường dẫn import tuyệt đối bằng đường dẫn repo tương đối; logic giống lượt đã chạy.
4. Dùng Playwright CLI mở http://127.0.0.1:5500/, viewport1440x900, chạy callback trong [browser-flow.js](browser-flow.js), rồi [browser-negative.js](browser-negative.js), [browser-final.js](browser-final.js). Scripts là QA callback cho CLI run-code, không module web; từ thư mục tạm có `output/playwright/` để ghi ảnh/log. Snapshot trước thao tác; không đặt output vào đường Live Server theo dõi. Lượt này dùng wrapper skill Playwright, Chromium, Linux và live-server2.2.0 trong extension ritwickdey.liveserver5.7.10.
5. Ctrl+C API fixture, tắt Live Server và đóng browser. Các dịch vụ QA của lượt này đã dừng; không giữ API giả ở cổng8000 sau bàn giao.

Chưa thao tác Go Live qua UI VS Code/Windows trong phiên này; đã chạy đúng engine extension với host/root/port tương ứng. Chưa đo cảm biến→dashboard/command→ACK10 lượt, MANUAL60s theo clock node, reconnect/socket thực, ba node/stability30phút hoặc EX-series. Xem next-task.md cho đề xuất riêng.

## Vướng mắc và xử lý

Không có vướng mắc còn chặn phạm vi bàn giao. Khi phát triển, ảnh/log trong root Live Server từng gây tự reload; đã bổ sung ignoreFiles/ignore tương ứng và chạy lại browser đạt. Một assertion ban đầu giả định PWM đổi ngay sau ACK đã sửa để chờ telemetry riêng đúng hợp đồng. Quyền ghi hai repo cùng cấp được cấp qua công cụ; script so hash gốc trước khi ghi, xác minh hash sau copy để bảo toàn thay đổi có sẵn. Warning TestClient/HTTPX giữ nguyên stack đã chốt.
