# Kịch bản giới thiệu và demo dự án đèn đường thông minh

Tài liệu dành cho phần trình bày và bảo vệ đồ án của Nhóm 7. Kịch bản chính khoảng 20 phút, đi từ bài toán, kiến trúc đến thao tác thực trên ba node Wokwi, dashboard và dữ liệu đã lưu.

Mỗi cảnh có lời dẫn có thể đọc trực tiếp, thao tác của người vận hành, kết quả cần quan sát và điều kiện chuyển cảnh. Các đoạn “Lời trình bày” dùng để nói; phần “Thao tác” và “Kiểm trước khi chuyển cảnh” dùng để luyện tập, không đọc nguyên văn trước hội đồng.

Phân vai gợi ý: người A giới thiệu, giải thích và trả lời; người B thao tác màn hình, theo dõi Serial và chuẩn bị chuyển cảnh. Hai người có thể đổi vai khi luyện tập. Nếu chỉ một người thuyết trình, thực hiện thao tác xong rồi đọc tiếp, tránh vừa gõ vừa nói đoạn dài.

Phiên bản 1.0, ngày 18 tháng 11 năm 2026. Kịch bản sử dụng source hiện hành và kết quả thực nghiệm TASK-012. Đây là kịch bản để diễn tập, không phải biên bản xác nhận nhóm đã chạy thành công một buổi demo mới.

Hệ thống trình diễn là mô hình Wokwi. Người/xe được tạo theo quy ước PIR kết hợp khoảng cách; dòng, công suất và điện năng là đại lượng mô phỏng. Mọi lần dùng video hoặc dữ liệu đã ghi được giới thiệu rõ nguồn.

<!-- PAGE -->
# 1 Tổng thể buổi trình bày và phân vai

| Thời gian dự kiến | Nội dung | Người phụ trách |
|---|---|---|
| 00:00 đến 03:00 | Chào, bài toán, mục tiêu và phạm vi | A nói, B mở slide đầu |
| 03:00 đến 05:00 | Kiến trúc và các thành phần | A nói, B chỉ mạch và dashboard |
| 05:00 đến 06:30 | Kiểm ba node, mở phiên demo | B thao tác, A giải thích |
| 06:30 đến 08:30 | DAY, TWILIGHT, NIGHT | B chỉnh LDR node01 |
| 08:30 đến 10:30 | Người, xe, PIR và giữ sáng | B thao tác node01 |
| 10:30 đến 12:00 | MANUAL/AUTO đúng node | B điều khiển node02 |
| 12:00 đến 14:00 | OPEN_LOAD và phục hồi | B chỉnh tải node03 |
| 14:00 đến 16:00 | Mất broker và reconnect | B thao tác terminal và node01 |
| 16:00 đến 17:30 | Dừng phiên, lịch sử và CSV | B thao tác dashboard |
| 17:30 đến 19:00 | Kết quả thực nghiệm đã ghi | A nói, B mở bảng/biểu đồ |
| 19:00 đến 20:00 | Kết luận và hướng phát triển | A nói, B giữ màn hình tổng kết |

Thời gian là khung luyện tập theo giờ máy. Filter, hold, MANUAL và xác nhận lỗi dùng uptime của node; mô phỏng chậm làm thời gian chờ thực dài hơn. Chỉ nói “đã đạt” sau khi thấy đúng trạng thái. Nếu trễ lịch, dùng nhánh rút gọn hoặc video đã ghi, không tăng tốc bằng cách bỏ điều kiện kiểm.

Người B chuẩn bị thứ tự cửa sổ: slide, dashboard, Wokwi node01, node02, node03 và terminal broker. Chỉ chia sẻ cửa sổ dự án; đóng thông báo cá nhân. Người A nhắc tên node trước mỗi thao tác để khán giả biết đang quan sát đèn nào.

<!-- PAGE -->
# 2 Chuẩn bị trước buổi demo

## Trước buổi trình bày

- Làm theo docs/project-guide.md để cài và chạy hệ thống; không cài package hoặc nâng toolchain ngay khi bắt đầu bảo vệ.
- Chọn DB demo riêng, có tên và đường dẫn rõ. Muốn xem phiên thực nghiệm cũ trên dashboard, phục hồi bản DB sang tên mới theo hướng dẫn; không chạy backend trực tiếp trên bản bằng chứng gốc.
- Chuẩn bị Word/PPTX v05, CSV và biểu đồ TASK-012, video khoảng 7 phút. Thử mở tệp cục bộ trước, không chỉ lưu đường dẫn tới máy khác.
- Giữ đủ ba cửa sổ Wokwi, đúng binary/ID; kiểm license, gateway, Internet và tốc độ mô phỏng.

## Khởi động và trạng thái đầu

Trong firmware, khởi động Docker Engine trước nếu cần, rồi chạy:

```text
docker compose -f infra/compose.yaml up -d mosquitto
docker compose -f infra/compose.yaml ps
```

Trong backend, dùng đúng DB đã chọn và chạy một worker. Linux:

```bash
.venv/bin/python -m uvicorn smartlight.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Windows PowerShell:

```powershell
.venv/Scripts/python.exe -m uvicorn smartlight.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Mở ba Wokwi và dashboard bằng Live Server tại http://127.0.0.1:5500/. API mặc định 8000, broker 1883; nếu dùng QA8001 thì phải đồng bộ config.js. Kiểm /api/health OK, dropped_events=0; ba node ONLINE/FRESH, không pending hoặc phiên mở chưa xử lý.

Đưa cả ba node về AUTO, NIGHT Lux 0.1, biến trở tối đa1023, Distance 150 cm và không kích PIR. Chờ target/applied 25, fault OK, Serial mqtt=1. Đừng bắt đầu bản demo đầy đủ nếu vẫn thấy MQTT connect failed; dùng nhánh chỉ Wokwi ở phần16 khi chưa sửa được kết nối.

<!-- PAGE -->
# 3 Lời mở đầu chi tiết về bài toán

## Lời trình bày của người A

“Kính thưa thầy cô, chúng em là Nhóm 7. Hôm nay nhóm xin trình bày đề tài đèn đường thông minh tự động điều chỉnh độ sáng. Trong phần này, nhóm sẽ giới thiệu bài toán, cách tổ chức hệ thống và trực tiếp thao tác trên mô hình ba đèn để minh họa các chức năng đã xây dựng.

Bài toán nhóm quan tâm là làm thế nào để một tuyến đèn có thể thay đổi mức chiếu sáng theo điều kiện môi trường và hoạt động tại khu vực đang theo dõi. Trong mô hình của nhóm, ban ngày không cần duy trì mức sáng như ban đêm. Khi trời tối nhưng chưa có chuyển động, đèn giữ mức nền; khi phát hiện chuyển động, đèn tăng sáng rồi giảm dần sau khoảng giữ sáng.

