# TASK-013 — Cài skill tài liệu chính thức cho Codex cá nhân

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục
- Cập nhật: 2026-11-17T21:04:27+07:00

## Mô tả và phạm vi

Cài pptx, pdf, docx từ anthropics/skills vào ~/.codex/skills, cố định cùng commit. Chỉ cài skill; không cài runtime hay tạo tài liệu mẫu, không thay plugin OpenAI, không chạy TASK-012. [Trạng thái TASK-012 được bảo toàn](evidence/task-013/task-012-before.md).

## Tham chiếu SRS

Task hỗ trợ công cụ bàn giao ở SRS mục15; không triển khai FR hoặc nghiệm thu tài liệu đồ án.

## Tiêu chí hoàn thành và tiến độ

- [x] Cài đủ ba skill cùng commit, không ghi đè skill có sẵn.
- [x] Kiểm tra frontmatter/tệp tham chiếu và toàn vẹn theo nguồn, ghi manifest.
- [x] Cập nhật tài liệu, báo cáo, checklist, bước tiếp theo; công bố giới hạn kiểm tra nhận diện ở phiên mới.

## Vướng mắc và cách giải quyết

Không có vướng mắc với phạm vi cài tệp. PASS đối chiếu 131 tệp với Git blob ở commit cố định; xem [manifest](evidence/task-013/manifest.json). Chưa kiểm tra nhận diện ở lượt/phiên Codex mới; chưa chạy tạo/render tài liệu do người dùng chỉ yêu cầu cài skill.

## Phụ thuộc và điều kiện bắt đầu

Người dùng đã yêu cầu triển khai kế hoạch. Cần tải mạng và quyền ghi thư mục Codex cá nhân theo sandbox.
