## 2026-11-16T19:25:44+07:00 — TASK-010 — restart giữ dữ liệu và phân tích ca TIMEOUT chưa đạt

- Trạng thái: Đang thực hiện;2/4 nhóm nghiệm thu, nhóm1/3 PASS theo phạm vi giao việc.

### Đã thực hiện

Người dùng xác nhận Backend18828 dừng,43632 chạy8001/workers1, không init_db/xóa SQLite, giữ Wokwi/Mosquitto. Agent ghi PID/start/listener, capture MQTT/API75s sau restart và SQLite read-only; đối chiếu snapshot ngay trước lượt này với snapshot cuối trước restart. Không chạy lại OPEN_LOAD/MANUAL60s/build/68 Pytest đã PASS.

### Kiểm tra và kết quả

PASS quick_check/schema1/cùng đường dẫn DB;760 telemetry cũ giữ nguyên,13 command/20 ACK còn nguyên từng trường,106 alert và3 phiên còn. OPEN_LOAD30/33 giữ đúng thời điểm đóng. CSV3 phiên tải lại sau restart giống từng byte/SHA256; metadata cấu hình/notes/start/end khớp. Backend run ID đổi26989c18…→44cc197e…, firmware boot3268eb79 giữ nguyên/AUTO NIGHT25. Ranh giới row765→766 có continuity mới; history/stats cửa sổ hai đầu mút có DISCONTINUITY và0 năng lượng/valid_uptime, không nội suy qua gap. [Log/snapshot/CSV/audit](README.md).

### Vướng mắc và cách giải quyết

Recorder trước đó kết thúc trước thao tác restart, nên không có log API outage/STALE ngay lúc khởi động; không tái tạo log quá khứ. Không có lệnh PENDING/phiên mở tại restart, không chốt no-replay/khôi phục các tình huống này. Nhóm2 còn timeout/ACK muộn, broker disconnect/reconnect/no-replay/AUTO offline và UI terminal; nhóm4 còn sensor→Dashboard10 lượt. Tốc độ mô phỏng/độ phủ thấp ở lượt trước vẫn là giới hạn, không đổi ngưỡng để ép PASS.

Người dùng chạy timeout-check.py nhưng INCOMPLETE. Đã đọc nguyên log/summary và SQLite/API: command7aa224a2… có APPLIED/ACK ACCEPTED sau1,0231297s, attempts1, không retry. observed_timeout_wall_s≈1,297 là lúc script thấy APPLIED, không phải timer timeout Backend. Không có mốc Pause/halt MCU nên chưa phân biệt thao tác muộn với transport tiếp tục xử lý. Giữ nguyên source/log của phép thử, không yêu cầu lặp lại cửa sổ2s.

Đã chuẩn bị ack-delay-proxy.py/ack-delay-check.py: proxy local1884 giữ nguyên ACK thật12s trong khi chuyển telemetry bình thường, driver tự gửi một AUTO sau telemetry mới, không cần Pause. Công cụ PASS kiểm offline framing/không chặn frame thường/byte preservation và diagnostics roundtrip thật qua broker; không giả ACK hoặc gọi đó là TIMEOUT live PASS. Proxy smoke20s đã dừng. Chưa chuyển Backend hiện tại sang proxy hoặc tự restart; runbook ghi rõ cách tạm route1884 rồi khôi phục1883/giữ DB một worker. Không mở phiên đo mới, không dừng Backend/Wokwi/broker.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing/backend và hồ sơ mới. Checklist task hoàn thành giữ nguyên vì TASK-010 chưa4/4. TASK-011 chờ đặc tả. Không commit/push/merge/xóa DB/log/sửa schema hoặc thuật toán; report cũ giữ nguyên byte làm phần đuôi.
