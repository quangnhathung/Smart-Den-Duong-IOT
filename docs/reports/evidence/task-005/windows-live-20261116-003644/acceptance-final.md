# Nghiệm thu cuối TASK-005 — P1/A1 một node

Kết luận: P1-01 đến P1-08 PASS trong phạm vi firmware raw sensor/diagnostics một ESP32; TASK-005 đạt 4/4 nhóm nghiệm thu. Không phải nghiệm thu AUTO/MANUAL, telemetry nghiệp vụ, ba node hoặc ổn định dài hạn.

## Phần bổ sung chốt P1-08

Đã đọc toàn bộ 159 dòng [p108-recovery-20261116-0250.log](p108-recovery-20261116-0250.log). SHA-256 `fc70531ed9e75adfc6d2050b961da627389cd7cb343b9df00e076f3dc9ffad6b`.

- Thời gian stop 2026-11-16 02:50:00 +07:00/start 02:50:26 +07:00 do người vận hành xác nhận; không phải timestamp in trong Serial hoặc thao tác agent thực hiện ở lượt rà soát này. Không đổi uptime thành wall-clock.
- Disconnected: 106176 ms. Retry attempt ở 108076/112080 ms; failed tương ứng ở 108132/112114 ms. Có attempt tiếp ở 120087 ms rồi connected ở 120163 ms; retry_ms tăng 2000/4000/8000.
- Trong đoạn offline có 14 dòng SENSORS và đủ năm PWM 0/25/50/70/100%, duty 0/64/128/179/255, ready=1. Không treo vòng xử lý khi mqtt=0.
- Sau reconnect có ping subscribed, SENSORS tiếp tục và HEARTBEAT published=1 tại 122171/124179 ms rồi tiếp tục.
- Uptime SENSORS tăng nghiêm ngặt từ 83211 đến 135189 ms, không có banner/reset trong đoạn; bằng chứng xác nhận phục hồi không cần reset trong phạm vi capture.

Lượt 02:50 bổ sung Serial offline còn thiếu, không gán nó thành Serial của lượt 02:29. [Lượt recovery 02:29](p108-20261116-022831-review.md) đã có timeline Docker, broker reconnect, heartbeat thực nhận và [pong khớp sau phục hồi](p108-20261116-022831-mqtt.log). Lượt 02:50 không có dòng pong trong Serial được cung cấp; không bịa pong hoặc timestamp nhận cho lượt này. P1-08 được chốt trên bộ bằng chứng bổ sung của hai lượt cùng chức năng, không tuyên bố có một capture đồng bộ duy nhất. Không cần chạy lại phép thử.

## Ma trận nghiệm thu cuối

| Ca | Kết quả | Bằng chứng và nguồn xác nhận |
|---|---|---|
| P1-01 | PASS | [LDR](p101-ldr.log): 3894/2045/156; người vận hành xác nhận lux 1/100/10000; [đối chiếu](p101-p102-review-20261116.md) |
| P1-02 | PASS | [Biến trở cuối](p102-potentiometer-final.log): 4095/2122/0; vị trí tối đa/giữa/thấp nhất do người vận hành xác nhận; [đối chiếu](p102-final-and-p108-gap-20261116.md) |
| P1-03 | PASS | [PIR](p103-pir.log): LOW → HIGH → LOW và log hai cạnh; [đối chiếu](p103-review-20261116.md) |
| P1-04 | PASS | [HC-SR04](p104-ultrasonic.log): 2.00/101.41/405.64–405.66 cm cho điểm đặt 2/100/400 cm do người dùng xác nhận; sai số dưới giới hạn; [đối chiếu](p104-review-20261116.md) |
| P1-05 | PASS | [Serial timeout](p105-timeout.log), [ảnh](p105-timeout-screen.png), [MQTT](p105-20261116-014745-mqtt.log); invalid/NA, PWM tiếp tục, heartbeat khớp uptime; [giới hạn giờ thực](p105-review-20261116.md) |
| P1-06 | PASS | [Serial PWM](p102-potentiometer.log), đủ năm mức/duty/ready=1; người vận hành xác nhận PWM trong Wokwi |
| P1-07 | PASS | [Serial hai boot](p102-p107-main-secondboot.log) chỉ dùng boot thứ hai; [capture timestamp](p102-p107-20261116-020831-mqtt.log): 184 giây thực, 40 heartbeat khớp, ADC đổi trong cửa sổ, ping/pong; [đối chiếu](p102-p107-20261116-020831-review.md) |
| P1-08 | PASS | Serial 02:50 và recovery MQTT 02:29 nêu rõ ở trên; đủ offline/raw/PWM/retry, reconnect/heartbeat/pong và không reset trong đoạn Serial |

## Bốn nhóm hoàn thành

- [x] Mạch/pin map chính và bản timeout: kiểm tra tĩnh, người vận hành đã chạy đúng hai cấu hình, ảnh timeout.
- [x] Raw ADC/PIR/distance/Serial có bằng chứng thực, giá trị đặt được ghi nguồn người vận hành.
- [x] Build esp32dev/copy artifact/checksum đã PASS; năm PWM và MQTT hồi quy/offline/recovery đã nghiệm thu.
- [x] Tài liệu kỹ thuật, task/report/checklist/next-task cập nhật, giữ bằng chứng và lịch sử thất bại/PARTIAL trước đó.

## Giới hạn được giữ

Không có ảnh riêng cho mọi điểm đo; một số đoạn Serial do người dùng copy, không có timestamp thực/boot_id. Các giá trị đặt lux/khoảng cách/vị trí núm có nguồn xác nhận người dùng, không giả thành trường firmware. P1-05 không chứng minh độc lập giờ Start/Stop chính xác; không lấy metadata tệp thay giờ chạy. Các kết luận chức năng có log tương ứng, không cần tạo ảnh giả hoặc kiểm thử lại ca PASS.

Timeout ở những phiên dài trước đây vẫn là hạn chế theo dõi cho A3, chưa xác định nguyên nhân và chưa được tuyên bố đã sửa. Chưa nghiệm thu thời gian thực cứng, GPIO/điện áp phần cứng thật, AUTO/MANUAL/fault hoặc mạng nghiệp vụ.

## Bước tiếp theo

Đủ điều kiện chuyển đề xuất TASK-006 — thuật toán chiếu sáng P2/A2, gồm AUTO/MANUAL, hold/dimming/fault và kiểm thử clock theo SRS. Chưa triển khai TASK-006; cần yêu cầu giao việc riêng. Không build/test lại, không đụng broker/firmware, không commit/push trong lượt chốt hồ sơ.