Bên cạnh việc tự điều chỉnh, người vận hành còn cần biết từng đèn đang ở chế độ nào, mức sáng mục tiêu và mức đang áp dụng có khác nhau hay không, node có mất kết nối hay có dấu hiệu lỗi tải. Vì vậy, nhóm xây dựng cả phần điều khiển tại ESP32 và phần giám sát tập trung qua giao diện web.

Mục tiêu của nhóm gồm ba nội dung có thể kiểm chứng. Thứ nhất, mỗi node tự đọc cảm biến và điều khiển mức sáng phù hợp. Thứ hai, người vận hành theo dõi và gửi lệnh đúng đèn, có xác nhận từ node. Thứ ba, hệ thống lưu lịch sử và thống kê điện năng mô phỏng, đồng thời công bố khoảng dữ liệu hợp lệ và phần dữ liệu còn thiếu.

Phạm vi của đồ án là mô phỏng trên Wokwi với ba ESP32 độc lập. Nhóm chưa dùng mô hình này để kết luận về độ an toàn của mạch đèn công suất thật hoặc mức tiết kiệm tiền điện ngoài thực tế. Các kết quả được trình bày trong điều kiện cấu hình, thuật toán và lịch tác động đã ghi lại.”

## Màn hình và nhịp chuyển

B mở slide tiêu đề và mục tiêu, chưa đổi cảm biến trong lúc A giới thiệu. A nhìn người nghe khi nói mục tiêu; chuyển sang màn hình kiến trúc sau câu cuối. Không thêm số liệu “tiết kiệm bao nhiêu” ở phần này trước khi giải thích điều kiện đo.

<!-- PAGE -->
# 4 Lời giới thiệu kiến trúc và luồng dữ liệu

## Lời trình bày của người A

“Kiến trúc của hệ thống gồm ba tầng. Tầng thứ nhất là ba node ESP32 được mô phỏng độc lập. Mỗi node có cảm biến ánh sáng LDR, PIR để phát hiện chuyển động, HC-SR04 để lấy khoảng cách và một biến trở mô phỏng trạng thái tải. LED thể hiện mức PWM mà node đang áp dụng.

Tầng thứ hai là truyền thông và xử lý dữ liệu. Các node kết nối đến broker MQTT local. Backend dùng FastAPI nhận dữ liệu, kiểm tra định dạng và trạng thái, ghi vào SQLite, đồng thời cung cấp API cho giao diện. Khi người vận hành gửi lệnh, backend chuyển lệnh qua MQTT và theo dõi ACK trả về từ đúng node.

Tầng thứ ba là dashboard HTML, CSS và JavaScript, chạy bằng VS Code Live Server. Giao diện có tổng quan ba đèn, điều khiển từng node, lịch sử, cảnh báo và phiên thực nghiệm. Giao diện hiển thị dữ liệu backend đã nhận, còn quyết định AUTO được thực hiện ngay tại node.

Luồng quan sát đi từ cảm biến, qua ESP32 và MQTT đến backend, database rồi dashboard. Luồng điều khiển đi theo chiều ngược lại, nhưng phải có phản hồi xác nhận. Một phản hồi HTTP đã nhận yêu cầu không đồng nghĩa đèn đã áp dụng, và mức PWM thực có thể cần thêm thời gian để chuyển dần tới mục tiêu.

Cách tổ chức này cho phép mỗi đèn tiếp tục AUTO khi kết nối MQTT bị mất. Trong phần demo, nhóm sẽ chủ động dừng broker để minh họa khả năng này bằng Serial tại node, đồng thời cho thấy dashboard đánh dấu dữ liệu cũ thay vì tiếp tục báo như đang có dữ liệu mới.”

## Thao tác của người B

Chỉ ba cửa sổ node_01/node_02/node_03 và sơ đồ luồng dữ liệu trên slide. Sau đó mở dashboard tổng quan. Nhắc rõ ba node dùng chung source nhưng binary có định danh khác nhau; không đặt ba ESP32 trong cùng một phiên mô phỏng.

Câu chuyển của A: “Sau đây, nhóm sẽ lần lượt chứng minh điều khiển tự động, điều khiển từ xa, cảnh báo tải và khả năng tiếp tục hoạt động khi kết nối bị gián đoạn.”

<!-- PAGE -->
# 5 Giải thích phần cứng và nguyên lý điều khiển

## Lời trình bày ngắn

“LDR tạo đầu vào ánh sáng; firmware lọc và xác nhận trước khi chuyển vùng ngày, hoàng hôn hoặc đêm. PIR cho biết có chuyển động. Chỉ khi PIR báo chuyển động, khoảng cách từ HC-SR04 mới được dùng để tạo tình huống người hoặc xe theo quy ước. Biến trở tạo tín hiệu tải để thử cảnh báo hở tải.”

| Thành phần | Vai trò và điểm cần giải thích |
|---|---|
| LDR AO GPIO34 | Lux tăng thì ADC mô hình giảm; dashboard hiển thị ADC raw |
| PIR OUT GPIO27 | Điều kiện kích hoạt chuyển động, không bị thay thế bởi khoảng cách |
| HC-SR04 TRIG18 ECHO19 | Dưới100 cm tạo kịch bản xe, từ 100 cm tạo kịch bản người khi PIR HIGH |
| Biến trở SIG GPIO35 | Tải giả lập 0–1023 trên UI; firmware ADC12 bit 0–4095 |
| LED PWM GPIO26 qua 220 Ω | Thể hiện mức áp dụng, không phải phép đo dòng hoặc tải thực |

## Bảng quy tắc để nói trước khi thao tác

| Điều kiện AUTO | Mục tiêu |
|---|---|
| DAY | 0% kể cả có chuyển động |
| TWILIGHT yên tĩnh | 50% |
| NIGHT yên tĩnh | 25% |
| TWILIGHT/NIGHT, PIR và Distance 150 cm | 70% |
| TWILIGHT/NIGHT, PIR và Distance 50 cm | 100% |

“Ở đây, mức sáng mục tiêu là quyết định của bộ điều khiển; mức đang áp dụng là PWM thực mà firmware báo lại. Hai giá trị có thể khác trong lúc dimming. Nhóm sẽ chỉ kết luận đèn đã đến mức yêu cầu khi quan sát applied tương ứng.”

B đặt sẵn tab Serial node01. A lưu ý ngưỡng khoảng cách là quy ước demo, không khẳng định hệ thống nhận dạng đối tượng thật; chỉ có khoảng cách gần nhưng PIR chưa kích thì đèn vẫn giữ mức nền.

<!-- PAGE -->
# 6 Cảnh đầu xác nhận ba node và mở phiên demo

