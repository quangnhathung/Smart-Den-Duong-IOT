# Hồ sơ TASK-012 — thực nghiệm và bàn giao

**Hoàn thành5/5 nhóm nghiệm thu.** Đủ15/15 lượt chính và audit độc lập PASS. Word/PPTX v05, video chính, cold-start, cleanup hiện hành và backup đã kiểm xong. [Trạng thái task](../../../task.md); bản mô tả trước khi chốt giữ tại [checkpoint](checkpoint-before-closure/evidence-README.md).

## Nguồn và cấu hình

- [Baseline ba repo](baseline.json), [đối chiếu nguồn sản phẩm cuối](product-preserved-final.json):31 tệp firmware,26 backend,15 dashboard khớp. Không sửa thuật toán/pin map/schema/toolchain hoặc source backend/dashboard.
- [TASK-011 trước khi bắt đầu](task-011-before.md), [TASK-013 trước khi tiếp tục](task-013-before-resume.md). Giữ lịch sử cài skill riêng.
- QA root: `output/task-012/run-20261117-200024/`; deliverables: `output/task-012/deliverables/`. Raw/SQLite/ảnh/video/backup được Git ignore; cần giữ hoặc chuyển gói backup, không dựa vào commit để khôi phục dữ liệu lớn.
- Ba Wokwi độc lập cap4MHz, artifact kế thừa TASK-011; Mosquitto native2.1.2 local1883, API8001 một worker/SQLite riêng, dashboard HTML/CSS/JS qua engine VS Code Live Server5500. Docker sản phẩm giữ nguyên.
- Thời lượng/PIR theo uptime từng node; độ phủ theo UTC nhận. Công suất/điện năng là mô hình; người/xe là kịch bản quy ước.

## Dữ liệu chính và kiểm chứng

[Audit cuối](analysis-final.json): PASS15 lượt/45 cửa sổ node–lượt, errors/missing rỗng, SQLite quick_check=ok. Đối chiếu raw MQTT→SQLite→API/CSV và phép tính năng lượng độc lập trong1e-9Wh. [Campaign summary](campaign-summary.json), [campaign completed](campaign-completed.json), [34 Python test](python-tools-final-checks.log).

| Kịch bản | Lượt hợp lệ |
|---|---|
| EX01 — DAY | R1/a01 |
| EX02 — NIGHT yên tĩnh | R1/a02, R2/a01, R3/a04 |
| EX03 — người150cm | R1/a01, R2/a01, R3/a01 |
| EX04 — xe50cm | R1/a01, R2/a01, R3/a01 |
| EX05 — ba pha hỗn hợp | R1/a02, R2/a01, R3/a01 |
| EX06 — tải0/phục hồi | R1/a01 |
| EX07 — broker outage/AUTO offline | R1/a01 |

EX01/06/07 dài300s/node; EX02–04 dài600s/node; EX05 dài900s/node. Không tính phần node nhanh chờ node chậm. Tác động vật lý trễ lớn nhất1778ms≤2000ms. Công suất AUTO trung bình EX02/03/04/05 khoảng6/8,160/9,600/6,613W; EX05 baseline trung bình18,671W vì có pha DAY. EX04/R3 coverage có node99,004%; EX07 khoảng79,073–79,836% do mất broker chủ động. Không ghi mọi lượt100% hoặc suy tiết kiệm tiền điện thực tế.

QA root `attempts/` giữ config/result/cửa sổ SQL/API/CSV/lịch tác động/snapshot công cụ từng attempt. Raw MQTT/Serial/probe/UI/dashboard lưu riêng JSONL. API/UI nguyên phiên có thể khác bảng Word do cửa sổ chung; muốn đối chiếu phải dùng cùng node/from/to/experiment_id và biên năng lượng. Số1h trên ảnh dashboard không được dùng làm số liệu riêng một lượt.

## Lượt lỗi và phục hồi

PILOT-r01-a04 PASS90s/node ngoài dữ liệu chính; ba pilot trước giữ INCOMPLETE. EX02/R1 a01 FAIL do PIR/khoảng cách ngoài recipe, nguyên nhân chưa xác định; EX02/R3 a01–03 INCOMPLETE vì mất Serial/viewport/readiness; EX05/R1 a01 INCOMPLETE vì đổi pha trễ2257ms. Chạy lại trọn lượt, không ghép dữ liệu hoặc bỏ lượt hợp lệ.

