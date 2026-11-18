# TASK-020 — Rà soát báo cáo và diễn tập vận hành, bảo vệ

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/3 mục nghiệm thu dự kiến
- Cập nhật: 2026-11-18T16:41:28+07:00

## Mô tả và phạm vi

Đề xuất sau TASK-019, kế thừa TASK-018 chưa thực hiện. Hai thành viên rà soát Word bốn chương và dùng hướng dẫn/runbook/kịch bản TASK-017 để tự khởi động, demo và giải thích mô hình. Chỉ bắt đầu khi người dùng giao; chưa thực hiện trong TASK-019. Không tự bổ sung tính năng/cloud hoặc chạy lại15 lượt thực nghiệm.

## Tham chiếu SRS

SRS13,15–16; xác nhận khả năng vận hành/giải thích của nhóm và nội dung nộp, không thay bằng kiểm tự động.

## Tiêu chí hoàn thành và tiến độ

- [ ] Hai thành viên rà soát thông tin bìa, bố cục bốn chương, số liệu và yêu cầu của giảng viên; ghi các điều chỉnh được yêu cầu.
- [ ] Mỗi người tự khởi động ba node/backend/broker/dashboard bằng Live Server, thực hiện các cảnh demo và giải thích PIR/hold/ACK/clock/năng lượng/giới hạn; có phản hồi thật.
- [ ] Ghi biên bản diễn tập, xử lý lỗi trong phạm vi được giao và chốt bản nộp. Word là định dạng hiện được yêu cầu; người dùng tự xuất PDF nếu cần.

## Vướng mắc và cách giải quyết

Chưa có phản hồi trực tiếp hoặc buổi diễn tập của hai thành viên. Không tự ghi PASS. Bản Word TASK-019 đã qua QA kỹ thuật, chưa thay thế sự rà soát nội dung của nhóm/giảng viên.

## Phụ thuộc và điều kiện bắt đầu

TASK-012/015/017/019 hoàn thành; cần người dùng giao task, hai thành viên sẵn sàng và máy có runtime/PlatformIO/Wokwi/gateway, Python backend, MQTT, Live Server. Đối chiếu manifest và cấu hình hiện tại trước chạy; không dùng mù PID/helper QA cũ. Đề xuất018 cũ bảo toàn tại [snapshot](evidence/task-019/next-task.md-before.md).
