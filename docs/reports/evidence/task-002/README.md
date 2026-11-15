# Bằng chứng TASK-002

baseline-build.log và smoke-build.log: build đã thử trong phiên agent, thất bại do quyền cache PlatformIO. Không phải lỗi biên dịch đã xác nhận.

Khi chạy ngoài phiên, thêm build.log (build mới), broker.log, serial.log, mqtt.log, ảnh LED. Mỗi ca ghi thời gian, phiên bản, checksum BIN/ELF, kỳ vọng, thực tế và PASS/FAIL. Chưa có các bằng chứng live này.

| Ca | Trạng thái hiện tại |
| --- | --- |
| Build mẫu và firmware mới | Bị chặn quyền cache |
| Wokwi, Serial và năm mức PWM | Chưa chạy |
| Broker publish/subscribe qua host | Chưa chạy |
| Ba ping/pong và mất/khôi phục broker | Chưa chạy |