- [Bảo toàn dữ liệu qua phục hồi](recovery-20261118-091409/preservation-after-resume.json):43.719 telemetry cũ và prefix5 stream không đổi. Collector/result dùng host_boot_id để tách clock monotonic qua reboot; dữ liệu cũ chưa có tag giữ cohort riêng.
- [EX05 timing](recovery-20261118-091409/ex05-timing/physical-schedule-preserved.json): chuẩn bị UI trước10s thay5s, chỉ tác động cảm biến ở mốc300/600; lịch vật lý/giới hạn2s và10 cấu hình đã đạt không đổi.18 lần diễn tập ngoài cửa sổ đo PASS, cận lớn nhất1475ms; sau đó EX05/R1 a02 và R2/R3 PASS.
- [Automation ban đầu](recovery-20261118-091409/automation-as-run/manifest.json), [revision02](recovery-20261118-091409/automation-revision02/manifest.json), [revision03](recovery-20261118-091409/handover-revision03/manifest.json) giữ source as-run và sự cố helper status/result.
- [Video revision04](recovery-20261118-091409/video-capture-revision04/manifest.json): video02 decode được nhưng vùng xám đã có trong WebM; giữ bản lỗi. [Quay thử headless sau tải CSV](recovery-20261118-091409/video-capture-revision04/headless-scroll-download-pass.json) PASS toàn khung, byte CSV khớp.
- [Video revision05](recovery-20261118-091409/video-capture-revision05/manifest.json): node02 paused, xác nhận nút Resume và chạy tiếp cùng boot; cả3 ONLINE/FRESH/can_command. Click trúng toolbar là suy luận, không khẳng định đã quan sát trực tiếp.
- [Video revision06](recovery-20261118-091409/video-capture-revision06/manifest.json): video06 bị409 do click sát biên telemetry3s; helper chờ dữ liệu mới ngay trước click, giữ API guard và không retry POST. Cleanup xác minh broker khởi động lại bằng PID/start ticks/exact argv/process group khi metadata cũ chưa có host_boot_id.

## Tài liệu, video và cold-start

[Office QA cuối](office-final-qa.json): Word v05 sáu chương/23 trang và PPTX v05 12 slide16:9 qua schema, native WPS render và kiểm trực quan mọi trang/slide. Source SHA giữ nguyên; bản nháp, lỗi layout cũ và đề cương được giữ. Tệp chính:

- `Bao-cao-Den-duong-thong-minh-Nhom7-v05.docx`
- `Bao-ve-Den-duong-thong-minh-Nhom7-v05.pptx`

[Cold-start](cold-start.json) PASS14:38+07:00 ngày18/11: dừng đúng9 dịch vụ, khởi động ba boot mới ONLINE/FRESH/AUTO, health OK/dropped_events0, lệnh AUTO APPLIED.137.797 telemetry có sẵn trước/sau cùng SHA, quick_check=ok, không PENDING/phiên mở. Sau đó mở riêng tài nguyên QA để hoàn thiện video; [cleanup cuối](cleanup-final.json) PASS, các cổng QA đóng, chỉ dừng đúng dịch vụ sở hữu.

[Video QA cuối](video-final-qa.json) PASS: MP4 khoảng7 phút,1920×1080/tỷ lệ16:9,30fps, phụ đề Việt, không audio; full decode/phát Chrome và16 cảnh trực quan đạt. Tệp Demo-Den-duong-thong-minh-Nhom7-v01.mp4 cùng SRT/ASS ở deliverables. [Bảo toàn telemetry đến cuối](history-preserved-final.json) PASS. [Backup đầu đã kiểm](backup-first-verification.json) lưu nguồn ba repo, SQLite/raw/mọi attempt/config/artifact/deliverables; đọc lại từng member với SHA256 manifest. Snapshot cuối riêng được tạo sau đóng hồ sơ để chứa tài liệu hoàn thành; proof bên ngoài archive tránh tự tham chiếu. [Bảo toàn lịch sử](history-prepend-proof.json) chứng minh nguyên byte report/checklist cũ. Không coi video ngắn kiểm runtime hoặc decode đơn thuần là nghiệm thu trực quan.

## Giới hạn và tái lập

PDF do người dùng tự xuất WPS. Chưa kiểm mạch thật hoặc xác nhận hai thành viên tự vận hành/giải thích; đề xuất diễn tập riêng, không tự ghi PASS. Cold-start đã chạy trên máy này, không thay thử máy khác.

[Phương pháp](../../../../techs/experiments.md), [runbook](../../../../demo-runbook.md). Helper/PID/đường dẫn trong QA root là tham chiếu as-run, không chạy mù trên máy hoặc PID khác. Backup loại profile/license/credential/cache/venv/node_modules, giữ lockfile/runtime provenance. Không commit/push/merge/cloud trong task.
