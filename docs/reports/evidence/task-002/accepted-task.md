# TASK-002 — Kiểm chứng môi trường P0

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu môi trường
- Cập nhật: 2026-11-15T19:12:53+07:00

## Mô tả và phạm vi

Hoàn tất smoke test P0: build/pin, Wokwi/Serial/năm PWM, MQTT ping/pong và phục hồi broker, hồ sơ convention. Chưa nghiệm thu toàn đồ án. Xem [biên bản](acceptance.md).

## Tham chiếu SRS

[SRS](../../../srs.md) mục 4.3–4.5, 10–12.

## Tiêu chí hoàn thành và tiến độ

- [x] Build và khóa đúng phiên bản đã kiểm chứng.
- [x] License, Serial, đủ năm mức PWM theo ảnh/hội thoại.
- [x] Host pub/sub, ba pong và pong p0-004 sau restart broker; xác nhận người dùng không reset ESP32.
- [x] Mã/cấu hình/tài liệu và bằng chứng được đối chiếu.

## Vướng mắc và cách giải quyết

Lỗi tải registry ban đầu đã qua ở lượt build lại với package cục bộ. Timeout phiên dài còn được ghi nhận làm giới hạn theo dõi, không tuyên bố đã tìm ra nguyên nhân; xem acceptance.md. Không có thiếu sót trong các ca smoke tối thiểu đã chốt.

## Phụ thuộc và điều kiện bắt đầu

Đầu vào cho TASK-004/A0. Không tự triển khai cảm biến hoặc nhiều node.
