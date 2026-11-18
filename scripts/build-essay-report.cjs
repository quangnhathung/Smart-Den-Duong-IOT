#!/usr/bin/env node
// TASK-019: body manuscript only. merge-essay-report.py inherits the original cover/styles.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const [runPath, outputPath] = process.argv.slice(2);
if (!runPath || !outputPath) throw new Error('Usage: node scripts/build-essay-report.cjs RUN_DIR NEW_BODY.docx');
const q = path.resolve(runPath), output = path.resolve(outputPath);
if (fs.existsSync(output)) throw new Error('Refusing to overwrite output');
const d = require(path.join(q, 'runtime/office/node_modules/docx'));
const dataDir = path.resolve(q, '../deliverables/data');
const variation = JSON.parse(fs.readFileSync(path.join(dataDir, 'variation.json')));
const auditPath = path.join(q, 'analysis-final.json');
const audit = JSON.parse(fs.readFileSync(auditPath));
if (audit.status !== 'PASS' || audit.accepted_runs !== 15) throw new Error('Expected the accepted historical audit');
const W = 9071, pages = [], figures = [], sourceMetrics = [];
const p = (text, opts = {}) => new d.Paragraph({ children: [new d.TextRun({ text })], ...opts });
const h = (text, level = 2) => new d.Paragraph({ text, heading: level === 1 ? d.HeadingLevel.HEADING_1 : d.HeadingLevel.HEADING_2 });
const note = text => p(text, { style: 'Note' });
function table(headers, rows, widths) {
  if (widths.reduce((a, b) => a + b, 0) !== W) throw new Error('Table width mismatch');
  function row(values, header) {
    return new d.TableRow({ tableHeader: header, cantSplit: true, children: values.map((value, i) => new d.TableCell({
      width: { size: widths[i], type: d.WidthType.DXA }, margins: { top: 85, bottom: 85, left: 100, right: 100 },
      verticalAlign: d.VerticalAlign.CENTER, shading: { type: d.ShadingType.CLEAR, fill: header ? 'E8EDF2' : 'FFFFFF' },
      children: [p(String(value), { alignment: d.AlignmentType.LEFT, spacing: { before: 0, after: 0, line: 260 },
        children: [new d.TextRun({ text: String(value), font: 'Arial', size: 21, bold: header })] })]
    })) });
  }
  return new d.Table({ width: { size: W, type: d.WidthType.DXA }, columnWidths: widths,
    rows: [row(headers, true), ...rows.map(values => row(values, false))] });
}
function fig(relative, caption, maxWidth = 560, maxHeight = 340) {
  const source = path.join(q, relative), bytes = fs.readFileSync(source);
  if (bytes.toString('hex', 0, 8) !== '89504e470d0a1a0a') throw new Error('Expected original PNG');
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20), scale = Math.min(maxWidth / width, maxHeight / height);
  figures.push({ source, caption, width, height, sha256: crypto.createHash('sha256').update(bytes).digest('hex') });
  return [new d.Paragraph({ alignment: d.AlignmentType.CENTER, keepNext: true, spacing: { before: 100, after: 100 },
    children: [new d.ImageRun({ data: bytes, type: 'png', transformation: { width: Math.round(width * scale), height: Math.round(height * scale) } })] }), note(caption)];
}
function page(title, items, level = 2) {
  pages.push({ title, children: [h(title, level), ...items.map(item => typeof item === 'string' ? p(item) : item)] });
}
const fmt = (n, digits = 3) => Number(n).toLocaleString('vi-VN', { minimumFractionDigits: digits, maximumFractionDigits: digits });

page('LỜI NÓI ĐẦU', [
  'Chiếu sáng đường phố là một nhu cầu thiết yếu của hạ tầng đô thị. Trong những khoảng thời gian ít người và phương tiện qua lại, việc duy trì một mức sáng cố định tạo ra bài toán cân bằng giữa nhu cầu chiếu sáng và năng lượng sử dụng. Từ bài toán đó, nhóm lựa chọn đề tài “Đèn đường thông minh”, xây dựng mô hình có thể tự điều chỉnh độ sáng theo môi trường và chuyển động, đồng thời cung cấp công cụ giám sát tập trung.',
  'Đề tài vận dụng Internet vạn vật (Internet of Things – IoT) để kết nối ba nút đèn mô phỏng. Mỗi nút sử dụng ESP32 đọc cảm biến ánh sáng, chuyển động và khoảng cách, quyết định mức sáng tại chỗ rồi truyền trạng thái về hệ thống quản lý. Người vận hành theo dõi dữ liệu trên dashboard, gửi lệnh điều khiển có phản hồi, xem cảnh báo và đối chiếu các phiên thực nghiệm.',
  'Báo cáo trình bày từ cơ sở IoT đến phần cứng, kiến trúc phần mềm và kết quả demo. Các nội dung triển khai được đối chiếu với source hiện có; số liệu, hình ảnh và kết quả kiểm tra được kế thừa từ hồ sơ TASK-011 và TASK-012. Việc biên soạn lại báo cáo không tạo thêm một đợt đo hoặc một kết quả nghiệm thu mới.',
  'Phạm vi nghiên cứu là mô hình Wokwi trên máy tính, kết nối broker MQTT và ứng dụng local. Công suất, dòng điện và điện năng trong báo cáo được tính theo mô hình tải giả lập. Các giá trị này phục vụ kiểm tra thuật toán và phương pháp thống kê, chưa thay thế số đo điện, độ rọi hoặc đánh giá an toàn của một bộ đèn đường ngoài thực tế.',
  'Nhóm thực hiện gồm Quang Nhật Hưng và Nguyễn Văn Anh Tuấn, Nhóm 7. Nhóm mong nhận được các góp ý về cách thiết kế, trình bày kết quả và giới hạn thực nghiệm để tiếp tục hoàn thiện mô hình trong những giai đoạn phát triển sau.'
], 1);

page('MỤC LỤC', [
  table(['Nội dung', 'Trang'], [
    ['Lời nói đầu', '1'], ['Chương 1. Giới thiệu về IoT', '3'],
    ['1.1. Khái niệm; 1.2. Các thành phần', '3'], ['1.3. Kết nối và truyền thông', '4'], ['1.4. Xử lý tại thiết bị; 1.5. Bài toán của đề tài', '5'],
    ['Chương 2. Giới thiệu phần cứng', '6'], ['2.1. Mô hình; 2.2. ESP32', '6–7'], ['2.3. LDR; 2.4. PIR', '8'], ['2.5. HC-SR04; 2.6. Đầu vào tải', '9'], ['2.7. LED/PWM; 2.8. Giới hạn phần cứng', '10'],
    ['Chương 3. Giới thiệu phần mềm', '11'], ['3.1. Kiến trúc; 3.2. Firmware', '11–12'], ['3.3. AUTO; 3.4. MANUAL và lỗi tải', '13–14'], ['3.5. MQTT; 3.6. Backend', '15–16'], ['3.7. Dashboard; 3.8. Thống kê năng lượng', '17–18'],
    ['Chương 4. Kết quả demo', '19'], ['4.1. Phương pháp; 4.2. Demo AUTO', '19–20'], ['4.3. Điều khiển/lỗi; 4.4. Mất kết nối', '21–22'], ['4.5. Số liệu; 4.6. Chất lượng; 4.7. Đánh giá', '23–24'], ['Lời kết', '25'], ['Tài liệu tham khảo', '26']
  ], [7900, 1171]),
  note('Số trang tính từ Lời nói đầu, không tính bìa. Các đề mục dùng Heading của Word để hỗ trợ Navigation trong Word/WPS. Mức sáng được biểu diễn bằng phần trăm PWM; W và Wh là đại lượng mô phỏng khi không có chú thích khác.')
], 1);

