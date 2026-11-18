#!/usr/bin/env node
// Build the editable Vietnamese handover report from independently audited runs.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const [runDir, outDir, auditFile] = process.argv.slice(2);
if (!runDir || !outDir || !auditFile) throw new Error('Usage: node build-experiment-report.cjs RUN_DIR OUT_DIR AUDIT_JSON');
const q = path.resolve(runDir), out = path.resolve(outDir);
const d = require(path.join(q, 'runtime/office/node_modules/docx'));
const audit = JSON.parse(fs.readFileSync(auditFile, 'utf8'));
const complete = audit.status === 'PASS' && audit.accepted_runs === 15;
const stage = complete ? 'BÁO CÁO ĐỒ ÁN' : 'BẢN ĐANG HOÀN THIỆN';
const W = 9071, pages = [], manuscript = [];
const REPORT_TEXT = Symbol('reportText');
fs.mkdirSync(out, { recursive: true });
const display = text => text.replace(/(tháng|năm|cả|đủ|gồm|mỗi|giây|phút|tối đa|ổn định|nhân|mục|dưới|trong|sáng|nền|người|xe|hồi|về|ở|thêm)(?=\d)/gu, '$1 ');
const p = (text, options = {}) => { const paragraph = new d.Paragraph({ children: [new d.TextRun({ text: display(text) })], ...options }); paragraph[REPORT_TEXT] = display(text); return paragraph; };
const heading = (text, level = 1) => { const paragraph = new d.Paragraph({ text, heading: level === 1 ? d.HeadingLevel.HEADING_1 : d.HeadingLevel.HEADING_2 }); paragraph[REPORT_TEXT] = '#'.repeat(level)+' '+text; return paragraph; };
const note = text => p(text, { style: 'Note' });
function table(headers, rows, widths) {
  const make = (values, header) => new d.TableRow({ tableHeader: header, cantSplit: true, children: values.map((value, i) => new d.TableCell({
    width: { size: widths[i], type: d.WidthType.DXA }, verticalAlign: d.VerticalAlign.CENTER,
    margins: { top: 85, bottom: 85, left: 100, right: 100 },
    shading: { type: d.ShadingType.CLEAR, fill: header ? 'E8EDF2' : 'FFFFFF' },
    children: [new d.Paragraph({ alignment: d.AlignmentType.LEFT, spacing: { before: 0, after: 0, line: 260 }, children: [new d.TextRun({ text: display(String(value)), font: 'Arial', size: 21, bold: header })] })]
  })) });
  const result = new d.Table({ width: { size: W, type: d.WidthType.DXA }, columnWidths: widths,
    rows: [make(headers, true), ...rows.map(row => make(row, false))] });
  const mdRow = row => '| '+row.map(value=>display(String(value)).replace(/\|/g,'\\|')).join(' | ')+' |';
  result[REPORT_TEXT] = [mdRow(headers), mdRow(headers.map(()=> '---')), ...rows.map(mdRow)].join('\n');
  return result;
}
function page(title, items) {
  const children = [heading(title, /^\d\./.test(title) ? 2 : 1)];
  manuscript.push('\n# ' + title + '\n');
  for (const item of items) {
    if (typeof item === 'string') { children.push(p(item)); manuscript.push(display(item) + '\n'); }
    else { children.push(item); if(item[REPORT_TEXT]) manuscript.push(item[REPORT_TEXT]+'\n'); }
  }
  pages.push(children);
}
const fmt = (n, digits = 3) => n === null || n === undefined ? '—' : Number(n).toLocaleString('vi-VN', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const timingBounds = audit.runs.map(run=>run.action_summary?.maximum_lateness_upper_ms).filter(value=>typeof value==='number');
const scenarios = [
  ['EX-01', 'Ban ngày, thay đổi chuyển động', '1 × 300 s'],
  ['EX-02', 'Đêm yên tĩnh', '3 × 600 s'],
  ['EX-03', 'Đêm, người giả lập; 150 cm', '3 × 600 s'],
  ['EX-04', 'Đêm, xe giả lập; 50 cm', '3 × 600 s'],
  ['EX-05', 'Ba node, ba pha hỗn hợp', '3 × 900 s'],
  ['EX-06', 'Hở tải và phục hồi node_02', '1 × 300 s'],
  ['EX-07', 'Mất broker, AUTO và reconnect', '1 × 300 s']
];
page('TÓM TẮT', [
  'Đề tài xây dựng mô hình ba đèn đường tự điều chỉnh độ sáng theo ánh sáng môi trường và chuyển động. Mỗi node ESP32 thực hiện AUTO tại chỗ; dữ liệu đi qua MQTT đến FastAPI, được lưu trong SQLite và hiển thị trên dashboard HTML/CSS/JavaScript chạy bằng VS Code Live Server.',
  'Hệ thống tách môi trường DAY/TWILIGHT/NIGHT, chuyển động, chế độ AUTO/MANUAL, mức sáng mục tiêu và mức sáng đang áp dụng. PIR kết hợp HC-SR04 tạo hai tình huống người/xe theo khoảng cách quy ước; biến trở tạo đầu vào giả lập tải. Đây là mô hình Wokwi, không phải bộ nhận dạng phương tiện hoặc thiết bị đo điện năng thực.',
  'Nghiệm thu tích hợp TASK-011 đã ghi nhận ba node cùng hoạt động, lệnh có ACK đúng đích, lỗi tải, AUTO khi mất broker và một cửa sổ ổn định 1.800 giây thực. Hồ sơ gốc được giữ riêng; báo cáo này phân biệt kết quả kế thừa với thực nghiệm năng lượng TASK-012.',
  `Tại thời điểm tạo tệp, ${audit.accepted_runs}/15 lượt chính đã được kiểm tra độc lập. ${complete ? 'Bảng kết quả sử dụng đủ 15 lượt hợp lệ, giữ cả lịch sử các lượt lỗi.' : 'Các lượt chưa có kết quả được ghi “chưa đủ”; không dùng số liệu dự đoán để điền thay.'}`,
  'Điện năng được tích phân theo uptime của từng node; độ phủ tính theo thời gian nhận UTC. So sánh AUTO chỉ dùng các đoạn đủ điều kiện với baseline DAY 0 W, TWILIGHT/NIGHT 24 W. Khi baseline bằng 0, tỷ lệ tiết kiệm không xác định và được giữ null.',
  note(`Trạng thái: ${stage}. Nguồn số liệu: ${path.basename(auditFile)}; thời điểm audit ${audit.generated_at}.`)
]);
page('MỤC LỤC VÀ QUY ƯỚC', [
  table(['Phần', 'Nội dung'], [
    ['Chương 1', 'Bài toán, mục tiêu và phạm vi'], ['Chương 2', 'Cơ sở kỹ thuật và giới hạn cảm biến'],
    ['Chương 3', 'Yêu cầu, kiến trúc và thiết kế'], ['Chương 4', 'Xây dựng và vận hành hệ thống'],
    ['Chương 5', 'Kiểm thử, phương pháp và kết quả thực nghiệm'], ['Chương 6', 'Kết luận, giới hạn và hướng phát triển'],
    ['Phụ lục', 'Pin map, lệnh chạy, hợp đồng và bằng chứng'], ['Tài liệu tham khảo', 'Nguồn dự án và tài liệu kỹ thuật']
  ], [1800, 7271]),
  'Trong báo cáo, “mức sáng” là giá trị điều khiển PWM theo phần trăm; “công suất” và “điện năng” có hậu tố mô phỏng. Uptime là thời gian kể từ khởi động của node; UTC là thời điểm máy thu nhận dữ liệu. Hai clock phục vụ hai mục đích khác nhau.',
  'PASS chỉ dùng cho kiểm tra đã chạy và có bằng chứng. INCOMPLETE là lượt thiếu điều kiện nghiệm thu; FAIL là kiểm tra không đạt. Không ghép thời gian từ các lượt lỗi để tạo một lượt hoàn chỉnh.',
  'Các mã FR, TC, P và A tham chiếu docs/srs.md. Các mã TASK tham chiếu hồ sơ triển khai trong docs/reports/. SRS mô tả yêu cầu và có các đoạn lịch sử “dự kiến”; hiện trạng triển khai được xác định từ source và bằng chứng nghiệm thu.',
  note('Mục lục liệt kê các phần chính. Dùng Navigation/Đề mục trong WPS để chuyển đến tiêu đề tương ứng.')
]);
page('CHƯƠNG 1. BÀI TOÁN VÀ PHẠM VI', [
  heading('1.1. Bài toán', 2),
  'Đèn đường duy trì mức sáng cố định có thể tiêu thụ năng lượng vào những khoảng ít hoạt động. Một mô hình điều khiển thích ứng cần xác định môi trường, phản ứng với chuyển động và vẫn giữ khả năng điều khiển khi hệ thống giám sát mất kết nối. Đề tài dùng Wokwi để kiểm chứng luồng điều khiển và thu thập dữ liệu trước khi xem xét phần cứng thật.',
  heading('1.2. Mục tiêu', 2),
  'Mỗi node tự chọn mức sáng nền phù hợp, tăng sáng khi PIR báo chuyển động, giữ sáng rồi giảm dần. Người vận hành theo dõi ba node, gửi lệnh AUTO/MANUAL, phân biệt lỗi tải với offline/dữ liệu cũ và tra cứu lịch sử. Phần thống kê công bố giả định, cửa sổ hợp lệ và độ phủ cùng với điện năng.',
  heading('1.3. Phạm vi đã thực hiện', 2),
  table(['Thành phần', 'Phạm vi'], [
    ['Mô phỏng', 'Ba ESP32, ba phiên Wokwi VS Code độc lập'], ['Firmware', 'PlatformIO; Arduino; một source, ba định danh biên dịch'],
    ['Truyền dữ liệu', 'Mosquitto local, MQTT v1, telemetry/availability/command/ACK'], ['Ứng dụng', 'FastAPI một worker, SQLite, HTML/CSS/JS và Live Server'],
    ['Thực nghiệm', 'Kế hoạch15 lượt chính theo7 kịch bản; pilot tách riêng']
  ], [2100, 6971]),
  'Ngoài phạm vi nghiệm thu: mạch công suất thật, camera AI, nhận dạng xe ngoài thực tế, LoRa, OTA, ứng dụng điện thoại và cloud. Tính năng đón đầu là hướng mở rộng, không dùng để đánh giá phần bắt buộc.',
  'Nhóm thực hiện: Quang Nhật Hưng (2001230328), Nguyễn Văn Anh Tuấn (2001230863), Nhóm 7. Thông tin nhóm được kế thừa từ đề cương gốc.'
]);
page('CHƯƠNG 2. CƠ SỞ KỸ THUẬT', [
  heading('2.1. ESP32 và xử lý tại node', 2),
  'ESP32 cung cấp ADC, GPIO, bộ tạo PWM và kết nối Wi-Fi. Trong mô hình, node đọc cảm biến và quyết định AUTO; backend không cần gửi lệnh cho từng bước điều chỉnh. Kiến trúc này giữ điều khiển cục bộ khi broker hoặc ứng dụng giám sát tạm ngừng.',
  'Mạng và điều khiển được tách trách nhiệm. Connectivity sở hữu WiFiClient/PubSubClient trong FreeRTOS task riêng; vòng ứng dụng đọc snapshot, chạy controller và ghi PWM. Không chờ Wi-Fi/MQTT vô hạn trong vòng điều khiển; reconnect có timeout và backoff hữu hạn.',
  heading('2.2. PWM và chuyển mức sáng', 2),
  'LEDC được cấu hình 5 kHz, độ phân giải 8 bit tại GPIO26. brightness_target là yêu cầu của controller; brightness_applied là mức đã đi qua dimming. Dimming thay đổi tối đa 2 điểm phần trăm mỗi 20 ms, dừng đúng giá trị mục tiêu. PWM trong mô phỏng thể hiện yêu cầu điều khiển, không chứng minh quang thông hoặc hiệu suất bộ nguồn.',
  heading('2.3. LDR và xác nhận môi trường', 2),
  'LDR đưa tín hiệu analog vào ADC12 bit GPIO34. Bộ lọc trung bình trượt sử dụng 5 mẫu mới; trạng thái ứng viên phải ổn định 1 giây. Hysteresis dùng các biên khác nhau khi đi lên và đi xuống để hạn chế đổi trạng thái liên tục quanh ngưỡng.',
  'Trong mạch đã hiệu chỉnh, ADC nhỏ biểu thị sáng, ADC lớn biểu thị tối. Không dùng nguyên ngưỡng 300/700 của ý tưởng ban đầu vì cấu hình ADC và chiều biến thiên phải khớp mô phỏng hiện tại.',
  note('Nguồn triển khai: src/ControlConfig.h, SensorReader, LightingController; docs/techs/firmware.md. Chu kỳ theo clock node, không diễn giải thành độ trễ giao diện theo giây thực.')
]);
page('2.4. CẢM BIẾN, MQTT VÀ MÔ HÌNH ĐIỆN', [
  'PIR cung cấp tín hiệu chuyển động. HC-SR04 đo khoảng cách bằng thời gian echo; timeout 30 ms tạo đầu vào distance invalid. Chỉ khi PIR HIGH, khoảng cách hợp lệ dưới 100 cm được quy ước VEHICLE, từ 100 cm trở lên là PEDESTRIAN. Khoảng cách gần khi PIR LOW không tự làm tăng sáng.',
  'Quy ước trên phục vụ tạo kịch bản; khoảng cách đơn lẻ không xác định được chủng loại vật thể. Khi PIR HIGH nhưng khoảng cách không hợp lệ, controller chọn UNKNOWN và mức sáng an toàn 100%.',
  'Biến trở tại GPIO35 tạo current_adc. Ở tải bình thường, công suất mô phỏng gần bằng 24 × brightness_applied/100 W. Biến trở là đầu vào giả lập độc lập; đưa về 0 không có nghĩa LED vật lý trong Wokwi phải tắt. OPEN_LOAD là cảnh báo sự không khớp giữa yêu cầu sáng và đầu vào tải, không phải bảo vệ quá dòng.',
  'MQTT dùng cơ chế publish/subscribe qua broker. Topic chứa node ID để định tuyến; payload có schema_version, boot_id, seq và uptime_ms để kiểm tra phiên khởi động, thứ tự và khoảng dữ liệu. Retained ONLINE chỉ thông báo ứng viên boot; cần telemetry hợp lệ mới để xác nhận freshness.',
  'Lệnh điều khiển có ID, boot đích và deadline. API trả 202 biểu thị đã tiếp nhận yêu cầu; chỉ ACK từ node mới xác nhận APPLIED hoặc REJECTED. Timeout là trạng thái cuối, ACK muộn được lưu chẩn đoán và không biến một lệnh đã timeout thành thành công.',
  'SQLite lưu dữ liệu và trạng thái điều phối trên máy local. FastAPI cung cấp truy vấn và lệnh qua HTTP; dashboard không kết nối MQTT trực tiếp và không tính lại công thức điện năng trên trình duyệt.',
  note('Chọn MQTT vì phù hợp luồng telemetry và điều khiển bất đồng bộ trong mô hình. Kết quả đồ án không so sánh hiệu năng MQTT với giao thức khác và không khẳng định ưu thế trên mọi mạng.')
]);
page('CHƯƠNG 3. YÊU CẦU VÀ KIẾN TRÚC', [
  table(['Nhóm yêu cầu', 'Hành vi cần chứng minh'], [
    ['FR-01–05', 'Môi trường; AUTO; PIR + khoảng cách; hold; dimming'],
    ['FR-06–08', 'MQTT; giám sát ba node; lệnh đúng đích và có ACK'],
    ['FR-09–10', 'Lỗi tải/phục hồi; lịch sử bền vững qua restart'],
    ['FR-11–12', 'Năng lượng có công thức/CSV/độ phủ; AUTO khi mất MQTT']
  ], [2000, 7071]),
  heading('3.1. Luồng dữ liệu', 2),
  'Cảm biến → SensorReader → LightingController/DimmingController → LED và snapshot → Connectivity → Mosquitto → collector FastAPI → SQLite → API → dashboard.',
  heading('3.2. Luồng lệnh', 2),
  'Dashboard → POST command → lưu PENDING → publish MQTT → node kiểm tra boot/deadline/session → controller áp dụng → ACK → backend kết thúc lệnh → dashboard đọc trạng thái cuối.',
  'Ba node sử dụng ba phiên Wokwi độc lập. Gateway VS Code đưa kết nối đến host.wokwi.internal:1883; backend dùng 127.0.0.1:1883. Broker demo chỉ lắng nghe loopback, không triển khai Internet.',
  'Một source firmware được build thành esp32dev/node_02/node_03; chỉ khác SMARTLIGHT_NODE_INDEX. NodeIdentity thống nhất nhãn Serial, node ID, client ID và topic. Không sao chép source thành ba chương trình riêng.',
  note('API QA của đợt đo dùng cổng 8001; dashboard QA cổng 5500. Đây là cấu hình đợt kiểm tra, không tự đổi API mặc định 8000 trong source bàn giao.')
]);
page('3.3. TRẠNG THÁI VÀ BẢNG ĐIỀU KHIỂN', [
  table(['Môi trường', 'PIR LOW', 'Người giả lập', 'Xe/UNKNOWN'], [
    ['DAY', '0%', '0%', '0%'], ['TWILIGHT', '50%', '70%', '100%'], ['NIGHT', '25%', '70%', '100%']
  ], [2200, 2000, 2300, 2571]),
  'Giữ sáng 5 giây tính từ lần cuối PIR HIGH; sự kiện mới làm mới timer và mức cao nhất đang còn hiệu lực được giữ lại. Sang DAY hủy hold. Dimming chạy riêng để PWM tiến dần đến mục tiêu.',
  table(['Trạng thái hiện tại', 'Điều kiện ADC để đổi trạng thái'], [
    ['Khởi tạo', '<1200 DAY; 1200–2600 TWILIGHT; >2600 NIGHT'],
    ['DAY', '≥1300 → TWILIGHT; ≥2700 → NIGHT'], ['TWILIGHT', '≤1100 → DAY; ≥2700 → NIGHT'],
    ['NIGHT', '≤2500 → TWILIGHT; ≤1100 → DAY']
  ], [2500, 6571]),
  'MANUAL nhận số nguyên 0–100, ưu tiên mức sáng người vận hành trong tối đa 60 giây theo uptime node. Mất MQTT được xác định thì về AUTO; reconnect không phục hồi lệnh MANUAL cũ. LDR vẫn cập nhật trong MANUAL để AUTO có trạng thái mới khi chuyển lại.',
  'Với applied ≥20% ổn định 1 giây, đầu vào tải dưới 10% liên tục 2 giây gây OPEN_LOAD. Tải phục hồi từ 20% dòng kỳ vọng trong 3 giây mới xóa lỗi. Đổi mode không tự xóa fault; mất kết nối không đồng nghĩa fault đã phục hồi.',
  note('Các ngưỡng và timer giữ nguyên source/SRS đã chốt. Giá trị ADC invalid và UNKNOWN là xử lý bảo vệ phần mềm; không tuyên bố phát hiện đứt dây LDR trên mạch thật.')
]);
page('3.4. GIAO THỨC VÀ DỮ LIỆU', [
  table(['Topic dưới huit/nhom7/smartlight/v1/{node_id}', 'Vai trò'], [
    ['/telemetry', 'Sensor, mode/environment/motion, target/applied, power, faults, boot/seq/uptime'],
    ['/availability', 'ONLINE retained và LWT OFFLINE'], ['/command', 'Lệnh AUTO/MANUAL, định danh/deadline/boot'], ['/ack', 'Kết quả lệnh từ node']
  ], [5200, 3871]),
  'PubSubClient phát telemetry và ACK ở QoS0. Backend phát command QoS1, không retain; LWT yêu cầu QoS1. Chống lệnh cũ dựa trên ID/deadline/boot/session và cache kết quả, không suy luận rằng QoS tự đảm bảo “exactly once” ở tầng nghiệp vụ.',
  'Database có nodes, boots, telemetry, availability, alerts, commands, ack_events, experiments và ingest_errors. Unique(node_id, boot_id, seq) chống ghi trùng; seq/uptime lưu chuỗi thập phân để giữ miền số nguyên lớn. Payload gốc được giữ để audit.',
  'Telemetry không hợp lệ không trở thành mẫu 0. Collector ghi lý do và đặt rào cản continuity khi có mất dữ liệu. Mẫu cũ hoặc boot đã nghỉ không được ghi đè latest. Sau restart, dữ liệu lịch sử còn đọc được nhưng cần mẫu mới để cấp lại freshness và quyền điều khiển.',
  'Một worker sở hữu actor/SQLite; callback MQTT chỉ đưa sự kiện vào queue. OS lock ngăn hai backend cùng thu thập vào một DB. Khi backend khởi động lại, PENDING cũ chuyển TIMEOUT/BACKEND_RESTART và không được phát lại.',
  note('Hợp đồng đầy đủ: docs/techs/mqtt.md và /openapi.json. Báo cáo mô tả cấu trúc đã triển khai, không thay thế schema hoặc lược bỏ điều kiện kiểm tra payload.')
]);
page('CHƯƠNG 4. XÂY DỰNG HỆ THỐNG', [
  heading('4.1. Firmware và mô phỏng', 2),
  'PlatformIO giữ board esp32dev, framework Arduino và entry point src/main.cpp với setup()/loop(). Pin map và toolchain được khóa theo cấu hình dự án. Script prepare-simulation.py chọn đúng artifact từng node, kiểm nguồn/hash và sao chép vào cấu hình mô phỏng tương ứng.',
  'SensorReader lấy PIR 20 ms, analog 100 ms, siêu âm 200 ms. ECHO dùng ngắt cạnh, không chặn vòng điều khiển để chờ pulseIn. Uptime64 dùng esp_timer_get_time; timer điều khiển dựa phép trừ unsigned để chịu tràn bộ đếm.',
  'Connectivity gộp snapshot mới nhất, rate-limit 200 ms và heartbeat 2 giây mô phỏng. TASK-011 đã sửa generation khi raw cảm biến thay đổi để không chờ thay đổi control mới phát telemetry. Bộ đếm lấy mẫu nội bộ không làm phát thêm bản tin nghiệp vụ.',
  heading('4.2. Cấu hình môi trường đo', 2),
  'Ba diagram dùng cap thực thi Wokwi 4 MHz như baseline nghiệm thu; không dùng cap này làm kết luận tốc độ ESP32 thật. Mỗi node có Serial RFC2217 riêng 4000/4001/4002 và một Code profile QA riêng.',
  'Docker daemon không hoạt động trong phiên đo. Đợt QA dùng Mosquitto native 2.1.2 dựng từ nguồn chính thức trong thư mục riêng; cấu hình local tương đương vai trò broker cần kiểm. Không đổi hạ tầng sản phẩm để hợp thức hóa môi trường QA.',
  'LDR được đặt 100 klux cho DAY, 100 lux cho TWILIGHT và 0,1 lux cho NIGHT; giá trị quan sát tương ứng khoảng ADC32/2045/4063. Khoảng cách UI150 cm cho telemetry khoảng152 cm và UI50 cm cho khoảng51 cm; các trường hợp vẫn nằm đúng phía ngưỡng100 cm.',
  note('Nguồn/version/hash và cấu hình đợt đo nằm trong baseline.json, broker-build.json, calibration.json và runtime.json của hồ sơ TASK-012.')
]);
page('4.3. BACKEND VÀ DASHBOARD', [
  'Backend FastAPI có một worker, dùng Paho MQTT và SQLite WAL. Collector kiểm schema, boot/order/session, lưu dữ liệu rồi cập nhật trạng thái. Health tách database, broker, queue và dropped_events; không chỉ trả một cờ “server đang chạy”.',
  'Các nhóm API gồm health/nodes, history, commands/command result, alerts/stats, experiments/start/stop/detail/export.csv. Phiên đo được mở và đóng rõ ràng; export và thống kê ràng buộc theo experiment_id cùng biên truy vấn.',
  'Dashboard là HTML/CSS/JavaScript thuần, font hệ thống và SVG nội bộ; không yêu cầu framework hoặc build frontend. Chạy bằng engine Live Server từ extension VS Code. Năm view: tổng quan, chi tiết node, lịch sử, cảnh báo và phiên thực nghiệm.',
  'Health/nodes/kết quả lệnh được polling mỗi giây; stats/alerts/list phiên mỗi 5 giây khi view liên quan đang mở. GET có timeout và tránh chồng yêu cầu. Tab ẩn dừng/hủy GET; khi hiện lại phải đồng bộ trạng thái mới trước khi cho thao tác.',
  'Nút Áp dụng mới gửi command; draft form không bị polling ghi đè. APPLIED xác nhận mode/target, trong khi applied có thể đang dim. POST không tự retry; khi phản hồi không xác định, giao diện kiểm pending_command_id thay vì tạo lệnh trùng.',
  'Khi API mất hoặc node stale/offline, dashboard giữ snapshot kèm nhãn cũ và khóa lệnh. Fault tải, kết nối và freshness được hiển thị tách biệt. History ngắt đường khi boot/continuity/order/gap không phù hợp; bảng raw hỗ trợ đọc chính xác giá trị.',
  note('Các kiểm tra giao diện fixture của TASK-009 và kiểm tra tích hợp live TASK-010/011 có nguồn khác nhau. Chỉ bằng chứng live mới được dùng để mô tả phản ứng hệ thống ba node thật trong Wokwi.')
]);
const shot = path.join(q, fs.existsSync(path.join(q,'screenshots/handover-overview-1920.png')) ? 'screenshots/handover-overview-1920.png' : 'screenshots/EX-01-r01-a01-dashboard-end.png');
const shotItems = ['Ảnh dưới là dashboard của đợt thực nghiệm Wokwi. Mọi giá trị là trạng thái quan sát trong lần chụp; ảnh tĩnh không thay cho nhật ký hoặc phép đo độ trễ. KPI trên ảnh dùng cửa sổ mặc định một giờ của giao diện, khác cửa sổ riêng từng phiên trong Chương5.'];
if (fs.existsSync(shot)) { const png = fs.readFileSync(shot), ratio = png.readUInt32BE(16)/png.readUInt32BE(20), width = Math.min(560,450*ratio); shotItems.push(new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.ImageRun({ data: png, type: 'png', transformation: { width, height: width/ratio } })] })); }
shotItems.push(note('Hình 4.1. Vùng xem dashboard QA; nguồn screenshots/'+path.basename(shot)+'. Ảnh giữ đúng tỉ lệ; bản gốc và hash được giữ trong bộ bàn giao.'));
shotItems.push('Kiến trúc triển khai gồm ba phiên Wokwi qua gateway VS Code đến broker local, FastAPI, SQLite và dashboard.');
page('4.4. GIAO DIỆN VẬN HÀNH', shotItems);
page('CHƯƠNG 5. KIỂM THỬ VÀ THỰC NGHIỆM', [
  heading('5.1. Kết quả kiểm thử kế thừa', 2),
  table(['Tầng', 'Kết quả có bằng chứng'], [
    ['Host/build TASK-011', '11 lượt C++ host; 2 compile-fail đúng kỳ vọng; build đủ3 environment'],
    ['Điều khiển ba node', '30/30 command APPLIED đúng đích; 10/node'],
    ['Sensor → dashboard', '30/30 mẫu chính dưới3 giây thực; proxy render DOM có biên sai số'],
    ['Ổn định', '1.800 giây thực; 5.360 raw telemetry khớp SQLite ACCEPTED'],
    ['Công cụ TASK-012', '34 Python test PASS; gồm clock qua reboot và toàn vẹn CSV; pilot90s/node tách riêng']
  ], [2600, 6471]),
  'Cửa sổ ổn định TASK-011 có MQTT recorder và backend bao phủ đủ, nhưng HTTP/resource probe chỉ ghi 1.346,506 giây rồi dừng SIGTERM. Vì vậy không tuyên bố đã giám sát liên tục mọi frame dashboard hoặc đủ 900 mẫu HTTP trong30 phút.',
  'Latency sensor→dashboard được đo riêng bằng hành động LDR, raw/API/DOM và clock bracket; khác với khoảng cách giữa hai telemetry periodic. Khoảng nhận periodic có thể dài hơn3 giây thực khi mô phỏng chạy chậm, không tự suy thành độ trễ nhân quả của một hành động cảm biến.',
  heading('5.2. Thiết kế thực nghiệm', 2),
  'Mỗi lượt chạy đồng thời cả3 node, dùng recipe đã chốt trước. Pilot dùng để kiểm công cụ/clock/tác động; không đưa vào trung bình chính. Một lượt chỉ hợp lệ khi đủ thời lượng từng node, tác động đúng lịch, hành vi đúng và số học độc lập khớp API/CSV.',
  note('Nguồn kế thừa: docs/reports/evidence/task-011/run-20261117-135233/README.md. Source firmware/backend/dashboard được đối chiếu hash trước đo; không coi build đạt là bằng chứng chạy mô phỏng đạt.')
]);
page('5.3. LỊCH KỊCH BẢN VÀ CLOCK', [
  table(['Mã', 'Kịch bản', 'Số lượt × thời lượng/node'], scenarios, [1300, 5100, 2671]),
  'Tổng 15 lượt chính, tương ứng150 phút mô phỏng mỗi node. Thời lượng5/10/15 phút và lịch tác động dùng uptime riêng từng node, theo lựa chọn người dùng. Thời gian chạy trên máy có thể dài hơn do tốc độ mô phỏng; UTC/monotonic được ghi riêng.',
  'EX-03 và EX-04 kích PIR tại giây15 rồi mỗi30 giây. EX-01 thay khoảng cách và kích chuyển động trong DAY để kiểm đèn vẫn0%. EX-05 dùng ba pha300 giây: (DAY, NIGHT yên tĩnh, NIGHT người), (TWILIGHT, NIGHT người, NIGHT xe), (NIGHT xe, DAY, NIGHT yên tĩnh).',
  'EX-06 đặt tải node_02 về0 ở giây60 và phục hồi ở180. EX-07 dừng broker ở60, khởi động lại120 theo uptime node_02; đổi LDR node_01 sang DAY75 và NIGHT90. Serial chỉ đọc chứng minh AUTO vẫn phản ứng trong lúc không có MQTT.',
  'Tác động vật lý được chặn trễ tối đa2 giây mô phỏng. Mở bảng cảm biến trước là bước chuẩn bị, không phải tác động. Nếu vượt giới hạn hoặc mất giám sát, giữ lượt INCOMPLETE/FAIL và chạy lại toàn lượt; không bù bằng thao tác dồn.',
  ...(timingBounds.length ? [`Biên trễ cao nhất đã ghi trong các lượt hợp lệ là ${fmt(Math.max(...timingBounds)/1000,3)} giây mô phỏng. Nhật ký giữ mốc trước/sau và nguồn xác nhận PIR/cảm biến; chỉ số này tách biệt với độ trễ cảm biến→dashboard theo giây thực.`] : []),
  note('Dừng cửa sổ phân tích mỗi node tại mẫu được nhận đầu tiên đạt thời lượng, vì chu kỳ telemetry không đặt đúng mọi mốc. Phần vượt tối đa theo khoảng lấy mẫu được công bố; không tính toàn bộ thời gian node nhanh chờ node chậm.')
]);
page('5.4. CÁCH TÍNH NĂNG LƯỢNG VÀ ĐỘ PHỦ', [
  'Công suất mô hình: P_sim = V_nominal × I_sim. Ở tải bình thường, P_sim ≈24 × brightness_applied/100 W. Điện năng mỗi đoạn theo hình thang: ΔE_Wh = (P_trước + P_sau)/2 × Δuptime_giây/3600.',
  'Chỉ nối hai mẫu cùng boot, đúng thứ tự, cùng continuity và0 < Δuptime ≤6 giây; hai mẫu phải nằm trong cửa sổ truy vấn/phiên. Quality invalid, đổi boot, mất continuity hoặc khoảng dài tạo rào cản; không nội suy lấp dữ liệu mất.',
  'Tổng năng lượng hợp lệ của mọi chế độ được giữ riêng. So sánh AUTO loại đoạn có đầu mút MANUAL, UNKNOWN, fault, xác minh/phục hồi fault, load_factor<0,95 hoặc đổi environment/mode/fault. Lý do loại được đếm trong hồ sơ. Lỗi tải không được tính như “tiết kiệm” do đèn tiêu thụ0.',
  'Baseline trên cùng đoạn AUTO hợp lệ: DAY0 W; TWILIGHT/NIGHT24 W. Tỷ lệ =100 × (E_baseline−E_AUTO)/E_baseline. Baseline0 trả null. Không dùng đèn sáng100% cả ngày làm đối chứng vì sẽ phóng đại hiệu quả của DAY.',
  'Độ phủ sử dụng các khoảng thời gian nhận UTC đủ điều kiện nối, chia cho thời gian truy vấn. Độ phủ cao chỉ cho biết tính liên tục ở máy thu theo quy tắc này; không chứng minh cảm biến chính xác, không đại diện mật độ giao thông ngoài thực tế và không biến uptime thành thời gian thực.',
  'Phép tính độc lập đọc payload SQLite, đối chiếu API/CSV trong1e-9 Wh. Truy vấn UTC bao quanh hai endpoint SQL thêm2 microsecond để tránh làm rơi mẫu do làm tròn. CSV được lọc theo từng cửa sổ; năng lượng hàng đầu bị bỏ vì không có cặp trước trong cửa sổ đó.',
  note('Raw MQTT được đối chiếu nguyên payload với SQLite, kèm boot/seq và hash. Kết quả kiểm độc lập: ' + audit.status + '; ' + audit.accepted_runs + '/15 lượt đã có đủ hồ sơ tại thời điểm tạo tệp.')
]);
const resultRows = scenarios.map(([code]) => {
  const runs = audit.runs.filter(run => run.scenario === code);
  const values = runs.flatMap(run => Object.values(run.nodes));
  const sum = key => values.reduce((total, item) => total + item[key], 0);
  const baseline = sum('baseline_wh'), energy = sum('auto_energy_wh');
  return [code, String(runs.length) + '/' + (['EX-02','EX-03','EX-04','EX-05'].includes(code) ? '3' : '1'),
    values.length ? fmt(energy, 4) : 'Chưa đủ', values.length ? fmt(baseline, 4) : 'Chưa đủ', baseline ? fmt(100 * (baseline-energy)/baseline, 2) + '%' : '—'];
});
page('5.5. KẾT QUẢ TỔNG HỢP', [
  `${complete ? 'Bảng sử dụng đủ 15 lượt chính hợp lệ.' : 'Bảng tạm thời chỉ sử dụng các lượt đã PASS; không đại diện kết luận cuối cùng.'} Điện năng trong bảng là tổng các cửa sổ AUTO hợp lệ của ba node và các lần lặp tương ứng.`,
  table(['Kịch bản', 'Lượt đạt', 'E_AUTO (Wh)', 'Baseline (Wh)', 'Chênh lệch'], resultRows, [1400, 1300, 2100, 2200, 2071]),
  'Chênh lệch tổng được tính từ tổng năng lượng và tổng baseline, không lấy trung bình tùy ý các phần trăm có mẫu số khác nhau. EX-01 có baseline0 nên không báo tỷ lệ tiết kiệm. EX-06/07 chủ yếu kiểm chức năng lỗi/mạng; không dùng khoảng thiếu hoặc lỗi tải làm bằng chứng tăng hiệu quả.',
  'So sánh giữa các lần lặp cần xem cả công suất trung bình trên thời gian AUTO hợp lệ, vì số mẫu và endpoint có thể khác nhẹ. Bộ JSON/CSV giữ số liệu từng node/từng lượt để tái lập; giá trị làm tròn trong Word chỉ phục vụ trình bày.',
  note('Đây là năng lượng mô hình của recipe mô phỏng định trước. Không ngoại suy thành số tiền tiết kiệm hoặc tỷ lệ tiết kiệm cho một tuyến đường thật chưa được khảo sát.')
]);
const repeatRows = audit.runs.map(run => {
  const v = Object.values(run.nodes), sum = key => v.reduce((a,b) => a+b[key],0);
  const duration = sum('auto_valid_uptime_s'), power = duration ? sum('auto_energy_wh') * 3600 / duration : null;
  return [run.scenario + '/R' + run.repeat, fmt(power, 3), fmt(Math.min(...v.map(n => n.coverage_percent)), 3), String(v.reduce((a,n) => a+n.sample_count,0))];
});
page('5.6. SỐ LIỆU TỪNG LƯỢT', [
  table(['Lượt chính', 'P_AUTO TB (W/node)', 'Coverage thấp nhất (%)', 'Mẫu, cả3 node'], repeatRows.length ? repeatRows : [['Chưa có', '—', '—', '—']], [2100, 2500, 2500, 1971]),
  'P_AUTO trung bình là tổng E_AUTO chia tổng thời gian AUTO hợp lệ của các node, nhân3600; đây là trung bình có trọng số theo thời lượng. Coverage thấp nhất là min của ba node, không che node thiếu dữ liệu bằng cách cộng vào node khác.',
  'Các lần lặp là quan sát kỹ thuật trên cùng mô hình, không phải các đối tượng ngoài thực tế độc lập. Khoảng min–max mô tả độ biến thiên của recipe và runtime; không trình bày như khoảng tin cậy thống kê cho cả quần thể giao thông.',
  note('Chi tiết exclusion, total_energy_wh, seq đầu/cuối, duration từng node, hash payload và sai số đối chiếu nằm trong analysis-final.json hoặc bản snapshot đang dùng. CSV gốc từng attempt giữ nguyên precision.')
]);
const failed = audit.attempts.filter(item => ['FAIL', 'INCOMPLETE'].includes(item.status));
const failureReason = item => {
  const message = item.errors.map(error=>typeof error==='string'?error:[error.node_id,error.error].filter(Boolean).join(': ')).join('; ');
  if(message.includes('Quiet NIGHT25 not maintained')) return 'Không duy trì NIGHT25 yên tĩnh; ghi nhận PIR/khoảng cách ngoài recipe. Giữ dữ liệu và chạy lại toàn lượt.';
  if(message.includes('connection failed (reader thread died)')) return 'Mất kết nối Serial trong khi đo; giữ lượt bị ngắt và chạy lại từ đầu sau phục hồi.';
  if(message.includes('HTTP Error 500')) return 'Chuẩn bị UI thất bại do LDR bị toolbar che. Đã căn lại viewport trước khi đo lại.';
  if(message.includes('Connection refused')) return 'UI bridge chưa sẵn sàng; đã bổ sung kiểm tra readiness trước khi bắt đầu.';
  if(message.includes('Action late beyond2s') || message.includes('Missed action')) return 'Tác động không đạt lịch/biên trễ2s mô phỏng; giữ nhật ký và chạy lại trọn lượt.';
  return message;
};
const variationRows = ['EX-02','EX-03','EX-04','EX-05'].map(code => {
  const runs = audit.runs.filter(run => run.scenario === code);
  const values = runs.map(run => {
    const nodes = Object.values(run.nodes), sum = key => nodes.reduce((a,n) => a+n[key],0);
    return { power: sum('auto_energy_wh')*3600/sum('auto_valid_uptime_s'), saving: sum('baseline_wh') ? 100*(sum('baseline_wh')-sum('auto_energy_wh'))/sum('baseline_wh') : null };
  });
  const summary = key => values.length && values.every(v=>v[key]!==null) ? fmt(values.reduce((a,v)=>a+v[key],0)/values.length,3)+' ['+fmt(Math.min(...values.map(v=>v[key])),3)+'–'+fmt(Math.max(...values.map(v=>v[key])),3)+']' : 'Chưa đủ';
  return [code, String(runs.length)+'/3', summary('power'), summary('saving')];
});
const variationItems = [table(['Kịch bản','Lượt','P_AUTO TB [min–max], W','Chênh lệch TB [min–max], %'], variationRows, [1400,1000,3300,3371]),
  'Mỗi điểm là một lần lặp với ba node. Trước hết tính công suất từ tổng năng lượng và tổng thời gian AUTO hợp lệ trong lượt, sau đó tính trung bình/min–max giữa các lượt cùng recipe. Baseline của EX-05 gồm cả DAY0W và TWILIGHT/NIGHT24W trên đúng đoạn hợp lệ, nên công suất baseline trung bình có thể nhỏ hơn24W.'];
