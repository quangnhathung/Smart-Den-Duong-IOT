# TASK-012 — Thực nghiệm và bàn giao cuối (đề xuất)

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/0 — phạm vi chi tiết và checklist sẽ chốt khi được giao
- Cập nhật: 2026-11-17T16:32:01+07:00

## Mô tả và phạm vi

Đề xuất bước sau khi TASK-011 hoàn thành4/4: chạy bộ thực nghiệm theo SRS, xuất dữ liệu/độ phủ và phân tích năng lượng đúng giới hạn mô phỏng, tổng hợp báo cáo, runbook và video/demo bàn giao. Đây là đề xuất, không phải công việc đã thực hiện hoặc được tự động bắt đầu.

## Tham chiếu SRS

[SRS](../srs.md) mục9.2–9.3, P7 ở mục10.2, A7 ở mục11.2 và tiêu chí bàn giao mục cuối. Giữ EX-01–07; EX-02–05 lặp3 lần cùng lịch tác động, EX-05 chốt bảng thao tác ba node trước các lượt. Không đặt trước tỷ lệ tiết kiệm, không suy kết quả năng lượng đại diện từ cửa sổ ổn định TASK-011.

## Tiêu chí hoàn thành và tiến độ

Chưa chốt checklist nghiệm thu TASK-012. Dự kiến gồm dữ liệu gốc/CSV/ảnh từng phiên, mã phiên bản và cấu hình; năng lượng/baseline/độ phủ và lý do loại mẫu; kết quả giữa các lượt; tài liệu chạy lại và báo cáo/video phù hợp SRS. Chốt phạm vi, lịch tác động và phương pháp thời gian trước khi chạy; không ghi PASS từ dữ liệu chưa thu.

## Vướng mắc và cách giải quyết

Không có vướng mắc chặn từ TASK-011. Cần thống nhất phạm vi bàn giao thực tế và lịch thực nghiệm khi giao TASK-012; giữ các giới hạn mô phỏng và phần probe HTTP thiếu đã công bố trong [hồ sơ TASK-011](evidence/task-011/run-20261117-135233/README.md).

## Phụ thuộc và điều kiện bắt đầu

- TASK-011 hoàn thành4/4; giữ source/config/artifact đã nghiệm thu và bằng chứng cũ.
- Người dùng giao triển khai TASK-012 và chốt checklist/phạm vi bàn giao.
- Preflight nguồn ba repo, đồng hồ, tài nguyên/cổng QA, lịch tác động và phương pháp thu dữ liệu; không dùng lại DB đã đóng hoặc dừng dịch vụ người dùng.
- Chỉ áp dụng ui-ux-pro-max nếu phát sinh thay đổi giao diện được giao; dashboard tiếp tục HTML/CSS/JS qua VS Code Live Server.
