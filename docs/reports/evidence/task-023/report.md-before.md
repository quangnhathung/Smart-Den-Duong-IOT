## 2026-11-18T19:58:51+07:00 — TASK-022 — Dừng toàn bộ hệ thống

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

### Đã thực hiện

Theo yêu cầu dừng tất cả, dừng MQTT Compose, backend và tiến trình của ba cửa sổ node/dashboard. Giữ DB/source/kết quả cũ và VS Code firmware gốc. Không khởi động lại.

### Kiểm tra và kết quả

PASS không còn listener1883/8000/5500/4000/4001/4002. PID/backend đối chiếu ownership; renderer/extension host/file watcher đối chiếu code --status. [Bằng chứng](evidence/task-022/stop-all.json).

### Vướng mắc

Đóng cửa sổ ban đầu chưa nhả4000/5500; chưa thể ghi dừng hoàn toàn ở lần kiểm đầu.

### Cách giải quyết

Dừng đúng các tiến trình còn giữ mô phỏng/Live Server và kiểm lại cổng, đã trống. Không có vướng mắc còn lại.

### Tài liệu và bước tiếp theo

Cập nhật task/techs/setup/checklist/next-task. Chỉ khởi động lại khi người dùng yêu cầu.

---

## 2026-11-18T19:58:51+07:00 — TASK-021 — Khởi động hệ thống, đã hủy

- Trạng thái: Đã hủy
- Tiến độ: 2/4 nhóm nghiệm thu

### Đã thực hiện

Kiểm SHA source/artifact ba node, khởi động MQTT1883/backend8000 và mở workspace ba node/FE. Node01 đã ONLINE/FRESH; FE trả HTTP200. Node02/03 chưa có telemetry và chưa nghiệm thu giao diện đủ ba node. Đang xử lý launcher thì người dùng yêu cầu dừng.

### Kiểm tra và kết quả

PASS artifact/health/broker/database/queue và node01. Chưa đạt3 node/FE DOM; không ghi hoàn thành toàn hệ thống. [Hồ sơ](evidence/task-021/README.md).

### Vướng mắc

Điều khiển bằng phím chưa vào đúng cửa sổ; helper lệnh trực tiếp chưa xác nhận hoàn tất. Công cụ CUA không có surface khả dụng.

### Cách giải quyết

Dừng mọi thao tác khởi động theo yêu cầu mới; TASK-022 đã dừng dịch vụ và kiểm cổng. Không tiếp tục sửa/khởi động.

### Tài liệu và bước tiếp theo

Giữ snapshot task019/đề xuất020, baseline và log. Không sửa source sản phẩm hoặc xóa DB. Không chạy lại thực nghiệm.

---

## 2026-11-18T16:41:28+07:00 — TASK-019 — Viết lại báo cáo tiểu luận bốn chương

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu

### Đã thực hiện

Tạo Word mới27 trang theo yêu cầu: Lời nói đầu; Chương1 IoT; Chương2 phần cứng; Chương3 phần mềm/kiến trúc/hoạt động; Chương4 kết quả demo; Lời kết. Có28 mục con, mục lục, bảng và6 ảnh/biểu đồ từ hồ sơ hiện có, nguồn tham khảo. Giữ nguyên bìa/style/lề/header/footer của báo cáo v05 bằng ghép body vào OOXML; bản cũ bảo toàn. Chỉ bàn giao DOCX, không tạo PDF/PPTX/Markdown bài tiểu luận; không dùng skill humanize/humanizer/viet-humanize theo yêu cầu. Thêm generator body và helper merge có guard không ghi đè.

### Kiểm tra và kết quả

PASS schema462 paragraph, native WPS27/27 trang đã rà trực quan, mục lục/footer/heading/bảng/ảnh đạt.12 phần tử bìa và mọi package part gốc ngoài document/relationships giữ byte; PNG bìa trùng SHA bản v05. Source không đổi, WPS QA riêng đã đóng. Mean/min/max15 dòng CSV khớp variation; bảng Word khớp số sau làm tròn; audit15 lượt/45 cửa sổ;6 media khớp SHA. Kiểm đúng final latency audit30 mẫu và công bố probe HTTP lịch sử INCOMPLETE. Hash30 firmware/26 backend/15 dashboard không đổi. [Hồ sơ và Word](evidence/task-019/README.md).

### Vướng mắc

Không có vướng mắc còn chặn. Chưa có kết quả mạch thật/diễn tập con người mới; không chạy lại live hoặc build trong task biên soạn.

### Cách giải quyết

Phân biệt mô phỏng và số đo điện thực; AUTO phụ thuộc PIR, hold/dimming và hai clock được giải thích. Tách ảnh/video minh họa khỏi cửa sổ thực nghiệm, giữ các lượt lỗi và probe chưa đủ thời lượng trong phần giới hạn. Dùng runtime docx/WPS riêng đã có để render QA, không thay phụ thuộc hoặc xuất PDF.

### Tài liệu và bước tiếp theo

Cập nhật task/checklist/next-task và document-skills; SRS1–9/12–15 chỉ tham chiếu, không sửa sản phẩm/schema/pin. Đề xuất TASK-020 rà soát/diễn tập hai thành viên, kế thừa018 chưa thực hiện. Giữ mọi byte lịch sử cũ; không commit/push/cloud hoặc tự thực hiện đề xuất.

---

## 2026-11-18T16:20:56+07:00 — TASK-017 — Kịch bản giới thiệu và demo chi tiết

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu

### Đã thực hiện

Soạn [kịch bản](../demo-script.md), Word v03 chỉnh sửa được23 trang và Markdown đồng nội dung. Có mở đầu chi tiết/bài toán/kiến trúc, phân vai A/B, timeline20 phút, từng cảnh thao tác/lời nói/kỳ vọng/chờ/lỗi, nhánh chỉ Wokwi khi MQTT0, kết quả thực nghiệm có nguồn, kết luận, bản rút gọn7 phút,14 câu hỏi bảo vệ và phiếu diễn tập. Tái dùng generator, thêm source Markdown tùy chọn/title động và sửa liên kết nguồn theo vị trí DOCX; giữ cách gọi guide cũ và mọi tệp đã giao.

### Kiểm tra và kết quả

PASS schema, native WPS23 trang. V02 đã xem hết; v03 chỉ sửa đích hyperlink, render lại và23/23 PNG giống nguyên byte ảnh đã xem.411 dòng nội dung Markdown→DOCX,23 heading và10 liên kết nội bộ PASS; source không đổi trong render, WPS QA đã đóng. Timeline11 đoạn liên tục1200s/bản ngắn8 đoạn420s; số trung bình/tỷ lệ EX02–05 và coverage EX07 khớp JSON/CSV sau làm tròn. JSON/Bash cú pháp PASS. Hash30 tệp firmware,26 backend,15 dashboard không đổi. [Hồ sơ](evidence/task-017/README.md).

### Vướng mắc

Không có vướng mắc còn chặn. Các lệnh và lời dẫn là kịch bản cần diễn tập, không phải bằng chứng buổi demo mới hoặc Windows đã chạy. Không tự xác nhận hai thành viên đã trình bày thành công.

### Cách giải quyết

Mỗi cảnh có điều kiện chuyển thật theo telemetry/ACK/Serial; nhấn PIR mới kích người/xe, giữ hold/clock và tách target/applied. Phần no-replay/pending không được suy từ cảnh không tạo pending; số liệu chính tách phiên demo. Giữ giới hạn dữ liệu mô phỏng/coverage và chuyển video có thông báo khi live gián đoạn.

### Tài liệu và bước tiếp theo

Cập nhật runbook/README/experiments/document-skills/task/checklist/next-task, tham chiếu SRS1–9/12/13/15. Giữ nguyên mọi byte report/checklist cũ và snapshot task/đề xuất trước. Đề xuất TASK-018 diễn tập hai thành viên theo kịch bản mới, kế thừa016 chưa thực hiện; chưa triển khai. Không chạy lại stack live/build/15 lượt, không sửa sản phẩm/DB hoặc commit/push/cloud.

---

## 2026-11-18T15:50:12+07:00 — TASK-015 — Hướng dẫn cài đặt và vận hành toàn dự án

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu

### Đã thực hiện

Soạn [hướng dẫn đầu-cuối](../project-guide.md), Word chỉnh sửa được34 trang và Markdown đồng nội dung. Bao gồm cài Linux/Windows, ba repo/cổng/cấu hình, Docker MQTT, Python3.12/SQLite init, PlatformIO/build ba node, license/gateway/Wokwi, Live Server, năm màn hình/UI/API, AUTO/MANUAL/ACK, cảm biến/fault, năng lượng/coverage/clock, thực nghiệm, kiểm thử, dừng/restart, backup/restore/chuyển máy và xử lý lỗi. Thêm generator DOCX, ảnh QA có nguồn và liên kết từ README/setup/runbook; giữ sản phẩm và dữ liệu cũ.

### Kiểm tra và kết quả

PASS schema DOCX; native WPS34/34 trang đã xem trực quan, source SHA không đổi và chỉ instance QA được đóng. Đối chiếu695 dòng nội dung Markdown→DOCX,34 heading chính, bảng/list/ảnh16:9 và số trang PASS. CLI plan --all trả15 lượt, prepare --help, Bash/Python/JSON cú pháp PASS. SQLite tạm init hai lần giữ3 node/fixture, backup/quick_check/đọc lại và từ chối ghi đè PASS, source/đích không đổi sau ca từ chối. Hash28 tệp firmware,14 backend,8 dashboard giữ nguyên. [Bằng chứng](evidence/task-015/README.md).

### Vướng mắc

Lệnh đối chiếu ban đầu gọi Python hệ thống thiếu lxml. Không có vướng mắc còn chặn. Chưa cài/chạy Windows/PowerShell hoặc tái chạy Docker/Wokwi/15 lượt live trong task tài liệu; không dùng kiểm cú pháp thay nghiệm thu máy mới.

### Cách giải quyết

Dùng đúng runtime Office riêng đã có; không cài thư viện vào sản phẩm. Dẫn nguồn cấu hình/source hiện hành và tách các đoạn lịch sử P0/QA khỏi thao tác mặc định. PDF do người dùng tự xuất WPS; không xuất lại PDF hoặc sửa tài liệu TASK-012 đã giao.

### Tài liệu và bước tiếp theo

Cập nhật setup/document-skills/runbook/README/task/checklist/next-task; SRS3–9/12–15, không sửa SRS hoặc sản phẩm. Bảo toàn TASK-012 và đề xuất TASK-014 cũ; giữ nguyên mọi byte report/checklist trước. Đề xuất tiếp TASK-016 diễn tập hai thành viên dùng hướng dẫn mới, chưa triển khai. Không commit/push/cloud.

---

## 2026-11-18T15:25:24+07:00 — TASK-012 — Thực nghiệm và bàn giao đồ án

- Trạng thái: Hoàn thành
- Tiến độ: 5/5 nhóm nghiệm thu

### Đã thực hiện

Hoàn thành15 lượt EX01–07 ba node,45 cửa sổ dữ liệu riêng, đối chiếu năng lượng/baseline/coverage; tạo Word v05 sáu chương/23 trang, PPTX v05 12 slide16:9 và video MP4 khoảng7 phút1080p/phụ đề Việt. Bổ sung công cụ QA, runbook, backup nguồn ba repo/SQLite/raw/attempt/artifact/deliverables. PDF do người dùng tự xuất WPS. Giữ source sản phẩm, dữ liệu cũ và mọi attempt lỗi; không commit/push/merge/cloud.

### Kiểm tra và kết quả

PASS34 Python test,15/15 lượt chính, audit raw MQTT→SQLite→API/CSV độc lập trong1e-9Wh, quick_check=ok;45 cửa sổ riêng, trễ lớn nhất1778ms≤2000ms. Office schema và toàn bộ23 trang/12 slide WPS PASS. Video full decode/phát Chrome/tỷ lệ16:9/16 cảnh trực quan PASS. Cold-start PASS: ba boot mới ONLINE/FRESH/AUTO, lệnh APPLIED,137.797 telemetry cũ giữ SHA; cleanup đúng dịch vụ QA/cổng trống. Backup đọc lại archive và SHA256 PASS. [Hồ sơ](evidence/task-012/run-20261117-200024/README.md), [backup đã kiểm](evidence/task-012/run-20261117-200024/backup-first-verification.json).

### Vướng mắc

Các pilot và attempt lỗi được giữ riêng: EX02/R1 chuyển động ngoài recipe chưa xác định nguyên nhân; EX02/R3 mất Serial/viewport/readiness; EX05/R1 trễ2257ms. Video helper sai trường status/result, vùng xám trong raw sau cuộn/tải CSV, rồi node02 paused khi setup; video06 gặp biên telemetry3s đúng lúc gửi lệnh. Không còn vướng mắc chặn phạm vi bàn giao. Chưa có mạch thật hoặc xác nhận hai thành viên tự vận hành/giải thích.

### Cách giải quyết

