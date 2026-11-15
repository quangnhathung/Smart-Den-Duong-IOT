# Bằng chứng TASK-002

## Hiện trạng mới nhất

Xem [kết quả live và nguồn bằng chứng](live-progress.md), [ảnh Wokwi gốc](wokwi-first-run.png).

- build.log hiện tại: SUCCESS 7.31 giây, người dùng đã chạy lại và thay nội dung log trước đó.
- build-min-fix.log: SUCCESS 10.19 giây của lượt sửa min trước đó.
- baseline-build.log/smoke-build.log: lịch sử lỗi quyền cache, không phản ánh build hiện tại.
- broker.log: broker chạy, nhận client ESP32 ba lần rồi ngắt do exceeded timeout.
- Host pub/sub và thao tác restart lấy từ đầu ra terminal người dùng cung cấp; chưa có mqtt.log/serial.log thô đầy đủ.
- Wokwi đã chạy, PWM mới có bằng chứng một phần; ba pong và phục hồi sau restart chưa đạt.

Không thay đổi các log đầu vào trong lượt cập nhật này. Lịch sử báo cáo trước giữ nguyên; các câu ghi build.log là lỗi min mô tả thời điểm cũ, log đó đã được người dùng thay bằng build thành công.
