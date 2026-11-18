# TASK-017 — Kịch bản giới thiệu và demo toàn diện

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu
- Cập nhật: 2026-11-18T16:20:56+07:00

## Mô tả và phạm vi

Người dùng yêu cầu kịch bản demo chi tiết toàn diện, giới thiệu chi tiết. Tạo lời dẫn có thể đọc trực tiếp, thao tác Wokwi/dashboard, phân vai gợi ý hai người, thời lượng khoảng20 phút, bản rút gọn, kết quả quan sát, số liệu thực nghiệm có nguồn, câu hỏi bảo vệ và phương án sự cố. Bàn giao Word chỉnh sửa được cùng Markdown. Giữ toàn bộ source sản phẩm/dữ liệu, không tự chạy buổi demo hoặc triển khai dashboard mô phỏng mới.

Task mới dùng017 vì016 đang là mã đề xuất diễn tập chưa bắt đầu. [Task015 trước đó](evidence/task-017/task.md-before.md) và đề xuất016 được giữ nguyên trong hồ sơ.

## Tham chiếu SRS

SRS mục1–9,12,13,15; nhấn mạnh demo mô phỏng, AUTO tại node, PIR là điều kiện kích hoạt, MQTT/ACK và hai loại clock. Không dùng nội dung dự kiến làm bằng chứng chức năng.

## Tiêu chí hoàn thành và tiến độ

- [x] Đối chiếu controller/cấu hình/UI và số liệu TASK-012; chọn timeline, node và đầu vào không mâu thuẫn.
- [x] Soạn mở đầu/kiến trúc, từng cảnh gồm lời nói/thao tác/kỳ vọng/chờ/xử lý lỗi, kết luận/Q&A/checklist và nhánh chỉ Wokwi khi MQTT chưa chạy.
- [x] Tạo DOCX/Markdown đồng nội dung, schema và WPS kiểm mọi trang; giữ các tệp đã giao trước.
- [x] Kiểm timeline/số liệu/luồng/cú pháp/liên kết, bảo toàn source/lịch sử; cập nhật tài liệu liên quan và đề xuất tiếp theo.

## Vướng mắc và cách giải quyết

Không có vướng mắc chặn. Đã sửa đích liên kết nguồn trong bản cuối; WPS23 trang, schema,411 dòng nội dung và10 liên kết nội bộ đã kiểm. Tái dùng runtime riêng, không cài lại hoặc xuất PDF tự động. Mốc thời lượng là dự kiến cho trình bày, mỗi thao tác chuyển cảnh theo trạng thái thực, không giả định timer mô phỏng bằng giờ máy.

## Phụ thuộc và điều kiện bắt đầu

Đã được giao soạn tài liệu. Dữ liệu và bằng chứng TASK-011/012, guide TASK-015 và source hiện hành có sẵn. Chưa có xác nhận hai thành viên đã tự diễn tập; không ghi PASS thay con người.

## Kết quả bàn giao

[Markdown kịch bản](../demo-script.md); Word output/task-017/Kich-ban-gioi-thieu-va-demo-toan-du-an-Nhom7-v03.docx23 trang. [QA](evidence/task-017/document-qa.json), [timeline/số liệu](evidence/task-017/content-checks.json). Timeline chính20 phút và rút gọn7 phút là khung diễn tập, chưa xác nhận thời lượng buổi thực tế. Không chạy lại stack live, không ghi PASS cho hai người; đề xuất tiếp TASK-018 diễn tập theo kịch bản, chưa thực hiện.
