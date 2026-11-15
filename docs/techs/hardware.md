# Mạch mô phỏng node_01 P1/A1

## Tham chiếu và hiện trạng

[SRS](../srs.md) mục 4.1–4.2; [firmware đọc cảm biến](firmware.md), [cách chạy](simulation.md). Sơ đồ đã tạo và kiểm tra tĩnh; chưa xác minh linh kiện bằng Wokwi live ở TASK-005.

## Linh kiện và đấu nối

| ID / linh kiện | Chân tín hiệu | Nguồn |
|---|---|---|
| esp / board-esp32-devkit-c-v4 | ESP32 esp32dev | Board mô phỏng |
| ldr / wokwi-photoresistor-sensor | AO → esp:34 | VCC → 3V3, GND chung |
| pir / wokwi-pir-motion-sensor | OUT → esp:27 | VCC → 5V, GND chung |
| ultrasonic / wokwi-hc-sr04 | TRIG → esp:18, ECHO → esp:19 | VCC → 5V, GND chung |
| currentSim / wokwi-potentiometer | SIG → esp:35 | VCC → 3V3, GND chung |
| r / điện trở 220 Ω | esp:26 → r:1; r:2 → led:A | Giữ mạch P0 |
| led / LED vàng | led:C → esp:GND.1 | PWM GPIO26 |

Giữ TX/RX nối Serial Monitor như P0. LDR DO không sử dụng. GPIO34/35 thuộc ADC1. Giá trị đầu: LDR 500 lux, PIR LOW với delayTime=1 giây, siêu âm 100 cm, biến trở value=1023 (tối đa của núm mô phỏng). Range núm Wokwi không phải độ phân giải ADC ESP32; firmware đặt ADC12 bit, 0–4095.

## Sơ đồ lỗi để kiểm tra timeout

Cấu hình chính là simulations/node_01/wokwi.toml. Bản sao simulations/node_01/timeout/wokwi.toml dùng cùng firmware qua ../build, chỉ bỏ dây ultrasonic:ECHO → esp:19. Firmware cấu hình GPIO19 INPUT_PULLDOWN để đầu vào không thả nổi. Không sửa hoặc ghi đè sơ đồ chính để thực hiện ca lỗi.

## Kiểm tra và giới hạn

Kiểm tra tĩnh ID/loại linh kiện, dây, nguồn và hai cấu hình; chưa thay thế kiểm tra tín hiệu thực tế trong mô phỏng. Cần các ca ở [testing](testing.md). Mạch này chỉ cho Wokwi, không phải thiết kế nguồn/driver/đấu mức điện áp cho đèn công suất hoặc ESP32 thật.

Wokwi chưa mô phỏng analog đầy đủ; việc ADC có dữ liệu không chứng minh dây nguồn đã đúng. Biến trở chỉ là đầu vào raw trong P1, chưa quy đổi dòng hay phát hiện lỗi. Nguồn: [LDR](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor), [PIR](https://docs.wokwi.com/parts/wokwi-pir-motion-sensor), [HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04), [biến trở](https://docs.wokwi.com/parts/wokwi-potentiometer).