Tách host_boot_id qua reboot, bảo toàn raw/telemetry; chuẩn bị UI EX05 trước10s giữ lịch vật lý và ngưỡng2s, diễn tập18 lần rồi chạy lại trọn lượt lỗi. Sửa helper result, fit viewport/Resume thật, chờ telemetry mới ngay trước click, quay Chrome headless riêng; giữ bản quay lỗi, chỉ chốt sau kiểm ảnh. Native WPS render PNG, không tiếp tục xuất PDF tự động. Không dùng kiểm tự động thay xác nhận con người.

### Tài liệu và bước tiếp theo

Cập nhật experiments/testing/architecture, runbook, task/checklist/next-task và hồ sơ bằng chứng; SRS9/12/13/15. Word/PPTX cũ, đề cương và toàn bộ byte lịch sử báo cáo/checklist được giữ. Đề xuất TASK-014 diễn tập hai thành viên; chưa triển khai. Backup đầu đã kiểm làm bằng chứng nghiệm thu; snapshot cuối sau đóng tài liệu được tạo riêng, không ghi đè snapshot cũ.

---

## 2026-11-17T21:04:27+07:00 — TASK-013 — Cài skill tài liệu chính thức cho Codex cá nhân

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu cài tệp

### Đã thực hiện

Cài pptx/pdf/docx vào ~/.codex/skills từ anthropics/skills tại commit e4bb5d960d87126ff3b3a8af1a104b7db67560ba. Giữ plugin OpenAI, không cài runtime, không tạo tài liệu mẫu. Lưu nguyên trạng task/next-task trước khi chuyển task tại [hồ sơ TASK-013](evidence/task-013/).

### Kiểm tra và kết quả

PASS:131/131 tệp khớp danh sách và Git blob hash upstream (pptx58, pdf12, docx61); frontmatter, giấy phép và liên kết nội bộ SKILL.md hợp lệ. [Manifest](evidence/task-013/manifest.json) ghi nguồn, commit và SHA-256. Chưa chạy: nhận diện thực tế ở lượt/phiên Codex mới và tạo/render tệp Office/PDF. Không chạy build firmware vì không đổi firmware.

### Vướng mắc

Không có vướng mắc với cài tệp. Giới hạn: thiếu runtime tài liệu và chưa kiểm chứng nhận diện phiên mới.

### Cách giải quyết

Kiểm tra danh sách skill ở lượt tiếp theo, mở phiên mới nếu cần. Bổ sung runtime và kiểm mẫu chỉ khi được giao; không coi việc cài skill là nghiệm thu xuất tài liệu.

### Tài liệu và bước tiếp theo

Thêm [hướng dẫn skill](../techs/document-skills.md), cập nhật task/checklist/next-task. Task hỗ trợ SRS mục15; giữ công việc có sẵn và không thực hiện TASK-012.

---

## 2026-11-17T16:32:01+07:00 — TASK-011 — Hoàn thiện ba node và nghiệm thu30 phút

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu

### Đã thực hiện

Tham số hóa định danh1/2/3 từ một source, thêm ba environment/sơ đồ/cổng Serial, công cụ prepare kiểm artifact/freshness/hash và command chọn node. Kiểm live phát hiện raw cảm biến chờ control/periodic làm trễ; sửa đánh dấu snapshot khi sensor đổi, giữ coalescing/rate-limit200ms/periodic2s. Không đổi controller/timer/pin map/schema, source backend/dashboard hoặc SRS. Ba mô phỏng cap4MHz; dashboard QA dùng HTML/CSS/JS và engine VS Code Live Server5500, API8001/SQLite riêng.

### Kiểm tra và kết quả

PASS20 Python test,11 lượt host +2 compile-fail đúng kỳ vọng,3 build firmware và format9 tệp C++. Live PASS30 lệnh đúng đích, cảm biến cách ly/MANUAL timeout, OPEN_LOAD, tắt node02, AUTO offline/reconnect/no-replay, restart backend giữ hash telemetry cũ.30/30 mẫu sensor→dashboard cuối (10/node) dưới3s, max cận trên1272,235ms; command→ACK có đủ10/node, số liệu riêng trong hồ sơ.

PASS một cửa sổ1800 giây monotonic **15:36:05–16:06:05+07:00** ngày2026-11-17:1561/2216/1583 telemetry của ba node, tổng5360, không thiếu sequence/đổi boot, raw recorder không reconnect. Toàn bộ payload khớp SQLite ACCEPTED, continuity giữ nguyên, backend cùng PID/start ticks, health cuối dropped_events0, quick_check=ok. Cleanup PASS, các cổng QA đã đóng, dữ liệu/backup ngoài Git được giữ. [Bằng chứng, giới hạn và manifest](evidence/task-011/run-20261117-135233/README.md).

### Vướng mắc

Lỗi sensor telemetry chậm có ca red và FAIL live trước sửa. Công cụ QA đọc nhãn100k thành100 khiến raw trials End bị gắn INCOMPLETE. HTTP/resource probe nhận SIGTERM143 tại1346,506s/672 mẫu, nguyên nhân chính xác chưa xác định; stability-01 dừng trước sửa. Một số thao tác setup/recorder/cleanup gặp lỗi, có log tại qa-issues.json. Không còn vướng mắc chặn TASK-011 sau xử lý; các giới hạn quan sát vẫn được công bố.

### Cách giải quyết

Sửa coalescing, hồi quy/build cả3 và chạy lại trên firmware cuối; giữ FAIL cũ. Audit độc lập sửa riêng cách hiểu đơn vị k=1000 từ raw đã lưu, giữ timestamp/status gốc và đúng10 mẫu chính/node. stability-01 góp0 giây. Probe HTTP vẫn INCOMPLETE; audit raw MQTT/SQLite độc lập kiểm toàn bộ cửa sổ1800s đã định trước, không ghép đoạn hoặc tuyên bố probe đầy đủ. Không có bằng chứng HTTP/tài nguyên/dashboard liên tục trong phần probe thiếu. Cleanup ban đầu còn listener18773 đã xác minh đúng tiến trình QA rồi dừng, giữ cả kết quả ban đầu và cuối.

### Tài liệu và bước tiếp theo

Cập nhật README, architecture/firmware/MQTT/simulation/testing/backend/dashboard, task/checklist và đề xuất TASK-012 thực nghiệm/bàn giao cuối; chưa chạy TASK-012. Bảo toàn nguyên byte báo cáo/checklist cũ, TASK-010, đặc tả trước và source/thay đổi người dùng ở các repo anh em. Bước đóng hồ sơ không commit/push/merge. Chưa nghiệm thu EX-series, điện năng đại diện hoặc phần cứng thật.

---

## 2026-11-17T13:24:37+07:00 — TASK-011 — Chốt đặc tả trước triển khai

- Trạng thái TASK-011: Chưa bắt đầu; 0/4 nhóm nghiệm thu triển khai.
- Kết quả lượt tài liệu: hoàn tất đặc tả theo phạm vi người dùng đã chốt; chưa triển khai hoặc nghiệm thu ba node.

### Đã thực hiện

Cập nhật [next-task.md](next-task.md), thay nội dung chờ đặc tả bằng gói P6/A6: node_01/02/03 dùng chung source, ba environment/phiên Wokwi VS Code, đúng định danh/đúng đích, lỗi/phục hồi, latency từng node và một cửa sổ ổn định liên tục 1.800 giây thực. Ghi phương án công cụ, môi trường QA, trình tự, đầu ra, bốn nhóm nghiệm thu và điều kiện bắt đầu. Giữ Dashboard HTML/CSS/JS thuần chạy Live Server, schema/toolchain/thuật toán và giới hạn ngoài phạm vi.

Lưu nguyên byte [mô tả cũ](evidence/task-011/specification-20261117-131925/next-task-before.md), kèm [hồ sơ cập nhật](evidence/task-011/specification-20261117-131925/README.md). TASK-010 vẫn Hoàn thành 4/4 trong task.md; checklists.md và toàn bộ bằng chứng cũ giữ nguyên. Theo yêu cầu chỉ chuẩn bị đặc tả trước, chưa chuyển TASK-011 thành task đang thực hiện hoặc thêm vào danh sách task hoàn thành.

### Kiểm tra và kết quả

PASS kiểm tra tài liệu: trạng thái Chưa bắt đầu — 0/4, đủ bốn checkbox chưa đánh dấu, phạm vi/phương án đã chốt và liên kết nội bộ tài liệu mới hợp lệ; bản lưu khớp từng byte; task/checklist không đổi; phần đuôi report khớp toàn bộ nội dung cũ; git diff --check đạt. [Kết quả và hash](evidence/task-011/specification-20261117-131925/verification.json).

Không chạy host tests, build, Wokwi hoặc tích hợp; không khởi chạy dịch vụ và không suy kết quả kiểm tài liệu thành PASS chức năng. Chưa kiểm chứng quyền chạy đồng thời ba phiên hoặc năng lực máy; đó là bước preflight khi được giao triển khai.

### Vướng mắc

Không có vướng mắc về phạm vi hoặc cập nhật tài liệu. Giới hạn Wokwi CLI Unauthorized đã biết được ghi trong đặc tả cùng phương án VS Code; không coi đây là lỗi mới hoặc kết luận TASK-011 bị chặn.

### Cách giải quyết

Không có xử lý kỹ thuật mới. Lưu trạng thái cũ để truy vết, phân biệt kết quả hoàn thiện đặc tả với tiến độ triển khai; giữ nguyên tiêu chí live và yêu cầu xác minh môi trường trước khi thực hiện.

### Tài liệu và bước tiếp theo

Chỉ cập nhật next-task/report và hồ sơ đặc tả. Không sửa techs vì chưa thay đổi triển khai thực tế; không sửa SRS/source/config/runtime hoặc repo anh em. Khi người dùng giao triển khai, lưu task hiện tại, chuyển đặc tả TASK-011 sang task.md, đặt Đang thực hiện — 0/4 rồi thực hiện lần lượt. Chưa commit/push/merge hoặc chạy TASK-012.

---

## 2026-11-17T12:05:29+07:00 — TASK-010 — Hoàn tất nghiệm thu live một node: 4/4

- Trạng thái: Hoàn thành;4/4 nhóm nghiệm thu TASK-010. Không phải nghiệm thu toàn đồ án/ba node.

### Đã thực hiện

Môi trường QA riêng trên Linux: Wokwi VSCode/ESP32 thật mô phỏng → proxy/Mosquitto QA → FastAPI một worker/SQLite → dashboard Live Server. UI REJECTED/EXPIRED và TIMEOUT/ACK muộn, pending/open experiment qua restart/reload, broker outage/reconnect/no-replay/AUTO offline đều bổ sung bằng chứng live. Giữ các PASS Windows và không đo lại10 command→ACK cũ.

Phát hiện lỗi backend sau restart: availability retained đến trong lúc actor chờ queue bị xử lý với session cũ, node kẹt UNCONFIRMED_BOOT. Tạo nhánh `task/task-010-restart-sync`, sửa Service đồng bộ kết nối ngay sau dequeue/trước dispatch; thêm4 ca hồi quy, không đổi API/MQTT/schema/thuật toán. Node sau sửa trở lại fresh cùng boot, không restart ESP32.

### Kiểm tra và kết quả

PASS: hồi quy trước sửa2 FAIL/2 PASS → sau sửa72 Pytest/Ruff PASS/1 warning TestClient cũ;4 test lõi proxy PASS. UI và MQTT/Serial/API/SQLite thật xác nhận REJECTED/TIMEOUT, ACK muộn giữ trạng thái cuối, backend pending→TIMEOUT/BACKEND_RESTART, phiên mở còn sau reload rồi đóng. Khi broker QA dừng: mqtt0 vẫn AUTO, LDR đổi làm PWM25→0; reconnect cùng boot và0 publish lại command cũ, command mới APPLIED.

PASS10/10 sensor→dashboard dưới3s: median theo khoảng1417,832–1464,491ms, max2353,967–2401,274ms. T0 trusted key LDR Home/End, t4 DOM sau2rAF; clock có chặn sai số trước/sau, MQTT/API/DOM cùng boot/seq/ADC, không hidden và ADC nhìn thấy; video30fps bổ trợ. Hai pilot định trước tách khỏi10 mẫu. Foreground driver bị kết thúc143 sau8 mẫu, controller giữ nguyên và chỉ thu tiếp9/10; không bỏ mẫu hoặc chọn lại mẫu nhanh. Serial dùng cho AUTO offline, không lấy Serial receipt/HTTP RTT/command ACK làm sensor latency.

[Log, ảnh/video, audit và source công cụ](evidence/task-010/completion-20261117-105535/README.md). Snapshot cuối quick_check=ok, không còn pending/phiên QA mở. Cleanup đã dừng mọi dịch vụ/cửa sổ QA, không còn listener các cổng thử; bảo toàn dữ liệu/PASS cũ. Artifact firmware fresh/hash khớp nên không build lại.

### Vướng mắc

