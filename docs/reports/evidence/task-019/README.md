# TASK-019 — Báo cáo tiểu luận bốn chương, chỉ Word

Hoàn thành 2026-11-18T16:41:28+07:00; 4/4 nhóm nghiệm thu. [QA và manifest](document-qa.json), [kế thừa OOXML](inheritance.json), [bố cục/ảnh/nguồn số liệu](body-manifest.json), [schema](schema-validation.txt).

## Đầu ra

[Word mới 27 trang](../../../../output/task-019/Bao-cao-tieu-luan-Den-duong-thong-minh-Nhom7-v01.docx), gồm bìa và26 trang nội dung. SHA-256 `fb79505d398bb9e449d3f01c76b24c83aeaf2b9d022ace9968dbc2ee5b4662c7`. Chỉ bàn giao DOCX; không xuất PDF, PPTX hoặc bản Markdown của bài tiểu luận.

Lời nói đầu; Chương1 Giới thiệu về IoT (1.1–1.5); Chương2 Giới thiệu phần cứng (2.1–2.8); Chương3 Giới thiệu phần mềm (3.1–3.8); Chương4 Kết quả demo (4.1–4.7); Lời kết; Tài liệu tham khảo. Có mục lục số trang, Heading điều hướng, bảng pin/thuật toán/giao thức/kết quả và6 ảnh/biểu đồ gốc có chú thích nguồn. Nội dung7788 từ theo tách khoảng trắng; đây không phải phép đo chất lượng văn bản.

## Kế thừa và bảo toàn

Nguồn là Word TASK-012 v05, SHA `f59971322dbe7883e5fc6af8e4dfe92899fa61b132305abd482141391007dc11`. Giữ nguyên12 phần tử bìa, sectPr, mọi package part gốc trừ document.xml và document.xml.rels cần thay nội dung/quan hệ ảnh. Styles, theme, settings, header/footer và logo giữ nguyên byte. Trang bìa PNG WPS trùng SHA với bản v05 đã render; sourceDOCX không đổi. Không đổi thông tin trường, nhóm hoặc sinh viên.

Generator [build-essay-report.cjs](../../../../scripts/build-essay-report.cjs) tạo body bằng docx-js9.15.4 đã có; [merge-essay-report.py](../../../../scripts/merge-essay-report.py) ghép vào gói nguồn với rId/media riêng, giữ XML bìa/styles. Runtime và helper WPS riêng của TASK-012/015 được tái sử dụng, không cài thư viện thay thế. Dùng skill docx; không đọc hoặc áp dụng humanize/humanizer/viet-humanize theo yêu cầu người dùng.

Hash30 tệp firmware,26 backend,15 dashboard khớp baseline. Giữ nguyên các bộ tài liệu trước, raw/DB/CSV/ảnh/video. Các tệp dưới output/task-019 là artifact/QA được ignore; hồ sơ task/techs và source generator vẫn trong kho.

## Kiểm tra và kết quả

PASS schema462 paragraph; native WPS27 trang, đã xem toàn bộ trong9 contact sheet không thu nhỏ ảnh gốc. Mục lục trang1–26 khớp footer, bốn chương chính,28 mục con, bảng không tách hàng, ảnh đúng tỷ lệ, không tràn/cắt/trang trắng. WPS đọc read-only, source không đổi; chỉ instance riêng được đóng. PNG nội bộ phục vụ QA, không là định dạng bàn giao.

PASS mọi số mean/min/max của variation.json đối chiếu lại15 dòng repetition-metrics.csv; bảng Word EX02–05 khớp sau làm tròn. Plot source trỏ đúng audit SHA,15 lượt/45 cửa sổ node, action max1778ms. Số latency30 mẫu/cận trên1272,235ms dùng latency-final-audit.json, không chọn tất cả raw trials của firmware cũ;30 command và5360 telemetry/1800s khớp hồ sơ TASK-011. Probe HTTP672 mẫu/1346,506s/exit143 giữ INCOMPLETE trong báo cáo.6 media mới trùng SHA ảnh/biểu đồ gốc. Nguồn lý thuyết ITU/OASIS/Espressif/Wokwi đã đối chiếu, không coi cơ sở lý thuyết là kết quả chạy mới.

## Vướng mắc và cách giải quyết

Không có vướng mắc còn chặn. Các lỗi Qt in sau khi render của WPS RPC là hành vi teardown đã biết; proof xác nhận đã xuất27 trang, giữ source và dừng instance riêng. Không cần thay runtime. Phần cứng thật, diễn tập con người và probe lịch sử chưa hoàn tất không được ghi PASS. Không chạy lại live/build/thực nghiệm vì sản phẩm không đổi.

## Bước tiếp theo

Đề xuất TASK-020 rà soát nội dung nộp và diễn tập với hai thành viên, kế thừa đề xuất018 chưa thực hiện. Chưa thực hiện đề xuất. [Task cũ](task.md-before.md), [đề xuất cũ](next-task.md-before.md) giữ nguyên. Lịch sử report/checklist được prepend, mọi byte cũ bảo toàn trong snapshot và phần đuôi.
