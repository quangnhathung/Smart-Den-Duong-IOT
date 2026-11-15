# Đối chiếu bằng chứng TASK-005

Đây là rà soát hồ sơ, không phải lượt mô phỏng mới. Không cập nhật task.md hoặc chốt TASK-005. Nguồn tiêu chí: [testing.md](../../../../techs/testing.md). Các kết quả cảm biến/PWM do người vận hành xác nhận trong hội thoại; chưa có Serial/ảnh tương ứng trong cây evidence/task-005 tại thời điểm rà soát.

## Bảng nghiệm thu

| Ca | Trạng thái | Bằng chứng hiện có và phần thiếu |
|---|---|---|
| P1-01 | PARTIAL | Người dùng xác nhận LDR phản hồi. Chưa có Serial/ảnh ghép mức 1/100/10000 lux với ADC 0–4095 giảm khi lux tăng. |
| P1-02 | PARTIAL | Người dùng xác nhận biến trở phản hồi. Chưa có Serial current_adc ở vị trí thấp/giữa/tối đa và ảnh hoặc nhật ký vị trí đặt. |
| P1-03 | PARTIAL | Người dùng xác nhận PIR phản hồi. Chưa có Serial LOW → HIGH → LOW, log cạnh và ảnh thao tác Simulate Motion. |
| P1-04 | PARTIAL | Người dùng xác nhận HC-SR04 đã phản hồi đúng sau lượt chẩn đoán. Chưa có cặp giá trị đặt/đo 2/100/400 cm, distance_valid=1 và sai số. |
| P1-05 | PARTIAL | Người dùng từng chạy sơ đồ timeout, thấy distance_valid=0. Chưa có ảnh xác nhận cấu hình bỏ ECHO và Serial liên tiếp có NA, uptime/PWM tiếp tục; cần đối chiếu heartbeat cùng lượt. |
| P1-06 | PARTIAL | Người dùng xác nhận đủ năm PWM. Chưa có Serial đủ 0/25/50/70/100%, duty 0/64/128/179/255, ready=1 và ảnh mô phỏng tương ứng. |
| P1-07 | PARTIAL | Phần MQTT PASS theo log bên dưới; thiếu Serial/ảnh hoặc nhật ký thao tác cảm biến gắn với cùng cửa sổ 3 phút thực. |
| P1-08 | BLOCKED | Chưa được người dùng cho phép stop/start broker. Mốc offline-start.log của live-02 không đủ chứng minh đầy đủ raw/PWM/reconnect/pong và không reset ESP32; không dùng nó để chốt ca. |

Không có ca mới được kết luận FAIL từ việc thiếu hồ sơ. Không dùng host checks hoặc build để thay thế bằng chứng live.

## MQTT và thời gian P1-07 đã đủ

- [Subscriber](p107-20261116-010626-mqtt.log), [publisher](p107-20261116-010626-publish.log), [broker](p107-20261116-010626-broker.log), [tổng hợp](p107-20261116-010626-summary.txt).
- Cửa sổ thực: 2026-11-16T01:06:27+07:00 đến 01:09:47+07:00, khoảng 200 giây, lớn hơn 180 giây yêu cầu.
- 45 heartbeat nhận qua broker; uptime đầu/cuối 276892/365210 ms, chênh 88318 ms = 88,318 giây mô phỏng. Đây là khoảng giữa hai mẫu, không phải toàn bộ cửa sổ wall-clock và không phải phép đo chính xác tốc độ Wokwi.
- Pong khớp hoàn toàn payload duy nhất p107-win-20261116-010626. Payload này thay chuỗi ví dụ task005-001 theo yêu cầu người dùng.
- Broker không restart; không có timeout/disconnect của node trong log khoảng đo. Subscriber mới kết thúc do giới hạn -W 200; đây không phải lỗi node/broker.
- Không cần chạy lại MQTT chỉ để lấy thêm heartbeat hoặc thay payload cho giống chuỗi ví dụ.

## Bổ sung nhanh, ưu tiên khôi phục log đã có