Đã giải quyết: CLI token hiện có bị Unauthorized; lỗi race session backend; proxy QA ban đầu nhầm hậu tố HTTP/MQTT; locator phiên kèm timestamp; bind kiểm ngay sau stop gặp TIME_WAIT. Không có vướng mắc còn chặn phạm vi TASK-010.

### Cách giải quyết

Dùng VSCode dự phòng đã chọn, không đăng ký/mua dịch vụ. Sửa race có bằng chứng tái hiện và kiểm live, giữ event session cũ bị loại. Sửa đúng công cụ/locator rồi kiểm lại phần còn thiếu, giữ log lỗi. Phân biệt LISTEN/connect_ex với TIME_WAIT khi xác minh cleanup. Preview có nền cửa sổ trong suốt được loại khỏi hồ sơ, video nghiệm thu quay hai cửa sổ opaque; dữ liệu timing không đổi.

### Tài liệu và bước tiếp theo

Cập nhật task/report/checklist/next-task, README, architecture/backend/testing/dashboard/simulation và hồ sơ completion; report cũ giữ nguyên từng byte ở phần đuôi. Backend README bổ sung hành vi/test72; source dashboard và C++ giữ nguyên, không đổi SRS hoặc toolchain. TASK-011 vẫn chờ đặc tả chính thức. Ba node/stability30phút, EX-series và bàn giao cuối chưa nghiệm thu. Không commit/push/merge.

---

## 2026-11-17T09:45:17+07:00 — TASK-010 — Rà soát tiến độ sau pull và cập nhật flow report

- Trạng thái TASK-010: Đang thực hiện; 2/4 nhóm nghiệm thu live. Lượt rà soát tài liệu hoàn tất 3/3 tiêu chí; không chốt hoàn thành TASK-010.

### Đã thực hiện

Đối chiếu main firmware `7e8f5c4` sau PR #3 với publication-status/final-status và bằng chứng đã pull. Nhóm 1 (một node xuyên suốt) và 3 (dữ liệu/restart/CSV/gap) PASS; nhóm 2 còn UI trạng thái lệnh cuối, broker outage/reconnect/no-replay/AUTO offline; nhóm 4 còn cảm biến → dashboard đủ 10 mẫu. Command → ACK đã có 10 lượt, median 686,217 ms/max 1002,001 ms. Sensor đã thử 5 lượt nhưng 0/10 mẫu đủ điều kiện; không tính thành hoàn thành một nửa. TASK-011 giữ Chưa bắt đầu, chờ đặc tả chính thức.

Cập nhật task/next-task và ghi chú checklist, thêm bản tổng hợp tiếng Việt có dấu vào testing/dashboard. Giữ nguyên ghi chú mất dấu, log và kết quả cũ. Repo dashboard local dùng API8000/chưa có trang ghi latency, khác bản Windows/API8001; ghi nhận để đối chiếu trước lượt live, không tự thay cấu hình. [Hồ sơ rà soát](evidence/task-010/review-20261117-094517/README.md).

### Kiểm tra và kết quả

PASS kiểm tra file mới tại máy này: 112/112 tệp của 4 manifest SHA256 khớp (31/24/24/33), 70/70 JSON TASK-010 đọc hợp lệ; trạng thái 2/4 và số liệu latency khớp JSON gốc. Ba repo sạch trước lượt tài liệu; checklist và bằng chứng cũ được bảo toàn, report cũ giữ nguyên từng byte ở phần đuôi. Kiểm tra liên kết, trạng thái tài liệu, phạm vi diff và git diff --check được lưu trong verification.json. Không chạy lại các bài live đã PASS, build, pytest hoặc Node; không tuyên bố kết quả live mới từ kiểm tra file.

### Vướng mắc

Không có vướng mắc chặn việc cập nhật báo cáo. Các tiêu chí TASK-010 còn PENDING: phương pháp đo sensor/render chưa ổn định và chưa đủ kiểm độ tin cậy/UI; một số ghi chú cũ mất dấu; source/config dashboard giữa máy local và bản live có khác biệt.

### Cách giải quyết

Dùng JSON gốc, manifest và bản tổng hợp khi bàn giao PR làm nguồn; thêm bản tổng hợp có dấu thay vì sửa raw evidence. Giữ nguyên trạng thái PENDING, xác nhận người vận hành và dữ liệu máy thu có nguồn riêng. Chuẩn bị phương pháp đo/cô lập kết nối và đối chiếu repo trước lượt live tiếp khi được giao; không mở thêm ca thử hoặc dừng dịch vụ trong lượt báo cáo này.

### Tài liệu và bước tiếp theo

Áp dụng quy trình development.md và tham chiếu SRS10.2/12. Task/report/checklist/next-task, techs/testing/dashboard và hồ sơ rà soát được cập nhật; không sửa SRS, firmware, backend/dashboard source, API hoặc schema. Không commit/push/merge; không tự thực hiện TASK-011.

---

# TASK-010 — Trạng thái khi bàn giao để mở PR

Người dùng đã cho phép add, commit và push nhánh `tuan` ở các repository có thay đổi. Người dùng sẽ tự tạo PR vào `main`; không merge hoặc force push.

TASK-010 đang thực hiện, đạt 2/4 nhóm nghiệm thu. Tích hợp một node và lưu trữ/lịch sử/phiên đo/CSV/gap/restart đã PASS theo bằng chứng trước. TIMEOUT/ACK muộn qua proxy và khôi phục MQTT1883 đã PASS. Backend dùng API8001, Dashboard5500; không đổi thuật toán hoặc MQTT schema.

Còn PENDING: UI trạng thái lệnh cuối, broker outage/reconnect/no-replay/AUTO offline và latency cảm biến đến Dashboard. Đã thao tác 5 lượt cảm biến nhưng chưa có đủ mẫu đạt điều kiện nghiệm thu; không khẳng định đã hoàn thành 10 lượt. Xem `run-20261116-195307/final-status.json`, `trial-05-summary.json` và `latency-events-cutoff.jsonl`. Xác nhận người dùng được phân biệt với dữ liệu máy thu trực tiếp. TASK-011 vẫn chờ đặc tả chính thức.

Dashboard chỉ đổi địa chỉ API sang8001 và bổ sung bộ ghi thử nghiệm live trong `tests/`. Bộ ghi còn giới hạn về timestamp/visibility và không phải tính năng production đã nghiệm thu. Backend không có thay đổi mã nguồn nên không tạo commit riêng.

Giữ SQLite và toàn bộ log tại máy. Hai stream đang ghi tiếp được loại khỏi Git bằng đường dẫn cụ thể trong `.gitignore`; các bản chụp bằng chứng đã chốt vẫn được commit. Không đưa `.env`, SQLite, môi trường Python hoặc firmware build vào commit. Kiểm tra cú pháp JavaScript, Python AST và `git diff --check`; không chạy lại kiểm thử live đã PASS.

Một số ghi chú trong đợt đo trước bị mất dấu khi truyền qua PowerShell. Dùng bản tổng hợp này và JSON gốc để đối chiếu; không sửa dữ liệu bằng chứng gốc hoặc xóa nhật ký cũ.


---

## TASK-010 ? Ch?t b?ng ch?ng, c?n2/4 nh?m PENDING

?? thao t?c5 l??t sensor, nh?ng0/10 m?u ??t ?? ?i?u ki?n nghi?m thu. L??t1 thi?u m? trang;2 browser b?o hidden;3 m?u c? tr??c marker;4 kho?ng1,469?6,081s c?t ng??ng3s, browser hidden d? ng??i d?ng x?c nh?n hai c?a s? lu?n nh?n th?y;5 ?? c? kho?ng t?c ??ng native48cm nh?ng render tr?/?i?u ki?n trang kh?ng li?n t?c, kh?ng d?ng kho?ng~203s l?m latency s?n ph?m b?nh th??ng. C?c l??t6?10 ch?a ch?y. Kh?ng th? suy ra ch? c?n5 thao t?c n?a l? ho?n t?t. B? ?o ch?a ?n ??nh ?? g?y nhi?u thao t?c cho ng??i d?ng; kh?ng y?u c?u thao t?c c?m bi?n th?m trong ??t n?y.

Ch?t4 nh?m: nh?m1 t?ch h?p m?t node PASS; nh?m2 ?? tin c?y PENDING (UI terminal command, outage/reconnect/no-replay/AUTO offline); nh?m3 d? li?u/restart/CSV/gap PASS; nh?m4 latency PENDING (10 command?ACK PASS c?; sensor ch?a ?? m?u). Kh?ng ch?y l?i PASS c?. Backend healthOK/database/broker/queue true. Gi? nguy?n SQLite v? ?ng d?ng ?ang ch?y, kh?ng command m?i. TASK-011 ch? ??c t?.

final-status.json v? snapshot latency-events-cutoff.jsonl ch?t b?ng ch?ng hi?n c?; JSONL g?c v?n ?ang ???c collector ghi. Tra c?u PID b?ng Windows CIM b? Access denied; kh?ng d?ng process ch?a x?c minh. Snapshot l? prefix ??y ?? d?ng, kh?ng ch?nh s?a d? li?u g?c. Kh?ng commit/push/merge ho?c thay schema/thu?t to?n. Chu?n b? outage ch? d?ng ? ph??ng ?n proxy ri?ng cho Backend; ch?a c? ph??ng ?n c?t ri?ng ???ng MQTT node ?? tin c?y, kh?ng d?ng Mosquitto d?ng chung.

Xem evidence/task-010/run-20261116-195307/final-status.json.

---

## TASK-010 ? ??i chi?u l??t4 (2026-11-16T21:04:57+07:00)

L??t4 ?? thu ???c baseline seq1239/distance69,96552cm, marker13:58:59.4735Z, MQTT/APIseq1240/distance151,1035cm13:59:04.072285Z, DOM ??ng151,1cm sau hai rAF13:59:05.5443Z. B? ghi marker-baseline-v2 ?? ch?n m?u c? th?nh c?ng. Kho?ng sensor?render1,469216?6,080600s c?t ng??ng3s, n?n INCOMPLETE. MQTT?render kho?ng1,472s ch? l? ?o?n truy?n sau MQTT, kh?ng thay sensor latency. ??ng page_id15197d89-1b03-44dd-ad2e-77abbb4505b8 b?o hidden13:59:03.2071Z?visible13:59:05.4744Z.

Ng??i d?ng x?c nh?n trang ?o lu?n nh?n th?y b?n c?nh Wokwi; l?u ri?ng trial-04-user-observation.json. Kh?ng quy nguy?n nh?n hidden cho ng??i d?ng chuy?n tab. Ch?a x?c ??nh nguy?n nh?n kh?c bi?t gi?a quan s?t ng??i d?ng v? Page Visibility. Kh?ng s?a log ho?c k?t lu?n PASS3s. trial-04-summary.json gi? ??y ?? m?c/ngu?n. B? ph?n t?ch ban ??u g?p KeyError seq v? x?t c? MQTT availability; ?? gi?i h?n ??ng topic /telemetry, ch?y l?i tr?n log hi?n c? th?nh c?ng, kh?ng ch?y l?i thao t?c sensor.

Sau khi reset kernel v? kh?i t?o m?i, Computer Use list_apps/??c accessibility kh?ng screenshot ho?t ??ng tr? l?i (<1s cho l?n ??c). M? ph?ng41:11.585, t?c ??12%; b?ng Distance hi?n ??ng. Ch? ?? ngh? m? b?ng ?? quan s?t th? ??ng v? thu h?p sai s? ? l??t k? ti?p, ch?a ch?y l??t5. Kh?ng ?i?u khi?n sensor b?ng tool, kh?ng d?ng Wokwi/Mosquitto/Backend. Hai nh?m1/3 gi? PASS c?; nh?m2/4 c?n PENDING, ch?a ??10 m?u sensor latency. Kh?ng commit/push/merge; TASK-011 ch?a tri?n khai.

B?ng ch?ng: evidence/task-010/run-20261116-195307/README.md.

---

## TASK-010 ? Ki?m tra nh?n qu? l??t3 (2026-11-16T20:55:02+07:00)

L??t3: ng??i d?ng x?c nh?n b? ghi hi?n ?? ghi. ??i chi?u c?ng boot3268eb79/seq1210/distance50,7069cm: MQTT13:51:09.498210Z, marker13:51:16.7248Z, render13:51:17.4558Z. M?u ??n tr??c marker7,2266s n?n INCOMPLETE; kh?ng d?ng kho?ng ?m ho?c render-marker0,731s l?m sensor latency. B?ng ch?ng g?c gi? nguy?n; trial-03-summary-causal-audit.json l? k?t lu?n s?a sau ki?m tra nh?n qu?, c?n trial-03-summary.json gi? b?n ph?n t?ch ??u.

