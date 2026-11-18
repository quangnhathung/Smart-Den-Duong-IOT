# TASK-018 — Diễn tập vận hành và bảo vệ với hai thành viên

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/3 mục nghiệm thu dự kiến
- Cập nhật: 2026-11-18T16:20:56+07:00

## Mô tả và phạm vi

Kế thừa đề xuất TASK-016 chưa thực hiện, đã có thêm kịch bản TASK-017. Mã đề xuất kế tiếp theo lịch sử là TASK-018. Đề xuất sau TASK-017: hai thành viên dùng bộ bàn giao/runbook/kịch bản demo để tự khởi động mô hình, chạy demo và giải thích thuật toán, giao thức, năng lượng/độ phủ và giới hạn. Chỉ thực hiện khi người dùng giao task; chưa chạy trong TASK-017. Không thêm tính năng hoặc tự triển khai cloud.

## Tham chiếu SRS

SRS mục13,15–16; kiểm khả năng vận hành/giải thích của nhóm, không thay bằng kiểm tự động.

## Tiêu chí hoàn thành và tiến độ

- [ ] Mỗi thành viên tự khởi động ba node/backend/broker/dashboard bằng Live Server theo runbook; ghi máy/môi trường/kết quả và lỗi thực tế.
- [ ] Mỗi người thực hiện các luồng demo và giải thích số liệu/giới hạn bằng bằng chứng, không coi mô phỏng là số đo phần cứng.
- [ ] Chốt phản hồi, sửa hướng dẫn trong phạm vi được giao và ghi biên bản diễn tập; PDF do người dùng xuất nếu cần nộp.

## Vướng mắc và cách giải quyết

Chưa có xác nhận trực tiếp từ hai thành viên. Agent không tự ghi PASS; cần buổi diễn tập và phản hồi thực tế.

## Phụ thuộc và điều kiện bắt đầu

TASK-012, TASK-015 và TASK-017 đã hoàn thành; cần người dùng giao TASK-018, hai thành viên sẵn sàng và máy có PlatformIO/Wokwi/gateway, Python backend, MQTT và VS Code Live Server. Kiểm lại manifest trước chạy; helper/PID của đợt QA cũ chỉ là tham chiếu, không chạy mù.
