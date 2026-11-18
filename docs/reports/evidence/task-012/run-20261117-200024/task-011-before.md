# TASK-011 — Hoàn thiện ba node và nghiệm thu ổn định30 phút

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu
- Cập nhật: 2026-11-17T16:32:01+07:00

## Mô tả và phạm vi

Đã triển khai `node_01`, `node_02`, `node_03` từ một source firmware, ba environment PlatformIO và ba phiên Wokwi VS Code đồng thời; dữ liệu/lệnh riêng qua MQTT → backend/SQLite → dashboard HTML/CSS/JS chạy Live Server. [Đặc tả được giao](evidence/task-011/run-20261117-135233/task-011-accepted.md) và [nhật ký trước khi đóng](evidence/task-011/run-20261117-135233/task-011-working.md) được lưu nguyên byte. TASK-010 vẫn giữ trong [bản lưu](evidence/task-011/run-20261117-135233/task-010-before.md) và hồ sơ lịch sử.

Định danh biên dịch tập trung, client ID/topic/Serial nhất quán; prepare kiểm artifact đúng node/fresh/hash; command generator chọn node và giữ guard cũ. Sửa lỗi raw cảm biến chờ periodic bằng đánh dấu snapshot khi cảm biến đổi, vẫn gộp cập nhật và giữ rate-limit200ms/periodic2s. Giữ Arduino/esp32dev/entry point, pin map, controller/timer/ngưỡng, MQTT v1. Không sửa source backend/dashboard hoặc SRS. Ba diagram dùng cap thực thi mô phỏng4MHz đã ghi rõ trong runbook.

## Tham chiếu SRS

[SRS](../srs.md): FR-06/07/08/09/10/12; mục2.3,6–9, P6/A6, mục12.1–12.2; ca trọng tâm TC-12/13/14/16/17/21–25. Không dùng build/host hoặc nghiệm thu một node làm bằng chứng ba node live.

## Tiêu chí hoàn thành và tiến độ

- [x] **Nhóm1 — Source/config/công cụ:** chung source,3 environment,3 sơ đồ cùng pin map, định danh live đúng;20 Python test,11 lượt host và2 compile-fail đúng kỳ vọng; build cả3 PASS, artifact/source được kiểm hash.
- [x] **Nhóm2 — Tích hợp đúng đích:**3 node cùng chạy MQTT/API/DOM;30 lệnh AUTO/MANUAL/ACK/PWM và cảm biến cách ly, không tác động chéo; MANUAL tự về AUTO sau khoảng60000ms theo clock node.
- [x] **Nhóm3 — Lỗi/phục hồi/latency:** OPEN_LOAD/phục hồi, tắt riêng node02, AUTO khi broker down, reconnect không replay command cũ, restart backend giữ dữ liệu;10 lệnh→ACK và10 mẫu sensor→dashboard/node.30/30 mẫu cảm biến cuối dưới3s thực, max cận trên1272,235ms.
- [x] **Nhóm4 — Ổn định và bàn giao:** một cửa sổ1800s monotonic đồng thời, không reset/dừng collector/mất sequence;5360 raw telemetry khớp SQLite ACCEPTED; hồ sơ/techs/báo cáo/checklist/manifest, kiểm toàn vẹn dữ liệu và cleanup QA hoàn tất.

## Kiểm tra và bằng chứng

[Hồ sơ nghiệm thu](evidence/task-011/run-20261117-135233/README.md) tổng hợp log cuối, artifact manifest, từng ca live, ảnh, phương pháp latency và giới hạn. Cửa sổ cuối **15:36:05–16:06:05+07:00 ngày2026-11-17** có1561/2216/1583 bản tin liên tục từ ba node; boot không đổi, raw recorder không reconnect, backend giữ PID/start ticks, health cuối dropped_events0, SQLite quick_check=ok. [Audit cửa sổ](evidence/task-011/run-20261117-135233/stability-02/wire-audit.json) dùng clock monotonic máy, không cộng uptime mô phỏng.

## Vướng mắc và cách giải quyết

Không còn vướng mắc chặn TASK-011. Đã phát hiện/sửa lỗi telemetry cảm biến chậm với ca red/green, build lại cả3 và chạy nghiệm thu trên firmware cuối. Giữ nguyên các FAIL cũ. Parser QA nhãn100k gây INCOMPLETE sai được audit từ raw đã lưu; không đổi timestamp hoặc loại mẫu chậm hợp lệ.

HTTP/resource probe bị SIGTERM143 sau1346,506s/672 mẫu, nguyên nhân chính xác chưa xác định; log đó vẫn **INCOMPLETE**. Kết quả1800s dựa trên raw MQTT và SQLite độc lập bao phủ toàn bộ cửa sổ đã định trước, backend không đổi PID và health cuối; không tuyên bố HTTP/tài nguyên/dashboard được quan sát liên tục đủ30 phút. stability-01 dừng trước sửa vẫn INCOMPLETE, không cộng thời gian. Chi tiết và các lỗi công cụ khác ở hồ sơ.

## Giới hạn và bước tiếp theo

Đây là nghiệm thu Wokwi trên cấu hình máy/cap mô phỏng đã ghi, DOM sau hai rAF là proxy render. Chưa thực hiện EX-series, so sánh tiết kiệm điện đại diện, báo cáo/video bàn giao cuối hoặc phần cứng thật. Dữ liệu cũ và thay đổi người dùng được bảo toàn; tài nguyên QA đã dừng. Không thực hiện thao tác Git commit/push/merge trong bước đóng hồ sơ này.

[Đề xuất TASK-012](next-task.md) là thực nghiệm và bàn giao cuối; chưa bắt đầu, chỉ triển khai khi được giao. TASK-011 giữ ở đây đến khi bắt đầu task mới.