B? ghi test ???c s?a marker-baseline-v2: baseline MQTT t?i l?c b?m; t? ch?i baseline ?? ? target, ch? nh?n seq m?i c?ng boot v? API last_seen sau c?n tr?n timestamp marker ?? ??ng b?. Analyzer ?? lo?i m?u seq1210 c? b?ng causal check, assertion tr?n b?ng ch?ng th?t PASS; JS node --check PASS. Kh?ng ph?i k?t qu? nghi?m thu live c?a b? ghi m?i. Ch?a c?10 m?u latency h?p l?. L??t4/150cm chu?n b?; ch? t?i l?i tr??c t?c ??ng. Kh?ng ch?y l?i PASS c?, kh?ng ??i firmware/schema/ng??ng3s, kh?ng restart backend/broker, kh?ng commit/push/merge; TASK-011 v?n ch? ??c t?.

Xem evidence/task-010/run-20261116-195307/README.md.

---

## TASK-010 ? ??i chi?u l??t2, chu?n b? marker l??t3

## C?p nh?t l??t2 v? ph??ng ph?p kh?ng ph? thu?c native UI

Ng??i d?ng x?c nh?n trang ?? ghi l??t2. Raw accessibility cho th?y slider cu?i149cm, gi? ?n ??nh ??n khi observer d?ng; `trial-02-derived-action.json` suy ra m?c t? hai b?n ghi th?t k?m nguy?n d? li?u ngu?n, kh?ng s?a JSONL. API/MQTT/DOM c?ng boot3268eb79/seq1172/distance151,1035cm. Trang c? page_id5e90c658-15b9-4a77-87ee-0ba963c69a98; ch?nh trang n?y chuy?n hidden13:41:29.3748Z v?13:41:33.0034Z tr??c render13:41:36.0827Z. K?t lu?n INCOMPLETE, kh?ng ghi PASS3s. Kh?ng y?u c?u l?m l?i l??t2 trong b??c hi?n t?i.

Native observer ch? ??ng150cm n?n kh?ng ph?t sensor-action-observed; tool call timeout300s v? phi?n Computer Use b?o ?? k?t th?c, kh?ng g?i ti?p native UI. B? ph?n t?ch d?ng b?n suy ra t? raw cho l??t2. B? ghi m?i c? n?t B?t ??u: marker browser l? c?n d??i tr??c t?c ??ng; MQTT th?t ??u ti?n nh?n gi? tr? m?i l? c?n tr?n sau t?c ??ng. t0 ???c gi? d?ng kho?ng, kh?ng d?ng MQTT l?m timestamp t?c ??ng ch?nh x?c. Kh?ng thay firmware, schema, chu k? hay ng??ng3s. Kho?ng c?t3s v?n INCOMPLETE; kh?ng h?a ph??ng ph?p n?y cho ?? ?? ch?nh x?c trong m? ph?ng ch?m. Kh?ng c? marker th? l??t require_marker kh?ng ghi render-match. L??t3/50cm ?? chu?n b?, ch? n?p trang m?i; ch?a ??i sensor.

Ki?m tra `node --check` b? ghi JS PASS. B? ph?n t?ch hi?n0 m?u nghi?m thu h?p l?: l??t1/2 INCOMPLETE,3?10 PENDING. Hai nh?m nghi?m thu1/3 gi? PASS c?; nh?m2/4 c?n PENDING. Kh?ng ch?y l?i ca ?? PASS, kh?ng th? outage ho?c d?ng broker, kh?ng commit/push/merge. TASK-011 ch?a tri?n khai.

B?ng ch?ng: evidence/task-010/run-20261116-195307/trial-02-summary.json v? README.md.

---

## TASK-010 ? ?o live v? quan s?t UI, 2026-11-16T20:36:33+07:00

## C?p nh?t ?o live l??t1

?? quan s?t ng??i d?ng k?o Distance100?50cm (qua c?c gi? tr? trung gian), kh?ng ph?t command. MQTT seq1138/boot3268eb79/distance50,7069 t?i13:34:34.735312Z; Dashboard ghi ??ng50,7cm sau hai rAF t?i13:34:45.1142Z. `trial-01-summary.json` gi? c?c m?c th?c. K?t qu? INCOMPLETE v? nghi?m thu latency: c? visibility hidden/visible nh?ng c?c event c? ch?a mang m? trang, kh?ng x?c ??nh ch?c trang ?o n?o b? ?n. Kho?ng m? t?12,873?13,652s ch?a c?ng sai s? clock, kh?ng ???c d?ng l?m k?t lu?n PASS/FAIL3s. Kh?ng x?a ho?c s?a log c?. B? ghi b? sung page_id/time_origin/visibility cho m?i event browser; ch? t?i l?i tr??c l??t2/150cm. Ch?a c?10 m?u h?p l?.

B?n nh?m hi?n t?i: (1) t?ch h?p m?t node PASS theo h? s? tr??c; (2) ?? tin c?y PENDING ? timeout/ACK mu?n PASS c?, UI stale/kh?a/ph?c h?i ?? quan s?t live, c?n terminal command UI/broker reconnect/AUTO offline; (3) d? li?u/phi?n/CSV/gap/restart PASS theo h? s? tr??c; (4) latency PENDING ? command?ACK10 m?u PASS c?, sensor?Dashboard ch?a ??10 m?u h?p l?. TASK-011 v?n ch? ??c t?.

Chu?n b? outage: proxy ri?ng ph?a Backend c? th? ki?m m?t/ph?c h?i k?t n?i Backend m? kh?ng d?ng Mosquitto1883 d?ng chung. N? kh?ng c?t k?t n?i Wokwi?1883, do ?? kh?ng ?? ch?ng minh AUTO offline ? node. Ch?a th?c hi?n outage trong l??t n?y; c?n ph??ng ?n c? l?p ri?ng ???ng k?t n?i node tr??c khi k?t lu?n ti?u ch? ??. Kh?ng thay c?u h?nh1883 ?ang ho?t ??ng.

B?ng ch?ng: [run-20261116-195307](evidence/task-010/run-20261116-195307/README.md). Kh?ng commit/push/merge.

---

## 2026-11-16T19:46:02+07:00 — TASK-010 — TIMEOUT/ACK muộn thật qua proxy và khôi phục: PASS

- Trạng thái: Đang thực hiện;2/4 nhóm nghiệm thu toàn TASK-010. Lượt kiểm proxy được giao đã PASS, không chạy lượt thứ hai.

### Đã thực hiện

Đọc lại harness/config và thông báo rollback trước thay đổi. Người dùng dừng graceful Backend43632; agent khởi động tạm32248/API8001/workers1/cùng SQLite/MQTT1884 qua proxy44580. Wokwi/Mosquitto giữ1883, không Pause/init_db/xóa dữ liệu. Preflight hai telemetry932/933 qua proxy/healthOK trước một POST AUTO.

### Kiểm tra và kết quả

PASS command0d8f20f5-4700-4be4-b5cc-37b555396adc: gửi19:37:15.226902+07, retry duy nhất19:37:17.268317; GET đầu TIMEOUT19:37:25.308628, script quan sát10,088672s. ACK firmware thật tới proxy sớm, được thả19:37:27.254744/27.255748 ở mốc12s từ lệnh đầu, hash raw bytes lúc giữ/thả khớp. Hai ACK vào SQLite LATE_OR_DUPLICATE; API/DB cuối TIMEOUT/ACK_TIMEOUT/attempts2. Một POST/một ID mới/hai MQTT publish cùng payload; không có retry/replay khác trong capture và sau khôi phục. [Log, audit, thời gian và giới hạn](evidence/task-010/run-20261116-193157/README.md).

Backend đã khôi phục14144→MQTT1883/API8001/workers1, health/database/broker/queue true, dropped0. Chỉ sau healthOK/proxy0 client mới dừng proxy; recorder dừng sau quan sát thêm. Dashboard HTTP/config/CORS PASS và người dùng xác nhận ONLINE/AUTO NIGHT25/LDR3917/boot3268eb79/seq963→969/dữ liệu mới19:44:21, không gửi thêm lệnh. Bảo toàn907 telemetry/14 command/21 ACK/245 alert/3 phiên cũ; chỉ thêm1 command và2 ACK đúng bài test, không mất bản ghi cũ.

### Vướng mắc và cách giải quyết

Ctrl+C qua PTY/pipeline không đến Uvicorn; control event trong riêng console Backend tạm đã cho application shutdown hoàn tất, không force-kill Backend hoặc dừng broker/Wokwi. Proxy chỉ bị dừng khi không còn client/frame chờ. Log status proxy là snapshot cuối trước dừng, trạng thái hiện tại xác nhận qua network và proxy-stop-action. Backend phục hồi vẫn chạy, nên manifest dùng bản sao log cố định và loại log đang tăng.

Không đổi thuật toán/schema hoặc dùng ACK fixture. Trễ12s là fault injection tính từ lệnh đầu, không gọi là mất ACK tự nhiên. Không dựng timeout_at vì DB không có cột này; ghi mốc quan sát thật. Nhóm2 còn broker outage/reconnect/no-replay lệnh chờ/AUTO offline/UI terminal, nhóm4 còn sensor→Dashboard10 lượt; chưa4/4.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing/backend và evidence; checklist task hoàn thành giữ nguyên. Giữ các hồ sơ PASS/INCOMPLETE cũ nguyên byte. TASK-011 tiếp tục chờ đặc tả. Không commit/push/merge/xóa DB/log; report cũ giữ nguyên làm phần đuôi.


---

## 2026-11-16T19:25:44+07:00 — TASK-010 — restart giữ dữ liệu và phân tích ca TIMEOUT chưa đạt

- Trạng thái: Đang thực hiện;2/4 nhóm nghiệm thu, nhóm1/3 PASS theo phạm vi giao việc.

### Đã thực hiện

Người dùng xác nhận Backend18828 dừng,43632 chạy8001/workers1, không init_db/xóa SQLite, giữ Wokwi/Mosquitto. Agent ghi PID/start/listener, capture MQTT/API75s sau restart và SQLite read-only; đối chiếu snapshot ngay trước lượt này với snapshot cuối trước restart. Không chạy lại OPEN_LOAD/MANUAL60s/build/68 Pytest đã PASS.

### Kiểm tra và kết quả

PASS quick_check/schema1/cùng đường dẫn DB;760 telemetry cũ giữ nguyên,13 command/20 ACK còn nguyên từng trường,106 alert và3 phiên còn. OPEN_LOAD30/33 giữ đúng thời điểm đóng. CSV3 phiên tải lại sau restart giống từng byte/SHA256; metadata cấu hình/notes/start/end khớp. Backend run ID đổi26989c18…→44cc197e…, firmware boot3268eb79 giữ nguyên/AUTO NIGHT25. Ranh giới row765→766 có continuity mới; history/stats cửa sổ hai đầu mút có DISCONTINUITY và0 năng lượng/valid_uptime, không nội suy qua gap. [Log/snapshot/CSV/audit](evidence/task-010/run-20261116-190549/README.md).

### Vướng mắc và cách giải quyết

Recorder trước đó kết thúc trước thao tác restart, nên không có log API outage/STALE ngay lúc khởi động; không tái tạo log quá khứ. Không có lệnh PENDING/phiên mở tại restart, không chốt no-replay/khôi phục các tình huống này. Nhóm2 còn timeout/ACK muộn, broker disconnect/reconnect/no-replay/AUTO offline và UI terminal; nhóm4 còn sensor→Dashboard10 lượt. Tốc độ mô phỏng/độ phủ thấp ở lượt trước vẫn là giới hạn, không đổi ngưỡng để ép PASS.

Người dùng chạy timeout-check.py nhưng INCOMPLETE. Đã đọc nguyên log/summary và SQLite/API: command7aa224a2… có APPLIED/ACK ACCEPTED sau1,0231297s, attempts1, không retry. observed_timeout_wall_s≈1,297 là lúc script thấy APPLIED, không phải timer timeout Backend. Không có mốc Pause/halt MCU nên chưa phân biệt thao tác muộn với transport tiếp tục xử lý. Giữ nguyên source/log của phép thử, không yêu cầu lặp lại cửa sổ2s.

Đã chuẩn bị ack-delay-proxy.py/ack-delay-check.py: proxy local1884 giữ nguyên ACK thật12s trong khi chuyển telemetry bình thường, driver tự gửi một AUTO sau telemetry mới, không cần Pause. Công cụ PASS kiểm offline framing/không chặn frame thường/byte preservation và diagnostics roundtrip thật qua broker; không giả ACK hoặc gọi đó là TIMEOUT live PASS. Proxy smoke20s đã dừng. Chưa chuyển Backend hiện tại sang proxy hoặc tự restart; runbook ghi rõ cách tạm route1884 rồi khôi phục1883/giữ DB một worker. Không mở phiên đo mới, không dừng Backend/Wokwi/broker.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing/backend và hồ sơ mới. Checklist task hoàn thành giữ nguyên vì TASK-010 chưa4/4. TASK-011 chờ đặc tả. Không commit/push/merge/xóa DB/log/sửa schema hoặc thuật toán; report cũ giữ nguyên byte làm phần đuôi.


---

## 2026-11-16T19:00:00+07:00 — TASK-010 — đối chiếu OPEN_LOAD và phục hồi đã chạy

