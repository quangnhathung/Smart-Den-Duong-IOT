# TASK-009 — Dashboard HTML/CSS/JS thuần qua VS Code Live Server

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu code/test/hướng dẫn
- Cập nhật: 2026-11-16T14:18:00+07:00

## Mô tả và phạm vi

Dashboard DoAn/dashboard/, Git riêng; HTML/CSS/JS ES modules, không framework/build/CDN, Live Server127.0.0.1:5500. Giao diện sáng Data-Dense Dashboard theo ui-ux-pro-max, gọi API TASK-008. Được phép bổ sung GET list/detail experiments, continuity history và CORS5500; không đổi MQTT/firmware. Không commit/push/deploy.

## Tham chiếu SRS

SRS7.3/8/9/12, TC17–22/26 và kiểm tra UI/thời gian. Yêu cầu mới thay stack React/TypeScript/Vite bằng HTML/CSS/JS/Live Server; cập nhật đúng phần stack và read API trong SRS, giữ yêu cầu nghiệp vụ.

## Tiêu chí hoàn thành và tiến độ

- [x] Thiết kế sáng/responsive/a11y,5 màn hình và Live Server hoạt động.
- [x] Dữ liệu/health/polling/uint64/stale và AUTO/MANUAL/ACK không POST lặp, xử lý lỗi/unknown đúng.
- [x] History gap/continuity, charts/table/pagination, alerts/experiments/stats/CSV; API read bổ sung/CORS đạt.
- [x] JS tests/backend regression/browser responsive/console/keyboard/reduced-motion, tài liệu/evidence/báo cáo hoàn tất.

## Kiểm tra và bằng chứng

16 Node test,68 Pytest/Ruff,18 browser checks +8 bổ sung PASS. Smoke bản bàn giao:0 console error/0 uncaught JS exception. [Hồ sơ TASK-009](evidence/task-009/README.md). Live Server engine của extension đã chạy; Go Live qua UI VS Code/Windows, MQTT/Wokwi thật, latency và ba node chưa chạy, không được ghi PASS từ fixture. Không đổi firmware/toolchain, không build lại hoặc commit/push/deploy.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn chặn phạm vi bàn giao. Đã thêm Live Server ignore cho ảnh/log để tránh reload khi QA và sửa assertion chờ telemetry riêng sau ACK. Quyền ghi repo cùng cấp đã được cấp, kiểm hash trước/sau copy.1 deprecation warning TestClient/HTTPX cũ giữ nguyên stack. Các dịch vụ QA đã dừng.

## Phụ thuộc và điều kiện bắt đầu

Người dùng giao thực hiện kế hoạch và chọn theme sáng/API read tối thiểu. Giữ mọi thay đổi TASK-008 có sẵn; lưu bản task cũ trong evidence/task-009/task-008-before-task009.md. Không tự làm task tích hợp tiếp theo.