page('CHƯƠNG 1. GIỚI THIỆU VỀ IoT', [
  h('1.1. Khái niệm Internet vạn vật'),
  'Theo ITU-T Y.2060, IoT hình thành hạ tầng kết nối các đối tượng vật lý và đối tượng trong thế giới thông tin thông qua công nghệ thông tin, truyền thông có khả năng tương tác. Việc định danh, thu thập, xử lý và trao đổi dữ liệu giúp các đối tượng tham gia cung cấp dịch vụ; yêu cầu an ninh và quyền riêng tư cần được xem xét cùng với chức năng kết nối [1].',
  'Trong đề tài này, đối tượng được quản lý là từng nút đèn với định danh node_01, node_02 và node_03. Giá trị cảm biến, chế độ hoạt động, mức sáng, trạng thái tải và phiên khởi động tạo thành biểu diễn dữ liệu của nút đèn. Người vận hành có thể quan sát biểu diễn đó và gửi yêu cầu thay đổi chế độ thông qua ứng dụng.',
  h('1.2. Các thành phần trong hệ thống của đề tài'),
  table(['Thành phần', 'Vai trò trong mô hình'], [
    ['Thiết bị và cảm biến', 'ESP32, LDR, PIR, HC-SR04 và đầu vào giả lập tải tạo dữ liệu; LED thể hiện PWM.'],
    ['Kết nối', 'Wi-Fi và MQTT đưa telemetry, lệnh, phản hồi và trạng thái kết nối qua broker.'],
    ['Lưu trữ, xử lý', 'Backend kiểm tra dữ liệu, lưu SQLite, điều phối lệnh và tính thống kê.'],
    ['Ứng dụng', 'Dashboard HTML/CSS/JS hiển thị ba node, lịch sử, cảnh báo và phiên đo.']
  ], [2200, 6871]),
  'Chuỗi xử lý có hai chiều: dữ liệu đi từ cảm biến tới giao diện; lệnh đi từ giao diện tới thiết bị và có phản hồi quay lại. Do đó, một giao diện hiển thị được số liệu chưa đủ chứng minh luồng điều khiển đã hoạt động. Báo cáo kiểm tra cả đường truyền dữ liệu lẫn kết quả áp dụng lệnh tại node.'
], 1);

page('1.3. Kết nối và truyền thông trong IoT', [
  'Trong mô hình, ba ESP32 kết nối Wi-Fi giả lập rồi trao đổi dữ liệu qua Mosquitto chạy local. MQTT 3.1.1 sử dụng mô hình publish/subscribe: bên gửi công bố dữ liệu lên topic, broker chuyển dữ liệu tới các bên đăng ký. Cách tổ chức này tách bên phát khỏi bên nhận và phù hợp với trao đổi telemetry bất đồng bộ [2].',
  'MQTT phân biệt ba mức QoS: 0 có thể mất bản tin; 1 bảo đảm chuyển ít nhất một lần nên có thể trùng; 2 cung cấp chuyển đúng một lần ở cấp giao thức tương ứng [2]. Trong đồ án, telemetry và ACK dùng QoS 0; lệnh từ backend dùng QoS 1. Hệ thống vẫn cần kiểm tra ID lệnh và phản hồi ứng dụng để xác nhận hành vi điều khiển.',
  table(['Luồng', 'Mục đích', 'Cách sử dụng trong đề tài'], [
    ['Telemetry', 'Đồng bộ trạng thái node', 'Gửi định kỳ và khi trạng thái thay đổi; không retained.'],
    ['Command', 'Yêu cầu AUTO/MANUAL', 'Có UUID, boot đích, deadline; không phát lại lệnh cũ khi reconnect.'],
    ['ACK', 'Phản hồi từ firmware', 'APPLIED hoặc REJECTED; backend có thể kết thúc TIMEOUT.'],
    ['Availability', 'Báo phiên kết nối', 'ONLINE/OFFLINE retained và LWT; cần telemetry mới để xác nhận dữ liệu tươi.']
  ], [1600, 2200, 5271]),
  'Topic của đồ án bắt đầu bằng huit/nhom7/smartlight/v1, sau đó là định danh node và loại bản tin. Tên topic giúp định tuyến, còn các trường trong payload giúp xác định đúng phiên khởi động và thứ tự dữ liệu. Hai lớp thông tin này hạn chế nhầm lẫn giữa các node hoặc giữa dữ liệu cũ và trạng thái hiện tại [6].',
  'Kết nối mạng có thể gián đoạn. Vì vậy, backend không xem dữ liệu vừa hiển thị là hiện trạng nếu đã quá hạn freshness; node cũng không chờ broker để thực hiện AUTO. Đây là lựa chọn thiết kế của đề tài, được kiểm tra qua các ca mất kết nối trong chương 4.'
]);

page('1.4. Xử lý tại thiết bị và quản lý dữ liệu', [
  'Xử lý tại thiết bị nghĩa là ESP32 trực tiếp đọc đầu vào và quyết định mức sáng theo trạng thái hiện có. Đường điều khiển cảm biến → controller → PWM không đi vòng qua dashboard. Nhờ đó, khi máy quản lý hoặc broker ngừng hoạt động, node vẫn có thể tiếp tục xử lý môi trường và chuyển động theo chương trình đã nạp.',
  'Ứng dụng trung tâm đảm nhiệm các công việc cần nhìn toàn hệ thống: nhận dữ liệu từ ba node, lưu lịch sử, gửi lệnh có theo dõi kết quả, tổng hợp cảnh báo và tính năng lượng. Cách phân chia trách nhiệm giúp kiểm thử riêng logic điều khiển, giao thức truyền dữ liệu và giao diện, sau đó đối chiếu khi tích hợp.',
  h('1.5. Bài toán, mục tiêu và phạm vi đề tài'),
  'Mục tiêu của mô hình là chọn mức sáng nền theo môi trường, tăng sáng khi có chuyển động, giữ sáng trong một khoảng thời gian rồi giảm dần. Cùng với đó, người vận hành cần phân biệt đèn đang AUTO hay MANUAL, lỗi tải hay mất mạng, và số liệu còn mới hay đã cũ. Kết quả tiết kiệm năng lượng phải gắn với điều kiện đo và baseline cụ thể.',
  table(['Trong phạm vi đã triển khai', 'Giới hạn của kết luận'], [
    ['Ba phiên ESP32 trên Wokwi; một source firmware', 'Chưa kiểm chứng ba bộ mạch vật lý.'],
    ['PIR kết hợp khoảng cách để chia hai nhóm sự kiện', 'Quy ước người/xe trong mô hình; không nhận dạng đối tượng thực.'],
    ['MQTT, FastAPI, SQLite, dashboard local', 'Chưa nghiệm thu cloud, OTA, LoRa hoặc ứng dụng điện thoại.'],
    ['Tích phân điện năng theo uptime và kiểm độ phủ', 'Dựa trên tải mô phỏng 12 V/24 W; chưa đo điện thực.']
  ], [4550, 4521]),
  'Cơ sở đánh giá là yêu cầu SRS và bằng chứng triển khai, không suy ra tính năng chỉ từ mô tả dự kiến. Các phần sau lần lượt giải thích phần cứng, phần mềm và kết quả đã có, qua đó làm rõ điều hệ thống đã chứng minh và điều cần tiếp tục kiểm tra [6].'
]);

page('CHƯƠNG 2. GIỚI THIỆU PHẦN CỨNG', [
  h('2.1. Mô hình một nút đèn'),
  'Mỗi node gồm ESP32, module LDR, PIR, HC-SR04, biến trở giả lập tải và LED qua điện trở 220 Ω. Ba node dùng cùng sơ đồ kết nối; sự khác nhau nằm ở định danh biên dịch và phiên mô phỏng. Hình 2.1 là ảnh đã ghi trong quá trình chuẩn bị video, không phải sơ đồ mạch công suất của đèn đường thật.',
  ...fig('screenshots/video-viewport-node01.png', 'Hình 2.1. Các linh kiện và dây nối của node_01 trên Wokwi. Nguồn: TASK-012, video-viewport-node01.png.', 500, 490),
  'Các đường GND dùng chung để tạo mốc tín hiệu. LDR và biến trở dùng 3,3 V; PIR và HC-SR04 nối nguồn 5 V trong cấu hình mô phỏng. Việc chuyển sang phần cứng thật cần thiết kế lại phần nguồn, mức logic và bộ điều khiển công suất phù hợp.'
], 1);