- Trạng thái: Đang thực hiện;1/4 nhóm nghiệm thu. OPEN_LOAD/phục hồi được đánh dấu PASS trong nhóm3, không chạy lại.

### Đã thực hiện

Đối chiếu xác nhận người vận hành về NIGHT/PIR0/AUTO25, current_adc0 gây OPEN_LOAD và tải4095 phục hồi; Serial báo OK tại uptime1340431ms/duty64/mqtt1, người dùng đã chụp ảnh. Chưa thấy file ảnh trong repo. Xuất SQLite read-only và API history/alerts/stats, giữ rõ nguồn bằng chứng. [Hồ sơ lượt này](evidence/task-010/run-20261116-184903/README.md).

### Kiểm tra và kết quả

PASS:16 mẫu quanh hai đợt đều AUTO/NIGHT/NONE/target25/applied25, cùng boot3268eb79. Hai OPEN_LOAD alert30/33 có thời gian mở/đóng; đợt cuối bắt đầu seq683/uptime1323338ms/current_adc0, hết lỗi seq692/uptime1340238ms/current_adc4095, đóng alert33 tại11:46:15.004905Z. Mốc telemetry sớm hơn Serial193ms; giữ cả hai, không đổi mốc hoặc suy exact timer từ mẫu thưa. Stats cùng cửa sổ loại FAULT_OR_RECOVERY/LOAD_CALIBRATION/STATE_CHANGE và DISCONTINUITY đúng dữ liệu.

Capture cũ kết thúc trước thao tác fault, vì vậy không có raw MQTT quá khứ; payload telemetry quá khứ lấy từ SQLite/API thật. Capture Serial mới sau phục hồi chỉ đọc, không gửi lệnh:48 dòng, gồm19 CONTROL AUTO25/duty64/faultOK/mqtt1. Clock node/wall trung vị≈0,1603; telemetry thực quan sát trung vị12,70s/max15,62s, có thể quá ngưỡng freshness10s dù mqtt1. Không sửa ngưỡng hoặc suy thành latency sensor→Dashboard.

### Vướng mắc và cách giải quyết

Đã lưu baseline, mở phiên3/capture600s và hướng dẫn người dùng Ctrl+C Backend/chờ5s/khởi động lại8001/workers1; không dừng cưỡng bức tiến trình người dùng. Restart chưa được chốt nếu không có bằng chứng thao tác/API outage/run mới. Timeout/ACK muộn, mất broker/reconnect/no-replay/AUTO offline, UI fault/terminal states và latency cảm biến→render vẫn cần phối hợp. Không chạy lại OPEN_LOAD/MANUAL60s/build/68 Pytest đã đủ xác nhận.

Cuối lượt: capture600s kết thúc,0 API outage/run ID không đổi/chưa có xác nhận restart, nên restart PENDING. Đã đóng riêng phiên3 và dừng recorders. CSV phiên3 có50 mẫu NIGHT6W, API/stats khớp;48 boundary gap không nối năng lượng, tổng0,0033416667Wh. Coverage chỉ1,534987%/valid_uptime2,005s; saving75% chỉ trên tập hợp hợp lệ nhỏ, không đại diện toàn khoảng. Bản ghi cũ còn đủ trong khoảng quan sát; không gọi là đã bảo toàn qua restart.

Audit lần đầu gặp lệch precision ở mép truy vấn ISO; đã sửa riêng script kiểm chứng dùng mép có đệm rồi chạy lại trên dữ liệu cũ PASS. Mở Serial lần đầu dùng write_timeout không được RFC2217 hỗ trợ; đã bỏ tùy chọn, giữ log lỗi và capture mới. Không sửa firmware/schema/thuật toán, không ghi log giả.

### Tài liệu và bước tiếp theo

Cập nhật task.md/next-task.md/techs/testing và evidence. Checklist task hoàn thành giữ nguyên vì TASK-010 chưa4/4. TASK-011 vẫn Chưa bắt đầu, chờ đặc tả chính thức. Không commit/push/merge, không xóa SQLite/log; report cũ giữ nguyên byte làm phần đuôi.


---

## 2026-11-16T18:41:30+07:00 — TASK-010 — bổ sung bằng chứng tích hợp live một node

- Trạng thái: Đang thực hiện;1/4 nhóm nghiệm thu, nhóm2–4 còn PENDING.

### Đã thực hiện

Ghi riêng [xác nhận người vận hành](evidence/task-010/run-20261116-180648/user-confirmation.md) về Python3.12/68 Pytest/Ruff/SQLite/build P3/A3/prepare/Dashboard MANUAL80/PWM80/tự AUTO60s; không chạy lại các bài này. Agent thu API8001/MQTT1883/SQLite read-only/hash build và mô phỏng; Dashboard5500 giữ cấu hình cổng8001 đã được người dùng chọn. Không sửa mã ứng dụng, MQTTv1, thuật toán, ngưỡng; không xóa DB/log hoặc commit/push/merge.

### Kiểm tra và kết quả

PASS: health OK, node_01 ONLINE/FRESH, node_02/03 UNKNOWN; singleton DB lock/quick_check/schema1, BIN/ELF khớp. SQLite tìm lại2 command MANUAL80 APPLIED/ACK và32 mẫu PWM80. PASS input sai422/node_02 offline409/command lạ404, pending guard409;3 reject wire đúng reason; cache lệnh AUTO sau deadline/ID trùng đổi nội dung không ghi đè cache gốc. Đo10/10 command→ACK từ server sent_at/ack_at có ACK MQTT: median686,217ms/max1002,001ms.

Hai phiên agent tạo đã đóng. Phiên1: CSV12 mẫu,0,0018346Wh, coverage92,2025129083%, valid_uptime2,284s; Phiên2: CSV423 mẫu DAY0W. API/history/CSV/stats/quality/clock khớp, phép tính điện năng độc lập PASS. Không phải EX-series hoặc nghiệm thu ba node. [Bộ log, CSV, audit, giới hạn](evidence/task-010/run-20261116-180648/README.md).

### Vướng mắc

Chưa nhận phản hồi thao tác fault Wokwi. Capture420s không có OPEN_LOAD hoặc API outage, chưa test restart. GUI observation hết thời gian chờ cấp quyền, không có ảnh mới. PENDING timeout/ACK muộn/UI REJECTED-TIMEOUT, mất API/broker/reconnect/no-replay/AUTO offline, OPEN_LOAD/phục hồi, restart giữ dữ liệu/gap, latency cảm biến→Dashboard10 lượt.

SQLite ban đầu có20 OFFLINE alert đã đóng;187 cặp có21 gap nhận≥10s thực, max13,83255s. Cần kiểm tốc độ mô phỏng/kết nối, chưa kết luận nguyên nhân. Probe cache lần đầu dùng nhầm chuỗi deadline HTTP trên MQTT nên INVALID_COMMAND; đã sửa riêng script bằng chứng sang JSON integer, chạy lại PASS với tag mới, giữ cả log lỗi. Firmware/schema không sửa.

### Cách giải quyết

Giữ Backend/Wokwi/Dashboard đang chạy; không dừng cưỡng bức tiến trình người dùng. Đã đóng riêng phiên1/2 và kết thúc capture. Ca tiếp theo cần người vận hành phối hợp pause/resume Wokwi để test timeout, tạo fault/phục hồi và Ctrl+C/restart Backend cùng DB trong khi agent capture; không thực hiện trước khi capture mới được bật. Đo sensor→UI cần timestamp thao tác và render thật, không thay bằng HTTP RTT hoặc MQTT→API.

### Tài liệu và bước tiếp theo

Cập nhật task.md, techs/testing/backend và next-task.md; checklist task hoàn thành giữ nguyên vì TASK-010 chưa đủ4/4. TASK-011 chưa có đặc tả chính thức, ghi Chưa bắt đầu/0/0, không tự suy P6/P7. Nội dung report cũ được giữ nguyên byte làm phần đuôi; manifest/preservation được lưu trong thư mục lượt này.


---

## 2026-11-16T14:18:00+07:00 — TASK-009 — Dashboard HTML/CSS/JS qua Live Server

- Trạng thái: Hoàn thành phạm vi code/test/hướng dẫn P5/A5.
- Tiến độ:4/4 nhóm nghiệm thu.

### Đã thực hiện

Tạo DoAn/dashboard Git riêng, HTML/CSS/JS ES modules/SVG, theme sáng Data-Dense theo ui-ux-pro-max;5 view tổng quan/tuyến đèn/chi tiết, history, alerts, experiments/CSV. Polling không chồng, pause hidden/abort, draft và telemetry tách riêng, điều khiển chỉ gửi khi Áp dụng, ACK/PWM/unknown/stale rõ; giữ uint64/UTC/gap. Cấu hình VS Code Live Server5500, không npm/build/framework/CDN để chạy. Backend thêm GET list/detail experiments, history.continuity và CORS5500 giữ5173; không đổi MQTT/SQLite schema/năng lượng. SRS cập nhật đúng stack/API do người dùng chốt. Không commit/push/deploy hoặc sửa firmware/toolchain.

### Kiểm tra và kết quả

PASS16 Node test; backend tại repo bàn giao Ruff check/format và68 Pytest/1 warning cũ; OpenAPI11 paths/12 thao tác. Playwright18 kiểm tra luồng chính +8 bổ sung PASS trên engine Live Server2.2.0 từ extension5.7.10, API/SQLite thật/transport giả, ảnh có nhãn fixture. Responsive375/768/1024/1440, keyboard/range, reduced motion, command/draft, history/alerts/experiment/reload/CSV và API mất/phục hồi/no-retry. REJECTED/TIMEOUT ở pha bổ sung được mock. Smoke cuối ở repo bàn giao:0 console error/0 uncaught exception. Copy/hashes khớp manifest; dịch vụ QA đã dừng. [Toàn bộ log/ảnh/scripts/giới hạn](evidence/task-009/README.md).

Chưa chạy MQTT/Paho/socket/Wokwi thật, VS Code Go Live thao tác tay/Windows, latency10 lượt, ba node30phút hoặc EX-series. Không build lại firmware vì không đổi source; không ghi tích hợp PASS từ fixture.

### Vướng mắc

Không có vướng mắc còn chặn phạm vi bàn giao. Trong QA, ảnh/log từng kích hoạt Live Server reload; một assertion ban đầu chờ PWM ngay sau ACK chưa đúng hợp đồng.1 deprecation warning TestClient/HTTPX đã tồn tại. Repo dashboard/backend nằm ngoài writable root.

### Cách giải quyết

Thêm ignoreFiles/ignore output/tests/Markdown cho Live Server, chạy lại browser đạt; tách chờ ACK và telemetry trong kiểm tra. Giữ dependency pin và warning rõ, không nâng toolchain. Ghi hai repo cùng cấp bằng quyền công cụ, guard hash gốc và xác minh sau copy để bảo toàn công việc có sẵn.

### Tài liệu và bước tiếp theo

README ba repo, dashboard design-system, techs/dashboard/backend/architecture/testing/development, SRS1.1, task/checklist/evidence cập nhật. Đề xuất TASK-010 kiểm chứng một node xuyên suốt MQTT–backend–dashboard trước khi mở rộng ba node; chỉ lập đề xuất, chưa thực hiện.

---

## 2026-11-16T13:17:56+07:00 — TASK-008 — Backend, SQLite và API P4/A4

- Trạng thái: Hoàn thành4/4 đầu ra code/test/OpenAPI/hướng dẫn; live A4 chưa chạy tại máy này.

### Đã thực hiện

Tạo DoAn/backend cùng cấp firmware với Git/venv riêng, không remote/commit/push. Collector MQTTv1/Pydantic strict, actor một SQLite writer/WAL/version/OS lock, persistence/quality/boot/alerts, API10 endpoint, command/ACK/retry/timeout không replay, năng lượng/baseline/coverage/experiment/CSV. Khóa dependency sau smoke; có README Linux/Windows và runbook live, không dashboard.

### Kiểm tra và kết quả

PASS tại thư mục bàn giao:66 Pytest/0.99s, Ruff lint/format21 file, pip check, init DB schema1 chạy2 lần an toàn, OpenAPI10 endpoint có response models.1 Starlette TestClient deprecation warning không bị ẩn. [Log/manifest/OpenAPI/giới hạn](evidence/task-008/README.md). Tất cả test MQTT/clock dùng fixture và DB tạm; không Wokwi/broker/Windows/ba node thật. Không build firmware vì không sửa code firmware.

### Vướng mắc

Không có vướng mắc còn chặn đầu ra được giao. DNS pip và ghi thư mục ngoài workspace ban đầu cần quyền; đã được cấp và xử lý. Tích hợp live và warning compatibility giữ rõ trong tài liệu.

### Cách giải quyết

Virtualenv riêng, dependency pin, một DB writer + OS lock; không tự nâng firmware/toolchain hoặc đổi giao thức. Kiểm ACK đúng10s, read-only/closed DB, no outgoing replay qua client Paho mới, precision64 và clock riêng; test cuối PASS. Live bàn giao người vận hành qua README, không giả evidence.

