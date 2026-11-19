# TASK-022 — Dừng toàn bộ dịch vụ dự án

Hoàn thành 2026-11-18T19:58:51+07:00,3/3 mục. [Bằng chứng dừng và kiểm cổng](stop-all.json).

Đã dừng container smartlight-p0-mosquitto-1, backend uvicorn có PID/start ticks khớp sở hữu, các renderer/extension host/file watcher thuộc bốn cửa sổ node01/02/03/dashboard được code --status xác nhận. Đóng cửa sổ đơn thuần chưa nhả4000/5500; sau khi dừng đúng tiến trình liên quan,1883/8000/5500/4000/4001/4002 đều không còn listener. Không dừng VS Code firmware gốc hoặc ứng dụng khác. Không khởi động thêm thành phần, xóa DB, artifact hay kết quả cũ.

TASK-021 được hủy theo yêu cầu người dùng khi mới xác nhận node01; chưa đủ ba node, không ghi PASS toàn hệ thống. Không có vướng mắc còn lại. Chỉ kiểm trạng thái dừng, không chạy build/tests/chiến dịch mới. Các tệp startup/helper vẫn giữ làm hồ sơ nội bộ, không tự chạy lại.
