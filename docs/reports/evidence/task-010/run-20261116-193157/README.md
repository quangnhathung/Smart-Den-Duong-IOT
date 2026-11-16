# TASK-010 — một lượt TIMEOUT/ACK muộn qua proxy local: PASS

## Phạm vi và khôi phục

Người dùng cho phép phương án proxy, yêu cầu một lượt test và khôi phục nguyên trạng. Trước thay đổi đã thông báo: Ctrl+C Backend, SMARTLIGHT_MQTT_PORT=1883, Uvicorn127.0.0.1:8001/workers1/cùng SQLite, healthOK rồi mới dừng proxy. Không chạy init_db, không Pause Wokwi hoặc dừng Mosquitto. Source firmware/Backend/Dashboard, MQTTv1 và thuật toán không sửa; chỉ công cụ thu bằng chứng trong thư mục này được bổ sung.

Baseline: Backend43632→broker1883, Wokwi40268→host.wokwi.internal:1883, Mosquitto15716 listen127.0.0.1:1883. Người dùng dừng graceful Backend cũ theo hướng dẫn. Agent khởi động Backend tạm32248 với SMARTLIGHT_MQTT_PORT=1884, SMARTLIGHT_MQTT_HOST=127.0.0.1 và SMARTLIGHT_DB=D:/IOT/Smart-Den-Duong-IOT-BE/data/smartlight.db; một worker8001. Không sửa .env hay biến hệ thống. Proxy44580 chỉ bind127.0.0.1:1884 và nối1883.

`proxy-preflight.json`/`.jsonl` PASS trước khi gửi lệnh: hai telemetry mới seq932/933 cùng boot3268eb79 tới API qua proxy, AUTO/NIGHT25, healthOK/dropped_events0; proxy chưa arm/targets rỗng, đúng một client Backend. Kiểm tra chỉ đọc, không gửi command.

## Kết quả duy nhất

Command ID **0d8f20f5-4700-4be4-b5cc-37b555396adc**. `ack-delay-check-20261116-193704-427746-summary.json` và `final-audit.json` đều PASS từ dữ liệu thật.

| Sự kiện | UTC | Giờ Việt Nam |
|---|---|---|
| Backend gửi lần đầu |12:37:15.226902Z |19:37:15.226902 |
| Retry duy nhất |12:37:17.268317Z |19:37:17.268317 |
| ACK firmware thật đầu tiên tới proxy |12:37:15.857795Z |19:37:15.857795 |
| GET đầu tiên quan sát TIMEOUT |12:37:25.308628Z |19:37:25.308628 |
| Proxy thả hai ACK |12:37:27.254744Z /27.255748Z |19:37:27.254744 /27.255748 |

Script quan sát TIMEOUT sau10,088672s. DB không có cột timeout_at: bảng ghi mốc GET đầu tiên và khoảng giữa GET cuối PENDING/GET đầu TIMEOUT trong audit, không dựng một timestamp chuyển trạng thái chính xác.

Proxy chọn mốc release12s từ lệnh đầu, không phải12s từ từng ACK đến; retry không gia hạn mốc. ACK thứ nhất được giữ khoảng11,397s, ACK retry khoảng9,401s, đều không tới Backend trước hạn10s tính từ request đầu. Node tạo ACK thật APPLIED; raw frame lúc giữ/thả có cùng SHA256, không thay payload/QoS/schema hoặc sinh ACK. Đây là fault injection có nhãn, không gọi là mất ACK tự nhiên.

SQLite/API cuối đều **TIMEOUT / ACK_TIMEOUT**, ack_at=null, attempts2. Hai ACK event22/23 có disposition **LATE_OR_DUPLICATE**; ACK muộn không đổi thành APPLIED. Đây là kết quả của Backend; node đã chấp nhận AUTO vốn đang hoạt động, PWM thực vẫn25 từ telemetry.

## Không có gửi lại ngoài dự kiến

`final-audit.py` đối chiếu:

- Đúng1 POST command, đúng1 command ID mới, không có POST tự retry.
- Hai MQTT command cùng ID/deadline/nội dung: lần đầu và1 retry ứng dụng sau2,041415s theo policy. Không có lần thứ3 hoặc UUID khác.
- Hai ACK thật bị giữ rồi thả nguyên bytes; không dùng fixture làm nghiệm thu.
- Sau khôi phục, command vẫn TIMEOUT/attempts2, không có PENDING sót; capture không có command phát lại hoặc ID ngoài dự kiến. Quan sát không replay tiếp tục khoảng2 phút sau dừng proxy, không suy ra bảo đảm vô hạn.

## Khôi phục: PASS

Backend tạm đã shutdown và hoàn tất application shutdown trong `backend-proxy.log`. Ctrl+C truyền qua PTY/pipeline không tới Uvicorn; đã dùng control event trong riêng console Backend tạm, Uvicorn xử lý shutdown, không force-kill Backend hoặc đụng Wokwi/Mosquitto. Tài liệu API control event: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/console/generateconsolectrlevent). `backend-stop-signal.json` chỉ ghi lần gửi CTRL_C; không dùng nó để chứng minh process đã dừng. Log shutdown mới là bằng chứng dừng hoàn tất.

Backend phục hồi PID14144, MQTT127.0.0.1:1883/API8001/workers1, SQLite cũ. `restored-network.log`, `snapshot-restored.jsonl`/`snapshot-final.jsonl` và `dashboard-http-restored.json` xác nhận healthOK, broker/database/queue true, dropped_events0, telemetry AUTO/NIGHT25 cùng boot. Dashboard5500 HTTP200, config vẫn8001, CORS5500 đúng.

Chỉ sau healthOK và proxy không còn client Backend, agent dừng riêng proxy44580; `proxy-stop-action.json` xác nhận proxy_stopped=true. Không còn listener1884. Proxy kết thúc bằng Stop-Process khi đã rỗng, không có frame đang chờ; `ack-delay-status.json` là status cuối khi process còn chạy, không dùng trường listening trong file đã ngừng cập nhật để suy trạng thái hiện tại.

**Xác nhận người dùng sau khôi phục:** Dashboard node_01 ONLINE, AUTO/NIGHT25%/25%, LDR3917, không lỗi tải, dữ liệu mới19:44:21 ngày16/11/2026, boot3268eb79/seq963→969; không gửi lệnh điều khiển thêm. Đây là xác nhận quan sát giao diện; không có ảnh mới trong repo. Không yêu cầu thao tác lại.

Giữ toàn bộ dữ liệu trước lượt test: telemetry907→957, commands14→15, ACK21→23, alerts245→292, experiments3→3, availability2→4; không thiếu hoặc sửa các bản ghi cũ bất biến. Alert đang mở được phép đóng theo dữ liệu mới. SQLite quick_check/schema và đường dẫn giữ nguyên. Không mở phiên đo mới hoặc xóa DB/log.

## Log và giới hạn

`capture-whole-test.jsonl` ghi MQTT thật từ broker1883 và API xuyên suốt chuyển/khôi phục, kết thúc bằng stop request sau quan sát. Helper `live-evidence.py` bổ sung tùy chọn stop-file để đóng recorder có kiểm soát; driver chỉ bổ sung chờ GET bắt kịp mẫu telemetry trực tiếp trước khi POST, tránh race vài millisecond. Hai thay đổi nằm ở bản sao lượt này, giữ script/log các lượt PASS trước nguyên byte.

`backend-restored.log` vẫn là log của dịch vụ đang chạy nên có thể tăng. Manifest loại file đang ghi này và giữ bản sao cố định `backend-restored-at-verification.log`; xem manifest-notes.json. Các log còn lại và script/CSV/JSON đã đóng được hash. Backend14144 tiếp tục chạy sau bàn giao, proxy/recorder đã dừng.

TASK-010 vẫn2/4 nhóm: TIMEOUT/ACK muộn/retry và khôi phục API/MQTT/Dashboard đã PASS; nhóm2 còn broker outage/reconnect/no-replay cho lệnh đang chờ/AUTO offline và trạng thái UI terminal; nhóm4 còn sensor→Dashboard10 lượt. TASK-011 chờ đặc tả. Không commit/push/merge hoặc xóa dữ liệu.