Thời gian gợi ý 05:00 đến 06:30. A nói, B kiểm và thao tác. Giữ ba node NIGHT/AUTO/tải bình thường và không chuyển động.

## Lời trình bày

“Trên tổng quan, chúng ta thấy ba định danh node_01, node_02 và node_03. Trước khi thử, nhóm kiểm tra dữ liệu mới của từng node và trạng thái kết nối. Hiện cả ba đèn đang ở AUTO, môi trường NIGHT và mức nền 25%.”

Chỉ đọc câu “hiện cả ba” sau khi B xác nhận trên màn hình. Nếu một node chưa fresh, nói đúng node đang chờ và xử lý theo phần16, không dùng con số cũ để lấp chỗ thiếu.

## Thao tác và kiểm

1. Mở Tổng quan, nhìn health và số node online.
2. Vào chi tiết từng node nếu cần, kiểm mode AUTO, NIGHT, target 25/applied 25, faults rỗng và dữ liệu mới.
3. Trong Wokwi, kiểm Serial uptime tăng, mqtt=1 và đúng node. Không Pause để cố giữ một trạng thái đẹp.
4. Vào Phiên thực nghiệm, đặt tên DEMO-BAOVE kèm ngày giờ, nhập cấu hình mẫu dưới và ghi lịch thao tác trong notes.
5. Bấm bắt đầu một lần; ghi ID trả về để dùng ở cảnh cuối. Nếu báo đã có phiên mở, xử lý đúng phiên đó trước.

```json
{
  "source": "live",
  "purpose": "presentation_demo",
  "voltage_v": 12,
  "rated_power_w": 24,
  "note": "Demo chuc nang, khong thay EX-series"
}
```

A nói: “Phiên này ghi lại các thao tác chức năng của buổi trình bày, gồm cả MANUAL, lỗi tải và gián đoạn kết nối. Nó được tách với bộ15 lượt thực nghiệm chính đã thu trước, nên nhóm không dùng tỷ lệ tiết kiệm của phiên ngắn này làm kết luận đại diện.”

B quay lại node01. Đảm bảo đã lưu ID phiên, không nhập một ID ví dụ như1 thay cho ID thực.

<!-- PAGE -->
# 7 Cảnh thay đổi ánh sáng ngày hoàng hôn và đêm

Thời gian 06:30 đến 08:30. Chỉ đổi LDR node01; node02/node03 giữ NIGHT và25%. Không kích PIR trong cảnh này.

## Lời nói và thao tác

A: “Đầu tiên, nhóm giữ nguyên điều kiện tải và chuyển động, chỉ thay ánh sáng môi trường của node_01. Cách này giúp quan sát đúng tác động của LDR.”

B click LDR, đặt Lux 100000. Chờ environment DAY rồi applied 0. A chỉ vào trạng thái thực: “Khi nhận điều kiện ban ngày, AUTO đưa mục tiêu về 0%; PWM giảm dần về mức đó.”

B đặt Lux 100. Chờ TWILIGHT, target 50 và applied 50. A: “Tại vùng hoàng hôn, đèn duy trì mức nền 50%. Firmware dùng lọc, ngưỡng có hysteresis và thời gian xác nhận để hạn chế đổi trạng thái liên tục khi tín hiệu dao động.”

B đặt Lux 0.1. Chờ NIGHT, target 25 và applied 25. A: “Ban đêm, khi chưa có chuyển động, đèn giữ mức nền 25%. Hai node còn lại vẫn giữ trạng thái riêng, chứng minh thay đầu vào một node không làm đổi toàn tuyến.”

## Điều kiện chuyển cảnh

| Đầu vào UI node01 | Trạng thái cần thấy |
|---|---|
| Lux 100000 | DAY, target 0, applied 0 |
| Lux 100 | TWILIGHT, target 50, applied 50 |
| Lux 0.1 | NIGHT, target 25, applied 25 |

Các ADC đã quan sát trong QA gần 32/2045/4063, có thể dao động. Đọc môi trường và ADC thực; không chỉ nhìn thanh Lux. Nếu vẫn MANUAL, chuyển AUTO có ACK trước rồi lặp cảnh. Nếu vẫn đang dimming, A tiếp tục giải thích target/applied và chờ, không nói đã đạt ngay sau click.

Không dùng độ sáng pixel của LED để suy điện năng. Chuyển tiếp khi node01 NIGHT/AUTO 25, không có hold chuyển động còn hiệu lực.

<!-- PAGE -->
# 8 Cảnh người giả lập và giữ sáng

Phần đầu khoảng 08:30 đến 10:30. Node01 NIGHT/AUTO, applied 25, tải tối đa. B chọn Distance 150 cm ở HC-SR04 trước khi kích PIR.

## Lời trình bày và thao tác

A: “Bây giờ nhóm tạo một tình huống chuyển động ở khoảng cách150 cm. Trong quy ước của mô hình, khi PIR báo chuyển động và khoảng cách từ 100 cm trở lên, node tạo trạng thái PEDESTRIAN và tăng mục tiêu lên 70%.”

B kiểm Distance trên UI và Serial. Sau đó click cảm biến PIR có chụp trắng, bấm Simulate Motion. Chỉ đổi Distance chưa đủ.

A khi thấy dữ liệu: “PIR đã kích hoạt, mục tiêu tăng lên 70%. Mức đang áp dụng tiến dần đến 70%, thể hiện cơ chế chuyển sáng thay vì nhảy ngay một bước.”

B chỉ Serial/telemetry có PIR HIGH hoặc motion PEDESTRIAN trong khoảng kích hoạt, sau đó target/applied 70. PIR có thể đã LOW khi ảnh cuối được xem; hold còn hiệu lực nên lúc đó motion NONE và applied 70 vẫn có thể đúng.

A: “Khi chuyển động kết thúc, đèn chưa giảm ngay. Firmware giữ mức sáng trong 5 giây theo đồng hồ node tính từ lần cuối PIR còn HIGH, sau đó giảm dần về nền 25%. Nếu có sự kiện mới, thời gian giữ được làm mới.”

## Kiểm trước khi chuyển cảnh

- Quan sát thật target 70 và applied đạt70; không dùng form điều khiển làm giá trị thực.
- Ngừng kích PIR, đợi hết hold và applied trở lại25 trước cảnh xe để người xem dễ phân biệt.
- Thời gian thực có thể dài hơn5 giây vì tốc độ Wokwi. Theo dõi uptime và log thay vì chỉ bấm đồng hồ máy.

Nếu log vẫn pir=0, motion=NONE và25% dù khoảng cách thay đổi, B mở đúng PIR và bấm Simulate Motion. A nói: “Cảm biến khoảng cách đang cập nhật; nhóm còn cần kích tín hiệu chuyển động để thỏa điều kiện của thuật toán.”

