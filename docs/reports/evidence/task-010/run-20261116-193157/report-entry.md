## 2026-11-16T19:46:02+07:00 — TASK-010 — TIMEOUT/ACK muộn thật qua proxy và khôi phục: PASS

- Trạng thái: Đang thực hiện;2/4 nhóm nghiệm thu toàn TASK-010. Lượt kiểm proxy được giao đã PASS, không chạy lượt thứ hai.

### Đã thực hiện

Đọc lại harness/config và thông báo rollback trước thay đổi. Người dùng dừng graceful Backend43632; agent khởi động tạm32248/API8001/workers1/cùng SQLite/MQTT1884 qua proxy44580. Wokwi/Mosquitto giữ1883, không Pause/init_db/xóa dữ liệu. Preflight hai telemetry932/933 qua proxy/healthOK trước một POST AUTO.

### Kiểm tra và kết quả

PASS command0d8f20f5-4700-4be4-b5cc-37b555396adc: gửi19:37:15.226902+07, retry duy nhất19:37:17.268317; GET đầu TIMEOUT19:37:25.308628, script quan sát10,088672s. ACK firmware thật tới proxy sớm, được thả19:37:27.254744/27.255748 ở mốc12s từ lệnh đầu, hash raw bytes lúc giữ/thả khớp. Hai ACK vào SQLite LATE_OR_DUPLICATE; API/DB cuối TIMEOUT/ACK_TIMEOUT/attempts2. Một POST/một ID mới/hai MQTT publish cùng payload; không có retry/replay khác trong capture và sau khôi phục. [Log, audit, thời gian và giới hạn](README.md).

Backend đã khôi phục14144→MQTT1883/API8001/workers1, health/database/broker/queue true, dropped0. Chỉ sau healthOK/proxy0 client mới dừng proxy; recorder dừng sau quan sát thêm. Dashboard HTTP/config/CORS PASS và người dùng xác nhận ONLINE/AUTO NIGHT25/LDR3917/boot3268eb79/seq963→969/dữ liệu mới19:44:21, không gửi thêm lệnh. Bảo toàn907 telemetry/14 command/21 ACK/245 alert/3 phiên cũ; chỉ thêm1 command và2 ACK đúng bài test, không mất bản ghi cũ.

### Vướng mắc và cách giải quyết

Ctrl+C qua PTY/pipeline không đến Uvicorn; control event trong riêng console Backend tạm đã cho application shutdown hoàn tất, không force-kill Backend hoặc dừng broker/Wokwi. Proxy chỉ bị dừng khi không còn client/frame chờ. Log status proxy là snapshot cuối trước dừng, trạng thái hiện tại xác nhận qua network và proxy-stop-action. Backend phục hồi vẫn chạy, nên manifest dùng bản sao log cố định và loại log đang tăng.

Không đổi thuật toán/schema hoặc dùng ACK fixture. Trễ12s là fault injection tính từ lệnh đầu, không gọi là mất ACK tự nhiên. Không dựng timeout_at vì DB không có cột này; ghi mốc quan sát thật. Nhóm2 còn broker outage/reconnect/no-replay lệnh chờ/AUTO offline/UI terminal, nhóm4 còn sensor→Dashboard10 lượt; chưa4/4.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing/backend và evidence; checklist task hoàn thành giữ nguyên. Giữ các hồ sơ PASS/INCOMPLETE cũ nguyên byte. TASK-011 tiếp tục chờ đặc tả. Không commit/push/merge/xóa DB/log; report cũ giữ nguyên làm phần đuôi.
