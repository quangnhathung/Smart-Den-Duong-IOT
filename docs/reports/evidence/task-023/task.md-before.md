# TASK-022 — Dừng toàn bộ dịch vụ dự án

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu
- Cập nhật: 2026-11-18T19:58:51+07:00

## Mô tả và phạm vi

Người dùng yêu cầu “dừng cho tôi tất cả”, thay thế yêu cầu khởi động đang thực hiện. Dừng MQTT, cả ba phiên node, backend, FE và launcher của đợt khởi động; bảo toàn dữ liệu và ứng dụng không liên quan. TASK-021 đã hủy ở2/4; chưa nghiệm thu đủ ba node.

## Tham chiếu SRS

SRS3–8/13; thao tác vận hành/dừng local, không triển khai FR mới.

## Tiêu chí hoàn thành và tiến độ

- [x] Xác định container/PID/cửa sổ thuộc dự án, giữ ứng dụng khác.
- [x] Dừng MQTT/backend và renderer/extension host liên quan ba node/FE, không còn listener1883/8000/5500/4000/4001/4002.
- [x] Giữ dữ liệu/source, lưu bằng chứng và cập nhật task/báo cáo/lịch sử; không tự khởi động lại.

## Vướng mắc và cách giải quyết

Đóng cửa sổ ban đầu chưa giải phóng4000/5500; dùng code --status đối chiếu đúng renderer/extension host/file watcher của cửa sổ3–6 rồi dừng. Đã kiểm các cổng trống. Không có vướng mắc còn lại.

## Phụ thuộc và điều kiện bắt đầu

Đã được người dùng yêu cầu dừng. [Hồ sơ](evidence/task-022/README.md). Chỉ chạy lại khi có yêu cầu mới.
