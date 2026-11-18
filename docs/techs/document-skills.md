# Skill tạo tài liệu cho Codex cá nhân

## Tham chiếu SRS

Hỗ trợ công cụ cho bộ bàn giao ở SRS mục15. Cài skill không chứng minh báo cáo hoặc slide đồ án đã được tạo hay nghiệm thu.

## Triển khai và cấu hình

TASK-013 cài ba skill từ https://github.com/anthropics/skills, commit `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`, bằng script `install-skill-from-github.py` của skill-installer. Không sửa nội dung upstream.

| Skill | Nguồn trong kho | Đích cá nhân | Số tệp |
| --- | --- | --- | --- |
| pptx | skills/pptx | /home/quangnhathung/.codex/skills/pptx | 58 |
| pdf | skills/pdf | /home/quangnhathung/.codex/skills/pdf | 12 |
| docx | skills/docx | /home/quangnhathung/.codex/skills/docx | 61 |

Giữ nguyên plugin presentations/documents/pdf của OpenAI. Khi cần chọn bộ Anthropic, yêu cầu rõ tên skill và đường dẫn SKILL.md tương ứng; không dựa vào tên “pdf” đơn lẻ để xác định nguồn. Skill có thể được nhận ở lượt tiếp theo; mở phiên Codex mới nếu danh sách chưa cập nhật.

Ví dụ kiểm tra chỉ đọc ở lượt tiếp theo: “Liệt kê ba skill pptx, pdf, docx tại ~/.codex/skills và nguồn của chúng. Không tạo tài liệu hoặc cài phụ thuộc.”

## Kiểm tra

PASS đối chiếu danh sách và Git blob hash của toàn bộ131 tệp với tree từ GitHub tại commit đã cố định; có frontmatter name/description, LICENSE.txt và các liên kết Markdown nội bộ trong SKILL.md đều tồn tại. [Manifest SHA-256 từng tệp](../reports/evidence/task-013/manifest.json).

Nhận diện thực tế ở lượt/phiên mới: chưa chạy. Tạo DOCX/PPTX/PDF, render và kiểm trực quan: chưa chạy theo phạm vi đã chốt. Không cần build firmware cho thay đổi công cụ này.

## Giới hạn và vấn đề còn lại

Chỉ cài skill, không cài runtime. Kiểm tra trước task cho thấy có Python/Node/Poppler nhưng không tìm thấy LibreOffice/Pandoc trong PATH; Python được kiểm tra chưa có pypdf/pdfplumber/reportlab/Pillow/lxml/defusedxml. Chưa kiểm tra toàn bộ phụ thuộc Node. Các giả định “preinstalled” trong skill Anthropic không phải bằng chứng môi trường máy này đã đủ thư viện.

Nếu cần tạo/xuất tài liệu, phải có yêu cầu bổ sung runtime, kiểm tra thư viện và render mẫu tiếng Việt trước khi dùng cho bộ bàn giao. Không thay cấu hình Claude Code/OpenCode; không tự nâng toolchain hoặc thực hiện TASK-012.

## Tài liệu vận hành TASK-015

Đã tạo [hướng dẫn toàn hệ thống](../project-guide.md), Word chỉnh sửa được34 trang. Script scripts/build-project-guide.cjs đọc Markdown, chuyển heading/list/table/code/hyperlink/ảnh thành thành phần Word, giữ A4, mục lục định hướng và số trang. Tạo tên output mới, không ghi đè bản đã giao.

```bash
node scripts/build-project-guide.cjs /path/to/node_modules/docx /path/to/new-guide.docx
```

Dùng runtime docx9.15.4 riêng đã có của TASK-012; không cần dependency tài liệu để chạy firmware/backend/dashboard. Native WPS Writer Page.SaveAsPNG xuất34/34 trang, đã xem từng trang; schema và695 dòng nội dung đối chiếu Markdown→DOCX PASS. Tỷ lệ ảnh dashboard16:9 giữ nguyên; [QA](../reports/evidence/task-015/document-qa.json). Instance WPS QA đã đóng, source không bị sửa. Không xuất PDF theo lựa chọn người dùng.

Kiểm hướng dẫn dùng SQLite tạm: init hai lần giữ3 ID và fixture phiên đã có, backup API/quick_check/đọc lại và guard từ chối đích tồn tại PASS. Linux Bash/Python/JSON được kiểm cú pháp; PowerShell/Windows và stack live không được chạy lại trong task tài liệu. Các mốc TASK-013 phía trên vẫn là lịch sử cài skill, không sửa lại thành kết quả tạo tài liệu.
