# TASK-023 — Kiểm tra và khởi động hệ thống local

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 mục nghiệm thu
- Cập nhật: 2026-11-18T20:05:42+07:00

## Mô tả và phạm vi

Người dùng yêu cầu kiểm tra dự án và khởi động 3 node Wokwi, backend, Live Server, MQTT. Kiểm tra cấu hình/artifact, dùng dịch vụ local đã có, giữ dữ liệu và thay đổi của người dùng. Không chạy thực nghiệm, nâng toolchain hoặc sửa chức năng ngoài yêu cầu.

## Tham chiếu SRS

SRS mục3–8,12–13: vận hành ba node, MQTT, collector/API và dashboard. Không coi kế hoạch hoặc kết quả cũ là kết quả lượt này.

## Tiêu chí hoàn thành và tiến độ

- [x] Kiểm tra cấu hình, artifact và dịch vụ/cổng trước khởi động.
- [x] MQTT1883/backend8000 hoạt động, health database/broker/queue đạt.
- [x] Ba node định danh riêng, nhận telemetry mới và ONLINE/FRESH tại backend.
- [x] Live Server5500 trả dashboard; lưu bằng chứng, cập nhật báo cáo/checklist/đề xuất.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn lại về khởi động. Đã chạy lệnh vận hành với quyền được cấp. Helper chụp ảnh thiếu Pillow sau khi gửi lệnh Wokwi; bỏ bước ảnh tùy chọn và kiểm chứng mô phỏng bằng MQTT/API. Không có trình duyệt kết nối với công cụ CUA nên chưa kiểm DOM/render dashboard; HTTP200 đã đạt.

## Phụ thuộc và điều kiện bắt đầu

Yêu cầu khởi động mới đã nhận; dùng Docker/venv backend/VS Code Wokwi/Live Server hiện có. Giữ nguyên DB backend/data/smartlight.db.

## Kết quả và giới hạn

Ba node ONLINE/FRESH, subscriber độc lập nhận2 telemetry/node; health OK/database/broker/queue=true/dropped_events=0. Live Server5500 HTTP200, MQTT1883, API8000, RFC2217 4000/4001/4002. Giữ stack hoạt động. Hash source/BIN/ELF đã chuẩn bị khớp manifest; không build hoặc chạy bộ kiểm thử/ổn định30 phút mới. [Bằng chứng](evidence/task-023/README.md).
