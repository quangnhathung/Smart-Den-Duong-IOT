# TASK-024 — Dừng dịch vụ dự án

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu
- Cập nhật: 2026-11-18T20:30:55+07:00

## Mô tả và phạm vi

Dừng ba node Wokwi, backend, Live Server và MQTT vừa khởi động trong TASK-023 theo yêu cầu người dùng; giữ DB/source và ứng dụng khác. Đề xuất kiểm dashboard024 trước đây chưa thực hiện, lưu snapshot.

## Tham chiếu SRS

SRS3–8/13: vận hành local, không triển khai FR mới.

## Tiêu chí hoàn thành và tiến độ

- [x] Đối chiếu sở hữu container/PID/workspace hiện tại.
- [x] Dừng dịch vụ, xác minh1883/8000/5500/4000/4001/4002 không còn listener.
- [x] Lưu bằng chứng, giữ dữ liệu và cập nhật lịch sử.

## Vướng mắc và cách giải quyết

Không có. Đã đối chiếu PID/start ticks và workspace trước khi dừng.

## Phụ thuộc và điều kiện bắt đầu

Đã có yêu cầu dừng; không tự khởi động lại.

## Kết quả

Đã dừng MQTT/backend/ba Wokwi/Live Server. Sáu cổng dự án không còn listener; giữ DB/source và VS Code firmware gốc. [Bằng chứng](evidence/task-024/README.md).
