# TASK-010 — OPEN_LOAD đã đối chiếu, tiếp tục kiểm restart

## Nguồn xác nhận người vận hành

Người dùng xác nhận: LDR1 lux, NIGHT, PIR0; biến trở0 làm current_adc0 và OPEN_LOAD; đưa tải về tối đa/current_adc4095 thì fault về OK tại Serial uptime1340431ms. AUTO tiếp tục target25/applied25/duty64/mqtt1. Người dùng đã chụp ảnh Serial; khảo sát thư mục TASK-010 chưa thấy file ảnh. Không gọi xác nhận này là ảnh hoặc Serial log đã lưu trong repo.

Không chạy lại OPEN_LOAD. Capture MQTT của lượt trước đã kết thúc trước thao tác người dùng; không có raw MQTT quá khứ của ca này trong file capture cũ. Dùng payload telemetry đã được Backend lưu thật trong SQLite, đối chiếu API history/alerts/stats. Capture mới chỉ ghi dữ liệu từ lúc khởi động trong lượt này.

## Kết quả OPEN_LOAD — PASS

`fault-audit.json` chứa dữ liệu SQLite thật và response API kèm URL/thời điểm thu; `fault-audit.py` chỉ đọc, không gửi command hoặc chỉnh DB.

| Nội dung | Bằng chứng |
|---|---|
| Phát hiện lỗi tải và phục hồi | Hai đợt dữ liệu riêng, alert30 và33 đều có started_at/ended_at; không gộp thành một sự kiện hoặc coi là alert lặp ở mỗi mẫu |
| Đợt cuối bắt đầu | seq683, uptime1323338ms, current_adc0, faults=[OPEN_LOAD], received_at11:44:26.108335Z |
| Đợt cuối còn lỗi khi tải đã trở lại | seq691, uptime1339377ms, current_adc4095, OPEN_LOAD còn giữ trong giai đoạn xác nhận phục hồi |
| Đợt cuối phục hồi | seq692, uptime1340238ms, current_adc4095, faults=[], received_at11:46:15.004905Z; alert33 đóng đúng timestamp mẫu này |
| AUTO không bị fault cắt PWM |16 mẫu quanh hai đợt đều AUTO/NIGHT/NONE, target25/applied25, cùng boot3268eb79 |
| Không trộn fault và offline | Trong lúc alert33 mở có các alert OFFLINE riêng; OPEN_LOAD chỉ đóng khi telemetry hết lỗi, không tự đóng theo OFFLINE |
| Loại khoảng fault khỏi so sánh AUTO | API stats cùng cửa sổ có FAULT_OR_RECOVERY4, LOAD_CALIBRATION_OR_FAULT_CONFIRMATION3, STATE_CHANGE4, DISCONTINUITY10 |

Mốc Serial người dùng1340431ms lệch193ms so với telemetry đầu hết lỗi1340238ms. Hai nguồn ghi ở thời điểm lấy mẫu/log khác nhau; giữ nguyên cả hai, không coi là cùng một timestamp. Không suy exact timer2s/3s từ telemetry thưa. Duty64/mqtt1 là xác nhận Serial của người dùng; schema telemetry không có hai trường này.

Lần audit đầu dùng timestamp mẫu ở mép cửa sổ và gặp lệch precision float→ISO microsecond làm số mẫu không khớp. Script đã đổi sang mép cửa sổ có đệm15s và chạy lại kiểm dữ liệu đã lưu PASS; không tác động hoặc chạy lại firmware/fault.

## Kiểm tra còn lại và capture mới

`live-evidence.py` là bản sao nguyên byte của harness lượt run-20261116-180648 tại lúc bắt đầu; chỉ dùng snapshot/capture/experiment-export trong lượt này. `snapshot-initial.jsonl`/`sqlite-initial.json` giữ hiện trạng; `snapshot-before-restart.jsonl`/`sqlite-before-restart.json` là baseline trước thao tác dự kiến.

Phiên3 do agent tạo qua API để quan sát restart NIGHT25, không phải phiên hồi tố của OPEN_LOAD. `owned-experiment.json` giữ response tạo phiên; không đưa dữ liệu OPEN_LOAD cũ vào phiên mới hoặc gọi đó là EX-series.

