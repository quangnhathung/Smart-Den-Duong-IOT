## 2026-11-16T19:00:00+07:00 — TASK-010 — đối chiếu OPEN_LOAD và phục hồi đã chạy

- Trạng thái: Đang thực hiện;1/4 nhóm nghiệm thu. OPEN_LOAD/phục hồi được đánh dấu PASS trong nhóm3, không chạy lại.

### Đã thực hiện

Đối chiếu xác nhận người vận hành về NIGHT/PIR0/AUTO25, current_adc0 gây OPEN_LOAD và tải4095 phục hồi; Serial báo OK tại uptime1340431ms/duty64/mqtt1, người dùng đã chụp ảnh. Chưa thấy file ảnh trong repo. Xuất SQLite read-only và API history/alerts/stats, giữ rõ nguồn bằng chứng. [Hồ sơ lượt này](README.md).

### Kiểm tra và kết quả

PASS:16 mẫu quanh hai đợt đều AUTO/NIGHT/NONE/target25/applied25, cùng boot3268eb79. Hai OPEN_LOAD alert30/33 có thời gian mở/đóng; đợt cuối bắt đầu seq683/uptime1323338ms/current_adc0, hết lỗi seq692/uptime1340238ms/current_adc4095, đóng alert33 tại11:46:15.004905Z. Mốc telemetry sớm hơn Serial193ms; giữ cả hai, không đổi mốc hoặc suy exact timer từ mẫu thưa. Stats cùng cửa sổ loại FAULT_OR_RECOVERY/LOAD_CALIBRATION/STATE_CHANGE và DISCONTINUITY đúng dữ liệu.

Capture cũ kết thúc trước thao tác fault, vì vậy không có raw MQTT quá khứ; payload telemetry quá khứ lấy từ SQLite/API thật. Capture Serial mới sau phục hồi chỉ đọc, không gửi lệnh:48 dòng, gồm19 CONTROL AUTO25/duty64/faultOK/mqtt1. Clock node/wall trung vị≈0,1603; telemetry thực quan sát trung vị12,70s/max15,62s, có thể quá ngưỡng freshness10s dù mqtt1. Không sửa ngưỡng hoặc suy thành latency sensor→Dashboard.

### Vướng mắc và cách giải quyết

Đã lưu baseline, mở phiên3/capture600s và hướng dẫn người dùng Ctrl+C Backend/chờ5s/khởi động lại8001/workers1; không dừng cưỡng bức tiến trình người dùng. Restart chưa được chốt nếu không có bằng chứng thao tác/API outage/run mới. Timeout/ACK muộn, mất broker/reconnect/no-replay/AUTO offline, UI fault/terminal states và latency cảm biến→render vẫn cần phối hợp. Không chạy lại OPEN_LOAD/MANUAL60s/build/68 Pytest đã đủ xác nhận.

Cuối lượt: capture600s kết thúc,0 API outage/run ID không đổi/chưa có xác nhận restart, nên restart PENDING. Đã đóng riêng phiên3 và dừng recorders. CSV phiên3 có50 mẫu NIGHT6W, API/stats khớp;48 boundary gap không nối năng lượng, tổng0,0033416667Wh. Coverage chỉ1,534987%/valid_uptime2,005s; saving75% chỉ trên tập hợp hợp lệ nhỏ, không đại diện toàn khoảng. Bản ghi cũ còn đủ trong khoảng quan sát; không gọi là đã bảo toàn qua restart.

Audit lần đầu gặp lệch precision ở mép truy vấn ISO; đã sửa riêng script kiểm chứng dùng mép có đệm rồi chạy lại trên dữ liệu cũ PASS. Mở Serial lần đầu dùng write_timeout không được RFC2217 hỗ trợ; đã bỏ tùy chọn, giữ log lỗi và capture mới. Không sửa firmware/schema/thuật toán, không ghi log giả.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing và evidence. Checklist task hoàn thành giữ nguyên vì TASK-010 chưa4/4. TASK-011 vẫn Chưa bắt đầu, chờ đặc tả chính thức. Không commit/push/merge, không xóa SQLite/log; report cũ giữ nguyên byte làm phần đuôi.
