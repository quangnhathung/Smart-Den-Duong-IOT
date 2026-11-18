# TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Hoàn thành
- Tiến độ: 5/5 nhóm nghiệm thu
- Cập nhật: 2026-11-18T15:25:24+07:00

## Mô tả và phạm vi

Thực hiện kế hoạch đã giao:15 lượt thực nghiệm ba node, phân tích độc lập, báo cáo Word sáu chương,12 slide, video demo6–8 phút, runbook và backup toàn vẹn. Giữ firmware, backend/dashboard, pin map, hợp đồng MQTT/API/schema và toolchain. Dashboard HTML/CSS/JS chạy qua Live Server. Không commit/push/merge hoặc triển khai cloud.

SRS mục9.1–9.3,12,13,15; P7/A7. Thời lượng/PIR theo uptime riêng mỗi node, coverage theo UTC nhận. Công suất/điện năng là mô hình; người/xe là kịch bản quy ước. PDF do người dùng tự xuất bằng WPS theo yêu cầu17/11. Lịch sử triển khai trước khi chốt được giữ tại [snapshot](evidence/task-012/run-20261117-200024/checkpoint-before-closure/docs__reports__task.md).

## Tiêu chí hoàn thành và tiến độ

- [x] Nhóm1 — Baseline/phương pháp, công cụ và pilot90s/node;34 Python test PASS.
- [x] Nhóm2 — 15/15 lượt chính PASS, giữ mọi attempt lỗi và chạy lại trọn lượt liên quan.
- [x] Nhóm3 — 45 cửa sổ node–lượt, raw MQTT/SQLite/API/CSV và phép tính độc lập khớp trong1e-9Wh; quick_check=ok.
- [x] Nhóm4 — DOCX v05 sáu chương/23 trang, PPTX v05 12 slide16:9 kiểm schema và toàn bộ ảnh WPS; MP4 khoảng7 phút1080p, phụ đề Việt, full decode/phát Chrome và16 cảnh kiểm trực quan PASS.
- [x] Nhóm5 — Runbook, cold-start ba node/lệnh APPLIED, giữ hash137.797 telemetry cũ, cleanup hiện hành PASS, backup SHA256/đọc lại archive PASS, cập nhật hồ sơ/lịch sử.

## Kết quả và bằng chứng

[Hồ sơ nghiệm thu](evidence/task-012/run-20261117-200024/README.md), [audit](evidence/task-012/run-20261117-200024/analysis-final.json), [Office QA](evidence/task-012/run-20261117-200024/office-final-qa.json), [video QA](evidence/task-012/run-20261117-200024/video-final-qa.json), [cold-start](evidence/task-012/run-20261117-200024/cold-start.json), [cleanup](evidence/task-012/run-20261117-200024/cleanup-final.json), [backup đã kiểm](evidence/task-012/run-20261117-200024/backup-first-verification.json). Tệp chính ở output/task-012/deliverables/; raw/SQLite/ảnh/video và backup được giữ ngoài Git, không phải dữ liệu đã có trong commit.

Công suất AUTO trung bình EX02/03/04/05 khoảng6/8,160/9,600/6,613W. EX04/R3 coverage có node99,004%; EX07 khoảng79,073–79,836% do outage chủ động. Trễ tác động lớn nhất1778ms trong giới hạn2000ms. Không bỏ mẫu/lượt hợp lệ hoặc đặt tỷ lệ tiết kiệm mục tiêu.

## Vướng mắc và cách giải quyết

Không còn vướng mắc chặn phạm vi TASK-012. Đã giữ FAIL/INCOMPLETE: PIR/khoảng cách ngoài recipe chưa xác định nguyên nhân ở EX02/R1; mất Serial/viewport/readiness ở EX02/R3; EX05/R1 trễ2257ms. Sửa riêng công cụ QA, chuẩn bị UI trước10s không đổi lịch vật lý; chạy lại trọn lượt, audit cuối PASS. Không sửa source sản phẩm; [đối chiếu baseline](evidence/task-012/run-20261117-200024/product-preserved-final.json).

Video01 lỗi helper đọc status thay result, video02 có vùng xám dù decode được; các setup03–05 lỗi viewport/node02 Pause. Đã sửa helper/viewport, Resume thật cùng boot, dùng Chrome headless riêng và quay lại toàn bộ; bản cuối qua kiểm trực quan. Giữ nguyên mọi lần lỗi và source as-run. Word/PPTX v05 tạo mới, giữ bản nháp và đề cương. PDF tự xuất theo lựa chọn người dùng.

## Giới hạn và phụ thuộc

Chưa kiểm mạch thật hoặc xác nhận hai thành viên tự chạy/giải thích độc lập; không ghi PASS thay con người. Cold-start đã chạy trên máy này, không thay thử trên máy khác. Đề xuất TASK-014 diễn tập hai thành viên tại next-task.md, chưa thực hiện. Không có phụ thuộc còn chặn bộ bàn giao đã chốt.
