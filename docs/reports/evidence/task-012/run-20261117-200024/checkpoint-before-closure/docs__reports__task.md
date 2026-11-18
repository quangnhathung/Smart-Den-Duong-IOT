# TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Đang thực hiện
- Tiến độ: 3/5 nhóm nghiệm thu
- Cập nhật: 2026-11-18T15:03:00+07:00

## Mô tả và phạm vi

Người dùng đã giao triển khai kế hoạch TASK-012: thực nghiệm đầy đủ, phân tích số liệu và bàn giao DOCX, PPTX, video MP4, runbook và backup. Kế thừa bìa/thông tin trường, nhóm, thành viên từ đề cương Word, tạo tệp mới và giữ nguyên đề cương. TASK-011 hoàn thành4/4 được lưu tại [bản trước](evidence/task-012/run-20261117-200024/task-011-before.md).

Giữ firmware ba node, MQTT/API/schema, controller/pin map/toolchain và dashboard HTML/CSS/JS qua Live Server. Chỉ sửa lỗi trực tiếp cản trở thực nghiệm có tái hiện/hồi quy. Không tự commit/push/merge hoặc triển khai cloud. Dữ liệu và output lớn tại output/task-012/ được ignore; bằng chứng gọn ở docs/reports/evidence/task-012/.

## Tham chiếu SRS

[SRS](../srs.md) mục9.1–9.3,12,15; P7/A7. Mốc phiên5/10/15 phút và PIR mỗi30s dùng uptime riêng mỗi node theo lựa chọn người dùng. UTC/monotonic máy ghi riêng; năng lượng theo uptime, độ phủ theo thời gian nhận. Không diễn giải mô hình điện năng như đo phần cứng.

## Phương pháp đã chốt

15 lượt chính: EX01 một lượt5 phút; EX02/03/04 mỗi kịch bản3 lượt10 phút; EX05 ba lượt15 phút; EX06/07 mỗi kịch bản1 lượt5 phút. Cả3 node hoạt động; phân tích cửa sổ riêng, không tính thêm thời gian node nhanh. PIR ở giây15 rồi mỗi30s trong pha có chuyển động. EX03 distance150cm, EX04 distance50cm. EX01 DAY đổi chuyển động; EX02 NIGHT yên tĩnh. EX05 ba pha300s: (DAY, NIGHT yên tĩnh, NIGHT người), (TWILIGHT, NIGHT người, NIGHT xe), (NIGHT xe, DAY, NIGHT yên tĩnh). EX06 node02 tải0 giây60, phục hồi180. EX07 broker down60/recover120 theo uptime node02, kiểm AUTO offline bằng Serial và LDR node01. Pilot ngoài dữ liệu chính; không dồn thao tác khi trễ quá2s mô phỏng.

Công cụ preflight/run/summarize/verify điều khiển Wokwi UI, thu raw MQTT/Serial/API/health và heartbeat độc lập. Giữ FAIL/INCOMPLETE, chạy lại trọn lượt lỗi; không chọn bỏ kết quả hợp lệ. API/CSV/phép tính độc lập phải khớp trong1e-9Wh; loại đúng MANUAL/fault/low-load/offline/gap/boot/session và công bố độ phủ. Không đặt tỷ lệ tiết kiệm mục tiêu.

## Tiêu chí hoàn thành và tiến độ

- [x] Nhóm1 — Baseline, công cụ/phương pháp và pilot được kiểm chứng.
- [x] Nhóm2 — Đủ15 lượt chính hợp lệ, raw/CSV/ảnh/cấu hình tái lập.
- [x] Nhóm3 — Phân tích năng lượng/baseline/độ phủ, đối chiếu độc lập và API/CSV.
- [ ] Nhóm4 — Báo cáo DOCX sáu chương,12 slide PPTX, video MP4 6–8 phút; kiểm trực quan mọi trang/slide và phát video.
- [ ] Nhóm5 — Runbook, diễn tập khởi động, backup/manifest/toàn vẹn SQLite, cleanup và tài liệu tiến độ.

