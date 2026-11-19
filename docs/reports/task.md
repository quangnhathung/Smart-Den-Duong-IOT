# TASK-025 — Kiểm tra và khởi động hệ thống local

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 mục nghiệm thu
- Cập nhật: 2026-11-19T07:28:45+07:00

## Mô tả và phạm vi

Khởi động3 node Wokwi/backend/Live Server/MQTT theo yêu cầu mới. Kiểm cấu hình/artifact/cổng, giữ dữ liệu và thay đổi người dùng. Không nâng toolchain hoặc tự chạy thực nghiệm.

## Tham chiếu SRS

SRS3–8/12–13: vận hành local, FR06–07; không nghiệm thu lại toàn bộ SRS.

## Tiêu chí hoàn thành và tiến độ

- [x] Kiểm cấu hình, artifact và cổng/tiến trình trước khởi động.
- [x] MQTT1883/backend8000, health database/broker/queue đạt.
- [x] Ba node ONLINE/FRESH, có telemetry mới từ MQTT độc lập.
- [x] Live Server5500 HTTP200; lưu bằng chứng/cập nhật tài liệu và giữ stack chạy.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn lại về khởi động. Docker báo chưa có socket ở lần đầu, kiểm lại daemon đã hoạt động. Node03 chưa có MQTT lúc kiểm đầu, sau đó kết nối và đủ telemetry; không đổi firmware.

## Phụ thuộc và điều kiện bắt đầu

Đã có yêu cầu mới; dùng venv/VS Code/extensions/artifact đã có. Giữ DB backend/data/smartlight.db.

## Kết quả và giới hạn

Ba node ONLINE/FRESH và subscriber độc lập đủ2 telemetry/node trở lên. Health OK/database/broker/queue=true/dropped_events=0. Live Server5500 HTTP200; giữ stack chạy. Hash source/artifact khớp, không build mới. Chưa kiểm DOM/render hoặc ổn định30 phút; CUA không có browser/app kết nối. [Bằng chứng](evidence/task-025/README.md).
