#!/usr/bin/env node
const fs = require('node:fs'), path = require('node:path');
const [runDir, outDir, auditFile] = process.argv.slice(2);
if (!runDir || !outDir || !auditFile) throw Error('Usage: node build-experiment-slides.cjs RUN_DIR OUT_DIR AUDIT_JSON');
const q = path.resolve(runDir), out = path.resolve(outDir);
const Pptx = require(path.join(q, 'runtime/office/node_modules/pptxgenjs'));
const { applyTheme } = require('/home/quangnhathung/.codex/skills/pptx/scripts/apply_theme.js');
const data = JSON.parse(fs.readFileSync(auditFile, 'utf8')), complete = data.status === 'PASS' && data.accepted_runs === 15;
const pres = new Pptx(); pres.layout = 'LAYOUT_WIDE'; pres.author = 'Nhóm 7'; pres.title = 'Đèn đường thông minh'; pres.subject = 'TASK-012 — thực nghiệm Wokwi và bàn giao'; pres.lang = 'vi-VN';
const THEME = { name: 'SmartLight Forest', headFontFace: 'Arial', bodyFontFace: 'Arial', colors: {
  dk1: '173A2E', lt1: 'FFFFFF', dk2: '475569', lt2: 'EDF4F0', accent1: '237A4B', accent2: 'E5AC36', accent3: 'C54F3D', accent4: '538777', accent5: '6B7280', accent6: 'DCE8E1', hlink: '237A4B', folHlink: '538777' } };
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor, S = pres.ShapeType;
for (const dark of [false, true]) pres.defineSlideMaster({ title: dark ? 'Dark' : 'Light', background: { color: dark ? C.text1 : C.background1 },
  objects: [{ placeholder: { text: '', options: { name: 'title', type: 'title', x: .6, y: .45, w: 12.1, h: .85, fontSize: 31, bold: true, color: dark ? C.background1 : C.text1, margin: 0 } } },
    { text: { text: 'NHÓM 7  ·  WOKWI / ESP32 / MQTT', options: { x: .6, y: 7.02, w: 9.5, h: .2, fontSize: 10, margin: 0, color: dark ? C.accent6 : C.text2, isTextBox: true } } }],
  slideNumber: { x: 12.1, y: 7.02, w: .6, h: .2, fontSize: 10, margin: 0, color: dark ? C.accent6 : C.text2 } });
