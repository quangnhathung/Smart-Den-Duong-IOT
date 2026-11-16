# Firmware P2/A2 — điều khiển AUTO/MANUAL

## Phạm vi và tham chiếu

SRS 5.1–5.8, P2/A2, TC-01–16/27/28. TASK-005 đã nghiệm thu và giữ nguyên evidence; TASK-006 chuyển runtime từ PWM diagnostics sang điều khiển. Không triển khai MQTT command/ACK/telemetry A3 hoặc backend/dashboard.

## Module và luồng thực tế

- main.cpp chỉ gọi setupFirmware()/loopFirmware(). FirmwareApp lấy snapshot, nhận lệnh Serial hữu hạn, chạy LightingController và là chủ duy nhất ghi LED GPIO26 (LEDC 5kHz/8bit); không còn vòng PWM diagnostics. EnvironmentSmokeTest được thay bằng FirmwareApp/Connectivity.
- SensorReader giữ pin map, ADC12bit/PIR20ms/analog100ms/siêu âm200ms. analogSequence tăng mỗi mẫu analog để filter không đếm lại cùng mẫu theo số vòng loop. ECHO GPIO19 INPUT_PULLDOWN được bắt cạnh CHANGE; trigger LOW2us/HIGH10us; timeout30ms theo micros unsigned, bỏ cạnh muộn, xóa distance/invalid khi timeout. Không gọi pulseIn; chỉ chờ microsecond để phát TRIG. ISR chỉ ghi dữ liệu, critical section ngắn ở cùng core app.
- ControlConfig.h gom ngưỡng, mức sáng và timer SRS bằng hằng có tên; không đổi giá trị đã chốt. LightingController thuần C++, không Arduino/mạng. ControlInput/ControlState tách mode, environment, motion, target/applied/fault.
- DimmingController tăng/giảm tối đa2 điểm mỗi20ms, dừng đúng mức lẻ, không catch-up nhảy nhiều bước khi loop bị chậm. FaultDetector đánh giá100ms nhưng quan sát mọi thay đổi applied để không bỏ qua dao động giữa hai kỳ kiểm tra.
- Connectivity sở hữu duy nhất WiFiClient/PubSubClient trong FreeRTOS task core0, stack6144B, priority1, yield10ms. App/core1 chỉ đọc atomic connected/loss-count; không gọi connect/publish. Giữ hostname/clientID/topics diagnostics, ping/pong tối đa64byte và heartbeat2s uptime32bit; không đổi hợp đồng nghiệp vụ. Buffer2048, socket/TCP timeout1s mỗi bước, backoff1/2/4/8/10s; subscribe lại sau reconnect. Loss-count buộc MANUAL về AUTO cả khi disconnect/reconnect xảy ra giữa hai lần đọc status.
- Loop foreground yield1ms, không chờ echo hoặc mạng; log CONTROL/SENSORS1s và PIR cạnh. Không tuyên bố hard realtime từ thiết kế task/host test; Serial/hardware/RTOS cần đo live.

## AUTO và điều kiện đầu vào

LDR trung bình trượt5 mẫu mới, xác nhận ứng viên1s kể cả khởi tạo; trong khoảng chưa đủ dữ liệu UNKNOWN/target50%. Khởi tạo <1200 DAY, 1200–2600 TWILIGHT, >2600 NIGHT. Hysteresis giữ nguyên SRS: DAY ≥1300 sang TWILIGHT hoặc ≥2700 NIGHT; TWILIGHT ≤1100 DAY/≥2700 NIGHT; NIGHT ≤2500 TWILIGHT hoặc ≤1100 DAY. Cho nhảy trực tiếp, ứng viên bị ngắt phải xác nhận lại từ đầu.

DAY AUTO0% bất kể chuyển động, TWILIGHT nền50%, NIGHT nền25%. Chỉ PIR HIGH mới phân loại: distanceValid và khoảng cách dương hữu hạn <100cm VEHICLE/100%, ≥100cm PEDESTRIAN/70%; timeout/NaN/giá trị không hợp lệ UNKNOWN/100%. PIR LOW là NONE; khoảng cách gần đơn độc không tăng sáng. Chấp nhận khoảng cách dương >400 vì mô phỏng có sai số, không cắt giá trị valid thành lỗi chỉ vì405cm.

Hold5s từ lần cuối PIR HIGH, giữ mức cao nhất còn hiệu lực, sự kiện mới làm mới timer. Sang DAY hủy hold. LDR raw ngoài0–4095: xóa filter, về UNKNOWN50%; đây là xử lý bảo vệ nội bộ cho input không hợp lệ, không phải phát hiện đứt LDR trên phần cứng. Fault ADC invalid đặt lại timer xác nhận/phục hồi, không xóa lỗi đã có.

## MANUAL và giao diện thử cục bộ

API requestManual(int, nowMs) nhận0–100, từ chối ngoài range; requestAuto() xóa hold và loop đánh giá ngay cảm biến hiện tại. Boot AUTO, MANUAL ưu tiên cả DAY, timeout60s; lệnh MANUAL mới refresh thời hạn. MQTT được xác định ngắt thì AUTO; reconnect không phục hồi MANUAL cũ. Filter môi trường vẫn cập nhật trong MANUAL. OPEN_LOAD không bị xóa vì đổi mode.

Trong Wokwi Serial gửi dòng `MANUAL 80` hoặc `AUTO` kết thúc newline. Đây là giao diện thử cục bộ A2, không phải MQTT command v1. App chỉ nhận MANUAL khi connected để không báo nhận rồi fallback ngay. Buffer32byte, xử lý tối đa16byte/loop; bỏ cả dòng overflow/non-ASCII/NUL, không nhận suffix của dòng lỗi. Parser không nhận số âm, thập phân, >100 hoặc ký tự thừa. MQTT JSON command/deadline/cache32ID/ACK vẫn thuộc A3; chưa subscribe topic command.

## OPEN_LOAD

Với applied≥20% ổn định1s, current_adc/4095 <10% liên tục2s thì OPEN_LOAD; ≥20% dòng kỳ vọng liên tục3s thì phục hồi. Ratio so bằng số nguyên để giữ biên409/410 và818/819 chính xác. Mỗi đổi applied hủy stability/confirmation; invalid ADC hoặc điều kiện không còn hợp lệ đặt lại timer. Tắt đèn không phát sinh lỗi mới, không xóa lỗi cũ. Không cắt PWM vì OPEN_LOAD; không tuyên bố bảo vệ quá dòng/ngắn mạch.

## Kiểm tra và giới hạn

[Testing](testing.md), [Wokwi 5 bước](simulation.md), [log TASK-006](../reports/evidence/task-006/validation.log). Bốn suite host chạy code thật với stub ADC/GPIO/mạng/RTOS; không kiểm chứng vật lý, contention hai core hoặc latency thực. Build dùng package pin hiện có, không thêm thư viện. Chưa chạy Wokwi bản P2; không chuyển kết quả live TASK-005 thành PASS P2. Task mạng tạo không thành công thì log lỗi, AUTO vẫn chạy offline. PWM attach/write có kiểm tra trả về và log lỗi; không suy applied từ CONTROL là phép đo điện thật.