### Tài liệu và bước tiếp theo

Cập nhật backend.md, architecture/mqtt/testing/development/README và task/checklist/next-task; giữ nguyên task007/evidence cũ và mọi byte report bên dưới. Đề xuất TASK-009 dashboard dùng ui-ux-pro-max, chưa triển khai. Git hai repo chưa commit/push.

---

## 2026-11-16T12:02:01+07:00 — TASK-007 — MQTT nghiệp vụ một node P3/A3

- Trạng thái: Hoàn thành 5/5 đầu ra code/test/hướng dẫn; live A3 chưa chạy tại máy này.

### Đã thực hiện

Thêm MqttProtocol/CommandProcessor/cacheFIFO32, MqttMailbox queue8/snapshot; nối FirmwareApp core1 với Connectivity core0. Telemetry uptime64/boot/seq/current-power/null/fault, strict JSON command/deadline/dedup, ACK sau controller nhận target, availability/LWT/reconnect. Pin ArduinoJson7.4.2 sau smoke/build, giữ toolchain/P2/diagnostics. Có generator command và runbook Linux/PowerShell A3-01…08.

### Kiểm tra và kết quả

PASS mới: 5 suite C++ host,11 unittest Python (7 RFC+4 generator), formatter14 file; build esp32dev SUCCESS exit0/6.73s, RAM53644/327680, flash933143/1310720; copy/hash BIN/ELF đạt. [Log và giới hạn](evidence/task-007/README.md). Không chạy Wokwi, Docker/broker hoặc kiểm mạng/RTOS thật; không tuyên bố live PASS.

### Vướng mắc

Không có vướng mắc còn chặn đầu ra được giao. Các assertion fixture/API trong phát triển đã sửa và chạy lại PASS. Timeout phiên dài lịch sử và live A3 còn cần xác nhận theo runbook.

### Cách giải quyết

Dùng ArduinoJson đúng API phiên bản pin, test JSON đầy đủ/NUL, cache invalid-ID reuse và session flush; không đổi SRS/schema hoặc nâng toolchain. Chuẩn bị hướng dẫn để máy dev kiểm chứng live, không tự chạy lại P2.

### Tài liệu và bước tiếp theo

Cập nhật mqtt/firmware/testing/simulation/architecture/development, task/checklists/next-task; bản task P2 và evidence cũ giữ nguyên. Đề xuất backend/A4 sau này theo hợp đồng/fixture; nghiệm thu tích hợp phụ thuộc live A3. Không commit/push. Mọi byte report cũ giữ nguyên bên dưới.

---

## 2026-11-16T11:28:57+07:00 - TASK-006 - Save implementation on tuan

- Work: fetched origin; verified TASK-005 PR #1 merge commit 9dbff58 preserves b24ac60; switched to tuan and fast-forwarded to origin/main without creating another merge commit. Preparing the requested TASK-006 commit; no push.
- Checks/results: backed up all 48 changed paths (46 existing files, 2 deletions), verified SHA-256 before/after branch switch. Build and host tests passed in the preceding review; this Git-only operation does not rerun Wokwi or touch the broker. Select only TASK-006 changes; leave TASK-005 evidence unchanged.
- Status: TASK-006 evidence remains PENDING as documented in acceptance-review.md. Saving implementation does not complete acceptance.
- Blockers: None for Git synchronization. Missing live evidence and its documented resolution remain unchanged; no unsupported PASS results added.

## 2026-11-16T11:21:17+07:00 — TASK-006 — Đối chiếu evidence live và kế hoạch commit tuan

- Trạng thái: Đang thực hiện4/5; toàn task PENDING hồ sơ, chưa chốt PASS.
- Đã làm: đọc log RFC2217, tìm CONTROL trên toàn repo ngoài cache/build; xác minh MANUAL80/applied80 và timeout23399→83399ms/mqtt1/RESULT PASS. Lưu trích đoạn fault/timeout do người dùng cung cấp vào báo cáo với nguồn rõ ràng, không tạo log gốc giả.
- Kiểm tra/kết quả: build esp32dev SUCCESS exit0 3.28s, RAM48028/327680, flash912763/1310720; bốn suite C++ host PASS,7 unittest RFC PASS; git diff --check đạt. Chưa thấy file live AUTO ba vùng/PIR-VEHICLE/OPEN_LOAD/timeout/reconnect ngoài lời xác nhận và trích đoạn người dùng.
- Vướng mắc/cách giải quyết: thiếu hồ sơ để đối chiếu độc lập các ca nêu trên; ưu tiên xuất dữ liệu đã có, không bắt kiểm thử lại toàn bộ hoặc thay đổi thuật toán. Giữ TASK-005/evidence cũ và Docker nguyên trạng.
- Git: đang main, local tuan và origin/tuan cùng b24ac60; chưa stage/checkout/commit/push/merge. Đề xuất switch tuan cùng base rồi commit chọn lọc, chỉ push khi được đồng ý. [Báo cáo, ma trận và kế hoạch](evidence/task-006/acceptance-review.md).

---

## 2026-11-16T11:03:41+07:00 — TASK-006 — Chuẩn bị Serial TCP RFC2217 cho MANUAL

- Đã làm: chỉ thêm rfc2217ServerPort=4000 trong cấu hình Wokwi chính; pyserial3.5 đã có trong Python PlatformIO. Tạo script gửi MANUAL/AUTO có LF, PROBE, ghi RX/TX timestamp và kiểm tra timeout60s theo uptime; không sửa thuật toán.
- Kiểm tra: 7 test Python offline PASS, gồm bytes newline và nhận xác nhận giả lập. Cấu hình hiện trước restart chưa có listener4000; chưa gửi lệnh live hoặc kết luận MANUAL PASS. Không cần build lại vì không sửa firmware.
- Vướng mắc: Terminal Wokwi không nhận input theo báo cáo người dùng; chưa xác minh nguyên nhân frontend. Giải quyết bằng RFC2217 chính thức, yêu cầu Stop/Start Wokwi đúng một lần rồi kiểm tra port/PROBE. Giữ TASK-006 Đang thực hiện4/5.
- [Lệnh CMD và tiêu chí](../techs/simulation.md). Không Docker/TASK-005/commit/push, không cài hoặc đổi dependency. Các test transport giả không phải evidence Wokwi.

---

## 2026-11-16T10:41:14+07:00 — TASK-006 — AUTO/MANUAL P2/A2, code và kiểm tra tự động

- Trạng thái: Đang thực hiện; 4/5 mục nghiệm thu, chờ Wokwi P2.

### Đã thực hiện

State machine thuần với cấu hình SRS có tên, filter LDR5 mẫu/hysteresis/dwell1s, AUTO/PIR/distance/invalid/max-hold5s, MANUAL0–100/60s/offline fallback và hủy hold cũ; dimming2điểm/20ms, OPEN_LOAD stable1s/detect2s/recover3s, fault độc lập mode/không tự cắt PWM. FirmwareApp thay EnvironmentSmokeTest, một chủ PWM. SensorReader chuyển pulseIn sang ISR ECHO/timeout hữu hạn; WiFi/PubSubClient thuộc task core0, atomic status/loss-count bảo vệ MANUAL cả khi mất/kết nối lại giữa poll. Giữ topic diagnostics, pin map, dependency và sơ đồ. MANUAL cục bộ qua API/Serial, chưa triển khai command/ACK A3.

File code: src/ControlConfig.h, ControlTypes.h, LightingController.h/.cpp, DimmingController.h/.cpp, FaultDetector.h/.cpp, FirmwareApp.h/.cpp, Connectivity.h/.cpp, LocalControlCommand.h/.cpp; sửa SensorReader.h/.cpp và main.cpp, bỏ EnvironmentSmokeTest.h/.cpp. Test: test/host/LightingControllerChecks.cpp, SensorReaderChecks.cpp, FirmwareAppChecks.cpp, ConnectivityChecks.cpp, Arduino.h/runtime stubs, README; scripts/check-firmware.py. Tài liệu: README, architecture/development/firmware/mqtt/simulation/testing, task/next-task/report. Evidence TASK-005 và checklists lịch sử không đổi.

### Kiểm tra và kết quả

PASS bốn suite host g++ C++17 -Wall -Wextra -Werror, formatter clang-format17.0.3 đọc cấu hình dự án; build cuối esp32dev SUCCESS exit0, 58.48s, RAM48028/327680 (14.7%), flash912763/1310720 (69.6%). Script prepare freshness/copy/hash PASS. [Log thực tế](evidence/task-006/validation.log). Test chạy code thật với GPIO/ADC/RTOS/network stub, không phải mạng thật hoặc Wokwi; không kiểm thử lại nghiệm thu TASK-005. Không chạy hoặc thao tác container.

### Vướng mắc và cách giải quyết

Đã sửa lỗi phát hiện qua test/code review: mất MQTT quá nhanh che fallback MANUAL (thêm loss-count); cạnh ECHO sau deadline và dao động PWM giữa kỳ fault (bổ sung test). Những test cuối đều PASS. Chưa xác minh live ISR/task hai core, timing và Serial/Wokwi sau thay đổi kiến trúc. Chưa coi task PASS hoặc thêm vào checklist hoàn thành. Không nâng toolchain/thêm thư viện hoặc sửa SRS để hợp thức hóa.

### Bước tiếp theo

[5 bước Wokwi P2](../techs/simulation.md): môi trường, PIR/hold, MANUAL/AUTO/60s, fault/recovery, timeout-ECHO. Artifact đã chuẩn bị. Tiếp tục cùng TASK-006 sau khi có Serial/ảnh; không tự chạy A3. Không commit/push. Lịch sử report cũ bảo toàn nguyên byte.

---

## 2026-11-16T03:04:48+07:00 — TASK-005 — Kiểm tra trước commit/push main

- Đã làm: rà 51 file TASK-005 (8 tài liệu, 43 evidence), không có file ngoài phạm vi; origin/main ngang main sau fetch. Người dùng cho phép commit/push trực tiếp main, không tạo nhánh/PR.
- Kiểm tra/kết quả: build esp32dev SUCCESS exit 0 (4.52 giây), RAM 47388 byte, flash 908071 byte; host g++ C++17 với -Wall -Wextra -Werror PASS lịch cảm biến, timeout/invalidation/recovery và tràn uint32. Rà credential/token theo mẫu không có phát hiện; liên kết Markdown nội bộ hợp lệ. Không stage .pio/BIN/ELF/.env; giữ log/ảnh nghiệm thu đã rà soát.
- Vướng mắc: Không có. Giữ nguyên giới hạn host test không thay Wokwi; không chạy lại Wokwi hoặc dừng broker. Không sửa firmware hoặc triển khai TASK-006.
- Cách xử lý: stage đúng tập file đã rà, commit theo thông điệp người dùng, push thường lên origin/main; nếu remote đổi hoặc lỗi/conflict thì dừng, không force push. Kết quả push và commit hash báo trực tiếp sau thao tác, không ghi PASS trước khi chạy.

---

## 2026-11-16T02:56:10+07:00 — TASK-005 — Nghiệm thu cuối P1/A1

- Trạng thái: Hoàn thành; 4/4 nhóm nghiệm thu, P1-01 đến P1-08 PASS trong phạm vi raw sensor/diagnostics một node.
- Đã làm: đọc toàn bộ Serial recovery mới 159 dòng, đối chiếu lịch sử MQTT recovery đã PASS; cập nhật biên bản, task/checklist/next-task và tài liệu. Không chạy lại test hoặc thao tác broker/firmware.
- Kiểm tra/kết quả: 14 mẫu SENSORS trong đoạn offline, năm mức PWM/duty/ready=1, retry và reconnect 120163 ms, heartbeat từ 122171 ms; uptime tăng, không banner boot. P1-02 đã đủ 4095/2122/0 và xác nhận vị trí núm. MQTT/pong sau recovery có bằng chứng lượt 02:29, Serial bổ sung từ lượt 02:50; ghi rõ hai lượt và nguồn xác nhận mốc thời gian.
- Vướng mắc: Không còn vướng mắc chặn TASK-005. Giữ giới hạn metadata/ảnh và timeout phiên dài chưa rõ nguyên nhân, không tuyên bố nghiệm thu toàn hệ thống.
- Cách giải quyết: nhận log bổ sung, đối chiếu dữ liệu thực; giữ các báo cáo PARTIAL cũ như lịch sử, không giả log/ảnh hoặc gộp sai timestamp.
- [Biên bản và ma trận bằng chứng](evidence/task-005/windows-live-20261116-003644/acceptance-final.md). Đủ điều kiện đề xuất TASK-006 P2/A2, chưa triển khai. Không commit/push.

---

## 2026-11-16T02:36:12+07:00 — TASK-005 — Chốt P1-02, rà Serial offline P1-08

