# TASK-010 — Trạng thái khi bàn giao để mở PR

Người dùng đã cho phép add, commit và push nhánh `tuan` ở các repository có thay đổi. Người dùng sẽ tự tạo PR vào `main`; không merge hoặc force push.

TASK-010 đang thực hiện, đạt 2/4 nhóm nghiệm thu. Tích hợp một node và lưu trữ/lịch sử/phiên đo/CSV/gap/restart đã PASS theo bằng chứng trước. TIMEOUT/ACK muộn qua proxy và khôi phục MQTT1883 đã PASS. Backend dùng API8001, Dashboard5500; không đổi thuật toán hoặc MQTT schema.

Còn PENDING: UI trạng thái lệnh cuối, broker outage/reconnect/no-replay/AUTO offline và latency cảm biến đến Dashboard. Đã thao tác 5 lượt cảm biến nhưng chưa có đủ mẫu đạt điều kiện nghiệm thu; không khẳng định đã hoàn thành 10 lượt. Xem `run-20261116-195307/final-status.json`, `trial-05-summary.json` và `latency-events-cutoff.jsonl`. Xác nhận người dùng được phân biệt với dữ liệu máy thu trực tiếp. TASK-011 vẫn chờ đặc tả chính thức.

Dashboard chỉ đổi địa chỉ API sang8001 và bổ sung bộ ghi thử nghiệm live trong `tests/`. Bộ ghi còn giới hạn về timestamp/visibility và không phải tính năng production đã nghiệm thu. Backend không có thay đổi mã nguồn nên không tạo commit riêng.

Giữ SQLite và toàn bộ log tại máy. Hai stream đang ghi tiếp được loại khỏi Git bằng đường dẫn cụ thể trong `.gitignore`; các bản chụp bằng chứng đã chốt vẫn được commit. Không đưa `.env`, SQLite, môi trường Python hoặc firmware build vào commit. Kiểm tra cú pháp JavaScript, Python AST và `git diff --check`; không chạy lại kiểm thử live đã PASS.

Một số ghi chú trong đợt đo trước bị mất dấu khi truyền qua PowerShell. Dùng bản tổng hợp này và JSON gốc để đối chiếu; không sửa dữ liệu bằng chứng gốc hoặc xóa nhật ký cũ.
