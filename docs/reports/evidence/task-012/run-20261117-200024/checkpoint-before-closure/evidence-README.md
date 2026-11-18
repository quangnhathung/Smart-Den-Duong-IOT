# Hồ sơ TASK-012 — thực nghiệm và bàn giao

**Đang thực hiện; chưa phải hồ sơ nghiệm thu cuối.** Trạng thái task xem [task.md](../../../task.md). Cập nhật mốc 2026-11-18T10:47:15+07:00: 7/15 lượt chính đã PASS và được đối chiếu độc lập; còn EX04/R1–R3, EX05/R1–R3, EX06/R1 và EX07/R1. Không dùng tiến độ này như bằng chứng hoàn thành toàn bộ TASK-012.

## Nguồn và cấu hình

- [Baseline ba repo](baseline.json): source, Git và hash đầu vào; firmware/artifact kế thừa TASK-011.
- [Trạng thái TASK-011 trước khi bắt đầu](task-011-before.md); [trạng thái TASK-013 trước khi tiếp tục](task-013-before-resume.md). Giữ lịch sử cài skill riêng.
- QA root trên máy: `output/task-012/run-20261117-200024/`; dữ liệu lớn được Git ignore, không phải dữ liệu đã bị xóa hoặc đã nằm trong Git.
- Ba Wokwi độc lập cap4MHz; broker local1883, API8001 một worker/SQLite riêng, dashboard HTML/CSS/JS qua engine VS Code Live Server5500. Không sửa source sản phẩm để khớp cổng QA.
- Thời lượng và lịch tác động dùng uptime riêng mỗi node; độ phủ dùng UTC nhận. Công suất/điện năng là mô hình, người/xe là kịch bản quy ước.

## Dữ liệu và đối chiếu

Trong QA root, `attempts/` giữ cấu hình, result, lịch tác động, cửa sổ SQLite từng node, API, CSV, phép tính độc lập và snapshot công cụ. Raw MQTT/Serial/probe/UI/dashboard được ghi riêng theo dòng; không sửa các record lịch sử. `campaign-status.json` ghi trạng thái đang chạy; chỉ khi đủ điều kiện mới có `campaign-completed.json` và audit cuối.

[Tóm tắt audit 7 lượt](recovery-20261118-091409/accepted-07-summary.json) có danh sách còn thiếu và không có lỗi đối chiếu; trạng thái tổng vẫn INCOMPLETE vì chưa đủ 15 lượt. EX03/R3 đủ60 tác động PIR, trễ lớn nhất714ms mô phỏng, giới hạn2000ms. Audit đầy đủ tại QA root `analysis-accepted-07.json`; các snapshot cũ được giữ nguyên.

PILOT-r01-a04 PASS90s/node nhưng nằm ngoài dữ liệu chính. Giữ ba pilot INCOMPLETE, EX02/R1 attempt01 FAIL vì PIR/khoảng cách ngoài recipe chưa xác định nguyên nhân, và EX02/R3 attempt01–03 INCOMPLETE do ngắt Serial/chuẩn bị viewport/readiness. Chạy lại trọn lượt bị ảnh hưởng; không ghép dữ liệu cũ.

## Phục hồi và runtime

- [Mốc trước phục hồi](recovery-20261118-091409/before-resume.json), [kiểm bảo toàn dữ liệu](recovery-20261118-091409/preservation-after-resume.json): giữ nguyên43.719 telemetry cũ và prefix5 stream log.
- Collector/result từ lần tiếp tục18/11 dùng host_boot_id để tách clock monotonic qua reboot; dữ liệu cũ chưa có tag giữ cohort riêng. Không đổi timestamp lịch sử.
- [Helper ban đầu và hash](recovery-20261118-091409/automation-as-run/); [revision02](recovery-20261118-091409/automation-revision02/manifest.json) bổ sung cô lập cửa sổ khi cold-start, chưa chạy diễn tập.
- [Quay thử runtime video](recovery-20261118-091409/video-runtime-smoke/proof.json): 3 giây thực,1920×1080/90 frame, decode và mở trong Chrome thành công. Giữ hai lần thử lỗi trước đó. Đây chưa phải video demo6–8 phút hoặc kiểm phát đầy đủ.

## Tài liệu và phần chưa nghiệm thu

Word/PPTX chỉnh sửa được ở `output/task-012/deliverables/`; v03 là bản đang hoàn thiện với dữ liệu4/15 tại thời điểm tạo. Word23 trang và PPTX12 slide đã render WPS/kiểm cấu trúc; bản cuối còn phải cập nhật đủ số liệu và kiểm trực quan lại. Theo yêu cầu người dùng, PDF do người dùng tự xuất bằng WPS.

Video chính, diễn tập cold-start, backup/manifest/toàn vẹn archive và cleanup cuối chưa nghiệm thu. Pipeline chờ đủ15 lượt; gặp lỗi thì dừng để điều tra. Không tự đánh dấu khả năng hai thành viên vận hành/giải thích; cần diễn tập trực tiếp.

Hướng dẫn tái lập và giới hạn xem [experiments.md](../../../../techs/experiments.md) và [demo-runbook.md](../../../../demo-runbook.md). Đường dẫn/PID trong QA root là tham chiếu của lượt đã chạy trên máy này; không chạy mù helper trên máy hoặc PID khác.
