# Bằng chứng TASK-005 P1/A1

## Kiểm tra đã chạy

- [Build sạch mới nhất](build-fresh.log): SUCCESS 9.06 giây, RAM 47388/327680 byte, flash 908071/1310720 byte. [Build đầu](build.log) và [build sau comment](build-final.log) giữ lịch sử.
- [Host checks](host-checks.log): actual SensorReader với GPIO/ADC/echo giả lập; không phải Wokwi live.
- [Artifact cuối](prepare-final.log): checksum nguồn/copy; [artifact đầu](prepare.log) giữ lịch sử.
- Formatter, sơ đồ/timer host/tài liệu kiểm tra tĩnh PASS; xem [kiểm tra convention](convention-checks.md). Không đánh dấu cảm biến live PASS.

## Live đang chờ

Theo [ma trận](../../../techs/testing.md) và [hướng dẫn Wokwi](../../../techs/simulation.md), người dùng chạy P1-01 đến P1-08, lưu serial-live.log, mqtt-live.log, broker-live.log và ảnh thao tác. File mới dùng tên của TASK-005; không lấy log P0 của TASK-002 để chứng minh đọc cảm biến P1.

Các ca LDR, biến trở, PIR, khoảng cách, timeout ECHO, PWM, MQTT hồi quy và broker offline đều chưa chạy trong lượt này. Các con số minh họa trong tài liệu không phải kết quả thực nghiệm. Chưa có bằng chứng điện áp hoặc đo dòng thật.

## Freshness và nguồn kết quả

[prepare-rejected.log](prepare-rejected.log) ghi script từ chối artifact cũ hơn source sau sửa comment; SCons đã compile nhưng không cần relink. Đã [clean](clean.log), build lại thật, rồi prepare-final.log PASS với checksum mới. Không sửa mtime hoặc bỏ guard. build-fresh.log dùng core dir tạm /tmp/iot-pio-check-de41spu8 với package cục bộ đã pin, không nâng phiên bản.

Snapshot invalid có distanceCm=0 nội bộ nhưng distanceValid=false; Serial in NA, không coi đó là đối tượng ở khoảng cách 0. Host checks không đo thời gian vật lý của pulseIn hoặc chất lượng ADC thực. Tất cả live P1 còn chờ người dùng. TASK-005 2/4 chỉ tính mạch tĩnh và tài liệu, không phải 50% chức năng toàn đồ án.