page('2.2. Vi điều khiển ESP32 và ánh xạ chân', [
  'ESP32 là phần tử xử lý trung tâm. Các ngoại vi Wi-Fi, ADC và PWM của họ ESP32 phù hợp với việc thu thập tín hiệu analog, đọc tín hiệu số và điều khiển đầu ra [3]. Dự án sử dụng board esp32dev với framework Arduino trong PlatformIO; điểm vào chương trình là setup() và loop().',
  table(['Thiết bị/tín hiệu', 'Chân ESP32', 'Chức năng'], [
    ['LDR AO', 'GPIO34', 'Đọc ánh sáng qua ADC 12 bit.'], ['PIR OUT', 'GPIO27', 'Đọc tín hiệu chuyển động HIGH/LOW.'],
    ['HC-SR04 TRIG', 'GPIO18', 'Phát xung kích phép đo khoảng cách.'], ['HC-SR04 ECHO', 'GPIO19', 'Bắt cạnh xung trả về bằng ngắt.'],
    ['Biến trở tải', 'GPIO35', 'Đọc hệ số tải mô phỏng qua ADC.'], ['LED + 220 Ω', 'GPIO26', 'Xuất PWM LEDC 5 kHz, 8 bit.']
  ], [2700, 1800, 4571]),
  'ADC 12 bit đưa ra giá trị 0–4095. Vì vậy, các ngưỡng xử lý ánh sáng và tỷ lệ tải phải dùng miền này. Giá trị điều chỉnh trên một số widget Wokwi có miền khác; chẳng hạn biến trở hiển thị 0–1023 nhưng firmware đọc lại qua ADC 0–4095. Không lấy trực tiếp con số trên widget thay cho giá trị đo của firmware.',
  'Ba environment esp32dev, node_02 và node_03 được build từ cùng source, với SMARTLIGHT_NODE_INDEX lần lượt bằng 1, 2 và 3. NodeIdentity tạo thống nhất node ID, MQTT client ID và topic. Cách cấu hình này tránh sai lệch do sao chép ba chương trình điều khiển riêng.',
  'Firmware tách tác vụ mạng và vòng điều khiển. Kết quả kiểm tra trong hồ sơ áp dụng cho cấu hình firmware đã dùng ở đợt nghiệm thu; thông số CPU của mô phỏng và thời gian thực trên máy không được coi là phép đo năng lực xử lý của mạch ESP32 vật lý [6].'
]);

page('2.3. Cảm biến ánh sáng LDR', [
  'Module LDR cung cấp đầu ra analog biểu diễn mức sáng của môi trường mô phỏng. Trong sơ đồ đang dùng, ADC nhỏ tương ứng môi trường sáng và ADC lớn tương ứng môi trường tối. Firmware đọc AO tại GPIO34, không sử dụng ngõ ra số để quyết định ba trạng thái môi trường.',
  'Bộ lọc lấy trung bình trượt 5 mẫu analog mới. Trạng thái ứng viên cần ổn định 1 giây trước khi được xác nhận; các biên hysteresis khác nhau khi đi lên và đi xuống giúp hạn chế đổi trạng thái liên tục. Ngưỡng khởi tạo là DAY dưới 1200, TWILIGHT từ 1200 đến 2600, NIGHT trên 2600.',
  table(['Trạng thái đang có', 'Điều kiện ra khỏi trạng thái'], [
    ['DAY', 'ADC đã lọc ≥ 1300 để xét chuyển lên.'], ['TWILIGHT', 'ADC ≤ 1100 vào DAY; ADC ≥ 2700 vào NIGHT.'], ['NIGHT', 'ADC ≤ 2500 để xét chuyển xuống.']
  ], [2600, 6471]),
  h('2.4. Cảm biến chuyển động PIR'),
  'PIR đưa tín hiệu OUT lên HIGH khi mô hình phát hiện chuyển động. Wokwi cho phép người dùng chọn cảm biến rồi bấm Simulate motion [5]. Trong sơ đồ của đề tài, delayTime được đặt 1 giây; khoảng HIGH của cảm biến và thời gian giữ sáng 5 giây của firmware là hai cơ chế khác nhau.',
  'PIR là điều kiện khởi phát xử lý chuyển động. Khi PIR vẫn LOW, dù khoảng cách đo thay đổi từ 2 cm đến hơn 200 cm, controller vẫn ghi motion=NONE và giữ mức nền NIGHT 25% nếu không còn hold. Vì thế, khi demo cần quan sát cả pir, motion và target, sau đó phát Simulate motion để tạo sự kiện.',
  'Giá trị ldr_adc khoảng 4063 trong log cho thấy đầu vào tối theo cấu hình hiện tại. Nếu environment đã là NIGHT, việc làm tối thêm không tạo một mức nền mới: controller tiếp tục chọn 25% cho thời gian yên tĩnh. Hành vi này phù hợp với bảng điều khiển AUTO của đề tài.'
]);

page('2.5. Cảm biến khoảng cách HC-SR04', [
  'HC-SR04 sử dụng chân TRIG để bắt đầu đo và ECHO để biểu diễn thời gian truyền âm. Tài liệu mô phỏng quy định xung kích tối thiểu 10 µs và quy đổi khoảng cách theo độ rộng ECHO; widget cho phép đặt khoảng cách từ 2 đến 400 cm [4]. Firmware của đề tài bắt cạnh ECHO bằng ngắt và có timeout 30 ms, không chờ pulseIn kéo dài trong vòng điều khiển.',
  'Khoảng cách chỉ được diễn giải thành nhóm sự kiện khi PIR HIGH. Dưới 100 cm là VEHICLE, từ 100 cm trở lên là PEDESTRIAN; đây là quy ước thử nghiệm. Đầu vào không hợp lệ trong lúc có chuyển động được xếp UNKNOWN và chọn mục tiêu 100%. Số đo khoảng cách không cung cấp bằng chứng nhận dạng xe hoặc người ngoài thực tế.',
  h('2.6. Biến trở giả lập trạng thái tải'),
  'Biến trở đưa một điện áp analog vào GPIO35 để tạo hệ số tải f = current_adc / 4095. Mô hình quy ước đèn định mức 12 V, 24 W, tương ứng dòng 2 A ở mức sáng 100% và tải đủ. Tên trường current_adc được giữ theo hợp đồng dữ liệu; linh kiện trong Wokwi không phải cảm biến dòng điện thật.',
  table(['Giá trị minh họa', 'Ý nghĩa trong mô hình'], [
    ['current_adc = 4095', 'f = 1; tải mô phỏng đủ. NIGHT 25% cho I_sim = 0,5 A và P_sim = 6 W.'],
    ['current_adc gần 0', 'Tải mô phỏng suy giảm; có thể phát OPEN_LOAD sau điều kiện xác nhận.'],
    ['LED vẫn sáng khi giảm biến trở', 'Biến trở không cắt mạch LED; cảnh báo được tính từ mô hình tải.']
  ], [3000, 6071]),
  'Việc giảm hệ số tải chỉ phục vụ demo phát hiện bất thường. Các khoảng giảm tải, xác minh lỗi và phục hồi được loại khỏi so sánh AUTO hợp lệ; báo cáo không coi công suất thấp do lỗi tải là thành quả tiết kiệm năng lượng.'
]);

