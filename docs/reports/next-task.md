# TASK-010 — Tích hợp một node MQTT–backend–dashboard

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 nhóm nghiệm thu dự kiến
- Cập nhật: 2026-11-16T14:18:00+07:00

## Mô tả và phạm vi

Đề xuất kiểm chứng xuyên suốt một node trước khi mở rộng ba node P6/A6: firmware A3 → broker local → backend A4/SQLite → dashboard A5/Live Server. Dùng code đã có, không đổi stack/ngưỡng/schema để làm test đạt. Đầu ra là runbook và bằng chứng live có cấu hình/hash/log/thời gian, sửa lỗi tích hợp có bằng chứng nếu phát hiện. Không tự thực hiện task này trong TASK-009.

## Tham chiếu SRS

SRS6/7/8/9/12, TC17–22/26, ma trận live A3 trong mqtt.md và runbook backend/README.md. Điều kiện chuẩn bị cho tích hợp ba node; không coi một node đạt là toàn hệ thống đạt.

## Tiêu chí hoàn thành và tiến độ

- [ ] Broker/Wokwi node_01 thật, backend một worker và dashboard Live Server kết nối; node02/03 chưa chạy giữ unknown, telemetry/target/applied/fault/clock hiển thị đúng.
- [ ] AUTO/MANUAL/ACK/reject/timeout/60s theo node, input sai/pending guard và mất API/broker/reconnect được kiểm theo ma trận, không replay lệnh cũ; firmware tiếp tục AUTO.
- [ ] Restart giữ history/alerts/experiments, gap không bị nối; phiên thực/CSV/stats/coverage khớp cùng mẫu và cấu hình; phân biệt thời gian node/wall clock.
- [ ] Đo latency cảm biến→dashboard và command→ACK ít nhất10 lượt, ghi median/max/điều kiện máy; lưu bằng chứng, kết quả chưa đạt và kế hoạch ba node tiếp theo.

## Vướng mắc và cách giải quyết

Chưa có kết quả tích hợp live A3–A5 tại máy kiểm tra TASK-009; fixture không thay thế được socket/Paho/ESP32/Wokwi. Cần máy có VS Code/Wokwi gateway, quyền tài khoản mô phỏng và broker local. Có thể dùng máy dev đã chạy firmware; giữ nguyên kết quả P2 người dùng xác nhận, chỉ bổ sung bằng chứng lớp tích hợp.

## Phụ thuộc và điều kiện bắt đầu

Chỉ bắt đầu khi được giao. Ba repo firmware/backend/dashboard đặt cạnh nhau; môi trường Python backend đã cài, VS Code Live Server và Wokwi hoạt động. Kiểm tra cổng/dịch vụ hiện có; không dừng dịch vụ người dùng hoặc ghi fixture vào DB live. Đọc README ba repo, techs/mqtt/backend/dashboard/testing và evidence TASK-007/008/009. Nếu yêu cầu sửa UI, tiếp tục dùng ui-ux-pro-max. Ba node/stability30phút và EX-series sẽ có tiêu chí riêng sau bước một node.
