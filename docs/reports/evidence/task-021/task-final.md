# TASK-021 — Khởi động toàn hệ thống local

- Trạng thái: Đã hủy
- Tiến độ: 2/4 nhóm nghiệm thu
- Cập nhật: 2026-11-18T19:43:23+07:00

## Mô tả và phạm vi

Người dùng yêu cầu chạy MQTT, ba node Wokwi, backend và FE. Khởi động hoặc tái sử dụng đúng dịch vụ trên máy hiện tại, FE bằng VS Code Live Server theo stack đã chốt. Giữ dịch vụ hoạt động để người dùng thao tác. Không tự chạy chiến dịch thực nghiệm, sửa thuật toán, xóa dữ liệu cũ hoặc triển khai cloud. Mã021 vì020 đang là đề xuất diễn tập chưa thực hiện; task019 và đề xuất020 đã lưu snapshot.

## Tham chiếu SRS

SRS3–8/12–13, FR06–08: kiểm luồng telemetry ba node và trạng thái ứng dụng, không nghiệm thu lại toàn bộ SRS.

## Tiêu chí hoàn thành và tiến độ

- [ ] Kiểm cổng/tiến trình, cấu hình, artifact và dữ liệu; bảo toàn thay đổi người dùng.
- [ ] MQTT local và backend một worker hoạt động, health/database/broker đạt.
- [ ] Ba Wokwi đúng node/boot phát telemetry mới; backend nhận đủ ONLINE/FRESH.
- [ ] FE Live Server mở được, hiển thị dữ liệu thật; ghi URL/PID/log, cập nhật hồ sơ và giữ stack chạy.

## Vướng mắc và cách giải quyết

Đang kiểm tra môi trường sau khi máy khởi động lại. Chỉ số kiểm cũ là tham chiếu, không dùng PID/profile cũ mà chưa xác minh. Có sửa sẵn .vscode/extensions.json của người dùng, giữ nguyên.

## Phụ thuộc và điều kiện bắt đầu

Đã được giao. Cần runtime/extension/license Wokwi còn dùng được, broker và Python venv. Nếu cổng đã có dịch vụ, xác minh trước khi tái dùng. Không tự thực hiện TASK-020 diễn tập con người.

## Kết thúc theo yêu cầu người dùng

Người dùng yêu cầu dừng tất cả khi chưa hoàn tất ba node. Đã xác minh artifact nguồn, MQTT/backend health và node01 ONLINE/FRESH; FE trả HTTP200 nhưng chưa nghiệm thu DOM, node02/03 chưa có telemetry. Không ghi PASS toàn hệ thống. TASK-022 dừng stack và kiểm cổng.
