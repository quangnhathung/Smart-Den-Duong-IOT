# TASK-011 — Chờ đặc tả chính thức

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/0 tiêu chí; chưa có đặc tả nghiệm thu
- Cập nhật: 2026-11-17T09:45:17+07:00

## Đối chiếu sau pull — 2026-11-17T09:45:17+07:00

TASK-011 tiếp tục Chưa bắt đầu, 0/0 tiêu chí; chờ đặc tả chính thức. TASK-010 vẫn Đang thực hiện, 2/4 nhóm theo final-status.json: luồng một node và dữ liệu/restart/CSV/gap PASS; còn UI trạng thái lệnh cuối, broker outage/reconnect/no-replay/AUTO offline và cảm biến → dashboard đủ 10 mẫu. Năm lượt cảm biến đã thử đều INCOMPLETE, chưa có mẫu đủ điều kiện; không hiểu là chỉ cần thêm năm lượt. Command → ACK đã có 10 lượt PASS phép đo, giữ kết quả cũ.

Bước cần chuẩn bị khi được giao tiếp: phương pháp đo cảm biến/render ổn định, xác định baseline/boot/seq/timestamp/visibility và sai số; phương án cô lập kết nối MQTT của node để kiểm offline mà không dừng broker dùng chung; đối chiếu cấu hình/source của repo dashboard trước khi dùng bộ ghi trên máy live. Đây là phụ thuộc cho TASK-010, không tự ánh xạ thành TASK-011 hoặc chạy thêm live. Ba node/stability30phút và EX-series vẫn chưa nghiệm thu.

[Kết quả rà soát và khác biệt môi trường](evidence/task-010/review-20261117-094517/README.md). Các ghi chú cũ bên dưới giữ nguyên để truy vết.

## Mô tả và phạm vi

Chưa được trưởng nhóm cung cấp mục tiêu, phạm vi, đầu ra và tiêu chí nghiệm thu TASK-011. Không tự ánh xạ TASK-011 sang P6/P7 hoặc triển khai ba node/EX-series. Người dùng đã yêu cầu TASK-011 tiếp tục chờ đặc tả chính thức.

## Tham chiếu SRS

Chưa xác định cho TASK-011; không dùng kế hoạch tổng thể thay giao việc cụ thể.

## Tiêu chí hoàn thành và tiến độ

Chưa xác định. Không đánh dấu công việc chưa được đặc tả là hoàn thành.

## Vướng mắc và cách giải quyết

Cần đặc tả chính thức: mục tiêu, phụ thuộc, phạm vi, đầu ra và tiêu chí nghiệm thu. Trong lúc chờ, tiếp tục TASK-010 trong task.md; hiện2/4 nhóm, OPEN_LOAD/phục hồi, restart giữ dữ liệu/gap/CSV, TIMEOUT/ACK muộn qua proxy và khôi phục Dashboard đã PASS. Còn broker outage/reconnect/no-replay cho lệnh chờ/AUTO offline/UI terminal và latency cảm biến→Dashboard. Xem evidence/task-010/run-20261116-193157/README.md.

## Phụ thuộc và điều kiện bắt đầu

Chỉ bắt đầu các hạng mục TASK-011 có yêu cầu rõ ràng sau khi TASK-010 đạt hoặc có báo cáo các mục còn bị chặn. Bản giao việc TASK-010 trước chuyển được giữ tại evidence/task-010/run-20261116-173103/task-010-accepted.md. Không commit/push/merge khi chưa được người dùng đồng ý.