1. Nếu Serial cũ còn trên VS Code hoặc đã lưu nơi khác: xuất bản sao mới vào thư mục này, tên serial-main-recovered-<thời điểm>.log. Giữ nguyên nội dung; ghi riêng nguồn và thời điểm xuất. Không tự gán thời gian thực cho dòng uptime. Ảnh đặt tên mới, không ghi đè.
2. Đối chiếu các điểm đo trong bảng. Chỉ thao tác lại điểm còn thiếu; không cần build lại. Có thể dùng cùng một Serial đầy đủ cho nhiều ca.
3. Nếu có Serial/ảnh/nhật ký thực sự từ 01:06:27–01:09:47, bổ sung để ghép với MQTT hiện có. Không tạo lại timestamp hoặc dùng ảnh hiện tại làm ảnh của lượt cũ.
4. Nếu không còn bằng chứng cảm biến của khoảng đó, cần một lượt kết hợp mới trên sơ đồ chính, đủ ít nhất 180 giây thời gian thực: ghi giờ bắt đầu/kết thúc có +07:00, xuất Serial, chụp giá trị đặt và tốc độ mô phỏng, đổi các cảm biến. Đồng thời thu MQTT và broker vào tên file mới. Gửi ping mới một lần để gắn phép thử với cửa sổ mới. Chuẩn bị subscriber trước khi bắt đầu lượt, chưa tự chạy lượt này trong rà soát.

Các điểm đo cần bổ sung trong lượt chính nếu log cũ không có:

- LDR 1/100/10000 lux: chờ ít nhất hai dòng SENSORS ổn định mỗi mức, ghi ldr_adc.
- Biến trở thấp/giữa/tối đa: ghi current_adc và vị trí núm; đây là ADC raw, không phải mA.
- PIR: ghi trước thao tác LOW, Simulate Motion, HIGH rồi trở lại LOW; giữ cả log cạnh PIR.
- HC-SR04 2/100/400 cm: ghi distance_valid và distance_cm. Sai số tối đa tương ứng 2/5/20 cm. Không dùng những giá trị này làm kết quả đã đo.
- PWM: giữ Serial đủ một vòng, xác nhận năm cặp phần trăm/duty và ready=1; không điều khiển LED theo cảm biến trong P1.

## Hướng dẫn P1-05 cho người vận hành

1. Xuất Serial/ảnh sơ đồ chính trước khi dừng Wokwi để không mất buffer. Không đụng broker.
2. F1 → Wokwi: Stop Simulator. F1 → Wokwi: Select Config File → simulations/node_01/timeout/wokwi.toml. Nếu không chọn được, mở riêng thư mục timeout trong cửa sổ VS Code; chỉ một mô phỏng được chạy.
3. Chụp cấu hình được chọn và sơ đồ không có dây ECHO → GPIO19. Cấu hình timeout dùng cùng BIN/ELF qua ../build, không cần build.
4. Ghi giờ bắt đầu thực, F1 → Wokwi: Start Simulator. Xác nhận banner P1/A1. Quan sát ít nhất một vòng PWM, chờ thêm nếu mô phỏng chậm.
5. Lưu nhiều dòng SENSORS liên tiếp có distance_valid=0 distance_cm=NA, uptime tăng, PWM tiếp tục; đối chiếu heartbeat đến broker cùng lượt. Chỉ một dòng invalid không chứng minh vòng điều phối không treo.
6. Lưu serial-timeout-<thời điểm>.log, ảnh timeout-<thời điểm>.png và nhật ký giờ thực/cấu hình/checksum vào thư mục này; dùng tên chưa tồn tại. Nếu subscriber đã hết hạn, mở capture mới trước bước 4.
7. Sau khi xuất bằng chứng, Stop Simulator bản timeout. Chọn lại simulations/node_01/wokwi.toml nếu cần quay lại sơ đồ chính. Tuyệt đối không chạy song song hai sơ đồ cùng client ID.

## Điều kiện chốt còn thiếu

Đủ bằng chứng từng ca P1-01 đến P1-07; P1-08 được người dùng cho phép và thực hiện có bằng chứng raw/PWM tiếp tục, reconnect/pong mới, không reset ESP32. Sau đó mới đề nghị review và cập nhật hồ sơ trong phạm vi được giao. Lượt này không cập nhật task.md, không đánh dấu hoàn thành và không triển khai TASK-006.