const plotFile = path.join(out, 'data/auto-power-repetitions.png'), plotSource = path.join(out, 'data/plot-source.json');
if (fs.existsSync(plotFile) && fs.existsSync(plotSource) && JSON.parse(fs.readFileSync(plotSource,'utf8')).audit_sha256 === crypto.createHash('sha256').update(fs.readFileSync(auditFile)).digest('hex')) {
  variationItems.push(new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.ImageRun({ data: fs.readFileSync(plotFile), type: 'png', transformation: { width: 590, height: 283 } })] }));
  variationItems.push(note('Hình 5.1. Công suất mô hình AUTO và baseline cùng cửa sổ; thanh sai số min–max giữa các lần lặp. n là số lượt đã kiểm chứng tại thời điểm tạo tệp.'));
}
variationItems.push('Khoảng biến thiên chỉ mô tả mô hình và recipe này. Không dùng các lần lặp trên cùng máy như bằng chứng định lượng cho tuyến đường thật hoặc làm khoảng tin cậy dân số.');
page('5.7. BIẾN THIÊN GIỮA CÁC LẦN LẶP', variationItems);
page('5.8. LƯỢT LỖI, PHỤC HỒI VÀ TOÀN VẸN', [
  'Ba pilot đầu được giữ INCOMPLETE: hai lượt trễ thao tác quá2 giây, một lượt timeout chuẩn bị giao diện. Công cụ được điều chỉnh chuẩn bị sẵn bảng cảm biến và tăng timeout setup, giữ nguyên giới hạn trễ tác động. Pilot thứ4 PASS90 giây/node, tách khỏi số liệu chính.',
  'Các lượt dưới đây được giữ nguyên trong hồ sơ và không đưa vào trung bình chính. Chỉ lượt chạy lại đủ điều kiện mới tham gia so sánh.',
  table(['Lượt','Kết quả','Nguyên nhân và xử lý'],failed.map(item=>[item.folder,item.status,failureReason(item)]),[2400,1500,5171]),
  'Lượt EX-02 đầu có hai PIR ngoài recipe và khoảng cách node_03 đổi bất ngờ; log không có request tác động tương ứng. Chưa xác định nguyên nhân. Sau đó UI cache được làm mới và khoảng cách thực được kiểm trước mỗi lượt; các cửa sổ QA được tách sang desktop riêng để giảm tương tác ngoài kịch bản.',
  'EX-05/R1 attempt01 bị giữ INCOMPLETE do đổi LDR/khoảng cách node01 tại600s trễ2257ms. Công cụ chuyển việc mở bảng và đọc tọa độ sang290/590s; đến300/600s mới đổi cảm biến bằng chuột/phím thật. Giữ nguyên lịch vật lý và giới hạn2000ms.18 lần diễn tập ngoài phiên đo đạt cận lớn nhất1475ms; lượt lỗi không tham gia kết quả chính.',
  'Đối chiếu độc lập đọc raw MQTT, SQLite và API theo đúng cửa sổ từng node. Audit kiểm payload, quality, boot/seq, số mẫu, thời lượng, công thức và SQLite quick_check. Mất sequence trong EX-07 phải được mô tả như khoảng thiếu do outage, không tự nối hình thang qua khoảng đó.',
  'Source sản phẩm, artifact và đề cương gốc được giữ nguyên theo baseline; chỉ công cụ thực nghiệm, báo cáo và tài liệu liên quan được bổ sung. Tệp output lớn và database nằm ngoài Git, đi kèm manifest SHA256 và bản sao dự phòng theo runbook.',
  note('Sự cố của công cụ đo được công bố cùng cách xử lý. Nguyên nhân thay đổi ngoài recipe chưa được xác định; dữ liệu lỗi được lưu và không tham gia so sánh chính.')
]);
page('CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN', [
  'Hệ thống đã có luồng cảm biến → điều khiển tại ESP32 → MQTT → FastAPI/SQLite → dashboard và luồng command/ACK ngược lại. Nghiệm thu TASK-011 chứng minh ba node độc lập, lệnh đúng đích, lỗi tải/phục hồi, AUTO khi mất broker và lưu lịch sử qua restart trong môi trường đã ghi.',
  `${complete ? 'TASK-012 bổ sung đủ15 lượt chính và đối chiếu độc lập cho dữ liệu điện năng mô phỏng.' : `TASK-012 hiện có ${audit.accepted_runs}/15 lượt chính đã audit; cần hoàn tất các lượt còn lại trước khi chốt kết luận về kết quả EX-series.`} Báo cáo không gán tỷ lệ tiết kiệm mục tiêu trước đo và giữ null khi baseline0.`,
  heading('6.1. Giới hạn', 2),
  'Mô phỏng không chứng minh độ bền, an toàn điện, nhiễu cảm biến, hiệu suất driver hoặc quan hệ PWM–quang thông của đèn thật. PIR/siêu âm chỉ tạo tình huống người/xe quy ước. Biến trở và power_sim là mô hình; chưa có đồng hồ điện hoặc cảm biến dòng được hiệu chuẩn.',
  'Kết quả phụ thuộc recipe, clock mô phỏng và cấu hình máy; thời lượng EX-series theo uptime không thay thế cửa sổ ổn định30 phút thực. HTTP probe của TASK-011 thiếu một phần được công bố riêng. Khả năng vận hành và giải thích của từng thành viên cần được xác nhận trong buổi diễn tập trực tiếp.',
  heading('6.2. Hướng phát triển', 2),
  'Bước kế tiếp có thể triển khai mạch điện áp thấp với driver phù hợp, đo dòng/áp và hiệu chuẩn công suất; sau đó khảo sát điều kiện ánh sáng, độ nhạy và lưu lượng chuyển động thực. Chỉ khi có dữ liệu mới đánh giá hiệu quả năng lượng và độ tin cậy ngoài mô phỏng.',
  'Các mở rộng như đón đầu giữa node, bảo mật MQTT, OTA hoặc cloud nằm ngoài bản nghiệm thu hiện tại và cần đặc tả, đánh giá riêng.'
]);
page('PHỤ LỤC A. CẤU HÌNH VÀ KHỞI ĐỘNG', [
  table(['Linh kiện', 'Chân / cấu hình'], [
    ['LDR analog', 'GPIO34; ADC12 bit'], ['PIR', 'GPIO27'], ['HC-SR04', 'TRIG GPIO18; ECHO GPIO19'],
    ['Tải giả lập', 'GPIO35; 0–4095'], ['LED vàng', 'GPIO26; PWM5 kHz/8bit; điện trở220Ω'], ['Định danh', 'esp32dev→node_01; node_02; node_03']
  ], [2900, 6171]),
  'Giữ ba repo firmware/backend/dashboard cạnh nhau dưới DoAn/. Từ firmware build ba environment theo platformio.ini, sau đó chạy python3 scripts/prepare-simulation.py --node all. Mở từng simulations/node_0N trong một cửa sổ VS Code và Start Simulator sau khi xác nhận Wokwi license/gateway.',
  'Khởi động broker local trước, backend sau với một worker và DB riêng, cuối cùng mở dashboard bằng Live Server. API mặc định8000; nếu dùng QA8001 phải cấu hình URL dashboard tương ứng và CORS cho origin5500. Không chạy hai backend collector trên cùngDB.',
  'Lệnh kiểm công cụ: python3 scripts/experiments.py plan --all; preflight --run-dir <QA_ROOT>; run --run-dir <QA_ROOT> --all --resume. Resume chỉ bỏ qua lượt PASS cùng recipe; không tiếp tục giữa một lượt bị ngắt.',
  'Kết thúc: đóng phiên đo, xuất CSV/backup SQLite qua API backup của SQLite, kiểm quick_check và SHA256, sau đó dừng đúng process QA có PID/start ticks đã ghi. Không xóa DB hoặc dừng dịch vụ khác của người dùng.',
  note('Lệnh/environment đầy đủ, điều kiện license, cold-start và xử lý lỗi xem runbook bàn giao cùng docs/techs/setup.md, simulation.md, backend.md, dashboard.md.')
]);
page('PHỤ LỤC B. TRUY VẤN VÀ BẢO VỆ ĐỒ ÁN', [
  table(['Đường dẫn HTTP', 'Mục đích'], [
    ['GET /api/health; /api/nodes', 'Sức khỏe, fresh/stale/offline, quyền gửi lệnh'], ['GET /api/nodes/{id}/history', 'Lịch sử theo from/to, quality/continuity'],
    ['POST /api/nodes/{id}/commands', 'Gửi AUTO hoặc MANUAL có brightness'], ['GET /api/commands/{id}', 'PENDING/APPLIED/REJECTED/TIMEOUT'],
    ['GET /api/stats; /api/alerts', 'Điện năng/độ phủ và cảnh báo'], ['POST /api/experiments; /{id}/stop', 'Mở/đóng phiên đo'], ['GET /api/experiments/{id}/export.csv', 'CSV gốc của phiên']
  ], [5000, 4071]),
  'Vì sao AUTO nằm tại node? Để vòng điều khiển không phụ thuộc khả năng truy cập backend/broker. Mất MQTT thu hồi MANUAL và chuyển AUTO; telemetry offline được chứng minh bằng Serial, không giả bằng dữ liệu API cũ.',
  'Vì sao cần ACK? HTTP202 và MQTT publish thành công chưa chứng minh controller đã áp dụng. ID/boot/deadline và kết quả từ node giúp phân biệt tiếp nhận, áp dụng, từ chối và hết hạn.',
  'Vì sao không tính khoảng mất dữ liệu bằng0? Không nhận được mẫu không chứng minh công suất bằng0. Khoảng thiếu phải được loại khỏi tích phân và công bố coverage; lỗi tải phải được tách khỏi hiệu quả AUTO.',
  'Vì sao hai kiểu thời gian? Uptime bảo toàn thời lượng mô phỏng để tích phân; UTC mô tả lịch thu nhận ở máy và biên truy vấn. Không nhân tốc độ VM vào công thức năng lượng hoặc dùng uptime để tuyên bố giám sát đủ phút thực.'
]);
page('TÀI LIỆU THAM KHẢO VÀ HỒ SƠ', [
  '[1] Nhóm7. Đèn đường thông minh_DeCuongNhom7 (1).docx. Đề cương gốc; chỉ kế thừa thông tin trường/nhóm/thành viên, không sửa tệp.',
  '[2] Dự án. docs/srs.md, phiên bản1.1 và các điều chỉnh người dùng đã chốt. Yêu cầu FR-01–12, phương pháp điện năng mục9, bộ bàn giao mục15.',
  '[3] Dự án. docs/techs/firmware.md, mqtt.md, backend.md, dashboard.md, simulation.md, testing.md, experiments.md. Mô tả triển khai, cấu hình và giới hạn.',
  '[4] Dự án. TASK-011 — Nghiệm thu ba node, run-20261117-135233. README, latency-final-audit.json, stability-02/wire-audit.json và manifest.',
  '[5] Dự án. TASK-012 — run-20261117-200024. Baseline, recipe, raw MQTT/Serial/probes, attempt result/CSV, independent audit và bộ bàn giao.',
  '[6] Wokwi. VS Code project configuration; FAQ; tài liệu PIR và HC-SR04. https://docs.wokwi.com/vscode/project-config ; https://docs.wokwi.com/faq ; https://docs.wokwi.com/parts/wokwi-pir-motion-sensor ; https://docs.wokwi.com/parts/wokwi-hc-sr04 .',
  '[7] Espressif. Arduino ESP32 LEDC và ADC API. https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html ; https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html .',
  '[8] Eclipse Mosquitto. Authentication methods và cấu hình listener. https://mosquitto.org/documentation/authentication-methods/ .',
  note('Các URL được kế thừa từ tài liệu kỹ thuật dự án; báo cáo không trích dẫn trực tiếp nội dung chưa đối chiếu. Tệp máy đọc được và log là nguồn số liệu chính; Word là bản diễn giải làm tròn để trình bày.')
]);
const center = text => p(text, { alignment: d.AlignmentType.CENTER, spacing: { before: 80, after: 80 } });
const logo = path.join(q, 'reference-assets/image1.jpeg');
const cover = [center('BỘ CÔNG THƯƠNG'), center('TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH'), center('KHOA CÔNG NGHỆ THÔNG TIN')];
if (fs.existsSync(logo)) cover.push(new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { before: 450, after: 450 }, children: [new d.ImageRun({ data: fs.readFileSync(logo), type: 'jpg', transformation: { width: 155, height: 155 } })] }));
cover.push(center(stage), new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { before: 280, after: 280 }, children: [new d.TextRun({ text: 'ĐÈN ĐƯỜNG THÔNG MINH', bold: true, size: 38 })] }),
  center('Tự động điều chỉnh độ sáng theo môi trường và chuyển động'), center('NHÓM 7'), center('Quang Nhật Hưng — 2001230328'), center('Nguyễn Văn Anh Tuấn — 2001230863'), center('Mô phỏng Wokwi · ESP32 · MQTT · FastAPI · Dashboard'),
  new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { before: 800, after: 0 }, children: [new d.TextRun({ text: 'TP. Hồ Chí Minh, tháng 11 năm 2026' })] }));