<!-- PAGE -->
# 9 Cảnh xe giả lập và phép thử không kích PIR

Tiếp tục đoạn người/xe. Giữ node01 NIGHT/AUTO và đã trở lại25%.

## Thao tác có chủ đích

1. B chỉ đổi Distance từ 150 xuống50 cm, chưa kích PIR.
2. Chỉ log distance_cm đã thay đổi nhưng pir=0, motion=NONE và applied 25.
3. Sau đó B bấm Simulate Motion trên PIR.
4. Chờ motion VEHICLE/target 100 rồi applied 100.
5. Ngừng kích, quan sát giữ sáng và giảm về 25 sau khi hết hold.

## Lời trình bày

“Nhóm vừa đưa vật thể mô phỏng lại gần, nhưng đèn chưa tăng sáng vì PIR chưa báo chuyển động. Đây là điều kiện kết hợp của thuật toán. Khoảng cách một mình không tạo sự kiện xe.

Sau khi kích PIR, khoảng cách dưới 100 cm được quy ước thành tình huống VEHICLE. Mục tiêu lúc này lên 100%, rồi mức đang áp dụng tăng tới100%. Khi hết sự kiện và hết thời gian giữ, đèn trở lại mức nền của môi trường hiện tại.

Hai tình huống150 cm và50 cm phục vụ kiểm thử thuật toán trong Wokwi. Hệ thống hiện không có camera hoặc mô hình học máy để nhận dạng phương tiện ngoài thực tế.”

## Log để đối chiếu khi luyện tập

```text
NIGHT + pir=0 + distance≈50cm -> motion=NONE, target=25
NIGHT + pir=1 + distance<100cm -> motion=VEHICLE, target=100
```

Hai dòng trên là bảng kỳ vọng để luyện tập, không phải log đã thu của buổi này. Log CONTROL có thể thể hiện applied chưa bằng target trong lúc dimming. Mỗi khi muốn thử lại70% sau khi đã lên 100%, cần chờ hold cũ kết thúc; firmware giữ mức cao nhất còn hiệu lực.

B để node01 NIGHT và trở lại25. Câu chuyển của A: “Tiếp theo, nhóm chuyển sang node_02 để kiểm tra lệnh điều khiển từ giao diện.”

<!-- PAGE -->
# 10 Cảnh điều khiển MANUAL và AUTO đúng node

Thời gian 10:30 đến 12:00. B mở chi tiết node02, xác nhận node ID, dữ liệu mới và không pending. Đặt LDR node02 DAY, đợi applied 0 trước lệnh để chứng minh MANUAL được ưu tiên cả ban ngày.

## Thao tác và lời dẫn

B chọn MANUAL, nhập80, đợi nút khả dụng rồi bấm Áp dụng thiết lập một lần.

A: “Lệnh đang được gửi đến riêng node_02. Phản hồi tiếp nhận chưa đủ kết luận đã áp dụng; nhóm chờ ACK từ node và đọc kết quả APPLIED. Sau đó kiểm mode thực, mục tiêu80 và PWM tiến tới80%.”

B kiểm APPLIED và applied 80. Chỉ node01/node03 vẫn độc lập.

A: “Ở chế độ MANUAL, người vận hành có thể đặt độ sáng dù môi trường là DAY. Chế độ này có giới hạn60 giây theo uptime node; hết hạn hoặc khi node xác định mất MQTT sẽ quay lại AUTO. Trong phần trình bày, nhóm chủ động gửi AUTO để tiếp tục, không chờ hết thời gian.”

B chọn AUTO và bấm Áp dụng; chờ ACK, mode AUTO và applied 0 theo DAY. Sau đó đặt Lux node02 về 0.1, chờ NIGHT/applied 25 để chuẩn bị cảnh kết nối cuối.

## Những điểm cần quan sát

- Chọn đúng node02, không nhìn bản nháp80 ở form rồi nói applied 80.
- HTTP202/PENDING khác APPLIED; trường API kết quả là result.
- Node online vẫn có thể bị khóa lệnh nếu telemetry quá3 s, đang pending hoặc health suy giảm. Chờ mẫu mới, không tăng ngưỡng.
- Nếu HTTP phản hồi không rõ, kiểm pending/command_id trước; không bấm liên tục để “cho chắc”.

Nếu lệnh bị từ chối, A nói: “Điều kiện gửi lệnh hiện chưa đạt; nhóm đang kiểm độ mới dữ liệu và kết quả lệnh trước.” B xử lý theo phần16. Không đổi sang Serial MANUAL rồi giới thiệu đó là lệnh dashboard có ACK.

<!-- PAGE -->
# 11 Cảnh phát hiện và phục hồi lỗi tải

Thời gian 12:00 đến 14:00. Chọn node03 NIGHT/AUTO/applied 25, không chuyển động, biến trở tối đa. Không dùng node đang DAY0 để thử OPEN_LOAD.

## Tạo lỗi

A: “Phần này mô phỏng tình huống đèn được yêu cầu sáng nhưng tín hiệu dòng tải thấp bất thường. Biến trở là đầu vào giả lập độc lập với PWM, không phải một phép đo dòng thật.”

B đưa biến trở node03 về 0, kiểm current_adc gần 0. Chờ applied≥20% ổn định1 giây và dòng dưới 10% kỳ vọng liên tục 2 giây theo clock node. Kiểm faults có OPEN_LOAD.

A: “Node đã xác nhận OPEN_LOAD sau khoảng kiểm tra, thay vì báo lỗi từ một mẫu thấp tức thời. Trên dashboard, cảnh báo tải được lưu cùng thời điểm bắt đầu và gắn đúng node_03.”

B mở Cảnh báo và lọc node03. Chỉ dòng lỗi tải đang mở, phân biệt các dòng đã kết thúc hoặc mất kết nối lịch sử.

## Phục hồi

B đưa biến trở về tối đa1023, giữ applied đủ và ổn định. Chờ dòng đạt ít nhất20% kỳ vọng liên tục 3 giây; kiểm faults rỗng và cảnh báo có thời điểm kết thúc.

A: “Sau khi tải giả lập phục hồi đủ điều kiện, lỗi được đóng. Việc đổi chế độ hoặc tắt đèn không phải thao tác xóa lỗi. Lịch sử cảnh báo vẫn được giữ để truy vết.”

## Kiểm trước cảnh mất broker

Node03 phải phục hồi thật, NIGHT/AUTO 25 và tải bình thường. Nếu fault còn mở, đợi hoặc xử lý; không dùng mất kết nối để làm nó biến mất. LED vẫn có thể sáng khi biến trở0 vì mô hình không tự cắt PWM do OPEN_LOAD. Không mô tả đây là bảo vệ ngắn mạch hoặc quá dòng.

