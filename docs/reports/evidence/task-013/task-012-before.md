# TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Đang thực hiện
- Tiến độ: 1/5 nhóm nghiệm thu
- Cập nhật: 2026-11-17T21:02:43+07:00

## Mô tả và phạm vi

Người dùng đã giao triển khai kế hoạch TASK-012: thực nghiệm đầy đủ, phân tích số liệu và bàn giao DOCX/PDF, PPTX/PDF, video MP4, runbook và backup. Kế thừa bìa/thông tin trường, nhóm, thành viên từ đề cương Word, tạo tệp mới và giữ nguyên đề cương. TASK-011 hoàn thành4/4 được lưu tại [bản trước](evidence/task-012/run-20261117-200024/task-011-before.md).

Giữ firmware ba node, MQTT/API/schema, controller/pin map/toolchain và dashboard HTML/CSS/JS qua Live Server. Chỉ sửa lỗi trực tiếp cản trở thực nghiệm có tái hiện/hồi quy. Không tự commit/push/merge hoặc triển khai cloud. Dữ liệu và output lớn tại output/task-012/ được ignore; bằng chứng gọn ở docs/reports/evidence/task-012/.

## Tham chiếu SRS

[SRS](../srs.md) mục9.1–9.3,12,15; P7/A7. Mốc phiên5/10/15 phút và PIR mỗi30s dùng uptime riêng mỗi node theo lựa chọn người dùng. UTC/monotonic máy ghi riêng; năng lượng theo uptime, độ phủ theo thời gian nhận. Không diễn giải mô hình điện năng như đo phần cứng.

## Phương pháp đã chốt

15 lượt chính: EX01 một lượt5 phút; EX02/03/04 mỗi kịch bản3 lượt10 phút; EX05 ba lượt15 phút; EX06/07 mỗi kịch bản1 lượt5 phút. Cả3 node hoạt động; phân tích cửa sổ riêng, không tính thêm thời gian node nhanh. PIR ở giây15 rồi mỗi30s trong pha có chuyển động. EX03 distance150cm, EX04 distance50cm. EX01 DAY đổi chuyển động; EX02 NIGHT yên tĩnh. EX05 ba pha300s: (DAY, NIGHT yên tĩnh, NIGHT người), (TWILIGHT, NIGHT người, NIGHT xe), (NIGHT xe, DAY, NIGHT yên tĩnh). EX06 node02 tải0 giây60, phục hồi180. EX07 broker down60/recover120 theo uptime node02, kiểm AUTO offline bằng Serial và LDR node01. Pilot ngoài dữ liệu chính; không dồn thao tác khi trễ quá2s mô phỏng.

Công cụ preflight/run/summarize/verify điều khiển Wokwi UI, thu raw MQTT/Serial/API/health và heartbeat độc lập. Giữ FAIL/INCOMPLETE, chạy lại trọn lượt lỗi; không chọn bỏ kết quả hợp lệ. API/CSV/phép tính độc lập phải khớp trong1e-9Wh; loại đúng MANUAL/fault/low-load/offline/gap/boot/session và công bố độ phủ. Không đặt tỷ lệ tiết kiệm mục tiêu.

## Tiêu chí hoàn thành và tiến độ

- [x] Nhóm1 — Baseline, công cụ/phương pháp và pilot được kiểm chứng.
- [ ] Nhóm2 — Đủ15 lượt chính hợp lệ, raw/CSV/ảnh/cấu hình tái lập.
- [ ] Nhóm3 — Phân tích năng lượng/baseline/độ phủ, đối chiếu độc lập và API/CSV.
- [ ] Nhóm4 — Báo cáo DOCX/PDF sáu chương,12 slide PPTX/PDF, video MP4 6–8 phút; kiểm trực quan mọi trang/slide và phát video.
- [ ] Nhóm5 — Runbook, diễn tập khởi động, backup/manifest/toàn vẹn SQLite, cleanup và tài liệu tiến độ.

## Vướng mắc và cách giải quyết

Pilot-r01-a04 PASS cả3 node, gồm PIR người/xe, OPEN_LOAD/phục hồi, clock và đối chiếu API/CSV/số học độc lập. Ba lượt pilot trước giữ INCOMPLETE (2 lượt trễ thao tác,1 lượt timeout chuẩn bị).32 Python test PASS. Đang chạy EX-01 chính thức; chưa hoàn thành15 lượt. Runtime tạo/render Word/PowerPoint thiếu, đã hỏi người dùng về bộ công cụ cục bộ thay thế và tiếp tục phần độc lập.

## Phụ thuộc và điều kiện bắt đầu

Đã có yêu cầu triển khai của người dùng. Cần ba Wokwi VS Code/gateway, broker QA, backend một worker/SQLite mới, Live Server, runtime tài liệu và công cụ video. Chỉ thao tác tài nguyên QA có quyền sở hữu; giữ dữ liệu cũ. Không tự ghi PASS khả năng hai thành viên chạy/giải thích nếu chưa có xác nhận trực tiếp.