page('2.7. LED, PWM và quá trình chuyển mức sáng', [
  'LED tại GPIO26 thể hiện đầu ra điều khiển, mắc qua điện trở 220 Ω trong mô phỏng. LEDC chạy ở tần số 5 kHz, độ phân giải 8 bit; miền duty là 0–255. Phần trăm mức sáng được quy đổi sang duty, nên 25% tương ứng khoảng 64. Đây là thông số PWM, chưa phải độ rọi đo trên mặt đường.',
  'Controller sinh brightness_target, còn DimmingController đưa brightness_applied tiến dần tới mục tiêu với bước tối đa 2 điểm phần trăm mỗi 20 ms. Hai giá trị có thể khác nhau trong giai đoạn chuyển tiếp. Khi lệnh đã APPLIED, cần tiếp tục xem applied để biết PWM đã ổn định ở mục tiêu hay chưa.',
  h('2.8. Giới hạn của phần cứng mô phỏng'),
  'Wokwi cho phép tạo đầu vào lặp lại và quan sát Serial thuận tiện, nhưng không tái hiện đầy đủ nhiễu, ánh sáng ngoài trời, sai số cảm biến, lắp đặt, nhiệt độ hoặc đặc tính bộ nguồn LED. Quan hệ công suất tuyến tính với phần trăm PWM là giả định của mô hình, chưa được hiệu chuẩn bằng thiết bị đo.',
  table(['Hạng mục', 'Yêu cầu trước khi thử phần cứng thật'], [
    ['Nguồn và tín hiệu', 'Kiểm tra cấp nguồn, mức ECHO, chuyển mức logic và nối đất phù hợp ESP32.'],
    ['Đèn công suất', 'Thiết kế driver/MOSFET, bảo vệ và tản nhiệt; không nối đèn đường trực tiếp vào GPIO.'],
    ['Đo lường', 'Đo dòng, áp, công suất, độ rọi và đặc tuyến PWM bằng thiết bị phù hợp.'],
    ['Cảm biến', 'Hiệu chỉnh ngưỡng LDR, vùng PIR và khoảng cách trong điều kiện lắp đặt thực.']
  ], [2300, 6771]),
  'Trong phạm vi báo cáo, sơ đồ phần cứng được đánh giá qua tính đúng của đầu vào, ánh xạ chân và phản ứng của firmware trong Wokwi. Các yêu cầu mạch công suất, bảo vệ điện và nghiệm thu chiếu sáng thực địa chưa được thực hiện.'
]);

page('CHƯƠNG 3. GIỚI THIỆU PHẦN MỀM', [
  h('3.1. Kiến trúc tổng thể và trách nhiệm các lớp'),
  'Hệ thống sử dụng PlatformIO/Arduino cho firmware, Mosquitto cho truyền thông, FastAPI và SQLite cho backend, HTML/CSS/JavaScript cho dashboard. Toàn bộ luồng demo chạy local. Dashboard được mở qua VS Code Live Server; không cần framework giao diện hoặc dịch vụ cloud để thực hiện các chức năng đã nghiệm thu.',
  table(['Lớp', 'Đầu vào → xử lý → đầu ra'], [
    ['Firmware', 'Cảm biến/lệnh hợp lệ → điều khiển, dimming, lỗi tải → PWM và snapshot.'],
    ['MQTT', 'Telemetry, availability, command, ACK → định tuyến theo node → các bên đăng ký.'],
    ['Backend', 'Bản tin và HTTP → xác thực, lưu trữ, điều phối, thống kê → API/CSV.'],
    ['Dashboard', 'API → cập nhật giao diện, hiển thị freshness → thao tác người vận hành.']
  ], [1800, 7271]),
  h('Luồng dữ liệu và luồng lệnh'),
  'Luồng dữ liệu: cảm biến → SensorReader → controller → snapshot → Connectivity → Mosquitto → collector → SQLite → API → dashboard. Backend lưu cả dữ liệu phục vụ lịch sử và thông tin cần thiết để xác nhận phiên hiện hành.',
  'Luồng lệnh: dashboard → HTTP POST → bản ghi PENDING → publish MQTT → firmware kiểm tra điều kiện → áp dụng hoặc từ chối → ACK → backend kết thúc lệnh → dashboard hiển thị kết quả. HTTP 202 chỉ xác nhận đã tiếp nhận yêu cầu, chưa xác nhận thiết bị đã thực hiện.',
  'Wokwi đi tới broker qua host.wokwi.internal:1883, trong khi backend dùng 127.0.0.1:1883. API mặc định là cổng 8000; chiến dịch QA trước đó dùng 8001. Việc trình bày kết quả QA không làm thay đổi cổng mặc định của source bàn giao [6].'
], 1);

page('3.2. Cấu trúc và lịch chạy firmware', [
  table(['Module', 'Trách nhiệm chính'], [
    ['FirmwareApp', 'Điều phối vòng ứng dụng và cập nhật snapshot.'], ['SensorReader', 'Lấy mẫu PIR/ADC, kích và nhận ECHO có timeout.'],
    ['LightingController', 'Xác định môi trường, chuyển động, AUTO/MANUAL và hold.'], ['DimmingController', 'Đưa PWM tiến dần tới mức mục tiêu.'],
    ['FaultDetector', 'Xác nhận lỗi tải và phục hồi theo mức sáng, tỷ lệ tải, thời gian.'], ['Connectivity', 'Quản lý Wi-Fi/MQTT, publish và reconnect trong task riêng.'],
    ['MqttProtocol/MqttMailbox', 'Kiểm tra payload và trao đổi lệnh/snapshot giữa các tác vụ.'], ['NodeIdentity', 'Thống nhất định danh node, client và topic từ cấu hình build.']
  ], [3000, 6071]),
  'PIR được đọc theo chu kỳ 20 ms, analog 100 ms và khoảng cách 200 ms. LDR chỉ đưa mẫu mới vào bộ lọc. Phép đo siêu âm bắt cạnh qua ISR để vòng điều khiển tiếp tục chạy khi chờ echo. Các phép so thời gian được thiết kế cho bộ đếm thời gian của node và uptime 64 bit của hợp đồng dữ liệu.',
  'Connectivity sở hữu WiFiClient và PubSubClient trong FreeRTOS task core 0, priority 1, stack 8192 byte, nhường lịch khoảng 10 ms. Vòng ứng dụng trên core 1 sở hữu quyết định PWM và nhường lịch ngắn 1 ms. Snapshot và mailbox giúp tách sở hữu tài nguyên giữa mạng và điều khiển.',
  'Kết nối MQTT có timeout hữu hạn; reconnect dùng backoff 1, 2, 4, 8 rồi tối đa 10 giây. Vì vậy, mỗi lần không kết nối được broker không được phép giữ vòng điều khiển vô hạn. Log MQTT lỗi cần được đọc cùng log CONTROL để xác định node có tiếp tục AUTO hay không.',
  note('Nguồn: src/main.cpp, FirmwareApp, SensorReader, Connectivity và tài liệu firmware/testing. Build firmware đạt chỉ chứng minh biên dịch; kết quả mô phỏng/tích hợp được nêu riêng ở chương 4.')
]);

page('3.3. Thuật toán điều khiển AUTO', [
  'Sau khởi động, node ở AUTO. Controller nhận môi trường đã lọc, tín hiệu PIR và khoảng cách hợp lệ để tính mức sáng. DAY luôn chọn 0% trong AUTO; TWILIGHT và NIGHT duy trì mức nền khác nhau khi không có chuyển động.',
  table(['Môi trường', 'Yên tĩnh', 'PEDESTRIAN', 'VEHICLE/UNKNOWN'], [
    ['DAY', '0%', '0%', '0%'], ['TWILIGHT', '50%', '70%', '100%'], ['NIGHT', '25%', '70%', '100%']
  ], [2200, 1700, 2400, 2771]),
  'PIR HIGH và khoảng cách hợp lệ dưới 100 cm tạo VEHICLE; từ 100 cm trở lên tạo PEDESTRIAN. Khi PIR HIGH mà khoảng cách không hợp lệ, UNKNOWN chọn 100%. PIR LOW thể hiện motion=NONE; mức sáng vẫn có thể cao trong thời gian hold của một sự kiện vừa kết thúc.',
  'Hold kéo dài 5 giây kể từ lần cuối PIR HIGH. Sự kiện mới làm mới timer và giữ mức cao nhất còn hiệu lực, tránh giảm sáng ngay giữa chuỗi hoạt động. Khi chuyển sang DAY, hold bị hủy và mục tiêu về 0%. Dimming sau đó thực hiện quá trình tăng/giảm PWM theo từng bước.',
  h('Ví dụ đọc log và đối chiếu demo'),
  'Với mode=AUTO, environment=NIGHT, pir=0, motion=NONE, target=25, applied=25 và duty=64, hệ thống đang ở mức nền ban đêm. distance_cm thay đổi nhưng PIR vẫn LOW thì target giữ 25% là hành vi đúng. Muốn chứng minh phản ứng theo khoảng cách, cần tạo chuyển động và quan sát các trường ở cùng thời điểm.',
  'Với khoảng cách 150 cm và PIR HIGH, mục tiêu ban đêm là 70%. Với 50 cm và PIR HIGH, mục tiêu là 100%. Khi PIR về LOW, chờ hết hold rồi quan sát applied giảm về 25%. Kiểm tra cả target và applied giúp phân biệt quyết định thuật toán với độ trễ có chủ đích của dimming.'
]);

