# TASK-006 — Thuật toán chiếu sáng AUTO/MANUAL P2/A2

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 mục nghiệm thu dự kiến
- Cập nhật: 2026-11-16T02:56:10+07:00

## Mô tả và phạm vi

Đề xuất triển khai logic chiếu sáng một node: AUTO theo môi trường/chuyển động, MANUAL có thời hạn, hold/dimming và fault theo SRS. Giữ source dùng chung, pin map, toolchain và hợp đồng đã chốt. Chưa triển khai trong lượt nghiệm thu TASK-005.

## Tham chiếu SRS

SRS mục 5, 10 P2, 11 A2, 12; architecture.md và mqtt.md. Trước khi triển khai phải đọc lại bảng ngưỡng/timer/ưu tiên và chốt checklist cụ thể trong task.md.

## Tiêu chí hoàn thành và tiến độ

- [ ] Logic AUTO, môi trường/chuyển động và ưu tiên đúng SRS; kiểm thử dữ liệu/clock giả lập.
- [ ] MANUAL, thời hạn/fallback, hold và dimming đúng SRS; không tự mở rộng giao thức MQTT A3.
- [ ] Fault/phục hồi và các biên timer/tràn được kiểm tra theo phạm vi A2.
- [ ] Build environment bị ảnh hưởng, tài liệu và bằng chứng phù hợp; phân biệt host/build/live, không tự triển khai A3.

## Vướng mắc và cách giải quyết

Không có phụ thuộc TASK-005 còn chặn. Các hạn chế mạng diagnostics/polling được giữ để đánh giá ở A2/A3; không mặc định firmware đã đáp ứng hard realtime.

## Phụ thuộc và điều kiện bắt đầu

TASK-005 đã nghiệm thu 4/4: [biên bản](evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Bắt đầu sau khi người dùng giao triển khai TASK-006; chuyển phạm vi sang task.md trước khi sửa mã. Không bắt đầu tự động từ đề xuất này.
