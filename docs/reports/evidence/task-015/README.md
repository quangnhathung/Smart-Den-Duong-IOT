# TASK-015 Hướng dẫn cài đặt và vận hành toàn dự án

Hoàn thành4/4 nhóm nghiệm thu ngày18/11/2026. Tạo tài liệu theo yêu cầu mới của người dùng; giữ nguyên bộ bàn giao TASK-012 và source sản phẩm.

## Đầu ra

- [Nguồn Markdown](../../../project-guide.md):30 phần chính, mục lục và hai phụ lục; setup Linux/Windows, init/run và thao tác toàn stack.
- Word: output/task-015/Huong-dan-cai-dat-va-van-hanh-toan-du-an-Nhom7-v01.docx,34 trang thực trên WPS. Cùng thư mục có Markdown đồng nội dung để sao chép lệnh.
- [Generator](../../../../scripts/build-project-guide.cjs), [ảnh QA dùng trong sách](../../../assets/project-guide/overview.png). Output/ảnh render/SQLite tạm được Git ignore; DOCX nhúng ảnh, không phụ thuộc ảnh bên ngoài khi mở.

## Kiểm tra và bằng chứng

- [Document QA](document-qa.json): schema PASS,34/34 trang PNG được xem trực quan; bảng/list/heading/page number/ảnh16:9 không tràn/cắt.695 dòng nội dung Markdown→DOCX khớp,34 heading chính.
- [Render proof](render-proof.json): native WPS Writer Page.SaveAsPNG, source không đổi, chỉ instance QA được mở và đóng; không tác động tài liệu người dùng. [Build và SHA](build.json), [schema log](schema-check.log).
- [Kiểm lệnh và DB tạm](command-checks.json): CLI plan --all đủ15 lượt, prepare --help; Bash/Python/JSON cú pháp hợp lệ; init_db hai lần giữ3 ID/fixture, backup API/quick_check/đọc lại và guard từ chối ghi đè PASS. Fixture có tên TASK015_INIT_FIXTURE, không được dùng làm dữ liệu live hoặc kết quả TASK-012.
- [Baseline source sản phẩm](product-baseline.json):28 tệp firmware,14 backend,8 dashboard giữ hash. Không đổi pin map/schema/thuật toán/dependency sản phẩm. [Bảo toàn lịch sử](history-preserved.json): report/checklist cũ còn nguyên byte ở đuôi.
- [Task trước](task.md-before.md) và [đề xuất TASK-014 trước](next-task.md-before.md) được giữ. Sau yêu cầu tài liệu TASK-015, mã đề xuất kế tiếp là TASK-016, kế thừa nội dung diễn tập hai thành viên chưa chạy.

## Nguồn đối chiếu

Các tệp source/config hiện hành của ba repo và SRS/techs/runbook; tài liệu chính thức PlatformIO, Docker Compose, Wokwi getting-started/project-config đã đối chiếu ngày18/11/2026. Các URL nguồn được gắn trong sách. Các phần lịch sử P0/chưa triển khai không được dùng thay source hiện hành.

## Giới hạn và vướng mắc

Không chạy lại Docker/Wokwi/build firmware/15 lượt thực nghiệm hoặc cài và xác nhận toàn stack trên Windows trong task tài liệu. Kiểm mới là cú pháp/CLI/SQLite tạm, đối chiếu source và chất lượng DOCX; bằng chứng live TASK-011/012 được dẫn nguồn riêng. Công cụ live QA phụ thuộc Linux/runtime/cổng/PID của đợt cụ thể, không phải bộ cài đa nền tảng một lệnh.

Một lệnh kiểm ban đầu dùng Python hệ thống thiếu lxml; chuyển runtime Office QA sẵn có, không cài vào venv sản phẩm. Không còn vướng mắc chặn bàn giao. PDF do người dùng tự xuất WPS. Không commit/push/cloud. Gói backup TASK-012 r02 được giữ nguyên; tài liệu TASK-015 được bàn giao riêng, không khẳng định gói cũ đã chứa tài liệu mới.