page('3.4. MANUAL và phát hiện lỗi tải', [
  h('3.4.1. Điều khiển MANUAL có thời hạn'),
  'MANUAL cho phép đặt mức sáng nguyên từ 0 đến 100%, có ưu tiên so với bảng AUTO kể cả ban ngày. Firmware duy trì chế độ này tối đa 60 giây theo uptime; hết thời hạn hoặc mất MQTT thì trở về AUTO. Node khởi động ở AUTO và reconnect không khôi phục một lệnh MANUAL cũ.',
  'Backend chỉ nhận lệnh khi node đủ tươi, broker hoạt động và không có lệnh PENDING cùng node. Firmware kiểm tra node, boot, deadline, phiên kết nối và ID lệnh trước khi thay đổi trạng thái. Một lệnh hợp lệ được báo APPLIED; sai điều kiện có thể REJECTED. Lệnh chưa có phản hồi hết hạn được backend ghi TIMEOUT.',
  h('3.4.2. Điều kiện OPEN_LOAD và phục hồi'),
  table(['Giai đoạn', 'Điều kiện của mô hình'], [
    ['Cho phép đánh giá', 'brightness_applied ≥ 20% và ổn định ít nhất 1 giây.'],
    ['Xác nhận lỗi', 'Tỷ lệ tải nhỏ hơn 10% mức kỳ vọng liên tục 2 giây.'],
    ['Xác nhận phục hồi', 'Tỷ lệ tải đạt ít nhất 20% mức kỳ vọng liên tục 3 giây.'],
    ['Khi đổi mode/tắt đèn', 'Không tự xóa lỗi chỉ vì đổi chế độ hoặc mức sáng bằng 0.']
  ], [2700, 6371]),
  'OPEN_LOAD là cảnh báo dựa trên đầu vào tải giả lập. Nó không tự cắt PWM và không phải bảo vệ ngắn mạch hoặc quá dòng. Khi minh họa, phải xem cảnh báo và thời điểm phục hồi thay vì kết luận LED sẽ tắt ngay khi biến trở về 0.',
  'Backend lưu sự kiện cảnh báo để truy vết, tách khỏi trạng thái node online/offline. Vì vậy, trạng thái kết nối tốt không chứng minh tải tốt; một cảnh báo tải đã đóng cũng không chứng minh node đang có dữ liệu mới. Dashboard biểu diễn riêng các thông tin này.'
]);

page('3.5. Giao thức MQTT và tính nhất quán của lệnh', [
  'Payload dùng schema_version=1. Telemetry có node_id, boot_id, seq và uptime_ms; boot_id 8 ký tự hex giúp phân biệt lần khởi động, seq tăng theo phiên, uptime_ms biểu diễn thời gian node. Collector kiểm tra schema, thứ tự và phiên trước khi cập nhật trạng thái sử dụng cho điều khiển.',
  table(['Đặc tính', 'Cách thực hiện'], [
    ['Tần suất telemetry', 'Định kỳ 2 giây node; khi thay đổi tối đa 5 Hz; QoS 0, không retained.'],
    ['Freshness', 'Giám sát cần dữ liệu dưới 10 giây; điều kiện gửi lệnh chặt hơn, tuổi dữ liệu không quá 3 giây.'],
    ['Deadline lệnh', 'Uptime mới nhất của node + 5000 ms; lệnh đích đúng boot.'],
    ['Theo dõi lệnh', 'Một PENDING/node; backend retry một lần sau 2 giây, timeout 10 giây.'],
    ['Chống áp dụng trùng', 'Firmware nhớ 32 ID; bản tin lặp không áp dụng lần nữa hoặc kéo dài timer MANUAL.']
  ], [2600, 6471]),
  'Trên MQTT, seq và uptime là số JSON theo hợp đồng; trên HTTP, các số nguyên lớn như seq, uptime và deadline được biểu diễn bằng chuỗi thập phân để tránh mất chính xác ở JavaScript. Đây là khác biệt có chủ đích giữa hai giao diện, không được tự đổi schema khi trình bày hoặc thao tác.',
  'ACK được xử lý như bằng chứng từ thiết bị. APPLIED biểu thị firmware đã nhận và áp dụng mode/target; việc applied đạt target còn phụ thuộc dimming. ACK đến muộn sau TIMEOUT được lưu phục vụ chẩn đoán và không đổi một lệnh đã timeout thành thành công.',
  'Availability retained và LWT hỗ trợ phát hiện kết nối, nhưng ONLINE cũ không đủ để xác nhận node sẵn sàng. Sau reconnect hoặc đổi boot, cần telemetry hợp lệ mới. Quy tắc này cùng với deadline và chống trùng hạn chế việc phát lại lệnh cũ vào một phiên hoạt động khác [6].'
]);

page('3.6. Backend, cơ sở dữ liệu và API', [
  'Backend sử dụng Python 3.12, FastAPI/Pydantic cho HTTP và kiểm tra dữ liệu, Paho MQTT cho collector. SQLite ở chế độ WAL lưu lịch sử local. Ứng dụng vận hành một worker và có khóa ở mức tiến trình để tránh hai collector cùng điều phối một bộ dữ liệu. File .env.example là mẫu cấu hình; chương trình không tự tải .env nếu chưa thiết lập môi trường.',
  table(['Nhóm bảng', 'Dữ liệu được lưu'], [
    ['nodes, boots', 'Định danh ba node, phiên khởi động và trạng thái mới nhất.'], ['telemetry, availability', 'Mẫu cảm biến/điều khiển và thay đổi kết nối.'],
    ['commands, ack_events', 'Vòng đời lệnh, phản hồi, retry và ACK chẩn đoán.'], ['alerts', 'Lịch sử mở/đóng cảnh báo.'],
    ['experiments', 'Cửa sổ phiên thực nghiệm để tính thống kê và xuất CSV.'], ['ingest_errors', 'Bản tin không hợp lệ hoặc lỗi thu nhận cần truy vết.']
  ], [3300, 5771]),
  'API cung cấp health, danh sách/chi tiết node, lệnh, lịch sử, cảnh báo và thực nghiệm. Truy vấn lịch sử có giới hạn tối đa 1000 mẫu mỗi trang cùng offset; đọc đủ dữ liệu cần xử lý phân trang. Một thời điểm chỉ có một experiment mở để giới hạn sự chồng lấn trong điều phối phiên đo.',
  'Khởi tạo cơ sở dữ liệu mới tạo ba node ID quy định, không chèn telemetry giả để làm đầy giao diện. Dữ liệu đã nhận được bảo toàn qua restart; backend không làm mới tuổi dữ liệu chỉ vì đọc lại bản ghi. Backup được kiểm tra bằng cơ chế SQLite và đối chiếu tính toàn vẹn trong hồ sơ bàn giao.',
  'Kết quả thống kê và CSV được tính tại backend. Dashboard hiển thị kết quả từ API, tránh một công thức năng lượng khác chạy trong trình duyệt. Khi đối chiếu số liệu, phải so cùng node, boot, cửa sổ và bộ lọc thay vì chỉ so hai con số Wh trên hai màn hình khác nhau.'
]);