Câu chuyển: “Sau khi kiểm lỗi tải, nhóm kiểm một tình huống khác là gián đoạn đường truyền MQTT.”

<!-- PAGE -->
# 12 Cảnh mất MQTT nhưng AUTO vẫn hoạt động

Thời gian 14:00 đến 16:00, chỉ thao tác broker thuộc chính buổi demo. Cả ba node AUTO và không còn lệnh pending. B ghi boot ID node01 để đối chiếu sau reconnect.

## Thao tác

Trong terminal firmware đã mở sẵn:

```text
docker compose -f infra/compose.yaml stop mosquitto
```

Giữ Wokwi chạy, không Pause hoặc reset. Chờ Serial node01 báo mqtt=0 và dashboard thể hiện suy giảm/offline/dữ liệu cũ. Phát hiện ngắt không nhất thiết tức thì ngay khi lệnh stop kết thúc.

B đổi LDR node01 sang Lux 100000, chờ Serial DAY/target 0/applied 0; sau đó đổi lại Lux 0.1, chờ NIGHT/applied 25. Không dùng dashboard cũ để xác nhận thay đổi trong thời gian MQTT mất.

## Lời trình bày

“Broker MQTT đã được dừng có chủ đích. Dashboard hiện cho biết dữ liệu bị gián đoạn và các lệnh từ xa bị khóa. Các mức sáng đang lưu trên web là dữ liệu cũ, không được coi như trạng thái mới nhận.

Tại node, bộ điều khiển AUTO vẫn đọc cảm biến và tính mức sáng. Nhóm đang dùng Serial để quan sát việc đổi từ NIGHT sang DAY, rồi trở lại NIGHT trong lúc mqtt=0. Điều này minh họa khả năng điều khiển tại biên tiếp tục hoạt động khi đường truyền gián đoạn.”

Chỉ nói câu khẳng định sau khi Serial thực đã cho thấy các trạng thái trên. Không thay mqtt=0 trong log bằng dữ liệu tự nhập. Nếu không thể kiểm đủ trong thời gian, giới thiệu video/bằng chứng đã ghi và nói rõ phần live đang dừng ở đâu.

Đây là kiểm mất broker. Không dừng backend hoặc toàn bộ Docker để thay ca khác; không reset ESP32 vì sẽ không còn chứng minh liên tục cùng boot.

<!-- PAGE -->
# 13 Cảnh kết nối lại và dừng phiên demo

B khởi động lại đúng broker:

```text
docker compose -f infra/compose.yaml start mosquitto
```

Chờ log MQTT kết nối lại, cả ba node có telemetry mới và dashboard ONLINE/FRESH. Kiểm boot node01 vẫn như trước outage nếu mô phỏng không reset. Nếu boot đổi thật, công bố đó là lần khởi động lại, không gọi là reconnect cùng boot.

## Lời trình bày

“Broker đã hoạt động trở lại. Nhóm chờ telemetry mới để khôi phục trạng thái online, vì một thông báo ONLINE retained chưa đủ chứng minh dữ liệu hiện tại. Các node tiếp tục AUTO; hệ thống không tự phát lại một yêu cầu MANUAL cũ sau khi nối lại.”

Trong buổi này, MANUAL đã được trả AUTO trước outage. Vì vậy chỉ dùng trạng thái hiện tại để minh họa tiếp tục AUTO; kiểm không replay đối với lệnh pending có bằng chứng tích hợp riêng, không suy từ một buổi chưa tạo pending.

## Đóng phiên chức năng

1. Vào Phiên thực nghiệm, chọn ID đã mở ở phần6.
2. Xác nhận tên và thời điểm; bấm Dừng phiên.
3. Kiểm ended_at/nhãn đã dừng. Reload vẫn thấy đúng phiên từ server.
4. Bấm Tải CSV và lưu tên chứa ID/ngày giờ; mở tệp nếu cần để chỉ cột dữ liệu.

A: “Phiên demo đã được đóng và có thể tra lại sau khi tải lại giao diện. CSV giữ các mẫu cùng trạng thái/quality và thông tin cấu hình. Khi có đoạn mất kết nối, chúng ta phải giữ và công bố phần thiếu đó thay vì tự nối dữ liệu cho liền.”

Dừng phiên không dừng mô phỏng. Để Wokwi và backend tiếp tục chạy nếu cần trả lời câu hỏi. Không xóa DB để chuẩn bị demo lại trước khi lưu dữ liệu phiên hiện tại.

<!-- PAGE -->
# 14 Cảnh lịch sử CSV và dữ liệu đã ghi

Thời gian 16:00 đến 17:30. Chọn đúng node và phiên vừa đóng để minh họa dữ liệu của buổi này. Khi chuyển sang kết quả chính, nói rõ đang mở dữ liệu TASK-012 đã thu trước.

## Thao tác trên lịch sử

B vào Lịch sử, chọn node01 và phiên demo, bấm Tải dữ liệu. Chỉ môi trường/mức sáng đã đổi trên biểu đồ và các dòng raw. Nếu hơn1000 mẫu, nhãn trang sẽ cho biết biểu đồ chỉ có trang đang tải; bảng raw có các nhóm 100 mẫu.

A: “Ở đây nhóm chọn cùng một node và phiên để đối chiếu thao tác. Biểu đồ độ sáng là mức đang áp dụng, còn bảng raw cho phép xem từng mẫu. Khoảng trống hoặc điểm ngắt được giữ khi dữ liệu không đủ điều kiện nối.”

## Chuyển sang số liệu chính

Nếu DB demo có dữ liệu phục hồi, B chọn phiên EX05/R3 đã đóng từ TASK-012 theo tên/ID thực trong DB. Nếu DB đang chạy là DB mới, mở bản CSV/bảng/biểu đồ đã bàn giao ngoài trình duyệt. Không tạo phiên giả cùng tên rồi gọi là dữ liệu cũ.

A: “Phần tiếp theo sử dụng bộ15 lượt thực nghiệm đã ghi trước. Nó tách với phiên thao tác chức năng vừa rồi. Báo cáo chính dùng cửa sổ riêng từng node theo uptime; màn hình nguyên phiên có cửa sổ chung, vì vậy trước khi so số phải thống nhất node, thời gian và quy tắc biên.”

## Chi tiết cần giải thích

- UI nhập/hiển thị giờ Việt Nam; API và CSV dùng UTC. Không diễn giải lệch7 giờ là mất dữ liệu.
- Điện năng trên Tổng quan là cửa sổ1 giờ gần nhất; không lấy KPI đó làm số một phiên EX.
- CSV được xuất khi yêu cầu thành công, không dùng một tệp JSON lỗi đã đổi đuôi.csv.
- Seq/uptime trên HTTP là chuỗi thập phân để giữ uint64 chính xác. Trong MQTT chúng là số JSON.