const text = (slide, value, x, y, w, h, opts = {}) => slide.addText(value, { x, y, w, h, fontSize: 22, color: C.text1, margin: 0, breakLine: false, isTextBox: true, ...opts });
const box = (slide, name, x, y, w, h, fill = C.background2) => slide.addShape(S.roundRect, { x, y, w, h, rectRadius: .15, radius: .15, line: { color: fill, transparency: 100 }, fill: { color: fill }, objectName: name });
function newSlide(title, section, dark = false) { const s = pres.addSlide({ masterName: dark ? 'Dark' : 'Light', sectionTitle: section }); s.addText(title, { placeholder: 'title' }); return s; }
function card(slide, title, body, x, y, w, h, number) { box(slide, title, x, y, w, h); if (number) text(slide, number, x + .25, y + .18, w - .5, .7, { fontSize: 42, bold: true, color: C.accent1 }); text(slide, title, x + .25, y + (number ? 1.05 : .25), w - .5, .5, { fontSize: 23, bold: true }); text(slide, body, x + .25, y + (number ? 1.8 : 1), w - .5, h - (number ? 2 : 1.2), { fontSize: 20, color: C.text2, valign: 'top' }); }
function tbl(slide, rows, opts = {}) { slide.addTable(rows, { x: .6, y: 1.7, w: 12.1, h: 3.8, fontSize: 20, margin: .13, color: C.text1, fill: C.background1, border: { type: 'solid', color: THEME.colors.accent6, pt: 1 }, rowH: .6, bold: false, autoPage: false, ...opts }); }
function lamp(slide, x, y, label, lit) { slide.addShape(S.line, { x, y, w: 0, h: 1.8, line: { color: C.accent6, width: 4 }, objectName: 'Cột đèn ' + label }); slide.addShape(S.line, { x, y, w: .6, h: 0, line: { color: C.accent6, width: 4 } }); slide.addShape(S.ellipse, { x: x + .4, y: y - .12, w: .48, h: .25, line: { transparency: 100 }, fill: { color: lit ? C.accent2 : C.text2 }, objectName: 'Đèn ' + label }); text(slide, label, x - .3, y + 2, 1.6, .35, { fontSize: 16, color: C.accent6 }); }
pres.addSection({ title: 'Bài toán và thiết kế' });
let s = newSlide('Đèn đường thông minh', 'Bài toán và thiết kế', true);
text(s, 'Khoa Công nghệ thông tin · Trường Đại học Công Thương TP.HCM', .6, 1.38, 12.1, .3, { color: C.accent6, fontSize: 14 });
text(s, 'Tự điều chỉnh tại node\nGiám sát và điều khiển ba đèn', .6, 1.8, 7.4, 1.6, { color: C.background1, fontSize: 36, bold: true, breakLine: true });
text(s, 'Quang Nhật Hưng · 2001230328\nNguyễn Văn Anh Tuấn · 2001230863', .6, 4, 7.3, .85, { color: C.accent6, fontSize: 21 });
text(s, complete ? '15/15 lượt chính đã được audit' : `${data.accepted_runs}/15 lượt đã audit · Bản đang hoàn thiện`, .6, 5.45, 7.4, .7, { color: C.accent2, fontSize: 23 });
[['01', 8.4, false], ['02', 9.9, true], ['03', 11.4, true]].forEach(([n,x,lit]) => lamp(s, x, 2.4, 'node_' + n, lit));
s.addNotes('Nhóm7, Khoa Công nghệ thông tin, Trường Đại học Công Thương TP.HCM. Đây là mô hình Wokwi; điện năng là mô hình. Trạng thái số liệu được ghi ngay trên slide để tránh trình bày bản chưa đủ như kết quả cuối.');
s = newSlide('Điều khiển thích ứng, giữ AUTO khi mất mạng', 'Bài toán và thiết kế');
card(s, 'Môi trường', 'DAY: tắt\nTWILIGHT: nền50%\nNIGHT: nền25%', .6, 1.8, 3.8, 3.9, '01');
card(s, 'Chuyển động', 'PIR + khoảng cách quy ước\nNgười70% / xe100%\nHold5s, giảm sáng dần', 4.75, 1.8, 3.8, 3.9, '02');
card(s, 'Giám sát', 'MQTT → SQLite → dashboard\nLệnh có ACK\nFault khác offline/stale', 8.9, 1.8, 3.8, 3.9, '03');
text(s, 'Phạm vi: ba phiên Wokwi local; chưa đo điện, chưa nhận dạng phương tiện thật.', .6, 6.15, 12.1, .55, { fontSize: 20, color: C.text2 });
s.addNotes('Mục tiêu là kiểm chứng luồng điều khiển và dữ liệu. Ba chiều mode/environment/motion được tách riêng. Đón đầu giữa node, cloud và mạch công suất thật là ngoài phạm vi nghiệm thu này.');
s = newSlide('Ba node độc lập, một luồng dữ liệu thống nhất', 'Bài toán và thiết kế');
['node_01','node_02','node_03'].forEach((node,i) => { box(s, node, .6, 1.8 + i * 1.28, 3.1, .95); text(s, node + ' · AUTO cục bộ', .8, 2.07 + i * 1.28, 2.7, .4, { fontSize: 21 }); });
[['Mosquitto',4.5,2.6],['FastAPI',8,2.6]].forEach(([v,x,y]) => { box(s,v,x,y,2.7,1.3);text(s,v,x+.2,y+.4,2.3,.45,{fontSize:25,bold:true}); });
s.addShape(S.chevron, { x:3.9,y:2.97,w:.4,h:.5,fill:{color:C.accent1},line:{transparency:100} });
s.addShape(S.chevron, { x:7.4,y:2.97,w:.4,h:.5,fill:{color:C.accent1},line:{transparency:100} });
box(s,'SQLite',8,4.5,2.7,.85);text(s,'SQLite',8.2,4.73,2.3,.4,{bold:true});
box(s,'Dashboard',8,1.35,4.7,.85);text(s,'Dashboard HTML/CSS/JS',8.2,1.58,4.3,.4,{fontSize:22,bold:true});
text(s,'Gateway VS Code\nhost.wokwi.internal:1883',4.5,4.4,3.2,1.1,{fontSize:19,color:C.text2});
text(s,'Telemetry đi lên · Command/ACK đi hai chiều · HTTP qua API',.6,6.15,12.1,.55,{fontSize:21});
s.addNotes('Ba ESP32 không chạy chung một diagram. Một source build thành ba environment với NodeIdentity. Broker local; backend một worker. API QA8001, Live Server5500; URL này không thay đổi mặc định8000 của sản phẩm.');
s = newSlide('Cảm biến tạo kịch bản; PWM thể hiện mức điều khiển', 'Bài toán và thiết kế');
tbl(s, [['LDR','PIR','HC-SR04','Tải giả lập','LED PWM'],['GPIO34','GPIO27','TRIG18 / ECHO19','GPIO35','GPIO26'],['ADC12bit','Chuyển động','Khoảng cách','Biến trở0–4095','5kHz / 8bit']], { y:1.8,h:2.2,fontSize:20,colW:[2.1,2,3,2.7,2.3] });
card(s,'Người / xe là quy ước','PIR HIGH + distance ≥100cm →70%\nPIR HIGH + distance <100cm →100%',.6,4.4,6.1,1.95);
card(s,'Giới hạn tải','Biến trở không đo dòng thật.\nLED không phải đồng hồ năng lượng.',7.05,4.4,5.65,1.95);
s.addNotes('Không chuyển sơ đồ Wokwi thành hướng dẫn đấu đèn công suất. Giả lập150cm đọc khoảng152cm,50cm đọc khoảng51cm. Nếu PIR HIGH và distance invalid, chọn UNKNOWN100%. Khoảng cách gần khi PIR LOW không tăng sáng.');
s = newSlide('AUTO: nền theo ánh sáng, tăng khi có chuyển động', 'Bài toán và thiết kế');
tbl(s,[['Môi trường','Yên tĩnh','Người giả lập','Xe / UNKNOWN'],['DAY','0%','0%','0%'],['TWILIGHT','50%','70%','100%'],['NIGHT','25%','70%','100%']],{y:1.75,h:3.15,fontSize:24,colW:[3.1,2.8,3.1,3.1]});
text(s,'LDR: lọc5 mẫu + xác nhận1s + hysteresis',.6,5.3,12,.5,{fontSize:25,bold:true});
text(s,'Hold5s · Dimming tối đa2 điểm/20ms · MANUAL60s theo uptime',.6,6.05,12,.5,{fontSize:22,color:C.text2});
s.addNotes('Ngưỡng khởi tạo1200/2600; biên hysteresis1100/1300 và2500/2700. Ngưỡng có trong ControlConfig.h, không lấy nguyên300/700 của đề cương ban đầu. DAY hủy hold. MANUAL ưu tiên mức yêu cầu nhưng mất MQTT phải về AUTO.');
pres.addSection({title:'Vận hành và nghiệm thu'});
s = newSlide('202 là tiếp nhận; ACK mới xác nhận áp dụng', 'Vận hành và nghiệm thu');
['Dashboard','API / PENDING','MQTT command','ESP32 / ACK'].forEach((v,i)=>{box(s,v,.6+i*3.15,2,2.65,1.2);text(s,v,.8+i*3.15,2.35,2.25,.55,{fontSize:21,bold:true});if(i<3)s.addShape(S.chevron,{x:3.35+i*3.15,y:2.36,w:.3,h:.45,fill:{color:C.accent1},line:{transparency:100}});});
card(s,'Đúng lệnh, đúng phiên','ID + boot đích + deadline\nLệnh trùng dùng cache kết quả',.6,4,5.85,2.3);
card(s,'Không phát lại lệnh cũ','Timeout là trạng thái cuối\nRestart/reconnect thu hồi phiên cũ',6.85,4,5.85,2.3);
s.addNotes('Backend command QoS1 không retain; firmware telemetry/ACK QoS0 qua PubSubClient. HTTP202 không phải PUBACK hoặc APPLIED. Một node chỉ có một PENDING. ACK muộn lưu chẩn đoán, không đổi trạng thái cuối. TASK-01130/30 lệnh đúng đích APPLIED.');
s = newSlide('Dashboard phân biệt trạng thái và cho truy vết dữ liệu', 'Vận hành và nghiệm thu');
const shot=path.join(q,fs.existsSync(path.join(q,'screenshots/handover-overview-1920.png'))?'screenshots/handover-overview-1920.png':'screenshots/EX-01-r01-a01-dashboard-end.png');
if(fs.existsSync(shot)){const png=fs.readFileSync(shot),ratio=png.readUInt32BE(16)/png.readUInt32BE(20),w=Math.min(8.3,4.95*ratio),h=w/ratio;s.addImage({path:shot,x:.6+(8.3-w)/2,y:1.55+(4.95-h)/2,w,h,altText:'Dashboard QA với dữ liệu thực nghiệm Wokwi',objectName:'Dashboard QA actual viewport'});}
text(s,'5 view',9.25,1.8,3.4,.7,{fontSize:38,bold:true,color:C.accent1});
text(s,'Tổng quan\nChi tiết node\nLịch sử\nCảnh báo\nPhiên / CSV',9.25,2.8,3.4,2.5,{fontSize:24,breakLine:true});
text(s,'Chạy bằng VS Code Live Server',9.25,5.75,3.4,.8,{fontSize:19,color:C.text2});
s.addNotes('Ảnh thật của đợtQA, không phải fixture. KPI dùng cửa sổ mặc định1h, không phải kết quả riêng một phiênEX. UI polling1s cho health/nodes/command;5s cho stats/alerts/phiên. Lệnh bị khóa khi stale/offline hoặc mấtAPI. History giữ raw và ngắt đường qua gap/boot/continuity.');
s = newSlide('15 lượt chính, clock riêng cho từng node', 'Vận hành và nghiệm thu');
tbl(s,[['Kịch bản','Số lượt','Thời lượng/node'],['EX01 · DAY','1','5 phút'],['EX02/03/04 · đêm','3 mỗi kịch bản','10 phút'],['EX05 · hỗn hợp','3','15 phút'],['EX06/07 · lỗi/mạng','1 mỗi kịch bản','5 phút']],{y:1.6,h:3.5,fontSize:23,colW:[6.2,2.7,3.2]});
text(s,'PIR ở15s rồi mỗi30s · trễ tác động ≤2s mô phỏng',.6,5.5,12.1,.5,{fontSize:25,bold:true});
text(s,'Giữ FAIL/INCOMPLETE, chạy lại trọn lượt · Pilot tách khỏi số liệu chính',.6,6.2,12.1,.5,{fontSize:20,color:C.text2});
s.addNotes('Tổng150 phút uptime mỗi node. Không đếm thời gian node nhanh chờ node chậm. UTC/monotonic máy ghi riêng; năng lượng theo uptime, coverage theo thời gian nhận. EX05 ba pha300s với bảng node/môi trường/chuyển động cố định. Chưa đủ15 lượt thì slide kết quả phải ghi trạng thái tạm.');
pres.addSection({title:'Kết quả và giới hạn'});
s = newSlide(complete?'Công suất AUTO trên các đoạn đủ điều kiện':'Số liệu tạm: chỉ các lượt đã được kiểm chứng','Kết quả và giới hạn');
const codes=Object.keys(data.aggregates).filter(code=>['EX-01','EX-02','EX-03','EX-04','EX-05'].includes(code));
const meanPower=(code,field)=>{const runs=data.runs.filter(r=>r.scenario===code);return runs.reduce((total,r)=>{const nodes=Object.values(r.nodes),duration=nodes.reduce((a,n)=>a+n.auto_valid_uptime_s,0);return total+(duration?nodes.reduce((a,n)=>a+n[field],0)*3600/duration:0);},0)/runs.length;};
const means=codes.map(code=>meanPower(code,'auto_energy_wh'));
if(codes.length)s.addChart(pres.ChartType.bar,[{name:'AUTO mô phỏng',labels:codes,values:means},{name:'Baseline cùng đoạn',labels:codes,values:codes.map(code=>meanPower(code,'baseline_wh'))}],{x:.6,y:1.65,w:8.4,h:4.95,barDir:'col',catAxisLabelsFontFace:'+mn-lt',valAxisLabelsFontFace:'+mn-lt',showLegend:true,legendPos:'b',legendFontSize:15,showValue:true,dataLabelPosition:'outEnd',dataLabelFormatCode:'0.0',showTitle:true,title:'Công suất trung bình (W/node)',catAxisLabelFontSize:17,valAxisLabelFontSize:16,valAxisMinVal:0,valAxisMaxVal:28,chartColors:[THEME.colors.accent1,THEME.colors.dk2],valGridLine:{color:THEME.colors.accent6,size:1},catGridLine:{style:'none'}});
text(s,`${data.accepted_runs}/15`,9.35,1.9,3.2,.85,{fontSize:48,bold:true,color:C.accent1});
text(s,'lượt chính\nđã kiểm chứng',9.35,2.9,3.2,.95,{fontSize:23});
text(s,'ΔE = P̄ × Δt / 3600\nΔt theo uptime\nDAY 0 W; đêm 24 W\nBaseline 0 → null',9.35,4.25,3.35,2.1,{fontSize:19,color:C.text2});
s.addNotes('Biểu đồ native có thể sửa dữ liệu. Đây là trung bình mô tả các node-run, không phải kết luận dân số. Kết quả chi tiết từnglượt và min–max ở Word/JSON. Loại MANUAL/fault/low-load/UNKNOWN/đổi trạng thái; không nối qua boot/continuity/gap>6s. Đối chiếu độc lập API/CSV1e-9Wh. Không ngoại suy tiền điện hoặc tỷ lệ tiết kiệm ngoài mô phỏng.');
s = newSlide('Bằng chứng được tách theo tầng kiểm tra', 'Kết quả và giới hạn');
card(s,'Lệnh đúng đích','10/node · có ACK\nTASK-011',.6,1.8,3.8,3.85,'30/30');
card(s,'Sensor → DOM','Mẫu chính dưới3s thực\nCó clock bracket',4.75,1.8,3.8,3.85,'30/30');
card(s,'Ổn định đồng thời','5.360 raw khớp SQLite\nGiữ boot/continuity',8.9,1.8,3.8,3.85,'1.800s');
text(s,'Giới hạn: HTTP/resource probe chỉ1.346,506s; không tuyên bố giám sát UI liên tục30 phút.',.6,6.15,12.1,.55,{fontSize:18,color:C.text2});
s.addNotes('Số liệu kế thừa TASK011, không gán thành kết quả TASK012. 34 Python test của công cụ đãPASS. Build đủ3 environment đãPASS ởbaseline. Build không chứng minh mô phỏng; fixtureUI không thay cho live; rawMQTT/SQLite vàSerial là các bằng chứng khác nhau.');
s = newSlide('Lỗi tải, offline và dữ liệu cũ là ba tình huống riêng', 'Kết quả và giới hạn');
tbl(s,[['Tình huống','Dấu hiệu','Phản ứng'],['OPEN_LOAD','Có telemetry + fault tải','Giữ cảnh báo đến phục hồi hợp lệ'],['Offline broker/node','Kết nối mất; dữ liệu ngừng','Khóa lệnh; node tiếp tục AUTO'],['Stale/API lỗi','Snapshot quá cũ/không đồng bộ','Hiện nhãn cũ; không báo thành công giả']],{y:1.8,h:3.5,fontSize:22,colW:[3.1,4.2,4.8]});
text(s,'EX06: tải0 ở60s, phục hồi180s · EX07: broker down60s, up120s',.6,5.8,12.1,.65,{fontSize:22,bold:true});
s.addNotes('EX07 Serial chỉ đọc chứng minh node01 đổiDAY0 vàNIGHT25 khi MQTT0. Đo nhận dữ liệu sau reconnect riêng; không giả lấp đoạn thiếu. Lượt EX02 đầu FAIL doPIR/distance ngoàirecipe, nguyênnhân chưa xác định; được giữ và chạy lại toànlượt.');
s = newSlide('Hoàn thiện mô hình, giữ rõ giới hạn thực nghiệm', 'Kết quả và giới hạn',true);
text(s,'Điều khiển tại node\nGiám sát có ACK và lịch sử\nNăng lượng có điều kiện và độ phủ',.6,1.8,8.5,2.35,{fontSize:31,bold:true,color:C.background1});
text(s,'Chưa đo phần cứng · chưa nhận dạng xe thật\nChưa xác nhận hai thành viên tự chạy/giải thích',.6,4.65,11.5,1.1,{fontSize:24,color:C.accent6});
text(s,'Bước sau: mạch điện áp thấp, hiệu chuẩn cảm biến và đo công suất thực.',.6,6.05,11.8,.6,{fontSize:21,color:C.accent2});
lamp(s,11,2.1,'AUTO',true);
s.addNotes('Bộ bàn giao gồm source/cấu hình, rawCSV/JSON, báo cáoWord, slidePPTX, videoMP4 vàrunbook/backup theo trạng thái nghiệmthu. Người dùng tự xuấtPDF bằngWPS. Các tính năng mở rộng cần yêu cầu và nghiệmthu riêng. Kiểm tra trạng thái bản cuối, không dùng bảnđanghoànthiện như kếtquả cuối.');
(async()=>{fs.mkdirSync(out,{recursive:true});let target=path.join(out,'Bao-ve-Den-duong-thong-minh-Nhom7.pptx'),version=1;while(fs.existsSync(target))target=path.join(out,'Bao-ve-Den-duong-thong-minh-Nhom7-v'+String(++version).padStart(2,'0')+'.pptx');await pres.writeFile({fileName:target});await applyTheme(target,THEME);fs.writeFileSync(path.join(out,'slides-build.json'),JSON.stringify({target,slides:12,accepted_runs:data.accepted_runs,complete},null,2)+'\n');console.log(JSON.stringify({target,slides:12,accepted_runs:data.accepted_runs,complete}));})().catch(error=>{console.error(error);process.exitCode=1;});