page('3.7. Dashboard và thao tác giám sát', [
  'Dashboard được xây dựng bằng HTML/CSS/JavaScript cơ bản, chạy bằng VS Code Live Server. Năm khu vực gồm Tổng quan, Điều khiển node, Lịch sử, Cảnh báo và Thực nghiệm. API health, node và lệnh được polling khoảng 1 giây; thống kê/cảnh báo khoảng 5 giây; polling tạm dừng khi tab bị ẩn.',
  ...fig('screenshots/handover-overview-1920.png', 'Hình 3.1. Dashboard tổng quan ba node từ hồ sơ bàn giao TASK-012. KPI trên ảnh thuộc phiên đang được chọn trong ảnh, không thay cho bảng thực nghiệm chính của chương 4.', 580, 300),
  'Tổng quan cho biết kết nối, mode, môi trường, chuyển động và mức sáng. Điều khiển node tách bản nháp nhập liệu khỏi trạng thái thiết bị; sau khi gửi, người vận hành xem kết quả ACK và telemetry. Giao diện không tự retry HTTP POST vì có thể tạo một yêu cầu mới ngoài ý định của người dùng.',
  'Khi broker hỏng hoặc dữ liệu cũ, trạng thái được gắn nhãn và khóa các thao tác không còn đủ điều kiện. Lịch sử hỗ trợ truy vấn theo node/thời gian; Cảnh báo thể hiện vòng đời lỗi; Thực nghiệm hiển thị năng lượng, độ phủ và xuất CSV.',
  'Dashboard không tự mô phỏng cảm biến. Trong cấu hình đã triển khai, đầu vào được thay đổi tại Wokwi; dashboard quan sát kết quả và gửi AUTO/MANUAL. Vì vậy, phần demo sử dụng đồng thời Wokwi, Serial và dashboard để nối đầy đủ nguyên nhân với trạng thái hiển thị.'
]);

page('3.8. Mô hình năng lượng và phương pháp thống kê', [
  'Mô hình quy ước điện áp U = 12 V, dòng định mức I_nom = 2 A và hệ số tải f = current_adc / 4095. Với b là brightness_applied theo phần trăm: I_sim = 2 × b/100 × f (A); P_sim = 12 × I_sim (W). Ở tải đủ và mức sáng 25%, P_sim bằng 6 W; ở 100%, bằng 24 W.',
  'Điện năng trên mỗi đoạn hợp lệ được tích phân hình thang: E_i = (P_i + P_(i−1))/2 × Δt_i/3600 (Wh), trong đó Δt_i tính bằng giây uptime của cùng node và cùng boot. Chỉ nối đoạn có 0 < Δt_i ≤ 6 giây; không nối qua restart, offline, dữ liệu lỗi hoặc khoảng trống vượt giới hạn.',
  table(['Đại lượng', 'Cơ sở tính và ý nghĩa'], [
    ['AUTO hợp lệ', 'Loại MANUAL, UNKNOWN, xác minh/phục hồi lỗi, tải dưới 0,95 và các đoạn chuyển mode/môi trường/lỗi.'],
    ['Baseline', 'DAY 0 W; TWILIGHT/NIGHT 24 W trên đúng các đoạn AUTO hợp lệ để so sánh.'],
    ['Tiết kiệm', '(E_baseline − E_AUTO) / E_baseline × 100%; baseline bằng 0 thì null.'],
    ['Độ phủ', 'Dùng thời gian nhận UTC để đánh giá khoảng dữ liệu quan sát trong cửa sổ thực.']
  ], [2300, 6771]),
  'Uptime và UTC là hai clock khác nhau. Wokwi có thể chạy chậm hơn thời gian thực nên không đổi giây node thành giây máy bằng một hệ số tùy ý. Cửa sổ thực nghiệm chính được chốt theo từng node; API của cả experiment có thể chứa phần chờ thêm của node chạy nhanh hơn và không mặc nhiên bằng cửa sổ công bố.',
  'Audit độc lập đối chiếu raw MQTT, SQLite, API và CSV với sai số cho phép 10⁻⁹ Wh. Cách làm này nhằm xác nhận dữ liệu được tính đúng theo mô hình đã công bố. Nó không loại bỏ sai số do bản thân mô hình tải hoặc chứng minh mức tiết kiệm khi triển khai ngoài đường [6, 7].'
]);

page('CHƯƠNG 4. KẾT QUẢ DEMO', [
  h('4.1. Dữ liệu, kịch bản và tiêu chí sử dụng kết quả'),
  'Chương này kế thừa các ca tích hợp TASK-011 và chiến dịch thực nghiệm TASK-012, không chạy lại phép đo khi viết báo cáo. Chiến dịch chính có 7 kịch bản, 15 lượt được chấp nhận và 45 cửa sổ node. Audit cuối ghi PASS, không còn errors hoặc missing; các lần thử lỗi vẫn được lưu trong hồ sơ [7].',
  table(['Mã', 'Nội dung', 'Lượt × giây/node'], [
    ['EX-01', 'Ban ngày, thay đổi chuyển động; kiểm tra AUTO 0%.', '1 × 300'], ['EX-02', 'NIGHT yên tĩnh, mức nền 25%.', '3 × 600'],
    ['EX-03', 'NIGHT, sự kiện PIR chu kỳ, khoảng cách 150 cm.', '3 × 600'], ['EX-04', 'NIGHT, sự kiện PIR chu kỳ, khoảng cách 50 cm.', '3 × 600'],
    ['EX-05', 'Ba giai đoạn môi trường/chuyển động theo recipe.', '3 × 900'], ['EX-06', 'node_02 tải thấp từ giây 60, khôi phục giây 180.', '1 × 300'],
    ['EX-07', 'Dừng broker giây 60, khởi động lại giây 120.', '1 × 300']
  ], [1300, 5871, 1900]),
  'Thời lượng trên tính theo uptime từng node. EX-03/04 phát chuyển động tại giây 15 rồi mỗi 30 giây theo recipe. Thao tác vật lý có dấu thời gian để kiểm tra độ trễ, không chỉ dựa vào thời điểm lên lịch yêu cầu. Độ trễ trên lớn nhất của thao tác trong 15 lượt được nhận là 1778 ms, dưới ngưỡng 2000 ms.',
  'Nguồn minh họa gồm ảnh trong chiến dịch và khung hình từ video demo đã có. Video dài 419,966667 giây, 1920 × 1080, 30 fps, có phụ đề tiếng Việt và không có âm thanh. Video phục vụ giới thiệu; không được thay cho raw log hoặc tự coi khung hình video là mẫu thuộc cửa sổ đo chính.'
], 1);

page('4.2. Kết quả demo điều khiển AUTO', [
  'Ở ban ngày, node ở AUTO giữ mục tiêu 0% khi có hoặc không có chuyển động. Khi chuyển sang NIGHT và hết hold, node ổn định tại 25%. Kết quả EX-01 và EX-02 phù hợp hai mức nền này; EX-03 và EX-04 bổ sung các lần tăng sáng theo PIR và quy ước khoảng cách.',
  ...fig('video-review/extra/frame-144.png', 'Hình 4.1. Khung hình video tại khoảng giây 144: minh họa sự kiện xe theo quy ước và mức sáng 100%. Nguồn: video-review/extra/frame-144.png, TASK-012.', 580, 310),
  'Với PIR HIGH và khoảng cách 150 cm, node tăng mục tiêu lên 70%; khi khoảng cách 50 cm, mục tiêu lên 100%. Hết chuyển động, hold duy trì mức sáng rồi applied giảm dần về nền. Do đó, công suất trung bình của cả kịch bản có chuyển động thấp hơn công suất tức thời lúc sáng 70% hoặc 100%.',
  'Ca quan sát khoảng cách thay đổi nhưng pir=0 và motion=NONE không phải ca chứng minh tăng sáng. Ở NIGHT, target=25 và duty=64 trong trường hợp đó là đúng thuật toán. Khi trình bày demo, nhóm cần thao tác Simulate motion, đọc lại PIR rồi so target/applied với bảng ở mục 3.3.',
  'Kiểm thử tích hợp TASK-011 có 30 mẫu cảm biến → DOM, 10 mẫu/node, đều dưới 3 giây; cận trên lớn nhất là 1272,235 ms. Đây là độ trễ đến nội dung giao diện của các mẫu đã kiểm, không phải độ trễ quang học của đèn hoặc cam kết cho mọi mạng [7].'
]);