Chỉ đọc số liệu của bảng đã kiểm ở phần15; không cố giải thích chênh lệch cửa sổ bằng việc sửa dữ liệu gốc.

<!-- PAGE -->
# 15 Lời trình bày kết quả thực nghiệm có nguồn

Thời gian 17:30 đến 19:00. B mở bảng hoặc biểu đồ TASK-012. Các con số dưới là kết quả đã ghi của mô hình, không phải số đang đo trực tiếp trong 20 phút này.

## Lời trình bày

“Nhóm đã thực hiện15 lượt chính trên ba node, tương ứng45 cửa sổ node–lượt. Các kịch bản gồm ban ngày, đêm yên tĩnh, người/xe giả lập định kỳ, hỗn hợp ba pha, lỗi tải và mất broker. Các lượt lỗi được giữ riêng và chạy lại trọn lượt liên quan; không ghép một lượt từ các đoạn rời.

Kết quả đã đối chiếu dữ liệu MQTT, SQLite, API, CSV và phép tính độc lập. Khi trình bày hiệu quả, nhóm dùng năng lượng AUTO đủ điều kiện, baseline cùng khoảng hợp lệ và đồng thời công bố độ phủ dữ liệu.”

| Kịch bản lặp3 lần | Công suất AUTO trung bình | Tiết kiệm so baseline cùng đoạn |
|---|---|---|
| EX02 đêm yên tĩnh | 6.000 W | 75.000% |
| EX03 người định kỳ150 cm | 8.160 W | 66.001% |
| EX04 xe định kỳ50 cm | 9.600 W | 60.001% |
| EX05 hỗn hợp ba pha | 6.613 W | 64.579% |

“Ví dụ, mức nền 25% ở tải bình thường tạo công suất mô hình khoảng 6 W so với 24 W của baseline ban đêm. Tuy nhiên không dùng75% như mức tiết kiệm chung cho mọi tình huống. EX05 có pha DAY nên công suất baseline trung bình khoảng 18.671 W, không mặc định24 W cho toàn lượt.”

“EX04/R3 có node đạt độ phủ thấp nhất khoảng 99.004%; EX07 có khoảng 79.073–79.836% vì mất broker có chủ đích. Phần thiếu phải được trình bày, không tính như một đoạn công suất0 hoặc tự nội suy để làm tỷ lệ tốt hơn.”

Nguồn số liệu: output/task-012/deliverables/data/variation.json và node-metrics.csv, audit analysis-final.json trong hồ sơ TASK-012. Dấu chấm trong bảng là dấu thập phân. Làm tròn để đọc, giữ giá trị đầy đủ trong CSV/JSON. Không quy đổi sang tiền điện thực tế hoặc hiệu năng MCU thật.

<!-- PAGE -->
# 16 Nhánh demo khi MQTT hoặc giao diện chưa sẵn sàng

## Trường hợp giống log người dùng vừa gặp

```text
mode=AUTO environment=NIGHT motion=NONE
pir=0 distance_cm=67.95 target=25 applied=25 mqtt=0
```

A nói: “Log cho thấy node đang điều khiển AUTO và cảm biến khoảng cách đã có dữ liệu. PIR hiện chưa báo chuyển động nên mức 25% là đúng nền NIGHT. Đồng thời, kết nối MQTT hiện chưa thiết lập, nên nhóm chưa dùng dashboard để kết luận trạng thái live.”

B đặt Distance 50 cm rồi bấm Simulate Motion trên PIR. Kiểm target 100/applied 100; ngừng kích và chờ về 25. Có thể đổi LDR để cho thấy AUTO hoạt động cục bộ khi mqtt=0. Các dòng trên được trích tình huống người dùng đã cung cấp, không đại diện toàn bộ chức năng đã được kiểm của buổi demo này.

## Khôi phục mạng có giới hạn thời gian

B kiểm broker trong firmware:

```text
docker compose -f infra/compose.yaml ps
docker compose -f infra/compose.yaml up -d mosquitto
docker compose -f infra/compose.yaml logs --tail=30 mosquitto
```

Kiểm Engine đang chạy, cổng1883 không bị broker khác chiếm, gateway và hostname host.wokwi.internal. Sau đó chờ mqtt=1 và telemetry mới. Không mặc định lỗi state=-2 chỉ có một nguyên nhân; log này chứng minh kết nối chưa thành công, chưa chốt nguyên nhân gốc.

Nếu chưa khôi phục trong khoảng đã thống nhất khi diễn tập, A nói: “Phần kết nối live đang gián đoạn. Nhóm xin chuyển sang video đã ghi để trình bày luồng MQTT, dashboard và ACK; phần đang chạy trực tiếp trên Wokwi chỉ minh họa điều khiển tại node.”

Không gọi bản demo cục bộ là đã kiểm toàn luồng web. Không gửi MANUAL cục bộ khi mqtt=0 rồi kỳ vọng được chấp nhận; firmware có điều kiện kết nối cho giao diện thử này.

<!-- PAGE -->
# 17 Các sự cố thường gặp và lời xử lý khi trình bày

| Hiện tượng | B kiểm gì | A nói ngắn gọn |
|---|---|---|
| Đổi distance nhưng đèn 25 | PIR chưa kích, mode/environment | “Nhóm còn cần tín hiệu chuyển động; khoảng cách chỉ tham gia phân loại.” |
| PIR có rồi vẫn chưa70 | Hold100 trước đó, DAY hoặc MANUAL | “Nhóm kiểm điều kiện hiện tại và thời gian giữ trước lần thử mới.” |
| Target đổi applied chưa tới | Dimming, uptime và telemetry mới | “PWM đang tiến đến mục tiêu; nhóm chờ mức áp dụng thực.” |
| Nút gửi bị khóa | age_s, pending, health và node chọn | “Điều kiện gửi lệnh chưa đủ; nhóm đợi dữ liệu mới.” |
| MQTT connect failed | Broker/Engine/cổng/gateway | “Kết nối chưa sẵn sàng; AUTO tại node vẫn có thể kiểm riêng.” |
| Serial uptime đứng | Pause, mô phỏng ngừng hoặc host treo | “Nhóm kiểm phiên mô phỏng trước khi kết luận logic điều khiển.” |
| Không có OPEN_LOAD | applied đủ 20%, tải0, stable/confirm | “Lỗi cần đủ điều kiện và thời gian xác nhận.” |
| Fault không đóng | Tải khôi phục, applied ổn định, recovery3 s | “Đổi mode hoặc mất mạng không tự xóa lỗi tải.” |
| Dữ liệu web chưa đổi | API, tab ẩn/polling, URL8000/8001 | “Nhóm kiểm dữ liệu mới tại nguồn, không dùng giá trị cũ làm trạng thái hiện tại.” |
| Không thấy phiên EX cũ | DB được chọn, danh sách/ID | “Nhóm mở bộ số liệu đã lưu riêng, không tạo dữ liệu thay thế.” |

