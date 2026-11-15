# Cập nhật bằng chứng live TASK-002

> Bản ghi theo thời điểm 18:19; trạng thái đã được thay bằng [biên bản nghiệm thu](acceptance.md). Giữ nguyên dữ liệu quan sát cũ bên dưới.

- Đối chiếu: 2026-11-15T18:19:35+07:00.
- Nguồn: log có sẵn, checksum artifact, ảnh và đầu ra terminal người dùng cung cấp trong hội thoại. Agent không tự chạy Docker/Wokwi trong lượt này.

## Kết quả

| Hạng mục | Trạng thái và bằng chứng |
|---|---|
| Build esp32dev | PASS: [build.log](build.log), SUCCESS 7.31 giây; RAM 47276 byte, flash 896215 byte |
| Chuẩn bị artifact | PASS: BIN/ELF nguồn và bản copy trùng SHA-256, khớp đầu ra người dùng |
| Wokwi/license/Serial | Đã chạy: [ảnh gốc](wokwi-first-run.png), Community License, banner Arduino 3.3.12 |
| PWM | Xác nhận một phần: ready=1, log 0%/duty 0 và 25%/duty 64; chưa đủ năm mức |
| Broker qua host | PASS theo terminal người dùng: subscriber nhận p0-broker-001; lần timeout đầu không phủ nhận lượt sau đạt. Chưa có mqtt.log thô riêng |
| ESP32 tới broker | Kết nối được: [broker.log](broker.log), client smartlight-node_01-p0 ba lần |
| Giữ kết nối | FAIL: broker ngắt do exceeded timeout sau 22–23 giây, keepalive k15 |
| Ba ping/pong | Chưa đạt: chỉ thấy lệnh publish; subscriber pong bị Ctrl+C, chưa có pong xác nhận |
| Phục hồi sau restart broker | Đã thao tác stop/start theo terminal; chưa có node kết nối lại/pong mới để nghiệm thu |
| Trạng thái cuối phiên | Theo lệnh người dùng: đã docker compose down; chưa kiểm tra lại runtime hiện tại |

## Checksum đối chiếu

- BIN: `33e2f750284e820bc531a2bfd8a4f710c0729dd092cc3aa6a76bb72d18ac1cf7`.
- ELF: `3010829f37246bb9785bbfbb6baeb0917778c64c13e128c09a8165affb48077c`.

## Ba lần timeout trong broker.log

- 18:12:58 → 18:13:20 (+07:00): 22 giây.
- 18:13:30 → 18:13:53 (+07:00): 23 giây.
- 18:13:59 → 18:14:22 (+07:00): 23 giây.

## Giới hạn và giả thuyết

Ảnh tại một thời điểm cho thấy wifi=3, mqtt=0 và tốc độ mô phỏng khoảng 39%. Giả thuyết: thời gian mô phỏng chậm có thể làm heartbeat trễ so với broker theo thời gian thực. Chưa có Serial đầy đủ/packet capture để khẳng định nguyên nhân; không coi đây là chẩn đoán đã xác nhận. Kết nối broker đã có nên chưa có căn cứ đổi hostname, broker hoặc mở thêm cổng.

Nguồn đối chiếu trước đó: [MQTT keepalive](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html), [Wokwi simulation clock](https://docs.wokwi.com/guides/esp32-wifi). Không sửa firmware trong lượt cập nhật này.