page('4.3. Kết quả điều khiển và cảnh báo tải', [
  'TASK-011 kiểm tra 30 lệnh, 10 lệnh/node, có phản hồi đúng đích và đối chiếu mục tiêu. Khi MANUAL được nhận, giao diện hiển thị trạng thái xử lý; sau ACK APPLIED, telemetry cho phép xem mode/target và applied. Các ca hết hạn, mất MQTT và reconnect được dùng để kiểm tra việc trở về AUTO, không phát lại lệnh MANUAL cũ.',
  ...fig('video-review/frame-215.png', 'Hình 4.2. Minh họa OPEN_LOAD tại node_02 trong video demo đã ghi. Nguồn: video-review/frame-215.png, TASK-012.', 580, 300),
  'EX-06 giảm đầu vào tải của node_02 tại giây 60 rồi khôi phục tại giây 180 theo uptime node. Sau các khoảng xác nhận đã nêu ở mục 3.4, firmware phát hiện OPEN_LOAD và sau đó xác nhận phục hồi. Dashboard và lịch sử cảnh báo cung cấp bằng chứng mở/đóng sự kiện.',
  'LED có thể vẫn thể hiện PWM khi biến trở tải đã giảm. Kết quả cần đọc là trạng thái fault và mô hình dòng/công suất, vì biến trở không nằm trong mạch cắt nguồn LED. Báo cáo chỉ kết luận chức năng phát hiện tải theo mô hình hoạt động trong các ca đã kiểm.',
  'Các đoạn fault, xác minh lỗi, phục hồi và tải thấp được loại khỏi năng lượng AUTO hợp lệ. Do đó, EX-06 không được dùng để quảng bá việc giảm điện do đèn hỏng; mục đích của ca này là kiểm tra cảnh báo, tính liên tục lịch sử và khả năng phục hồi.'
]);

page('4.4. Mất kết nối, khôi phục và độ ổn định', [
  'Trong EX-07, broker dừng tại giây 60 và khởi động lại tại giây 120 theo mốc thao tác của node_02. Khi MQTT mất, node vẫn tự điều khiển AUTO. Log node_01 có thay đổi DAY tại giây 75 và NIGHT tại giây 90 trong lúc mqtt=0, cho thấy đường điều khiển môi trường tiếp tục làm việc độc lập với broker.',
  ...fig('video-review/extra/frame-347.png', 'Hình 4.3. Ba node ONLINE sau reconnect trong video demo. Nguồn: video-review/extra/frame-347.png, TASK-012; ảnh minh họa, không thay cho log của EX-07.', 580, 290),
  'Khi kết nối trở lại, node gửi trạng thái mới; lệnh MANUAL cũ không được khôi phục. Dashboard chỉ coi node sẵn sàng sau dữ liệu hợp lệ mới. Độ phủ EX-07 nằm khoảng 79,073–79,836% tùy node do khoảng outage chủ động; các phần thiếu dữ liệu không được nội suy thành mẫu hoàn hảo.',
  'Cửa sổ ổn định TASK-011 kéo dài 1800 giây thực, có 5360 telemetry đối chiếu raw/SQLite khớp, dropped=0, giữ đúng seq/boot và tiến trình. Tuy nhiên, probe HTTP/tài nguyên dừng với mã 143 tại 1346,506 giây sau 672 mẫu, nên riêng phần probe này được giữ INCOMPLETE. Không kết luận toàn bộ HTTP/UI đã được quan sát liên tục đủ 30 phút.',
  'Cold-start trong hồ sơ TASK-012 bảo toàn 137797 telemetry cũ theo SHA, nhận ba boot mới ở AUTO và kiểm tra được lệnh APPLIED. Đây là bằng chứng phục hồi dữ liệu và phiên hoạt động trong mô hình local, chưa thay thế kiểm tra mất điện của một bộ mạch thật [7].'
]);

const energyRows = variation.filter(v => ['EX-02','EX-03','EX-04','EX-05'].includes(v.scenario)).map(v => {
  sourceMetrics.push(v);
  return [v.scenario, fmt(v.average_auto_power_w.mean), `${fmt(v.average_auto_power_w.minimum)}–${fmt(v.average_auto_power_w.maximum)}`,
    fmt(v.average_baseline_power_w.mean), fmt(v.saving_percent.mean)];
});
page('4.5. Kết quả năng lượng mô phỏng', [
  'Bảng 4.1 tổng hợp ba lần lặp của từng kịch bản EX-02 đến EX-05, lấy trực tiếp từ variation.json đã xuất từ audit. Giá trị được làm tròn đến ba chữ số thập phân để trình bày; hồ sơ CSV giữ độ chính xác gốc. Công suất trung bình được chuẩn hóa theo thời lượng AUTO hợp lệ, không phải toàn bộ thời gian chạy máy.',
  note('Bảng 4.1. Công suất AUTO, khoảng biến thiên giữa ba lần lặp, baseline và tỷ lệ tiết kiệm mô phỏng.'),
  table(['Kịch bản', 'AUTO TB (W)', 'AUTO min–max (W)', 'Baseline TB (W)', 'Tiết kiệm (%)'], energyRows, [1400, 1550, 2721, 1750, 1650]),
  'EX-02 có mức nền NIGHT 25%, công suất trung bình 6 W so với baseline 24 W, tương ứng 75%. EX-03 và EX-04 có các lần tăng sáng lên 70% và 100%, nên công suất trung bình cao hơn trường hợp yên tĩnh; tỷ lệ tiết kiệm lần lượt xấp xỉ 66,001% và 60,001%.',
  'EX-05 trộn môi trường theo ba giai đoạn và ba node. Baseline trung bình khoảng 18,671 W vì các đoạn DAY có baseline 0 W; không được áp một baseline 24 W cho toàn phiên. Công suất AUTO trung bình khoảng 6,613 W, tỷ lệ tiết kiệm khoảng 64,579%.',
  'EX-01 cho năng lượng AUTO và baseline đều bằng 0 trên các đoạn hợp lệ; tỷ lệ tiết kiệm để null, không ghi 100%. EX-06 và EX-07 tập trung kiểm tra fault/outage; phần hợp lệ còn lại có mức nền NIGHT nhưng không dùng các đoạn lỗi hoặc mất dữ liệu để tăng mức tiết kiệm công bố.',
  'Đơn vị Wh phản ánh năng lượng tích lũy, còn W phản ánh công suất trung bình. Chẳng hạn ba lần EX-02 có tổng năng lượng AUTO của ba node khoảng 3,001 Wh mỗi lượt, baseline khoảng 12,003 Wh. Chênh lệch nhỏ giữa các lượt phụ thuộc các biên mẫu hợp lệ, không phải số đo hiệu suất bộ đèn thật.'
]);