Đã bật `capture-restart-watch.jsonl` giới hạn600s và hướng dẫn người dùng Ctrl+C Backend, chờ dừng+5s rồi khởi động lại8001/workers1, giữ Wokwi/SQLite. Chỉ chốt restart sau khi có API outage/recovery, trạng thái/continuity mới và đối chiếu bản ghi. Chưa đủ bằng chứng thì PENDING; hai snapshot tự chúng không chứng minh đã restart.

`serial-capture.py` chỉ đọc RFC2217, DTR/RTS false và không gửi lệnh Serial. Log lỗi `serial-post-recovery.jsonl` giữ lần mở đầu với write_timeout không được pyserial RFC2217 hỗ trợ; đã bỏ tùy chọn này và chạy capture mới với tên có timestamp. Không sửa firmware/port/schema, không ghi đè log lỗi.

## Ma trận bốn nhóm

- Nhóm1: PASS kết nối live một node/trạng thái cơ bản theo hồ sơ trước, bổ sung fault→history/API/alert PASS ở đây.
- Nhóm2: PENDING timeout/ACK muộn/UI REJECTED-TIMEOUT, mất API/broker/reconnect/no-replay/AUTO offline. Các ca MANUAL/AUTO/reject/cache/pending đã PASS, không chạy lại.
- Nhóm3: PASS tiêu chí OPEN_LOAD/phục hồi/AUTO25, history và alert đóng; PASS phiên/CSV/stats đã có. Restart giữ dữ liệu/phiên mở/gap vẫn chờ đối chiếu; hiển thị Dashboard fault chưa có ảnh hoặc xác nhận trực tiếp riêng.
- Nhóm4: command→ACK10 lượt PASS ở lượt trước; cảm biến→Dashboard10 lượt PENDING.

Tổng1/4 nhóm hoàn thành. TASK-011 chờ đặc tả chính thức. Không commit/push/merge, không xóa SQLite/log hoặc sửa thuật toán/MQTT.

## Chốt lượt theo dõi restart

Capture600s kết thúc11:50:10Z→12:00:11Z. `restart-observation.json` ghi0 HTTP_UNAVAILABLE, Backend run ID trước/cuối cùng26989c18-61ec-478e-95cf-82f310ba944b, chưa có xác nhận người vận hành về restart. **Restart PENDING**; END/result=PASS trong log capture chỉ nghĩa recorder kết thúc bình thường. Đối chiếu snapshot không mất bản ghi cũ (telemetry710→760, commands13→13, ACK20→20, alerts57→106, experiments3→3, availability1→1) là bảo toàn trong khoảng quan sát, không phải nghiệm thu restart.

Đã đóng riêng phiên3, lưu response tại `owned-experiment-stop.json`; không còn phiên đo agent mở hoặc recorder chạy. Backend/Wokwi/Dashboard giữ nguyên. Phiên3 được đặt tên theo ca dự kiến, nhưng thực tế không có restart; không dùng tên phiên làm bằng chứng đã thực hiện.

`experiment-3-night-observation.csv`/`experiment-3-comparison-night-observation.json`:50 mẫu NIGHT25/6W, API/history/CSV/stats khớp. Có48 boundary DISCONTINUITY, đều không nối năng lượng qua gap theo `night-gap-audit.json` tính độc lập. Tổng hợp lệ0,0033416667Wh, baseline0,0133666667Wh, chỉ2,005s uptime và10,00758s wall được phủ trong khoảng651,965s thực; coverage1,534987%. Saving75% chỉ trên tập hợp hợp lệ rất nhỏ, không đại diện toàn khoảng hoặc kết quả EX-series. Gap do stale/offline PASS, gap qua restart vẫn PENDING.

`serial-post-recovery-185255.jsonl` giữ48 dòng Serial thật. `post-recovery-serial-audit.json` kiểm19 CONTROL AUTO25/duty64/faultOK/mqtt1, không gửi command; đây là trạng thái sau phục hồi, không tái chạy OPEN_LOAD. Clock/tần suất tính trên đoạn dữ liệu có trong file tại thời điểm audit, không suy là đo latency cảm biến→UI.
