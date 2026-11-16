# TASK-006 — Hoàn thiện hồ sơ nghiệm thu P2/A2

- Trạng thái: Chưa bắt đầu
- Tiến độ: 4/5 mục nghiệm thu TASK-006
- Cập nhật: 2026-11-16T11:21:17+07:00

## Mô tả và phạm vi

Code AUTO/MANUAL/hold/dimming/fault và vòng điều khiển/ISR/network task đã tích hợp; bốn suite host và build PASS. Chỉ còn đối chiếu live P2 với 5 bước trong simulation.md; không kiểm thử lại hoặc thay kết quả TASK-005.

## Tham chiếu SRS

SRS 5.1–5.8, P2/A2 và TC-01–16/27/28. MQTT command/ACK và backend/dashboard thuộc các gói sau, chưa triển khai.

## Tiêu chí và tiến độ

- [x] State machine, AUTO/MANUAL, dimming/fault, invalid/wrap/offline test đạt.
- [x] Firmware build, host sensor/app/MQTT regression và artifact/hash đạt; [log](evidence/task-006/validation.log).
- [ ] Wokwi P2: ISR ECHO/task core0, LDR/motion/hold, MANUAL/timeout, fault/recovery và diagnostics có Serial/ảnh.
- [ ] Đối chiếu live rồi quyết định chốt TASK-006; chưa tự bắt đầu A3.

## Vướng mắc và cách giải quyết

Chưa chạy live bản P2 nên không lấy bằng chứng P1 hoặc host stub thay cho kết quả này. Kiểm tra timing theo clock node; không đụng Docker/container nếu chưa được giao. Nếu lỗi, giữ Serial/điều kiện cụ thể rồi sửa đúng phạm vi A2.

## Phụ thuộc và điều kiện bắt đầu

Artifact mới đã copy tới simulations/node_01/build. Người vận hành mở đúng cấu hình Wokwi chính, giữ một phiên; xem [5 bước](../techs/simulation.md). Không mua/cài/nâng toolchain, không commit/push. Chưa triển khai TASK-007/A3.

## Rà soát sau live

MANUAL80 và timeout60s có file gốc PASS, bốn suite host +7 test RFC và build kiểm tra lại PASS. Người dùng đã chạy các bài live khác; chưa lưu đủ log/ảnh nên không yêu cầu làm lại toàn bộ. Chỉ bổ sung nguồn đã có hoặc ghi nguồn xác nhận theo [acceptance-review](evidence/task-006/acceptance-review.md). TASK-006 giữ4/5; kế hoạch Git là chuyển an toàn sang nhánh tuan cùng base rồi commit chọn lọc, chưa thực hiện khi chưa được đồng ý. Không tự push/merge hoặc bắt đầu A3.