page('4.6. Chất lượng dữ liệu và đánh giá kết quả', [
  ...fig('../deliverables/data/auto-power-repetitions.png', 'Hình 4.4. Công suất AUTO qua các lần lặp; biểu đồ đã có của TASK-012, lấy từ cùng nguồn số liệu với Bảng 4.1.', 580, 290),
  'Các lần lặp EX-02/03/05 có độ phủ gần 100%; EX-04 lần 3 có node thấp nhất khoảng 99,004%. EX-07 có độ phủ thấp hơn do chủ động ngắt broker. Audit độc lập giữ đúng ranh giới từng node và đối chiếu raw MQTT, SQLite, API, CSV trong dung sai 10⁻⁹ Wh; không kéo dài cửa sổ của node nhanh để bù node chậm.',
  'Hồ sơ giữ các lần không đạt: EX-02 có lần đầu xuất hiện PIR ngoài recipe, nguyên nhân chưa xác định; EX-05 lần 1 thiếu điều kiện vì thao tác trễ 2257 ms. Nhóm chuẩn bị giao diện sớm hơn, giữ nguyên mốc tác động rồi chạy lại toàn lượt; 18 thao tác diễn tập kiểm tra sửa đổi có độ trễ lớn nhất 1475 ms. Chỉ các lượt đủ điều kiện mới được đưa vào 15 lượt chính.',
  h('4.7. Ý nghĩa và giới hạn'),
  'Kết quả cho thấy mô hình thực hiện được điều khiển thích ứng, giám sát ba node, lệnh có phản hồi, cảnh báo tải và phục hồi sau gián đoạn. Sự nhất quán giữa nguồn dữ liệu và thống kê củng cố cách triển khai trong phạm vi thử nghiệm; mức tiết kiệm phụ thuộc recipe và giả định tải đã công bố.',
  'Chưa có kiểm chứng phần cứng thật, độ rọi, hiệu suất nguồn, nhiễu cảm biến, an ninh triển khai Internet hoặc diễn tập bởi một người vận hành độc lập. Ba lần lặp mỗi kịch bản cung cấp phạm vi biến thiên của phép thử hiện có, chưa đủ để khái quát mức tiết kiệm cho mọi tuyến đường hoặc mọi điều kiện giao thông.'
]);

page('LỜI KẾT', [
  'Đề tài “Đèn đường thông minh” đã xây dựng một chuỗi IoT local từ cảm biến tới giao diện quản lý. Trên mỗi ESP32 mô phỏng, firmware xử lý ánh sáng, chuyển động, khoảng cách, giữ sáng và dimming; ở cấp hệ thống, MQTT, FastAPI, SQLite và dashboard hỗ trợ thu thập dữ liệu, điều khiển có ACK, lưu lịch sử và theo dõi cảnh báo.',
  'Thiết kế đặt quyết định AUTO tại node giúp hệ thống tiếp tục phản ứng với đầu vào khi broker gián đoạn. Việc phân biệt target/applied, boot/seq, dữ liệu mới/cũ và kết quả tiếp nhận/áp dụng lệnh giúp người vận hành đánh giá chính xác trạng thái. Đây cũng là các điểm cần trình bày rõ khi demo, tránh kết luận từ một giá trị hiển thị đơn lẻ.',
  'Kết quả kế thừa gồm kiểm thử tích hợp ba node, lệnh đúng đích, các mẫu độ trễ cảm biến đến giao diện, cửa sổ telemetry ổn định 1800 giây thực và 15 lượt thực nghiệm chính theo 7 kịch bản. Các lượt lỗi và probe chưa đủ thời lượng được công bố cùng phần đạt để giữ đúng giới hạn của bằng chứng.',
  'Theo mô hình điện 12 V/24 W, các kịch bản NIGHT yên tĩnh, chuyển động quy ước người, chuyển động quy ước xe và chuỗi môi trường hỗn hợp cho tỷ lệ tiết kiệm trung bình khoảng 75%; 66,001%; 60,001% và 64,579% trên các đoạn hợp lệ. Những con số này phản ánh mô phỏng theo recipe, không phải mức cam kết tiết kiệm của đèn đường ngoài thực tế.',
  'Hướng tiếp theo phù hợp là rà soát báo cáo và diễn tập thao tác bằng bộ bàn giao hiện có; sau đó, nếu mở rộng phạm vi, xây dựng phần cứng có driver phù hợp, đo dòng/áp/công suất và độ rọi thực, hiệu chỉnh cảm biến, bổ sung yêu cầu bảo mật rồi đánh giá lại trong điều kiện sử dụng cụ thể. Các nội dung này là đề xuất, chưa được tính vào kết quả hoàn thành hiện tại.'
], 1);

page('TÀI LIỆU THAM KHẢO', [
  '[1] ITU-T. Recommendation Y.2060 (06/2012), Overview of the Internet of things; hiện mang số Y.4000. Nguồn: https://www.itu.int/rec/T-REC-Y.2060-201206-I/en.',
  '[2] OASIS. MQTT Version 3.1.1, OASIS Standard, 29/10/2014. Nguồn: https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html.',
  '[3] Espressif Systems. ESP32 Series Datasheet, phiên bản 5.3. Nguồn: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf.',
  '[4] Wokwi. HC-SR04 Ultrasonic Distance Sensor. Nguồn: https://docs.wokwi.com/parts/wokwi-hc-sr04.',
  '[5] Wokwi. PIR Motion Sensor. Nguồn: https://docs.wokwi.com/parts/wokwi-pir-motion-sensor.',
  '[6] Nhóm 7. SRS và tài liệu triển khai dự án đèn đường thông minh. Nguồn nội bộ: docs/srs.md; docs/techs/firmware.md, hardware.md, mqtt.md, backend.md, dashboard.md, testing.md và experiments.md; source firmware/backend/dashboard hiện có.',
  '[7] Nhóm 7. Hồ sơ nghiệm thu TASK-011 và TASK-012. Nguồn nội bộ: docs/reports/evidence/task-011/; docs/reports/evidence/task-012/run-20261117-200024/analysis-final.json; output/task-012/deliverables/data/node-metrics.csv, repetition-metrics.csv, variation.json và plot-source.json.',
  '[8] Nhóm 7. Báo cáo Đèn đường thông minh v05; ảnh và video demo TASK-012. Nguồn nội bộ: output/task-012/deliverables/Bao-cao-Den-duong-thong-minh-Nhom7-v05.docx; output/task-012/run-20261117-200024/screenshots/ và video-review/.',
  note('Nguồn trực tuyến được đối chiếu ngày 18/11/2026. Đường dẫn nội bộ tính từ gốc firmware; backend và dashboard là các thư mục cùng cấp. Bìa, hệ thống style và thông tin nhóm được kế thừa từ báo cáo v05. Bản viết lại chỉ thay tổ chức và nội dung báo cáo, không tạo thêm số đo hoặc sửa kết quả gốc.')
], 1);

const children = pages.flatMap((page, index) => index ? [new d.Paragraph({ children: [new d.PageBreak()], spacing: { before: 0, after: 0, line: 1 } }), ...page.children] : page.children);
const doc = new d.Document({ creator: 'Nhóm 7', title: 'Đèn đường thông minh — Báo cáo tiểu luận bốn chương',
  styles: { default: {
    document: { run: { font: 'Times New Roman', size: 26, color: '111827' }, paragraph: { alignment: d.AlignmentType.JUSTIFIED, spacing: { before: 0, after: 140, line: 310 } } },
    heading1: { run: { font: 'Times New Roman', size: 30, bold: true, color: '16324F' }, paragraph: { keepNext: true, spacing: { before: 0, after: 200 } } },
    heading2: { run: { font: 'Times New Roman', size: 27, bold: true, color: '111827' }, paragraph: { keepNext: true, spacing: { before: 160, after: 100 } } }
  }, paragraphStyles: [{ id: 'Note', name: 'Note', basedOn: 'Normal', run: { font: 'Times New Roman', size: 22, italics: true, color: '475569' }, paragraph: { alignment: d.AlignmentType.LEFT, spacing: { before: 140, after: 100, line: 270 } } }] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1701, header: 450, footer: 500 } } }, children }]
});
d.Packer.toBuffer(doc).then(bytes => {
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, bytes, { flag: 'wx' });
  fs.writeFileSync(path.join(path.dirname(output), 'body-manifest.json'), JSON.stringify({ logical_pages: pages.map((p, i) => ({ page: i + 1, title: p.title })), figures,
    audit: { path: auditPath, sha256: crypto.createHash('sha256').update(fs.readFileSync(auditPath)).digest('hex'), accepted_runs: audit.accepted_runs }, sourceMetrics }, null, 2) + '\n');
  console.log(JSON.stringify({ body: output, pages: pages.length, figures: figures.length }));
});
