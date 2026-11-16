# TASK-009 — Dashboard giám sát và điều khiển P5/A5

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 nhóm nghiệm thu dự kiến
- Cập nhật: 2026-11-16T13:17:56+07:00

## Mô tả và phạm vi

Đề xuất dashboard React/TypeScript/Vite theo SRS8, dùng API TASK-008. Tổng quan/tuyến3 node/chi tiết/lịch sử/cảnh báo/phiên/CSV, điều khiển AUTO/MANUAL có xác nhận. Bắt buộc đọc và vận dụng skill ui-ux-pro-max khi lập kế hoạch/thiết kế/triển khai UI theo yêu cầu người dùng. Không tạo dashboard, chọn theme hay chạy task này tự động trong TASK-008.

## Tham chiếu SRS

SRS7.3/8/9/10P5/11A5/12. API types/clock/uint64 theo backend.md và OpenAPI TASK-008. Giữ MQTTv1, dashboard chỉ gọi HTTP, không publish MQTT trực tiếp.

## Tiêu chí hoàn thành và tiến độ

- [ ] Chốt vị trí/repo, thiết kế theo ui-ux-pro-max, responsive/a11y và trạng thái loading/empty/stale/error có lý do rõ.
- [ ] Tổng quan/3 node/chi tiết hiển thị target/applied/fault/offline/mô phỏng đúng; không bịa node chưa chạy.
- [ ] AUTO/MANUAL nút Áp dụng, pending/ACK/reject/timeout và khóa thao tác đúng API; polling1s, stats/alerts5s.
- [ ] Lịch sử/gap/coverage/experiment/export, API errors/CORS/precision64 và kiểm thử UI/build/tài liệu đạt.

## Vướng mắc và cách giải quyết

Live A3/A4 chưa chạy tại máy này. Có thể làm UI với fixture có nhãn và API thật, nhưng không coi fixture là hệ thống live hoặc lấp gap bằng dữ liệu giả. Trước nghiệm thu tích hợp cần kết quả runbook máy dev, kiểm độ trễ thật và ba node ở giai đoạn tích hợp.

## Phụ thuộc và điều kiện bắt đầu

Chỉ bắt đầu khi người dùng giao TASK-009 và chốt vị trí/repo/dashboard preferences. Backend repo DoAn/backend có code/test/OpenAPI, README hướng dẫn. Không tự chỉnh firmware/API/schema hoặc deploy cloud để làm UI đạt. Không tự commit/push.
