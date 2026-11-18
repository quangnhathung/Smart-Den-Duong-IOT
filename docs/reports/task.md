# TASK-019 — Viết lại báo cáo tiểu luận bốn chương

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu
- Cập nhật: 2026-11-18T16:41:28+07:00

## Mô tả và phạm vi

Người dùng yêu cầu viết lại báo cáo: Lời nói đầu; Chương1 Giới thiệu về IoT có mục1.1/1.2…; Chương2 Giới thiệu phần cứng; Chương3 Giới thiệu phần mềm/kiến trúc/hoạt động; Chương4 Kết quả demo; Lời kết. Chỉ tạo Word, dùng kết quả hiện có, kế thừa bìa và style hiện tại, không dùng skill humanize/humanizer/viet-humanize. Nguồn kế thừa là báo cáo TASK-012 v05 sáu chương. Tạo tệp mới, giữ nguyên bản cũ; không PDF/Markdown/PPTX bàn giao, không chạy lại thực nghiệm hoặc sửa sản phẩm/dữ liệu.

Task mới019 vì018 đang là mã đề xuất diễn tập. [Task017 trước](evidence/task-019/task.md-before.md) và đề xuất018 được bảo toàn.

## Tham chiếu SRS

SRS mục1–9,12–15; biên soạn lại tài liệu học thuật, không triển khai FR mới. Mô tả phần cứng/phần mềm thực tế, dùng audit/CSV/ảnh/video TASK-011/012 đã có, công bố giới hạn mô phỏng và hai clock.

## Tiêu chí hoàn thành và tiến độ

- [x] Xác minh DOCX nguồn/bìa/style, lập bố cục và số liệu hiện có; tham chiếu nguồn lý thuyết phù hợp.
- [x] Viết đủ lời nói đầu, bốn chương có mục con, kết quả demo thực và lời kết; số liệu/ảnh có nguồn, không thêm kết quả chưa chạy.
- [x] Xuất DOCX mới, giữ nguyên bìa/styles và bản nguồn; schema, render WPS/kiểm mọi trang, mục lục/heading/bảng/ảnh đạt.
- [x] Đối chiếu số liệu/nguồn/định dạng/bảo toàn sản phẩm và lịch sử; cập nhật hồ sơ/techs/task/report/checklist/đề xuất.

## Vướng mắc và cách giải quyết

Chưa có vướng mắc. Dùng skill docx và runtime Office riêng đã có, không dùng các skill humanize theo yêu cầu. WPS render PNG phục vụ QA, không tạo PDF bàn giao. Kết quả lịch sử được dẫn đúng phạm vi, không đổi thành nghiệm thu phần cứng thật.

## Phụ thuộc và điều kiện bắt đầu

Đã được giao. Báo cáo v05, audit/CSV/ảnh/biểu đồ và runtime WPS có sẵn. Không tự diễn tập con người, bật lại broker/Wokwi, chạy chiến dịch mới hoặc commit/push/cloud.

## Kết quả và bằng chứng

Word mới27 trang,6 ảnh/biểu đồ. Schema/WPS27 trang, PNG bìa/source style byte-identical, bảng CSV/audit và bảo toàn source/lịch sử PASS. [Hồ sơ, Word và giới hạn](evidence/task-019/README.md). Không dùng humanize/humanizer/viet-humanize; không tạo bản PDF/PPTX/Markdown của tiểu luận. Không chạy thực nghiệm/build hoặc sửa sản phẩm. Đề xuất tiếp theo020, chưa thực hiện.
