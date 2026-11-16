# TASK-006 — Thuật toán chiếu sáng AUTO/MANUAL P2/A2

- Trạng thái: Đang thực hiện
- Tiến độ: 4/5 mục nghiệm thu
- Cập nhật: 2026-11-16T11:21:17+07:00

## Mô tả và phạm vi

Logic thuần state machine AUTO/MANUAL, lọc/hysteresis môi trường, phân loại PIR/distance, hold/dimming, fault tải; tích hợp ESP32, Serial điều khiển cục bộ và giữ MQTT diagnostics. Không backend/dashboard, không MQTT command/ACK A3, không Docker hoặc commit/push. TASK-005 đã hoàn thành giữ nguyên biên bản/evidence/checklist.

## Tham chiếu SRS

SRS 5.1–5.8, 10 P2, 11 A2, 12: môi trường UNKNOWN/DAY/TWILIGHT/NIGHT; AUTO 0/25/50/70/100; hold5s, dim2%/20ms, MANUAL60s/offline fallback; OPEN_LOAD sau PWM ổn định1s và xác nhận2s, phục hồi3s.

## Tiêu chí hoàn thành và checklist

- [x] State machine/AUTO theo filter5 mẫu, hysteresis và xác nhận1s; chuyển động/timeout/hold/ưu tiên đúng, test clock.
- [x] MANUAL/AUTO, giá trị hợp lệ, hết hạn60s, offline/reconnect và hủy hold cũ; test clock/tràn.
- [x] Dimming và OPEN_LOAD/phục hồi độc lập mode; không tự tắt PWM; test biên/invalid.
- [x] Tích hợp chỉ một chủ PWM, lấy mẫu/loop không chặn bởi pulseIn hoặc mạng, diagnostics giữ topic/payload; build và kiểm tra tích hợp tự động.
- [ ] Tài liệu/bằng chứng gọn và kiểm tra Wokwi thực tế tối thiểu; không tuyên bố live PASS khi chưa chạy.

## Quyết định phạm vi và giới hạn

A2 cung cấp API controller và Serial AUTO / MANUAL <0..100> dùng thử cục bộ. MQTT v1 command/ACK/telemetry thuộc A3, chưa subscribe command hoặc thêm topic mới. Không đổi pin map/dependency/schema để hiện thực giao diện cục bộ này. Mạng PubSubClient có các đoạn chờ hữu hạn nên dự kiến chuyển sang task riêng; siêu âm dự kiến bắt cạnh để tránh pulseIn chặn vòng điều khiển. Mọi API phần cứng phải kiểm tra build, không coi host test thay Wokwi.

## Phụ thuộc và điều kiện bắt đầu

Người dùng đã giao TASK-006; TASK-005 nghiệm thu4/4. Không thử lại nghiệm thu TASK-005 hoặc thay đổi evidence cũ. Sau triển khai tự kiểm tra, đưa 3–5 bước Wokwi; chưa tự thực hiện A3.

## Kết quả lượt triển khai

PASS bốn suite host (controller, sensors, app, mqtt), formatter clang-format17.0.3; build esp32dev SUCCESS exit0, RAM48028/327680, flash912763/1310720; prepare BIN/ELF freshness/hash đạt. [Log kiểm tra](evidence/task-006/validation.log). Các assertion phát triển ban đầu đã được xử lý, gồm sự kiện disconnect/reconnect quá nhanh che fallback, deadline ECHO và ổn định PWM giữa kỳ fault; các test cuối PASS.

Không có lỗi chặn host/build còn biết. Chưa chạy Wokwi P2 hoặc mạng/RTOS thực, vì vậy chưa tuyên bố TASK-006 PASS. Cần 5 bước tối thiểu trong [simulation](../techs/simulation.md). Giữ trạng thái Đang thực hiện 4/5, không thêm task này vào checklist hoàn thành. MQTT command/ACK thuộc A3, không được nhận là đã triển khai ở A2.

## Rà soát nghiệm thu sau live

[Báo cáo hiện tại](evidence/task-006/acceptance-review.md) thay trạng thái chờ chạy ở lượt triển khai: người dùng đã thực hiện live, đã có file RFC2217 chứng minh MANUAL80 và timeout60s PASS; các ca AUTO/PIR/fault/timeout/reconnect khác được người dùng xác nhận, một số có trích đoạn trong hội thoại nhưng chưa có file lưu đủ để đối chiếu độc lập. Đã tìm toàn repo, không thấy thêm log CONTROL tương ứng. Giữ toàn task PENDING hồ sơ, trạng thái Đang thực hiện4/5, không bắt kiểm thử lại toàn bộ. Build kiểm tra lại SUCCESS3.28s, bốn suite host và7 test RFC PASS. Chưa checkout/commit/push/merge; chỉ đề xuất commit riêng trên tuan, giữ mọi thay đổi.

## Bổ sung kiểm thử MANUAL qua RFC2217

Người dùng báo AUTO/PIR/distance/MQTT đã hoạt động P2 nhưng Wokwi Terminal không nhập được lệnh. Chỉ thêm rfc2217ServerPort=4000 vào cấu hình chính, tạo scripts/wokwi-serial.py dùng pyserial3.5 đã có sẵn, không sửa thuật toán. 7 test Python offline PASS, gồm exact LF TX, parser xác nhận/RX, MANUAL applied, AUTO, timeout gần60s theo uptime, không false PASS khi offline/reset/lệnh khác. Chưa có listener4000 trước restart; chờ người dùng Stop/Start đúng một lần rồi xác minh PROBE/lệnh thực. Chưa nâng task4/5 hoặc coi MANUAL live PASS. Không build lại/Docker/TASK-005/commit/push trong lượt chuẩn bị này.
