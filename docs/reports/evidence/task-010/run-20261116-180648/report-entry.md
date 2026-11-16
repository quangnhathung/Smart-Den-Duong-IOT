## 2026-11-16T18:41:30+07:00 — TASK-010 — bổ sung bằng chứng tích hợp live một node

- Trạng thái: Đang thực hiện;1/4 nhóm nghiệm thu, nhóm2–4 còn PENDING.

### Đã thực hiện

Ghi riêng [xác nhận người vận hành](user-confirmation.md) về Python3.12/68 Pytest/Ruff/SQLite/build P3/A3/prepare/Dashboard MANUAL80/PWM80/tự AUTO60s; không chạy lại các bài này. Agent thu API8001/MQTT1883/SQLite read-only/hash build và mô phỏng; Dashboard5500 giữ cấu hình cổng8001 đã được người dùng chọn. Không sửa mã ứng dụng, MQTTv1, thuật toán, ngưỡng; không xóa DB/log hoặc commit/push/merge.

### Kiểm tra và kết quả

PASS: health OK, node_01 ONLINE/FRESH, node_02/03 UNKNOWN; singleton DB lock/quick_check/schema1, BIN/ELF khớp. SQLite tìm lại2 command MANUAL80 APPLIED/ACK và32 mẫu PWM80. PASS input sai422/node_02 offline409/command lạ404, pending guard409;3 reject wire đúng reason; cache lệnh AUTO sau deadline/ID trùng đổi nội dung không ghi đè cache gốc. Đo10/10 command→ACK từ server sent_at/ack_at có ACK MQTT: median686,217ms/max1002,001ms.

Hai phiên agent tạo đã đóng. Phiên1: CSV12 mẫu,0,0018346Wh, coverage92,2025129083%, valid_uptime2,284s; Phiên2: CSV423 mẫu DAY0W. API/history/CSV/stats/quality/clock khớp, phép tính điện năng độc lập PASS. Không phải EX-series hoặc nghiệm thu ba node. [Bộ log, CSV, audit, giới hạn](README.md).

### Vướng mắc

Chưa nhận phản hồi thao tác fault Wokwi. Capture420s không có OPEN_LOAD hoặc API outage, chưa test restart. GUI observation hết thời gian chờ cấp quyền, không có ảnh mới. PENDING timeout/ACK muộn/UI REJECTED-TIMEOUT, mất API/broker/reconnect/no-replay/AUTO offline, OPEN_LOAD/phục hồi, restart giữ dữ liệu/gap, latency cảm biến→Dashboard10 lượt.

SQLite ban đầu có20 OFFLINE alert đã đóng;187 cặp có21 gap nhận≥10s thực, max13,83255s. Cần kiểm tốc độ mô phỏng/kết nối, chưa kết luận nguyên nhân. Probe cache lần đầu dùng nhầm chuỗi deadline HTTP trên MQTT nên INVALID_COMMAND; đã sửa riêng script bằng chứng sang JSON integer, chạy lại PASS với tag mới, giữ cả log lỗi. Firmware/schema không sửa.

### Cách giải quyết

Giữ Backend/Wokwi/Dashboard đang chạy; không dừng cưỡng bức tiến trình người dùng. Đã đóng riêng phiên1/2 và kết thúc capture. Ca tiếp theo cần người vận hành phối hợp pause/resume Wokwi để test timeout, tạo fault/phục hồi và Ctrl+C/restart Backend cùng DB trong khi agent capture; không thực hiện trước khi capture mới được bật. Đo sensor→UI cần timestamp thao tác và render thật, không thay bằng HTTP RTT hoặc MQTT→API.

### Tài liệu và bước tiếp theo

Cập nhật task.md, techs/testing/backend và next-task.md; checklist task hoàn thành giữ nguyên vì TASK-010 chưa đủ4/4. TASK-011 chưa có đặc tả chính thức, ghi Chưa bắt đầu/0/0, không tự suy P6/P7. Nội dung report cũ được giữ nguyên byte làm phần đuôi; manifest/preservation được lưu trong thư mục lượt này.