- Đã làm: đọc nguyên log biến trở cuối, xác nhận đủ 4095/2122/0 tại đúng uptime; vị trí tối đa/giữa/thấp nhất do người dùng xác nhận. P1-02 PASS, không thử lại.
- Kiểm tra/kết quả: TASK-005 3/4 nhóm nghiệm thu, P1-08 recovery MQTT đã PASS nhưng toàn ca vẫn PARTIAL. Tìm log đã lưu chưa có Serial offline/retry. Cửa sổ Wokwi còn mở, đọc terminal/screenshot qua UI bị timeout nên chưa xác định buffer còn hay mất.
- Vướng mắc/cách giải quyết: chỉ cần xuất đoạn Serial đang có của lượt 02:29:15–02:29:46 để chứng minh raw/PWM/retry và không boot lại; nếu không còn bằng chứng thì giữ PARTIAL, không tự tạo log hoặc ngắt broker.
- [Báo cáo chi tiết](evidence/task-005/windows-live-20261116-003644/p102-final-and-p108-gap-20261116.md). Không sửa firmware, build, commit/push, đóng TASK-005 hoặc triển khai TASK-006.

---

## 2026-11-16T02:32:06+07:00 — TASK-005 — Kiểm thử recovery P1-08 trên Windows

- Trạng thái: Bị chặn; 2/4 nhóm nghiệm thu, còn đối chiếu hồ sơ.
- Đã làm: xác minh đúng project/service/config/container Mosquitto; capture timestamp; stop riêng mosquitto, giữ offline 20 giây, start lại trong finally. Không tác động PostgreSQL/Redis hoặc source.
- Kiểm tra: PASS recovery MQTT thực tế: broker start 02:29:36, node reconnect 02:29:46, heartbeat tiếp tục, pong khớp payload lúc 02:30:19. P1-07 đã PASS với 184 giây thực và 40 heartbeat khớp Serial boot thứ hai.
- Vướng mắc: thiếu Serial chứng minh raw/PWM/retry và không reset trong khoảng offline để chốt P1-08; người dùng xác nhận ADC 4095/2122/0 nhưng chưa thấy mẫu 2122 trong log hiện có.
- Cách giải quyết: xuất đoạn Serial đang có, không thử lại các ca PASS hoặc ngắt broker thêm lần nữa. Giữ TASK-005 chưa hoàn thành; chưa triển khai TASK-006.
- Bằng chứng: [tổng hợp và timeline/MQTT/broker](evidence/task-005/windows-live-20261116-003644/p108-20261116-022831-review.md). Broker đã khôi phục, đang chạy. Không commit/push. Toàn bộ byte báo cáo cũ được giữ bên dưới.

---

## 2026-11-15T19:29:24+07:00 — TASK-005 — Triển khai mạch và raw sensor P1/A1

- Trạng thái: Bị chặn
- Tiến độ: 2/4 nhóm nghiệm thu

### Đã thực hiện

Thêm SensorReader setup/update/snapshot, raw ADC12 bit, PIR20 ms, ADC100 ms, siêu âm200 ms timeout30000 µs; timeout xóa distance cũ/cờ invalid. Tích hợp vào EnvironmentSmokeTest, banner P1/A1, log SENSORS mỗi giây, PIR đổi mức, CRLF; giữ P0 PWM/MQTT. Mở rộng sơ đồ một node, thêm cấu hình timeout ECHO dùng cùng artifact. Thêm host checks cho code SensorReader thật. Cập nhật hardware/firmware/simulation/testing, README, architecture, development và hồ sơ. Giữ main, SRS, package pin và hợp đồng MQTT.

### Kiểm tra và kết quả

PASS host pin/lịch lấy mẫu, xung trigger, giới hạn timeout, invalidation/recovery và tràn uint32; đây là stub GPIO/ADC, không phải live. Formatter và wiring/JSON/TOML/tài liệu kiểm tra tĩnh PASS. Build sạch cuối SUCCESS 9.06 giây, RAM 47388 byte, flash 908071 byte; artifact copy/hash khớp. [Bằng chứng](evidence/task-005/README.md), [host](evidence/task-005/host-checks.log), [build](evidence/task-005/build-fresh.log), [checksum](evidence/task-005/prepare-final.log). Không chạy Docker/Wokwi hoặc ca P1 live; các ca đó chưa PASS.

### Vướng mắc

Script copy từ chối artifact cũ sau lần sửa comment: build SUCCESS nhưng SCons không relink. Đã clean/rebuild thật và copy đạt; giữ log từ chối, không bỏ freshness. Còn thiếu nghiệm thu live LDR/PIR/pot/distance/PWM/MQTT và timeout. Giới hạn timeout phiên dài P0 chưa được khẳng định đã giải quyết.

### Cách giải quyết

Người dùng chạy P1-01 đến P1-08 theo simulation/testing, lưu Serial/ảnh/log đúng task. Cấu hình timeout riêng chỉ bỏ ECHO; không thay sơ đồ chính. Theo dõi polling có thể chậm quanh pulseIn/MQTT connect, không khẳng định hard realtime. Không coi lịch sử P0 là nghiệm thu P1.

### Tài liệu và bước tiếp theo

TASK-005 tiếp tục phần live, chưa vào checklist task hoàn thành; checklist các task cũ giữ nguyên. Chưa triển khai TASK-006/P2/A2. Toàn bộ byte report cũ giữ nguyên phía sau.

---

## 2026-11-15T19:15:52+07:00 — TASK-004 — Chốt kiến trúc và giao thức A0

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục nghiệm thu

### Đã thực hiện

Tạo architecture.md về trách nhiệm, luồng, trạng thái hiện tại/mục tiêu và điểm bàn giao. Tạo mqtt.md theo SRS với topic/QoS/retain, telemetry, availability/LWT, command/ACK, deadline_uptime_ms, result/reason/status, retry/cache và tám JSON. Cập nhật README và development theo source P0 thực tế. Hoàn tất TASK-004, đề xuất TASK-005/P1-A1; không tự triển khai.

### Kiểm tra và kết quả

PASS tám nhóm kiểm tra: formatter ba source/header, Compose config, liên kết file/UTF-8/LF, import convention, JSON/TOML/Python, tám JSON hợp đồng và đối chiếu SRS, build/pin/checksum, bảo toàn source/infra/lịch sử. [Chi tiết](evidence/task-004/convention-checks.md). Không tạo model session mới để kiểm tra convention runtime. Không chạy Wokwi/Docker live hoặc MQTT v1 nghiệp vụ trong A0.

### Vướng mắc

Không có vướng mắc A0 còn chặn. Timeout phiên dài P0 là giới hạn đã ghi tại [nghiệm thu](evidence/task-002/acceptance.md), chưa kết luận nguyên nhân. Không coi ví dụ hợp đồng là code đã triển khai.

### Cách giải quyết

Giữ hạn chế trong tài liệu và theo dõi ở A3; các gói triển khai dùng hợp đồng A0 và bổ sung kiểm thử thực tế. Không ghi PASS cho phần chưa chạy hoặc thay SRS để hợp thức hóa lỗi.

### Tài liệu và bước tiếp theo

SRS 3–7, 10–12, 16. [Task hiện tại](task.md) hoàn thành và giữ nguyên tới lần giao việc mới. [TASK-005](next-task.md) chưa bắt đầu. Giữ nguyên mọi byte báo cáo cũ phía sau.

---

## 2026-11-15T19:12:53+07:00 — TASK-002 — Chốt smoke P0 và phiên bản kiểm chứng

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu môi trường

### Đã thực hiện

Khóa platform/framework/libs/PubSubClient; sửa đúng hai đường dẫn đề cương trong SRS, không đổi yêu cầu; cập nhật README/setup/bằng chứng. Lưu [task đã nghiệm thu](evidence/task-002/accepted-task.md), [biên bản](evidence/task-002/acceptance.md). Source ứng dụng không đổi.

### Kiểm tra và kết quả

PASS formatter, Compose config và các kiểm tra tĩnh trước đó. Lần build sau pin đầu lỗi tải registry; retry với package cục bộ đã hiện hữu PASS 8.37 giây, RAM 47276 byte, flash 897039 byte. Copy/checksum PASS. File MQTT xác nhận đủ pong 001–004, broker restart 19:02:25 và node trở lại 19:02:27; Serial hội thoại đủ năm PWM. Người dùng xác nhận không restart ESP32. Không tự chạy Docker/Wokwi live.

### Vướng mắc

Đã xử lý trở ngại build qua retry, giữ cả log lỗi và log đạt. Timeout cuối phiên dài chưa được kết luận nguyên nhân; đây là giới hạn theo dõi, không được xóa hoặc diễn giải thành ổn định tuyệt đối. Chưa có serial.log thô đầy đủ; nguồn Serial là hội thoại.

### Cách giải quyết

Nghiệm thu các ca smoke đã thỏa; giữ hạn chế trong biên bản và theo dõi ở mạng nghiệp vụ. Không cần nâng toolchain. Build/copy sau pin không được tính là lượt live mới.

### Tài liệu và bước tiếp theo

Đã ghi checklist TASK-002; người dùng giao tiếp TASK-004 để hoàn thiện A0. Giữ nguyên toàn bộ báo cáo cũ phía sau.

---

## 2026-11-15T18:32:51+07:00 — TASK-002 — Firmware chẩn đoán timeout MQTT

- Trạng thái: Bị chặn (chờ live bản mới)
- Tiến độ: 1/4 nhóm nghiệm thu; triển khai lượt heartbeat hoàn tất

### Đã thực hiện

Thêm nghỉ 10 ms đầu loopSmokeTest, heartbeat mỗi 2 giây theo millis không retained trên diagnostics/heartbeat, payload uptime_ms, kiểm tra độ dài/publish; reset timer sau subscribe. Giữ keepalive 15 giây, broker/pin/topic ping-pong. Thêm log uptime cho chuyển kết nối, connect failed, loop failed, Wi-Fi reconnect và heartbeat. Build/copy artifact mới; cập nhật setup, task, next-task và README bằng chứng. Không chạy Docker/Wokwi, không mở rộng cảm biến/AUTO hoặc nhiều node.

### Kiểm tra và kết quả

Formatter ban đầu phát hiện xuống dòng; đã format đúng file thay đổi, dry-run PASS. Build cuối esp32dev exit 0, SUCCESS 4.89 giây, RAM 47276/327680 byte, flash 897039/1310720 byte: [log](evidence/task-002/build-heartbeat.log). Build dùng core dir tạm /tmp/iot-pio-check-de41spu8 và package/platform cục bộ. Script prepare-simulation PASS; [checksum](evidence/task-002/prepare-heartbeat.log). Kiểm tra liên kết mới, artifact khớp checksum, lịch sử report và tệp ngoài phạm vi được giữ nguyên.

### Vướng mắc

Chưa có live cho bản mới. Bằng chứng cũ cho thấy timeout 22–23 giây; tốc độ mô phỏng chậm là giả thuyết. Người dùng xác nhận từng thấy dòng subscribe; chưa đủ chứng minh kết nối ổn định. Không đánh dấu fix runtime/P0 PASS từ build.

### Cách giải quyết

Người dùng restart Wokwi với artifact mới, mở subscriber diagnostics/# trước khi gửi ping, xác nhận heartbeat và ba pong, giữ 3 phút thực, đủ năm PWM, rồi thử stop/start broker và pong p0-004 không reset ESP32. Nếu còn lỗi thu Serial/PCAP. Không chỉ tăng keepalive để che lỗi.

### Tài liệu và bước tiếp theo

Setup mô tả bản P0 hiện tại và lệnh nhận heartbeat/pong. Giữ TASK-002, chưa khóa toolchain hoặc thêm vào danh sách task hoàn thành; checklists.md giữ nguyên. Tham chiếu SRS 4.3–4.5, 10–12. Giữ toàn bộ lịch sử report và log trước.

---

## 2026-11-15T18:19:35+07:00 — TASK-002 — Cập nhật tiến độ theo bằng chứng live

- Trạng thái: Bị chặn
- Tiến độ: 1/4 nhóm nghiệm thu gốc; đã đạt thêm nhiều bước con

### Đã thực hiện

Cập nhật task/next-task, setup và README bằng chứng; thêm [tổng hợp live](evidence/task-002/live-progress.md) và bản sao nguyên ảnh Wokwi người dùng. Giữ nguyên firmware, cấu hình, SRS, log và checklist các task hoàn thành. Không tự chạy Docker/Wokwi hoặc gói kế tiếp.

### Kiểm tra và kết quả

Build.log hiện tại SUCCESS 7.31 giây. Đã đối chiếu checksum BIN/ELF nguồn và copy khớp nhau/khớp đầu ra người dùng. Ảnh xác nhận Wokwi/Serial, ready=1 và PWM 0%/25%; chưa đủ năm mức. Host pub/sub PASS theo terminal người dùng; chưa có mqtt.log thô riêng. Broker.log có ESP32 kết nối ba lần, timeout 22–23 giây. Chưa xác nhận ba pong, SUBACK hay phục hồi sau restart.