## Vướng mắc và cách giải quyết

Đã đủ 15/15 lượt chính PASS và audit độc lập PASS cho45 cửa sổ node–lượt; raw MQTT/SQLite/API/CSV không sai lệch, quick_check=ok, không sai lệch raw MQTT/SQLite/API/CSV. EX02/R3 attempt01 bị mất cả3 Serial và giữ INCOMPLETE; sau phục hồi có attempt02 lỗi viewport, attempt03 bridge chưa sẵn sàng. Đã sửa chuẩn bị QA và attempt04 đã PASS; EX05/R1 attempt01 INCOMPLETE do đổi pha node01 trễ2257ms, vượt giới hạn2000ms. Đã chuẩn bị UI trước10s,18 lần diễn tập PASS với cận lớn nhất1475ms; giữ nguyên lịch vật lý và10 cấu hình chính đã đạt. EX05/R1 attempt02 và R2/R3 đã PASS, trễ tác động lớn nhất lần lượt621/649/845ms. EX06 và EX07 PASS; Serial chứng minh AUTO và phản ứng LDR khi mqtt=0. Word/PPTX v05 đã kiểm trực quan đủ23 trang/12 slide. Video01 giữ INCOMPLETE do helper đọc nhầm status thay result; lệnh thực tế APPLIED sau371ms. Đã sửa riêng helper và đang quay lại; cold-start/backup/cleanup còn chờ; không ghép dữ liệu cũ. Health OK, dropped_events0, ba node ONLINE/FRESH.

34 Python test PASS, gồm hồi quy tách monotonic theo host_boot_id qua reboot và phát hiện CSV thiếu/sai/NaN. Đã xác nhận giữ nguyên43.719 telemetry cũ và prefix5 stream log. Source/artifact firmware, backend/dashboard khớp baseline; không sửa chức năng sản phẩm.

Word v03 sáu chương đã render 23 trang bằng WPS và đạt schema; PPTX v03 đủ 12 slide, native chart/table, ảnh dashboard giữ đúng tỷ lệ. Lỗi tràn chữ slide9 đã được xác minh sửa. Hai tệp còn mang trạng thái đang hoàn thiện vì số liệu chính chưa đủ. PDF do người dùng tự xuất. Quay thử riêng 3 giây dashboard đạt 1920×1080, giải mã đủ 90 frame và trình duyệt mở được; đây chưa phải video 6–8 phút. Đã giữ lỗi thiếu FFmpeg và lỗi Video.path của kết nối từ xa, bổ sung runtime đúng phiên bản và dùng saveAs. Video chính, diễn tập cold-start và backup cuối chưa chạy; chưa chốt các nhóm2–5.

## Phụ thuộc và điều kiện bắt đầu

Đã có yêu cầu triển khai của người dùng. Cần ba Wokwi VS Code/gateway, broker QA, backend một worker/SQLite mới, Live Server, runtime tài liệu và công cụ video. Chỉ thao tác tài nguyên QA có quyền sở hữu; giữ dữ liệu cũ. Không tự ghi PASS khả năng hai thành viên chạy/giải thích nếu chưa có xác nhận trực tiếp.

## Tiếp tục sau TASK-013

Ở lượt tiếp tục ngày17/11, người dùng đã cài bộ skill docx/pptx/pdf Anthropic tại ~/.codex/skills và yêu cầu kiểm tra để tiếp tục TASK-012. Đã đọc cả3 SKILL.md và cài runtime QA riêng cho docx/pptxgenjs/Python. WPS native render PNG đã được kiểm chứng, không tiếp tục cài LibreOffice; giữ nguyên plugin OpenAI. TASK-013 hoàn thành và toàn bộ báo cáo/checklist/bằng chứng của lượt cài skill được bảo toàn. EX-01-r01-a01 đã PASS; đang chạy14 lượt còn lại, không chạy lại EX-01 đã đạt.

