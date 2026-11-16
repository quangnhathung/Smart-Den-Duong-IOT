# TASK-008 — Backend, SQLite và API P4/A4

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/4 nhóm nghiệm thu dự kiến
- Cập nhật: 2026-11-16T12:02:01+07:00

## Mô tả và phạm vi

Đề xuất triển khai collector MQTT, SQLite, FastAPI, lệnh/ACK và tính điện năng theo SRS7/9, dùng hợp đồng MQTTv1 đã có code firmware. Chỉ là đề xuất, không tự tạo backend/dashboard hoặc deploy. Không suy test fixture thành tích hợp live.

## Tham chiếu SRS

SRS7,9,10P4,11A4,12; mqtt.md và đầu ra TASK-007. API endpoint/status theo SRS7.3, một worker collector; đọc lại và lập checklist chi tiết khi giao task.

## Tiêu chí hoàn thành và tiến độ

- [ ] Collector validate/dedup/order/boot, trạng thái mới/cũ/offline và SQLite persistence đạt kiểm thử.
- [ ] API/lệnh/ACK retry-timeout đúng SRS, không coi publish là áp dụng.
- [ ] Điện năng/coverage/gap/export theo mô hình, fixture có nhãn rõ.
- [ ] Test backend/API và tài liệu/chạy lại/bằng chứng phù hợp; phân biệt fixture và tích hợp thật.

## Vướng mắc và cách giải quyết

Live A3 chưa chạy tại máy này. TASK-007 đã bàn giao code/test/hướng dẫn5/5; trước nghiệm thu tích hợp firmware–backend cần kết quả live A3 theo mqtt.md A3-01…08 từ máy dev. Có thể làm backend với fixture có nhãn từ hợp đồng; chưa được báo end-to-end PASS trước khi chạy thật.

## Phụ thuộc và điều kiện bắt đầu

Người dùng giao TASK-008 riêng; hợp đồng MQTTv1 và test TASK-007 là đầu vào, giữ nguyên kết quả P2 và evidence. Người vận hành có thể kiểm chứng live A3 bằng runbook đã giao; không tự stop/start broker hoặc chạy gói tiếp theo từ đề xuất này. Không commit/push/deploy khi chưa được giao.