Trước buổi diễn tập, thống nhất một người xử lý và một người nói. Tránh cả hai cùng bấm, đổi cảm biến không báo hoặc restart nhiều thành phần đồng thời khiến khó xác định nguyên nhân.

Mọi lời thoại xử lý chỉ mô tả điều đang biết. Nếu chưa xác định nguyên nhân, nói đang kiểm; không cam kết “chỉ lỗi hiển thị” khi chưa có bằng chứng. Giữ log/ID phiên và không xóa dữ liệu để reset tình huống trước hội đồng.

<!-- PAGE -->
# 18 Lời kết luận chi tiết

Thời gian 19:00 đến 20:00, sau khi đã trình bày đúng những cảnh thực sự đạt. B mở slide tổng kết hoặc dashboard tổng quan đang fresh.

## Lời trình bày của người A

“Qua phần trình bày, nhóm đã giới thiệu mô hình ba node đèn đường dùng chung một source nhưng hoạt động độc lập. Mỗi node tự xác định môi trường, kết hợp chuyển động và khoảng cách theo quy ước, giữ sáng rồi dimming về mức nền. Người vận hành có thể giám sát trạng thái, gửi lệnh có xác nhận, xem cảnh báo tải, lịch sử và xuất dữ liệu phiên.

Điểm nhóm muốn nhấn mạnh là việc tách điều khiển tại node khỏi giám sát tập trung. Khi đường truyền MQTT gián đoạn, AUTO vẫn được thiết kế để tiếp tục tại node; giao diện phải thể hiện đúng dữ liệu cũ và điều kiện điều khiển, thay vì giữ một trạng thái online không còn được xác nhận.

Về đánh giá, nhóm sử dụng bộ thực nghiệm đã ghi cùng cấu hình, raw log, CSV và kiểm tra độc lập. Điện năng được tính theo uptime từng node, độ phủ theo thời gian nhận. Kết quả mô phỏng giúp đánh giá thuật toán trong các điều kiện đã chốt, chưa thay thế đo đạc điện năng hoặc kiểm an toàn trên mạch thật.

Hướng phát triển tiếp theo có thể là xây dựng và đo kiểm phần cứng thật với nguồn, driver và bảo vệ phù hợp; hiệu chỉnh cảm biến; đánh giá trên kịch bản rộng hơn và bổ sung bảo mật nếu mở hệ thống ra ngoài môi trường local. Đây là các hướng đề xuất, không phải những chức năng nhóm đang khẳng định đã triển khai.

Phần trình bày của nhóm xin kết thúc tại đây. Chúng em cảm ơn thầy cô đã theo dõi và sẵn sàng trao đổi về nguyên lý, cách kiểm thử cũng như giới hạn của mô hình.”

## Điều chỉnh theo buổi thực tế

Nếu có cảnh chưa chạy được live, thay đoạn mở đầu bằng danh sách cảnh đã thực hiện và nêu cảnh dùng video/bằng chứng cũ. Không đọc nguyên văn “qua phần trình bày đã...” cho một chức năng vừa thất bại mà chưa làm rõ. Không tự điền tên giảng viên, môn học hoặc kết luận triển khai ngoài phạm vi.

<!-- PAGE -->
# 19 Bản rút gọn trong khoảng bảy phút

Dùng khi được yêu cầu giảm thời lượng. Bật sẵn môi trường; bảng dưới là gợi ý phân bổ, không ép các timer node chạy theo giờ máy.

| Thời gian | Lời nói và thao tác cốt lõi |
|---|---|
| 00:00 đến 01:00 | Giới thiệu vấn đề, ba node, AUTO tại node và giới hạn mô phỏng |
| 01:00 đến 02:00 | Tổng quan3 node, node01 DAY→TWILIGHT→NIGHT, đọc0/50/25 |
| 02:00 đến 03:00 | Distance 150/PIR rồi50/PIR; target/applied 70 và100 |
| 03:00 đến 03:45 | MANUAL 80 đúng node02, ACK, trả AUTO |
| 03:45 đến 04:45 | Node03 tải0/OPEN_LOAD, khôi phục và alert đóng |
| 04:45 đến 05:45 | Broker stop/start, Serial AUTO và telemetry mới sau reconnect |
| 05:45 đến 06:30 | Lịch sử/CSV và số liệu đã thu, nói rõ baseline/coverage |
| 06:30 đến 07:00 | Kết luận, giới hạn và cảm ơn |

## Lời mở đầu rút gọn

“Nhóm 7 xin giới thiệu mô hình đèn đường thông minh gồm ba ESP32 trên Wokwi. Mỗi đèn tự điều chỉnh theo ánh sáng và chuyển động; dữ liệu được gửi qua MQTT đến FastAPI/SQLite và dashboard web. Nhóm sẽ minh họa điều khiển tự động, lệnh từ xa có ACK, lỗi tải và hoạt động khi mất kết nối. Các tình huống người/xe và điện năng trong phần này đều thuộc mô hình mô phỏng.”

Để tránh vừa chờ vừa đọc dài, A giải thích target/applied hoặc clock trong lúc B chờ trạng thái. Nếu không đủ thời gian, chọn bớt một cảnh theo yêu cầu của hội đồng và giới thiệu phần đó qua video đã ghi; nói rõ đã bỏ live cảnh nào. Không bỏ kiểm recovery để tiết kiệm thời gian nhưng vẫn tuyên bố lỗi đã phục hồi.

Video bàn giao TASK-012 dài khoảng 7 phút và không có âm thanh. Khi dùng video, A thuyết minh theo cảnh hoặc dùng phụ đề đã gắn; không chờ video tự có lời nói.

<!-- PAGE -->
# 20 Câu hỏi bảo vệ về thuật toán và mô phỏng

## Tại sao đổi khoảng cách mà đèn không đổi

“Thuật toán yêu cầu PIR báo chuyển động trước. Khi PIR LOW, khoảng cách vẫn cập nhật nhưng motion là NONE và đèn giữ mức nền. Trong NIGHT mức đó là25%. Muốn tạo tình huống xe hoặc người, phải kích PIR cùng khoảng cách tương ứng.”

## Đây có phải hệ thống nhận dạng người và xe thật không

“Hiện tại là quy ước trong mô phỏng: PIR HIGH, khoảng cách dưới 100 cm tạo VEHICLE, từ 100 cm tạo PEDESTRIAN. Nhóm chưa khẳng định cảm biến này có thể nhận dạng loại đối tượng ngoài thực tế.”