Kiểm tra tài liệu: liên kết mới, bảo toàn ảnh/checksum, lịch sử report và các tệp ngoài phạm vi. Không build lại vì chỉ cập nhật hồ sơ dựa trên bằng chứng đã có.

### Vướng mắc

MQTT chưa ổn định, thiếu Serial đầy đủ và pong. Mô phỏng chậm là giả thuyết, chưa kết luận nguyên nhân. Build.log lỗi cũ đã được người dùng thay bằng log SUCCESS; không phục dựng hoặc giả tạo log cũ.

### Cách giải quyết

Lần thử tiếp khởi động lại broker sau compose down, giữ Wokwi chạy, thu Serial và kiểm tra heartbeat; nghiệm thu đủ PWM và ping/pong trước/sau restart. Chỉ khóa toolchain sau khi smoke live đạt. Giữ 1/4 vì tiêu chí build còn gộp khóa phiên bản, PWM thiếu mức, MQTT chưa đạt; không ghi phần trăm tùy ý.

### Tài liệu và bước tiếp theo

Setup cập nhật theo SRS 4.3–4.5, 10–12. Next-task giữ TASK-002, chưa triển khai đề xuất sửa timeout. Không thêm task chưa hoàn thành vào checklists.md. Lịch sử report cũ giữ nguyên toàn bộ phía sau.

---

## 2026-11-15T18:10:41+07:00 — TASK-002 — Sửa lỗi biên dịch min

- Trạng thái: Bị chặn (còn chờ nghiệm thu live)
- Tiến độ: 1/4 mục nghiệm thu tổng; lượt sửa lỗi hoàn tất

### Đã thực hiện

Thêm <algorithm>, đổi min thành std::min<uint32_t> trong EnvironmentSmokeTest.cpp để xử lý xung đột unsigned long/unsigned int; không đổi thuật toán hoặc mức trần backoff. Cập nhật task, next-task, setup và README bằng chứng. Giữ nguyên build.log và các log cũ.

### Kiểm tra và kết quả

PASS: clang-format --dry-run --Werror src/EnvironmentSmokeTest.cpp. PASS: build esp32dev, exit 0, SUCCESS 10.19 giây, RAM 47276/327680 byte, flash 896199/1310720 byte. Xem [log mới](evidence/task-002/build-min-fix.log). Dùng core dir tạm /tmp/iot-pio-check-de41spu8 với package/platform cục bộ; không nâng toolchain hoặc sửa quyền hệ thống.

### Vướng mắc

Lỗi biên dịch đã xử lý. Wokwi/Serial/PWM, broker và ping/pong/reconnect live chưa chạy. Tiêu chí đầu tiên còn gộp build và khóa phiên bản sau smoke live nên chưa đánh dấu đạt toàn mục.

### Cách giải quyết

Người vận hành tiếp tục chuẩn bị artifact và nghiệm thu live theo setup; sau khi đạt mới khóa platform/framework. Không tự chạy Docker/Wokwi trong lượt sửa này.

### Tài liệu và bước tiếp theo

Tham chiếu SRS 4.3–4.5, 10–12. Giữ TASK-002 chờ kiểm chứng; không đánh dấu task hoàn thành hoặc thêm mục hoàn thành vào checklists.md. Lịch sử checklist giữ nguyên. Toàn bộ nội dung report cũ giữ nguyên ở phía sau.

---

## 2026-11-15T17:55:23+07:00 — TASK-002 — Chuẩn bị môi trường P0

- Trạng thái: Bị chặn
- Tiến độ: 1/4 mục nghiệm thu

### Đã thực hiện

- Tạo Docker Compose Mosquitto 2.1.2-alpine và service MQTT client profile tools trên host networking Linux; broker chỉ publish 127.0.0.1:1883, cấu hình read-only, anonymous local, không persistence.
- Thay code mẫu bằng main điều phối EnvironmentSmokeTest: Serial, LEDC 5 kHz/8 bit, năm mức PWM, Wi-Fi/MQTT với retry hữu hạn, ping/pong tối đa 64 byte, không retained. Thêm PubSubClient 2.8; chưa pin platform/framework vì chưa build/smoke đạt.
- Tạo sơ đồ và cấu hình Wokwi node_01, script chuẩn bị BIN/ELF kiểm tra freshness/checksum và gitignore artifact.
- Tạo [setup](../techs/setup.md), README, cập nhật development và [bằng chứng](evidence/task-002/README.md). Giữ nguyên SRS và lịch sử checklist; chưa có task hoàn thành mới.

### Kiểm tra và kết quả

PASS: Compose config, clang-format, JSON/TOML, liên kết tài liệu; thử script với fixture tạm gồm thiếu file, artifact cũ và copy checksum. Chi tiết tại [kiểm tra tĩnh](evidence/task-002/static-checks.md).

Build code mẫu và code mới: bị chặn quyền cache PlatformIO, xem baseline-build.log/smoke-build.log trong thư mục bằng chứng. Chưa xác nhận biên dịch mã mới. Chuẩn bị artifact thật từ chối vì thiếu BIN/ELF; không xuất artifact cũ.

Docker runtime, license Wokwi, Serial/PWM live, broker host và ping/pong/reconnect: chưa chạy. Không coi kiểm tra tĩnh là kết quả nghiệm thu mô phỏng.

### Vướng mắc

PlatformIO không ghi được cache/lock trong ~/.platformio ở sandbox. Người dùng chọn tự chạy Docker Compose và Wokwi; chưa có log live.

### Cách giải quyết

Chạy theo setup từ terminal ngoài phiên: khởi động broker, xác nhận host pub/sub, build SUCCESS, copy artifact, chọn cấu hình và chạy Wokwi, thử ba ping/pong rồi stop/start broker. Lưu log và ảnh vào evidence/task-002. Sau khi có bằng chứng đạt, tiếp tục cùng TASK-002 để khóa toolchain đã kiểm chứng và nghiệm thu. Không cần thay quyền hệ thống hoặc xóa cache từ agent.

### Tài liệu và bước tiếp theo

[SRS](../srs.md) mục 3, 4, 10–12; setup là tài liệu chính cho firmware/mạch/MQTT thử P0. [Task tiếp theo](next-task.md) là phần kiểm chứng còn lại của TASK-002; TASK-004 chỉ được đề xuất khi P0 môi trường đạt. Chưa tự triển khai A0/P1.

---

## 2026-11-15T17:41:58+07:00 — TASK-003 — Dùng chung convention cho Codex, Claude Code và OpenCode

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

### Đã thực hiện

- Giữ [AGENTS.md](../../AGENTS.md) làm nguồn convention chung, bổ sung chỉ dẫn đồng bộ và khởi động tại gốc firmware.
- Thêm [CLAUDE.md](../../CLAUDE.md) với import @AGENTS.md theo cơ chế chính thức của Claude Code. Codex/OpenCode sử dụng AGENTS.md trực tiếp, không nhân bản convention hoặc thêm cấu hình nạp trùng.
- Cập nhật [development.md](../techs/development.md) với tài liệu nguồn, cách kiểm tra trên phiên mới và giới hạn xác minh.
- Cập nhật task hiện tại và checklist. TASK-002 vẫn là đề xuất P0 chưa bắt đầu; mã TASK-003 dùng cho yêu cầu mới vì TASK-002 đã được dành trong next-task.md.

### Kiểm tra và kết quả

- PASS: đối chiếu tài liệu chính thức Codex AGENTS.md, Claude Code memory/imports và OpenCode instructions; liên kết nguồn trong development.md.
- PASS: CLAUDE.md có đúng một import trỏ tới AGENTS.md hiện hữu; không có vòng import hoặc AGENTS.override.md tại gốc.
- PASS: kiểm tra 31 đường dẫn Markdown nội bộ trước khi đóng hồ sơ; tệp đọc được UTF-8/LF, có newline cuối.
- PASS: SHA-256 của SRS, src/main.cpp, platformio.ini, .clang-format, .editorconfig và next-task.md giữ nguyên.
- PASS: giữ nguyên lịch sử report/checklists trước khi ghi; thêm mục report mới lên đầu và xác nhận toàn bộ nội dung cũ giữ nguyên ở cuối.
- PASS: lệnh opencode --version với XDG_DATA_HOME/XDG_STATE_HOME/XDG_CACHE_HOME trỏ thư mục tạm cho kết quả v2.0.26.
- Chưa kiểm chứng bằng phiên model mới: không gọi Codex/Claude/OpenCode để thực hiện prompt hoặc phát sinh phiên agent khác. Không chạy build firmware vì chỉ sửa hướng dẫn.

### Vướng mắc

Claude CLI không có trong PATH của môi trường kiểm tra. OpenCode --version với vị trí dữ liệu mặc định lỗi EROFS khi mở log trong ~/.local/share/opencode/log/opencode.log. Điều này giới hạn kiểm tra runtime, không ngăn tạo các entry point hướng dẫn tại dự án.

### Cách giải quyết

Đã dùng các thư mục XDG tạm trong /tmp để đọc phiên bản OpenCode, không sửa cấu hình global. Để xác nhận context thực tế, mở phiên mới tại firmware bằng từng công cụ; với Claude Code kiểm tra /context all, rồi dùng prompt chỉ đọc trong development.md để xác nhận quy định SRS/techs/báo cáo/task/checklist/Arduino. Cần môi trường có Claude Code khả dụng nếu muốn chạy kiểm chứng Claude CLI.

### Tài liệu và bước tiếp theo

Tham chiếu [SRS](../srs.md) mục 11, 16. Tài liệu development đã cập nhật. Giữ [đề xuất P0](next-task.md), chưa thực hiện. Cấu trúc nhận convention đã được thiết lập; việc model tuân thủ không được cưỡng chế bằng tệp Markdown.

---

## 2026-11-15T17:37:41+07:00 — TASK-001 — Thiết lập convention agent

- Trạng thái: Hoàn thành
- Tiến độ: 3/3 mục

### Đã thực hiện

- Tạo [AGENTS.md](../../AGENTS.md) tại gốc firmware: đọc SRS mỗi task, xác định phạm vi, cập nhật tài liệu kỹ thuật và báo cáo trước khi kết thúc.
- Tạo [development.md](../techs/development.md) với vòng đời task, trạng thái, mẫu task/báo cáo, danh mục techs, cách thêm báo cáo lên đầu và giữ lịch sử.
- Thêm [.clang-format](../../.clang-format) và [.editorconfig](../../.editorconfig): định dạng C/C++ Arduino, UTF-8/LF; giữ khoảng trắng Markdown có chủ đích. Không format lại source mẫu.
- Khởi tạo [task hiện tại](task.md), [checklist hoàn thành](checklists.md) và [đề xuất TASK-002](next-task.md). Chưa thực hiện P0, chưa nghiệm thu chức năng firmware.

### Kiểm tra và kết quả

- PASS: kiểm tra các đường dẫn Markdown nội bộ trong AGENTS, development và các tệp task đang có tại thời điểm kiểm tra, không có đích thiếu.
- PASS: chạy clang-format 23.1.4 với `--style=file --assume-filename=src/main.cpp` trên mẫu Arduino qua stdin. Cấu hình thật được đọc; thụt 2 dấu cách, chèn ngoặc nhánh if, format hai lần cho cùng kết quả; `--dry-run --Werror` đạt với mẫu đã định dạng.
- PASS: các tệp mới có nội dung đọc được UTF-8, dùng LF và có newline cuối tệp.
- PASS: đối chiếu SHA-256 trước/sau, SRS, src/main.cpp và platformio.ini giữ nguyên.
- PASS: đã đọc báo cáo cũ trước khi thêm mục mới. Tệp ban đầu trống (0 byte); kiểm tra thêm khối mới giữ nguyên lịch sử không rỗng bằng mẫu trong bộ nhớ. Thao tác ghi báo cáo thật cũng nối nguyên nội dung cũ ở phía sau.
- Đã rà văn phong bằng vi_scan.py và đọc lại các cảnh báo: chủ yếu là dấu câu, khoảng mục SRS và thuật ngữ trong tài liệu kỹ thuật; giữ các cấu trúc cần thiết.
- Chưa chạy build firmware, Wokwi hoặc MQTT: ngoài phạm vi task thuần tài liệu/cấu hình định dạng. Không coi formatter đạt là chức năng firmware đạt.

### Vướng mắc

Không có vướng mắc chặn task. Git CLI không nhận diện thư mục hiện tại là repository trong môi trường này, nên không dùng git diff để xác minh thay đổi.

### Cách giải quyết

Đã đối chiếu nội dung và SHA-256 của SRS, source cùng cấu hình build thay cho git diff. Không cần hành động bổ sung để hoàn thành task convention. Khi làm P0, cần kiểm tra quyền build cache, Wokwi và kết nối MQTT theo task kế tiếp.

### Tài liệu và bước tiếp theo

Tham chiếu [SRS](../srs.md) mục 3–6, 10–12 và 16. Quy trình và convention đã ghi ở development.md. Đề xuất TASK-002 kiểm chứng môi trường P0, chỉ bắt đầu khi người dùng giao việc; không tự chuyển task.