## Điều chỉnh bàn giao theo người dùng

- 2026-11-17T21:52:03+07:00 — Người dùng yêu cầu nhận Word và tự xuất PDF bằng WPS. Bỏ PDF khỏi đầu ra bắt buộc; dừng xử lý xuất PDF tự động. Giữ DOCX và PPTX chỉnh sửa được, kiểm tra cấu trúc và mở trên WPS; ghi rõ mức kiểm trực quan thực tế. Các nhóm nghiệm thu còn lại giữ nguyên.

## Tiến độ tài liệu và kiểm tra WPS

- 2026-11-17T22:16:08+07:00 — Bản DOCX sáu chương đã mở đúng22 trang trên WPS; SaveAsPNG xuất đủ22 trang, đã rà trực quan bản nháp. PPTX12 slide có bảng/biểu đồ native đã qua schema, WPS xuất ảnh12/12; đã rà và sửa tràn chữ slide9. Hai tệp hiện là bản đang hoàn thiện, chưa chốt nhóm4. Đã có runbook tại docs/demo-runbook.md.
- Audit raw MQTT→SQLite→API đã đối chiếu2 lượt chính PASS; còn13 lượt. Không thay đổi source sản phẩm. WPS RPC có lỗi destructor sau cleanup; kết quả ảnh đã xuất thành công, chưa coi Quit request là đã dừng tiến trình.

## Tiếp tục ngày18/11/2026

- 2026-11-18T09:14:09+07:00 — Người dùng yêu cầu tiếp tục. Còn3/15 lượt chính PASS; EX-02-r03-a01 INCOMPLETE do cả3 kết nối Serial ngắt. Không còn process QA sống; đã giữ trạng thái/log và backup SQLite trước phục hồi (quick_check=ok). Khôi phục cùng source/artifact, giữ lượt đã đạt và chạy lại trọn lượt bị ngắt.
- Bổ sung host_boot_id cho raw/result để tách clock monotonic qua các lần khởi động máy; audit cũ chỉ dùng cohort cũ, không trộn record của clock mới. Không sửa công thức, schema sản phẩm hoặc recipe.

- Đã phục hồi đủ3 node ONLINE/FRESH, health OK/dropped_events0; source/artifact khớp TASK-011. Runner tiếp tục --all --resume, tái dùng EX01/R1 và EX02/R1,R2; đang chạy lại EX02/R3 từ đầu.

## Chuỗi bàn giao sau thực nghiệm

Đã chuẩn bị pipeline riêng trong QA root: chờ đủ15 lượt, audit/verify, tạo biểu đồ/Word/PPTX và render WPS, quay demo, kiểm decode/phát video, diễn tập cold-start, dừng đúng dịch vụ QA. Pipeline dừng khi gặp lỗi; không tự bỏ lượt. Sau các bước tự động vẫn cần rà mọi ảnh tài liệu/slide và các cảnh video, rồi mới chốt video/backup/tài liệu hoàn thành. Source/helper as-run và hash được giữ trong evidence/recovery-20261118-091409/automation-as-run/.

## Tiếp tục chốt bàn giao

Đã có audit 15/15 PASS, Word v05 kiểm 23/23 trang, PPTX v05 kiểm 12/12 slide và cold-start PASS. Video02 không đạt kiểm trực quan vì vùng ảnh xám sau cuộn/tải CSV; bản quay headless ngắn đã kiểm hết vùng ảnh. Các lần chuẩn bị quay tiếp theo dừng đúng điều kiện node02 không fresh; đang kiểm tra trạng thái Pause của Wokwi, phục hồi phiên QA rồi quay lại trọn video. Không chạy lại 15 lượt chính hoặc sửa nguồn sản phẩm. Chỉ chốt nhóm4–5 sau kiểm trực quan video, cleanup hiện hành và backup toàn vẹn.