const properties = { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1701, right: 1134, header: 450, footer: 500 } } };
const doc = new d.Document({ creator: 'Nhóm7', title: 'Đèn đường thông minh — Báo cáo đồ án', subject: 'TASK-012: thực nghiệm và bàn giao', description: stage,
  styles: { default: { document: { run: { font: 'Times New Roman', size: 26, color: '111827' }, paragraph: { alignment: d.AlignmentType.JUSTIFIED, spacing: { before: 0, after: 140, line: 310 } } },
    title: { run: { font: 'Times New Roman', size: 38, bold: true }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
    heading1: { run: { font: 'Times New Roman', size: 30, bold: true, color: '16324F' }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
    heading2: { run: { font: 'Times New Roman', size: 27, bold: true, color: '111827' }, paragraph: { spacing: { before: 160, after: 100 }, keepNext: true } } },
    paragraphStyles: [{ id: 'Note', name: 'Ghi chú', basedOn: 'Normal', run: { font: 'Times New Roman', size: 22, italics: true, color: '475569' }, paragraph: { alignment: d.AlignmentType.LEFT, spacing: { before: 140, after: 100, line: 270 } } }] },
  sections: [{ properties, children: cover }, { properties: { ...properties, type: d.SectionType.NEXT_PAGE, page: { ...properties.page, pageNumbers: { start: 1 } } },
    headers: { default: new d.Header({ children: [new d.Paragraph({ children: [new d.TextRun({ text: 'ĐÈN ĐƯỜNG THÔNG MINH  |  NHÓM7', font: 'Arial', size: 18, color: '64748B' })], border: { bottom: { color: 'CBD5E1', size: 4, style: d.BorderStyle.SINGLE } } })] }) },
    footers: { default: new d.Footer({ children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.TextRun({ text: 'Trang ', size: 20 }), new d.TextRun({ children: [d.PageNumber.CURRENT], size: 20 })] })] }) },
    children: pages.flatMap((items, i) => i ? [new d.Paragraph({ children: [new d.PageBreak()] }), ...items] : items) }]
});
(async () => {
  let target = path.join(out, 'Bao-cao-Den-duong-thong-minh-Nhom7.docx'), version = 1;
  while (fs.existsSync(target)) target = path.join(out, 'Bao-cao-Den-duong-thong-minh-Nhom7-v' + String(++version).padStart(2,'0') + '.docx');
  fs.writeFileSync(target, await d.Packer.toBuffer(doc));
  fs.writeFileSync(target.replace(/\.docx$/,'.md'), '# ' + stage + '\n\nĐèn đường thông minh — Nhóm7\n\nQuang Nhật Hưng (2001230328), Nguyễn Văn Anh Tuấn (2001230863).\n\n' + manuscript.join('\n'));
  fs.writeFileSync(path.join(out, 'report-build.json'), JSON.stringify({ status: stage, audit: path.resolve(auditFile), accepted_runs: audit.accepted_runs, planned_content_pages: pages.length + 1, target, sha256: crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex') }, null, 2) + '\n');
  console.log(JSON.stringify({ target, planned_content_pages: pages.length + 1, accepted_runs: audit.accepted_runs, status: stage }));
})().catch(error => { console.error(error); process.exitCode = 1; });
