# Công cụ QA đã dùng trong TASK-011

Đây là source as-run gắn với môi trường, đường dẫn và cổng của lượt Linux này; không chạy setup/cleanup hoặc producer mù quáng trên máy khác. Khi tái lập, tạo QA root mới, xác minh cổng/quyền sở hữu và đặt run-state mới; không trỏ vào dữ liệu cũ. Không có token hoặc credentials trong bộ source này.

Lệnh dùng hằng ngày là PlatformIO build và scripts/prepare-simulation.py trong repo. Công cụ ở đây giải thích phương pháp kiểm live, không thêm chức năng sản phẩm.

Raw JSONL/log đóng được nén lossless; xem ../archives.json. Trước khi đọc bằng script as-run cần giải nén bản sao vào QA root mới hoặc điều chỉnh reader; không ghi đè bằng chứng gốc. latency-final-audit.json kiểm nguyên dữ liệu trial đã thu, sửa riêng parser nhãn100k; wire-audit.json kiểm toàn bộ1800s bằng MQTT và SQLite. HTTP probe bị dừng sớm được ghi INCOMPLETE riêng, không giả làm900 mẫu API.
