# Kiểm thử host cho SensorReader

Chạy từ gốc firmware:

```bash
g++ -std=c++17 -Wall -Wextra -Werror -Itest/host -Isrc src/SensorReader.cpp test/host/SensorReaderChecks.cpp -o /tmp/task005-sensor-checks
/tmp/task005-sensor-checks
```

Arduino.h trong thư mục này giả lập các hàm SensorReader sử dụng. Test biên dịch cùng SensorReader.cpp thật để kiểm tra lịch lấy mẫu qua tràn uint32, tham số TRIG/timeout, xóa khoảng cách cũ và phục hồi với xung echo giả lập. Không mô phỏng điện áp, Serial, Wi-Fi hoặc Wokwi. Build PlatformIO đích dùng Arduino thật và không biên dịch thư mục test này.
