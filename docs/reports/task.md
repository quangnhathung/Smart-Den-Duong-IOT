# TASK-002 — Kiểm chứng môi trường P0

- Trạng thái: Bị chặn
- Tiến độ: 1/4 nhóm nghiệm thu; nhiều bước con đã đạt
- Cập nhật: 2026-11-15T18:19:35+07:00

## Mô tả và phạm vi

Đã có build thành công, artifact đã copy khớp checksum, Wokwi khởi chạy với Serial/PWM và broker host pub/sub đạt theo bằng chứng người dùng. ESP32 đã kết nối Mosquitto nhưng bị timeout lặp lại. Chưa có đủ năm mức PWM, ba pong hoặc phục hồi sau restart broker. Chưa triển khai cảm biến/AUTO/MANUAL hoặc hoàn tất P0/A0. Lượt này chỉ cập nhật tài liệu.

## Tham chiếu SRS

[SRS](../srs.md) mục 3.1, 4.3–4.5, 10.2–10.3, 11–12.

## Tiêu chí hoàn thành và tiến độ

- [ ] Build mới esp32dev thành công và khóa phiên bản platform/framework sau smoke test đạt. Build đã PASS; khóa phiên bản còn chờ live đạt.
- [ ] License Wokwi, Serial và năm mức PWM được xác nhận bằng log/ảnh. Đã chạy Wokwi/Serial, thấy 0%/25%; còn thiếu 50%/70%/100%.
- [ ] Broker qua host, ba ping/pong và mất/khôi phục broker đạt bằng chứng live. Host pub/sub đạt; node kết nối nhưng timeout; chưa xác nhận pong/phục hồi.
- [x] Chuẩn bị mã/cấu hình, tài liệu setup và hồ sơ kiểm tra; ghi rõ phần chưa xác minh.

Giữ 1/4 nhóm nghiệm thu gốc vì ba nhóm đầu đều còn điều kiện chưa đủ; không quy đổi thành phần trăm hoàn thành dự án. Chi tiết từng phần đã đạt tại [bằng chứng live](evidence/task-002/live-progress.md).

## Vướng mắc và cách giải quyết

Lỗi min đã sửa; build.log hiện tại là bản SUCCESS 7.31 giây do người dùng chạy lại, không còn là log lỗi cũ. Broker ghi smartlight-node_01-p0 kết nối ba lần rồi exceeded timeout sau 22–23 giây. Tốc độ mô phỏng thấp là giả thuyết cần kiểm tra, chưa kết luận nguyên nhân. Thu Serial đầy đủ và đối chiếu hoạt động MQTT/heartbeat; không tự đổi broker hoặc hostname. Chưa khóa platform/framework vì smoke live chưa đủ.

## Phụ thuộc và điều kiện bắt đầu

Theo chuỗi thao tác người dùng, phiên cuối đã compose down. Lần thử tiếp cần up -d mosquitto, giữ Wokwi chạy liên tục, chờ subscribe rồi mở subscriber trước khi gửi ping. Cần log Serial, ba pong, bằng chứng đủ năm mức PWM và pong sau restart broker. Không tự sửa firmware hoặc khởi chạy dịch vụ trong lượt cập nhật tiến độ.

## Phần đã hoàn tất trong TASK-002

- [x] Chuẩn bị mã/cấu hình/tài liệu P0.
- [x] Sửa kiểu min, kiểm tra formatter, build thành công (lượt trước).
- [x] Đối chiếu build mới và checksum nguồn/copy.
- [x] Ghi nhận Wokwi/Serial/PWM một phần và broker host pub/sub.
- [x] Lưu ảnh gốc, tổng hợp timeout, cập nhật hồ sơ; chưa đánh dấu P0 hoàn thành.
