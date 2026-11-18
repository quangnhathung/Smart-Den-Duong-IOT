"""Close TASK012 only after all actual handover gates and first verified backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys
q=Path(__file__).resolve().parent;root=Path(json.loads((q/'runtime.json').read_text())['root']);e=root/'docs/reports/evidence/task-012/run-20261117-200024';out=root/'output/task-012/deliverables'
backup_path=Path(sys.argv[1]).resolve();backup=json.loads(backup_path.read_text());assert backup['status']=='PASS' and Path(backup['archive']).is_file()
assert hashlib.sha256(Path(backup['archive']).read_bytes()).hexdigest()==backup['sha256']
for file in ['analysis-final.json','cold-start.json','cleanup.json']:assert json.loads((q/file).read_text())['status']=='PASS'
demo=json.loads((q/'demo-status.json').read_text());assert demo['status']=='QA_PASSED'
video_qa=json.loads((e/'video-final-qa.json').read_text());assert video_qa['status']=='PASS' and video_qa['reviewed_scenes']==16
assert json.loads((e/'office-final-qa.json').read_text())['status']=='PASS'
assert json.loads((e/'history-preserved-final.json').read_text())['status']=='PASS'
stamp=datetime.datetime.now().astimezone().isoformat(timespec='seconds');relative='evidence/task-012/run-20261117-200024/'
shutil.copy2(backup_path,e/'backup-first-verification.json')
task=f'''# TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Hoàn thành
- Tiến độ: 5/5 nhóm nghiệm thu
- Cập nhật: {stamp}

## Mô tả và phạm vi

Thực hiện kế hoạch đã giao:15 lượt thực nghiệm ba node, phân tích độc lập, báo cáo Word sáu chương,12 slide, video demo6–8 phút, runbook và backup toàn vẹn. Giữ firmware, backend/dashboard, pin map, hợp đồng MQTT/API/schema và toolchain. Dashboard HTML/CSS/JS chạy qua Live Server. Không commit/push/merge hoặc triển khai cloud.

SRS mục9.1–9.3,12,13,15; P7/A7. Thời lượng/PIR theo uptime riêng mỗi node, coverage theo UTC nhận. Công suất/điện năng là mô hình; người/xe là kịch bản quy ước. PDF do người dùng tự xuất bằng WPS theo yêu cầu17/11. Lịch sử triển khai trước khi chốt được giữ tại [snapshot]({relative}checkpoint-before-closure/docs__reports__task.md).

## Tiêu chí hoàn thành và tiến độ

- [x] Nhóm1 — Baseline/phương pháp, công cụ và pilot90s/node;34 Python test PASS.
- [x] Nhóm2 — 15/15 lượt chính PASS, giữ mọi attempt lỗi và chạy lại trọn lượt liên quan.
- [x] Nhóm3 — 45 cửa sổ node–lượt, raw MQTT/SQLite/API/CSV và phép tính độc lập khớp trong1e-9Wh; quick_check=ok.
- [x] Nhóm4 — DOCX v05 sáu chương/23 trang, PPTX v05 12 slide16:9 kiểm schema và toàn bộ ảnh WPS; MP4 khoảng7 phút1080p, phụ đề Việt, full decode/phát Chrome và16 cảnh kiểm trực quan PASS.
- [x] Nhóm5 — Runbook, cold-start ba node/lệnh APPLIED, giữ hash137.797 telemetry cũ, cleanup hiện hành PASS, backup SHA256/đọc lại archive PASS, cập nhật hồ sơ/lịch sử.

## Kết quả và bằng chứng

[Hồ sơ nghiệm thu]({relative}README.md), [audit]({relative}analysis-final.json), [Office QA]({relative}office-final-qa.json), [video QA]({relative}video-final-qa.json), [cold-start]({relative}cold-start.json), [cleanup]({relative}cleanup-final.json), [backup đã kiểm]({relative}backup-first-verification.json). Tệp chính ở output/task-012/deliverables/; raw/SQLite/ảnh/video và backup được giữ ngoài Git, không phải dữ liệu đã có trong commit.

Công suất AUTO trung bình EX02/03/04/05 khoảng6/8,160/9,600/6,613W. EX04/R3 coverage có node99,004%; EX07 khoảng79,073–79,836% do outage chủ động. Trễ tác động lớn nhất1778ms trong giới hạn2000ms. Không bỏ mẫu/lượt hợp lệ hoặc đặt tỷ lệ tiết kiệm mục tiêu.

## Vướng mắc và cách giải quyết

Không còn vướng mắc chặn phạm vi TASK-012. Đã giữ FAIL/INCOMPLETE: PIR/khoảng cách ngoài recipe chưa xác định nguyên nhân ở EX02/R1; mất Serial/viewport/readiness ở EX02/R3; EX05/R1 trễ2257ms. Sửa riêng công cụ QA, chuẩn bị UI trước10s không đổi lịch vật lý; chạy lại trọn lượt, audit cuối PASS. Không sửa source sản phẩm; [đối chiếu baseline]({relative}product-preserved-final.json).

Video01 lỗi helper đọc status thay result, video02 có vùng xám dù decode được; các setup03–05 lỗi viewport/node02 Pause. Đã sửa helper/viewport, Resume thật cùng boot, dùng Chrome headless riêng và quay lại toàn bộ; bản cuối qua kiểm trực quan. Giữ nguyên mọi lần lỗi và source as-run. Word/PPTX v05 tạo mới, giữ bản nháp và đề cương. PDF tự xuất theo lựa chọn người dùng.

## Giới hạn và phụ thuộc

Chưa kiểm mạch thật hoặc xác nhận hai thành viên tự chạy/giải thích độc lập; không ghi PASS thay con người. Cold-start đã chạy trên máy này, không thay thử trên máy khác. Đề xuất TASK-014 diễn tập hai thành viên tại next-task.md, chưa thực hiện. Không có phụ thuộc còn chặn bộ bàn giao đã chốt.
'''
(root/'docs/reports/task.md').write_text(task)
(root/'docs/reports/next-task.md').write_text(f'''# TASK-014 — Diễn tập vận hành và bảo vệ với hai thành viên

- Trạng thái: Chưa bắt đầu
- Tiến độ: 0/3 mục nghiệm thu dự kiến
- Cập nhật: {stamp}

## Mô tả và phạm vi

Đề xuất sau TASK-012: hai thành viên dùng bộ bàn giao/runbook để tự khởi động mô hình, chạy demo và giải thích thuật toán, giao thức, năng lượng/độ phủ và giới hạn. Chỉ thực hiện khi người dùng giao task; chưa chạy trong TASK-012. Không thêm tính năng hoặc tự triển khai cloud.

## Tham chiếu SRS

SRS mục13,15–16; kiểm khả năng vận hành/giải thích của nhóm, không thay bằng kiểm tự động.

## Tiêu chí hoàn thành và tiến độ

- [ ] Mỗi thành viên tự khởi động ba node/backend/broker/dashboard bằng Live Server theo runbook; ghi máy/môi trường/kết quả và lỗi thực tế.
- [ ] Mỗi người thực hiện các luồng demo và giải thích số liệu/giới hạn bằng bằng chứng, không coi mô phỏng là số đo phần cứng.
- [ ] Chốt phản hồi, sửa hướng dẫn trong phạm vi được giao và ghi biên bản diễn tập; PDF do người dùng xuất nếu cần nộp.

## Vướng mắc và cách giải quyết

Chưa có xác nhận trực tiếp từ hai thành viên. Agent không tự ghi PASS; cần buổi diễn tập và phản hồi thực tế.

## Phụ thuộc và điều kiện bắt đầu

TASK-012 đã hoàn thành; cần người dùng giao TASK-014, hai thành viên sẵn sàng và máy có PlatformIO/Wokwi/gateway, Python backend, MQTT và VS Code Live Server. Kiểm lại manifest trước chạy; helper/PID của đợt QA cũ chỉ là tham chiếu, không chạy mù.
''')
report=f'''## {stamp} — TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Hoàn thành
- Tiến độ: 5/5 nhóm nghiệm thu

### Đã thực hiện

Hoàn thành15 lượt EX01–07 ba node,45 cửa sổ dữ liệu riêng, đối chiếu năng lượng/baseline/coverage; tạo Word v05 sáu chương/23 trang, PPTX v05 12 slide16:9 và video MP4 khoảng7 phút1080p/phụ đề Việt. Bổ sung công cụ QA, runbook, backup nguồn ba repo/SQLite/raw/attempt/artifact/deliverables. PDF do người dùng tự xuất WPS. Giữ source sản phẩm, dữ liệu cũ và mọi attempt lỗi; không commit/push/merge/cloud.

### Kiểm tra và kết quả

PASS34 Python test,15/15 lượt chính, audit raw MQTT→SQLite→API/CSV độc lập trong1e-9Wh, quick_check=ok;45 cửa sổ riêng, trễ lớn nhất1778ms≤2000ms. Office schema và toàn bộ23 trang/12 slide WPS PASS. Video full decode/phát Chrome/tỷ lệ16:9/16 cảnh trực quan PASS. Cold-start PASS: ba boot mới ONLINE/FRESH/AUTO, lệnh APPLIED,137.797 telemetry cũ giữ SHA; cleanup đúng dịch vụ QA/cổng trống. Backup đọc lại archive và SHA256 PASS. [Hồ sơ]({relative}README.md), [backup đã kiểm]({relative}backup-first-verification.json).

### Vướng mắc

Các pilot và attempt lỗi được giữ riêng: EX02/R1 chuyển động ngoài recipe chưa xác định nguyên nhân; EX02/R3 mất Serial/viewport/readiness; EX05/R1 trễ2257ms. Video helper sai trường status/result, vùng xám trong raw sau cuộn/tải CSV, rồi node02 paused khi setup; video06 gặp biên telemetry3s đúng lúc gửi lệnh. Không còn vướng mắc chặn phạm vi bàn giao. Chưa có mạch thật hoặc xác nhận hai thành viên tự vận hành/giải thích.

### Cách giải quyết

Tách host_boot_id qua reboot, bảo toàn raw/telemetry; chuẩn bị UI EX05 trước10s giữ lịch vật lý và ngưỡng2s, diễn tập18 lần rồi chạy lại trọn lượt lỗi. Sửa helper result, fit viewport/Resume thật, chờ telemetry mới ngay trước click, quay Chrome headless riêng; giữ bản quay lỗi, chỉ chốt sau kiểm ảnh. Native WPS render PNG, không tiếp tục xuất PDF tự động. Không dùng kiểm tự động thay xác nhận con người.

### Tài liệu và bước tiếp theo

Cập nhật experiments/testing/architecture, runbook, task/checklist/next-task và hồ sơ bằng chứng; SRS9/12/13/15. Word/PPTX cũ, đề cương và toàn bộ byte lịch sử báo cáo/checklist được giữ. Đề xuất TASK-014 diễn tập hai thành viên; chưa triển khai. Backup đầu đã kiểm làm bằng chứng nghiệm thu; snapshot cuối sau đóng tài liệu được tạo riêng, không ghi đè snapshot cũ.
'''
check=f'''# TASK-012 — Thực nghiệm và bàn giao đồ án

- Hoàn thành: {stamp}; **5/5 nhóm nghiệm thu**.
- [x] Baseline/phương pháp/pilot90s-node;34 Python test PASS.
- [x] 15/15 lượt EX01–07 hợp lệ; giữ FAIL/INCOMPLETE, chạy lại trọn lượt bị lỗi.
- [x] 45 cửa sổ node–lượt, raw MQTT/SQLite/API/CSV và năng lượng độc lập khớp1e-9Wh; công bố coverage/giới hạn mô phỏng.
- [x] Word v05 sáu chương/23 trang, PPTX v05 12 slide16:9; schema và mọi ảnh WPS PASS. Video khoảng7 phút1080p/subtitle Việt, full decode/phát/16 cảnh trực quan PASS; PDF người dùng tự xuất.
- [x] Runbook/cold-start/lệnh APPLIED,137.797 telemetry cũ giữ SHA, cleanup QA và backup SHA/đọc lại archive PASS; tài liệu/lịch sử bảo toàn.

[Hồ sơ nghiệm thu]({relative}README.md). Không sửa source sản phẩm hoặc commit/push/merge. Chưa mạch thật hoặc xác nhận hai thành viên tự vận hành/giải thích; đề xuất TASK-014 chưa thực hiện. Các mục dưới giữ nguyên lịch sử.
'''
proof={'at':stamp,'status':'PASS','files':{}}
for filename,block in [('report.md',report),('checklists.md',check)]:
 p=root/'docs/reports'/filename;old=p.read_bytes();assert not old.startswith(('# TASK-012' if filename=='checklists.md' else '## '+stamp).encode())
 snap=e/('history-before-'+filename);assert not snap.exists();snap.write_bytes(old)
 prefix=(block+'\n---\n\n').encode();p.write_bytes(prefix+old);new=p.read_bytes();assert new[len(prefix):]==old
 proof['files'][filename]={'prefix_bytes':len(prefix),'old_bytes':len(old),'old_sha256':hashlib.sha256(old).hexdigest(),'preserved_tail_sha256':hashlib.sha256(new[len(prefix):]).hexdigest()}
(e/'history-prepend-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
p=root/'docs/techs/architecture.md';s=p.read_text().replace('đang hoàn thiện kiểm tra bàn giao.','đã hoàn thành bộ bàn giao và kiểm tra tài liệu/video/cold-start/backup.');p.write_text(s)
p=root/'docs/techs/experiments.md';s=p.read_text()+'''\nKết thúc TASK-012: video chính đã qua full decode/phát Chrome và16 cảnh trực quan, cleanup hiện hành PASS, backup đã kiểm SHA256 và từng member archive. Xem video-final-qa.json, cleanup-final.json và backup-first-verification.json trong hồ sơ. Word v05/PPTX v05 là bản chính; các bản cũ giữ để truy vết. Bộ bàn giao không nghiệm thu thay hai thành viên hoặc mạch thật.\n''';p.write_text(s)
p=root/'docs/demo-runbook.md';s=p.read_text()+'''\nTASK-012 đã kiểm cold-start ba node/lệnh APPLIED, bảo toàn137.797 telemetry cũ và dừng đúng dịch vụ QA. Video cuối đã kiểm decode/phát Chrome/16 cảnh; backup SHA256 và archive toàn vẹn đã đạt. Bằng chứng tại reports/evidence/task-012/run-20261117-200024/README.md. Các xác nhận này áp dụng máy/lượt QA đã ghi; diễn tập con người hoặc máy khác chưa thực hiện.\n''';p.write_text(s)
p=e/'README.md';s=p.read_text();s=s.replace('**Đang thực hiện,3/5 nhóm nghiệm thu.** Đã đủ15/15 lượt chính và audit độc lập PASS. Word/PPTX v05 và cold-start đã kiểm xong; video cuối, cleanup hiện hành và backup đang hoàn thiện.','**Hoàn thành5/5 nhóm nghiệm thu.** Đủ15/15 lượt chính và audit độc lập PASS. Word/PPTX v05, video chính, cold-start, cleanup hiện hành và backup đã kiểm xong.')
s=s.replace('Sau đó mở riêng tài nguyên QA để hoàn thiện video; cleanup cuối phải kiểm lại.','Sau đó mở riêng tài nguyên QA để hoàn thiện video; [cleanup cuối](cleanup-final.json) PASS, các cổng QA đóng, chỉ dừng đúng dịch vụ sở hữu.')
s=s.replace('Video chính đang hoàn thiện; chỉ chốt sau full decode/phát Chrome và16 cảnh trực quan. Backup chỉ thực hiện sau QA video và cleanup hiện hành PASS. Không coi video ngắn kiểm runtime là demo6–8 phút hoặc coi RECORDED là đã QA.','[Video QA cuối](video-final-qa.json) PASS: MP4 khoảng7 phút,1920×1080/tỷ lệ16:9,30fps, phụ đề Việt, không audio; full decode/phát Chrome và16 cảnh trực quan đạt. Tệp Demo-Den-duong-thong-minh-Nhom7-v01.mp4 cùng SRT/ASS ở deliverables. [Bảo toàn telemetry đến cuối](history-preserved-final.json) PASS. [Backup đầu đã kiểm](backup-first-verification.json) lưu nguồn ba repo, SQLite/raw/mọi attempt/config/artifact/deliverables; đọc lại từng member với SHA256 manifest. Snapshot cuối riêng được tạo sau đóng hồ sơ để chứa tài liệu hoàn thành; proof bên ngoài archive tránh tự tham chiếu. [Bảo toàn lịch sử](history-prepend-proof.json) chứng minh nguyên byte report/checklist cũ. Không coi video ngắn kiểm runtime hoặc decode đơn thuần là nghiệm thu trực quan.')
p.write_text(s)
p=root/'README.md';old=p.read_bytes();(e/'root-README-before-closure.md').write_bytes(old);s=old.decode().replace('Bộ thực nghiệm/bàn giao cuối chưa thực hiện.','TASK-012 hoàn thành5/5:15 lượt thực nghiệm hợp lệ, audit độc lập, Word/PPTX/video, runbook/cold-start/backup. Xem [hồ sơ bàn giao và giới hạn](docs/reports/evidence/task-012/run-20261117-200024/README.md).');s=s.replace('metadata và phạm vi mô phỏng đã ghi trong biên bản; chưa nghiệm thu toàn hệ thống.','metadata và phạm vi mô phỏng đã ghi trong biên bản; chưa nghiệm thu mạch thật.');p.write_text(s)
shutil.copy2(root/'docs/demo-runbook.md',out/'RUNBOOK.md')
print(json.dumps({'status':'CLOSED','at':stamp,'history_tail_preserved':True}))
