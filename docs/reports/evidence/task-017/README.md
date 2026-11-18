# TASK-017 Kịch bản giới thiệu và demo toàn diện

Đầu ra gồm [Markdown](../../../demo-script.md) và Word23 trang tại output/task-017/Kich-ban-gioi-thieu-va-demo-toan-du-an-Nhom7-v03.docx. Kịch bản chính20 phút, rút gọn7 phút, mở đầu/kiến trúc/kết luận có lời đọc, thao tác Wokwi/dashboard, nguồn số liệu,14 câu hỏi bảo vệ, checklist và nhánh MQTT0.

## Kiểm tra

- [Document QA](document-qa.json), [schema log](schema-check.log), [build/hash](build.json).23 trang v02 đã xem trực quan; v03 sửa đích hyperlink, render lại và mọi PNG giống nguyên byte bản đã xem. [Proof v02](preview-v02-proof.json), [proof cuối](preview-v03-proof.json).411 dòng nội dung khớp Markdown,23 heading chính,10 liên kết nguồn trong DOCX tồn tại; không tràn/cắt, WPS QA đã đóng.
- [Nội dung/timeline/số liệu](content-checks.json):11 đoạn liên tục tổng1200s,8 đoạn bản ngắn tổng420s; số công suất/tỷ lệ EX02–05 khớp variation.json sau làm tròn; coverage EX07 khớp ba node trong CSV. JSON/Bash cú pháp đạt; không thực thi Docker hoặc PowerShell.
- [Baseline sản phẩm](product-baseline.json) ghi source/hash trước task;30 tệp firmware,26 backend,15 dashboard giữ nguyên. Không sửa thuật toán, schema, dependency hoặc dữ liệu.
- [Trạng thái trước](task.md-before.md), [đề xuất diễn tập016 trước](next-task.md-before.md) được giữ; task mới017 chỉ tạo kịch bản, chưa chạy diễn tập con người.

## Phạm vi và giới hạn

Đối chiếu SRS/controller/guide/runbook, UI và kết quả TASK-012; không dùng thiết kế dự kiến làm bằng chứng chức năng. Mỗi cảnh có điều kiện chờ thật; không suy ACK=PWM đã tới mục tiêu hoặc khoảng cách gần=PIR HIGH. Cảnh outage không tự nhận đã kiểm pending/no-replay khi buổi này không tạo pending. Số liệu đã thu được giới thiệu tách phần live, power/energy là mô hình.

Không chạy lại Wokwi/broker/backend/dashboard, build/15 lượt hoặc Windows; không ghi PASS cho khả năng hai thành viên. PDF người dùng tự xuất WPS. Bộ Word hướng dẫn TASK-015 và báo cáo/PPTX/video TASK-012 được giữ nguyên. Output lớn và preview nằm ngoài Git, nguồn Markdown/generator và proof gọn được giữ trong repo. Không commit/push/cloud.