## Tại sao cần lọc hysteresis và xác nhận

“Lọc giảm ảnh hưởng của dao động mẫu. Hysteresis dùng ngưỡng vào/ra khác nhau; xác nhận1 s ngăn việc đổi trạng thái do một khoảng tín hiệu ngắn. Các tham số là lựa chọn của mô hình đã kiểm, không phải tiêu chuẩn chiếu sáng đô thị.”

## Tại sao motion NONE nhưng đèn vẫn sáng70 hoặc100

“PIR có thể đã trở LOW nhưng hold còn hiệu lực. Firmware giữ mức cao nhất còn hiệu lực trong 5 s từ lần cuối PIR HIGH. Sau đó target về mức nền và applied chuyển dần.”

## ACK APPLIED có nghĩa đèn đã sáng đúng80 chưa

“ACK xác nhận node đã chấp nhận mode/mục tiêu. Dimming còn tiếp tục nên phải xem brightness_applied trong telemetry để biết mức đang áp dụng. HTTP202 trước ACK chỉ là tiếp nhận yêu cầu.”

## Vì sao chọn NIGHT25 TWILIGHT50

“Đó là bảng mức sáng đã chốt cho mô hình để so sánh các tình huống. Muốn áp dụng thực tế phải khảo sát yêu cầu chiếu sáng, hiệu chỉnh cảm biến và kiểm đèn/driver thật; nhóm không gọi các mức này là tiêu chuẩn bắt buộc.”

## Wokwi chạy chậm thì MANUAL 60 s tính thế nào

“Thời hạn MANUAL chạy theo uptime tại node. 60 s mô phỏng có thể dài hơn60 s giờ máy. Ngược lại, độ trễ người dùng thấy trên web và cửa sổ ổn định30 phút dùng đồng hồ máy theo hồ sơ.”

<!-- PAGE -->
# 21 Câu hỏi bảo vệ về kết nối dữ liệu và kết quả

## Mất backend thì node có dừng không

“AUTO nằm tại node. Nếu backend dừng nhưng broker vẫn nối, node tiếp tục điều khiển; MANUAL vẫn có thời hạn riêng. Nếu firmware phát hiện MQTT ngắt, nó về AUTO. Cần tách hai tình huống này khi kiểm.”

## Vì sao không gửi lại MANUAL cũ sau reconnect

“Lệnh gắn với boot, command ID và deadline. Hệ thống tránh đưa một ý định điều khiển đã cũ vào trạng thái mới; node boot AUTO và không tự phục hồi MANUAL. Khi cần điều khiển lại, người dùng gửi yêu cầu mới sau khi có telemetry đủ mới.”

## Vì sao đèn vẫn sáng khi đã báo OPEN_LOAD

“Biến trở là tín hiệu tải giả lập độc lập, còn LED thể hiện PWM. Mô hình hiện giám sát lỗi tải và không tự cắt PWM do OPEN_LOAD; chưa triển khai bảo vệ ngắn mạch/quá dòng.”

## Tại sao số nguyên phiên khác bảng báo cáo

“API/UI chọn biên chung của phiên, còn báo cáo chính chọn biên riêng của từng node để bỏ thời gian node nhanh chờ node chậm. Muốn so cần cùng node, from/to, experiment_id và quy tắc xử lý biên.”

## Vì sao không tính phần thiếu là0 W

“Không có dữ liệu không chứng minh công suất bằng0. Nhóm giữ gap, loại đoạn không đủ điều kiện và báo coverage; không tích phân nối qua reset, invalid hoặc gap dài.”

## Tiết kiệm75% có áp dụng toàn bộ tuyến ngoài thực tế không

“Không. 75% trong EX02 là kết quả mô hình đêm yên tĩnh với bảng mức sáng và baseline cùng khoảng hợp lệ. Các kịch bản người/xe/hỗn hợp có tỷ lệ khác. Chưa có phép đo phần cứng hoặc khảo sát đại diện để quy đổi thành tiết kiệm thực tế.”

## Nếu hỏi nhóm đã kiểm những gì

Nêu đúng hồ sơ: TASK-011 có ba node và một cửa sổ1800 s thực theo audit MQTT/SQLite; probe HTTP/tài nguyên của cửa sổ đó thiếu một phần và được công bố. TASK-012 có 15 lượt/45 cửa sổ và audit năng lượng độc lập. Không nói mọi tầng đều được quan sát liên tục đủ 30 phút hoặc buổi hôm nay đã tự chạy lại toàn bộ chiến dịch.

<!-- PAGE -->
# 22 Phiếu diễn tập kiểm cuối và nguồn tham chiếu

## Phiếu dùng trước buổi bảo vệ

| Mục | Ghi khi diễn tập thật |
|---|---|
| Ngày máy OS người A người B | Điền thực tế, không dùng dữ liệu mẫu |
| Hash source/binary và DB đang chạy | Đường dẫn, version và bản backup |
| Ba node fresh và không Pause | ID/boot, health và giờ kiểm |
| Các cảnh0/50/25/70/100 | Đã thấy target/applied đúng, ghi lỗi nếu có |
| MANUAL/ACK và AUTO | Đúng node, ID/kết quả và trở lại trạng thái đầu |
| Fault/recovery và broker reconnect | Log/ảnh/giờ, không xóa lỗi bằng reset |
| Phiên demo và CSV | ID thật, tệp đã lưu, phân biệt số liệu chính |
| Thời lượng chính/rút gọn và Q&A | Thời gian thực đạt được và phần cần luyện |
| Kết quả từng cảnh | PASS/FAIL/chưa chạy cùng bằng chứng |

Tài liệu này không điền sẵn PASS cho khả năng hai thành viên tự trình bày. Mỗi người nên tự chạy lại một lượt và giải thích được nguyên nhân PIR, hold, target/applied, ACK và hai clock trước khi chốt buổi diễn tập.

## Nguồn nội bộ

- [Hướng dẫn cài đặt và vận hành](project-guide.md), [runbook](demo-runbook.md).
- [SRS](srs.md), [firmware và controller](techs/firmware.md), [MQTT](techs/mqtt.md), [dashboard](techs/dashboard.md).
- [Phương pháp thực nghiệm](techs/experiments.md), [audit TASK-012](reports/evidence/task-012/run-20261117-200024/analysis-final.json).
- [Kết quả và bằng chứng tích hợp](reports/evidence/task-011/run-20261117-135233/README.md), [hồ sơ bàn giao TASK-012](reports/evidence/task-012/run-20261117-200024/README.md).

Các lời nói về kết quả có điều kiện quan sát trong từng cảnh. Nếu thực tế khác, giữ thông tin đúng và chuyển nhánh xử lý; không thay log, giả telemetry hoặc gọi dữ liệu lưu trước là dữ liệu đang chạy.
