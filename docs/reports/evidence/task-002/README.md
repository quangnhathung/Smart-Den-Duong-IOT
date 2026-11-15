# Bằng chứng TASK-002

## Hiện trạng đã chốt

TASK-002 đạt 4/4 ca môi trường, xem [nghiệm thu](acceptance.md). Build sau pin: [log](build-pinned-retry.log), [checksum](prepare-pinned.log). Đủ pong p0-001 đến p0-004, PWM theo Serial hội thoại; người dùng xác nhận không reset ESP32 khi phục hồi broker. Giữ hạn chế timeout phiên dài và nguồn bằng chứng trong biên bản. Các mục bên dưới là lịch sử, không phải trạng thái hiện tại.

## Lịch sử bằng chứng trước khi chốt

Xem [kết quả live và nguồn bằng chứng](live-progress.md), [ảnh Wokwi gốc](wokwi-first-run.png).

- build.log hiện tại: SUCCESS 7.31 giây, người dùng đã chạy lại và thay nội dung log trước đó.
- build-min-fix.log: SUCCESS 10.19 giây của lượt sửa min trước đó.
- baseline-build.log/smoke-build.log: lịch sử lỗi quyền cache, không phản ánh build hiện tại.
- broker.log: broker chạy, nhận client ESP32 ba lần rồi ngắt do exceeded timeout.
- Host pub/sub và thao tác restart lấy từ đầu ra terminal người dùng cung cấp; chưa có mqtt.log/serial.log thô đầy đủ.
- Wokwi đã chạy, PWM mới có bằng chứng một phần; ba pong và phục hồi sau restart chưa đạt.

Không thay đổi các log đầu vào trong lượt cập nhật này. Lịch sử báo cáo trước giữ nguyên; các câu ghi build.log là lỗi min mô tả thời điểm cũ, log đó đã được người dùng thay bằng build thành công.

## Bản firmware xử lý timeout

- build-heartbeat.log: SUCCESS 4.89 giây, sau formatter; giữ build.log/build-min-fix.log làm lịch sử bản trước.
- prepare-heartbeat.log: copy BIN/ELF mới và SHA-256, khớp source artifact.
- Firmware mới nghỉ 10 ms, heartbeat không retained 2 giây, keepalive 15 giây, log kết nối/lỗi.
- Chưa có serial-heartbeat-live.log, mqtt-heartbeat-live.log hoặc broker-heartbeat-live.log; không suy diễn ảnh/live-progress.md của bản trước thành kết quả bản mới.
- Wokwi/Docker do người dùng chạy; chờ đủ năm PWM, ba pong, ổn định 3 phút và pong sau restart.
