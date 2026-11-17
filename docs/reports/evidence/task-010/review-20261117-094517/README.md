# TASK-010 — Rà soát tiến độ và flow report sau pull

- Kiểm tra: 2026-11-17T09:45:17+07:00, Asia/Ho_Chi_Minh; máy Linux hiện tại.
- Trạng thái TASK-010: Đang thực hiện, **2/4 nhóm nghiệm thu live**. Lượt rà soát tài liệu hoàn tất; không thực hiện thêm ca live.
- Nguồn chốt: [final-status.json](../run-20261116-195307/final-status.json); [bản tổng hợp khi bàn giao PR](../publication-status.md). Các số liệu live là kết quả đã thu trên máy Windows ngày 16/11/2026, không phải phép đo mới hôm nay.

## Tiến độ có bằng chứng

| Nhóm | Trạng thái | Kết quả/phần còn thiếu |
|---|---|---|
| 1. Tích hợp một node | PASS | Wokwi/MQTT/backend/SQLite/dashboard đã có bằng chứng và xác nhận người vận hành |
| 2. Điều khiển, độ tin cậy | PENDING | MANUAL/ACK, reject wire, guard, TIMEOUT/ACK muộn qua proxy đã PASS; còn UI trạng thái cuối, broker outage/reconnect/no-replay/AUTO offline |
| 3. Dữ liệu, restart, phiên/CSV/gap | PASS | Bảo toàn dữ liệu đã lưu, CSV và discontinuity đã kiểm; không mở rộng kết luận sang lệnh chờ/phiên đang mở qua restart |
| 4. Latency | PENDING | Command → ACK đủ 10 lượt; sensor → dashboard 0/10 mẫu đủ điều kiện sau 5 lượt thử |

Command → ACK có median **686,217 ms**, max **1002,001 ms**, đối chiếu [số liệu gốc](../run-20261116-180648/command-latency-command-latency.json). Không thay bằng latency cảm biến → dashboard. Năm lượt sensor INCOMPLETE vì thiếu mốc/trang bị ẩn/mẫu cũ trước marker hoặc điều kiện đo không ổn định; lượt 6–10 chưa chạy. Không suy ra chỉ cần thêm năm thao tác để hoàn thành.

P0–P5 đã có các thành phần triển khai; kết quả P2 người dùng xác nhận giữ nguyên. Ba node đồng thời, stability30phút, EX-series và báo cáo/slide/video/bàn giao cuối chưa hoàn tất. Không suy phần trăm nghiệm thu toàn dự án từ số nhóm của TASK-010 hoặc giờ công dự kiến trong SRS.

## Kiểm tra mới tại máy này

- Firmware main `7e8f5c4` nhận PR #3. Backend main `2e6a15f`, dashboard main `6cb402b`; cả ba repo sạch trước lượt cập nhật tài liệu.
- Bốn manifest của các lượt 180648/184903/190549/193157: lần lượt **31/24/24/33 tệp** khớp SHA256, tổng **112/112**, không thiếu hoặc sai hash.
- **70/70 JSON** bằng chứng TASK-010 đọc hợp lệ; kiểm theo byte/BOM, không ghi lại file nguồn. Kết quả chi tiết trong [review.json](review.json).
- Bảo toàn report cũ từng byte ở phần đuôi, checklist cũ và toàn bộ bằng chứng trước lượt này; kiểm liên kết và diff. Kết quả cuối trong [verification.json](verification.json).

Không chạy lại pytest/Node/build/Wokwi hoặc gửi command, mở DB/API/MQTT, restart/dừng dịch vụ. Các kết quả kiểm tra firmware/backend/dashboard trước đó được trích dẫn theo thời điểm cũ, không ghi thành PASS mới.

## Khác biệt môi trường và tài liệu

Dashboard local dùng API8000, chưa có trang `tests/task010-live-latency.html`; bản Windows đã kiểm dùng API8001/Live Server5500 và bộ ghi riêng. Cần đối chiếu repo/config trước khi tiếp tục ca live, không tự đổi cổng hoặc kết luận production lỗi chỉ từ khác biệt này. HealthOK trong final-status.json là snapshot cũ, không chứng minh dịch vụ đang chạy tại máy này hôm nay.

Một số ghi chú từ PowerShell mất dấu. Giữ nguyên tài liệu và raw log cũ, thêm bản tổng hợp tiếng Việt có dấu để đọc cùng JSON; không đoán phục hồi dữ liệu đã mất hoặc thay kết luận INCOMPLETE.

## Flow report và bước tiếp theo

Cập nhật [task hiện tại](../../../task.md), [báo cáo](../../../report.md), [checklist](../../../checklists.md), [task tiếp theo](../../../next-task.md), [hướng dẫn kiểm tra](../../../../techs/testing.md) và [dashboard](../../../../techs/dashboard.md). SRS10.2/12 được dùng làm tham chiếu, không sửa nghiệp vụ/API/schema/firmware.

TASK-011 tiếp tục chờ đặc tả chính thức. Khi được giao tiếp TASK-010, chuẩn bị phương pháp đo sensor/render ổn định và phương án cô lập kết nối node; giữ các PASS cũ, không bắt người dùng chạy lại. Lượt này không commit/push/merge hoặc sửa repo backend/dashboard.
