# TASK-006 P2/A2 — rà soát nghiệm thu và kế hoạch commit riêng

## Kết luận hiện tại

Code/build/host tests PASS; MANUAL80 và MANUAL timeout có file live PASS. Chưa có lỗi chức năng FAIL được chứng minh trong lượt này. Nghiệm thu đủ hồ sơ toàn TASK-006: PENDING, giữ 4/5, không tự chốt hoàn thành. Một số bài live được người vận hành xác nhận đã chạy thành công, nhưng chưa có file/ảnh đủ để đối chiếu độc lập; không yêu cầu chạy lại toàn bộ.

## Đã kiểm tra thực tế

- Đọc các file trong thư mục TASK-006, tìm log CONTROL trên toàn repo (bỏ .git/.pio/cache/build). Chỉ hai file RFC2217 MANUAL dưới đây có CONTROL: 2 và 61 dòng, đều environment=NIGHT, motion=NONE, fault=OK; không có DAY/TWILIGHT/PEDESTRIAN/VEHICLE/OPEN_LOAD hoặc distance_valid=0 trong các file này. Không tìm được log gốc cho những ca còn thiếu ở vị trí khác trong repository.
- Build lại `pio run -e esp32dev`: SUCCESS exit0, 3.28s; RAM48028/327680, flash912763/1310720. Đây là kiểm tra mới trên phiên rà soát, không phải mô phỏng.
- Chạy lại `python scripts/check-firmware.py`: cả4 suite controller/sensors/app/mqtt PASS; code thật với phần cứng/mạng/RTOS stub.
- Chạy lại `python -B test/host/test_wokwi_serial.py`: 7 test PASS; transport giả không phải evidence live.
- `git diff --check` không báo lỗi whitespace; không sửa thuật toán hoặc chạy lại Wokwi/Docker trong lượt rà soát.

## Ma trận bằng chứng

| Nhóm | Kết quả đã chứng minh | Nguồn file / phần còn thiếu |
|---|---|---|
| State machine/AUTO/filter/hysteresis/hold/dimming | Host PASS; live người dùng xác nhận đạt, hồ sơ PENDING | [Validation triển khai](validation.log), suite được chạy lại trong lượt này; chưa có file live DAY/TWILIGHT/NIGHT và hold |
| PIR/HC-SR04 PEDESTRIAN/VEHICLE | Host PASS; live người dùng xác nhận đạt, hồ sơ PENDING | Chưa có file CONTROL ghi motion/target/applied cùng raw PIR/distance trong P2; không dùng evidence P1 thay cho P2 |
| MANUAL80 | Live PASS có file | [rfc2217-manual-20261116-110643-131632.log](rfc2217-manual-20261116-110643-131632.log): TX MANUAL80 có LF, accepted=1, mode MANUAL/target80, applied61 rồi80/duty204, mqtt1 |
| MANUAL timeout60s | Live PASS có file | [rfc2217-manual-20261116-110721-893400.log](rfc2217-manual-20261116-110721-893400.log): 61 CONTROL; MANUAL tại23399ms, AUTO tại83399ms, delta60000ms; MQTT1, target trở25/applied72 đang dimming; RESULT PASS |
| RFC2217 transport | PASS | [Probe](rfc2217-probe-20261116-110619-708467.log): thương lượng thành công; không phải phép thử điều khiển |
| OPEN_LOAD/phục hồi, PWM không bị cắt | Host PASS; live người dùng xác nhận và cung cấp trích đoạn, hồ sơ PENDING | Trích đoạn bên dưới có fault OPEN_LOAD rồi OK, thiếu applied/current khi phục hồi và toàn đoạn để đối chiếu timer ổn định/phục hồi |
| HC-SR04 timeout/P2 loop vẫn chạy | Host PASS; live người dùng xác nhận và cung cấp trích đoạn, hồ sơ PENDING | Trích đoạn bên dưới chứng minh invalid/NA ở một thời điểm; chưa có file nhiều mẫu/ảnh cấu hình/CONTROL liên tiếp cho P2 |
| MQTT reconnect/heartbeat | Host PASS; live heartbeat phía firmware có file; reconnect và broker nhận còn PENDING | Log RFC có HEARTBEAT published=1 và mqtt1; chưa có file reconnect/P2 subscriber. Không biến published=1 thành bằng chứng broker thực nhận hoặc dùng TASK-005 thay thế |

## Trích đoạn người dùng cung cấp trong hội thoại

Các dòng dưới đây được lưu đúng nội dung trích dẫn, gồm dấu `...` do người dùng cung cấp. Đây không phải file Serial nguyên bản hoặc dữ liệu agent tự capture; không đặt tên .log hoặc điền phần bị lược.

OPEN_LOAD/phục hồi:

```text
SENSORS uptime_ms=114399 ... current_adc=0
CONTROL uptime_ms=116399 ... fault=OPEN_LOAD mqtt=1
CONTROL uptime_ms=121399 ... fault=OK mqtt=1
```

Timeout HC-SR04:

```text
SENSORS uptime_ms=6399 ... distance_valid=0 distance_cm=NA
CONTROL uptime_ms=6399 mode=AUTO environment=DAY ... fault=OK mqtt=1
uptime_ms=5873 HEARTBEAT published=1 state=0
```

Người dùng xác nhận AUTO/PIR/VEHICLE/MQTT reconnect, PWM không bị cắt khi fault và CONTROL tiếp tục khi timeout. Đây là nguồn xác nhận thao tác/kết quả, không phải các trường đã tìm thấy trong file hiện tại. Không suy ra khoảng thời gian thực hoặc chuỗi liên tục từ trích đoạn.

## Hoàn thiện ngắn nhất, không chạy lại toàn bộ

Ưu tiên xuất/copy log hoặc ảnh đã quan sát từ buffer/đoạn chat cũ thành nguồn bổ sung có ghi xuất xứ; không tạo lại dữ liệu bị thiếu hoặc gán timestamp mới cho lượt cũ. Cần phần còn lưu về AUTO ba vùng/PIR-motion-target, fault có applied/current trước-sau, timeout có nhiều mẫu và cấu hình, reconnect nếu muốn nghiệm thu live riêng. Nếu không còn nguồn, giữ hồ sơ PENDING thay vì yêu cầu chạy lại các bài đã PASS; người review quyết định phần xác nhận nhân chứng có đáp ứng hồ sơ nhóm hay cần bổ sung ngắn từng phần. Chưa tự thay đổi tiêu chí hoặc chốt TASK-006.

## Git và đề xuất commit trên tuan

Tại lúc rà soát: nhánh đang dùng `main`, HEAD `b24ac606ea27f650ccfdfc56a9a01e861309c2a0`. Nhánh local `tuan` và remote-tracking `origin/tuan` cùng commit đó; main...tuan =0/0. `origin/main` đang được lưu ở ea913d5; đây là ref local hiện có, chưa fetch lại trong lượt chỉ đề xuất này.

Trước khi tạo báo cáo này có 47 file sửa/thêm/xóa, tất cả thuộc TASK-006: src controller/runtime/sensor và bỏ EnvironmentSmokeTest, scripts, test/host và stub, RFC2217 trong cấu hình node_01, tài liệu và evidence/task-006. Không có file thay đổi thuộc evidence TASK-005/checklist nghiệm thu TASK-005 hoặc file ngoài phạm vi; platformio.ini/infra/sơ đồ mạch giữ nguyên. .pio và simulations/*/build vẫn bị ignore. Chưa stage, commit, checkout, fetch, push hoặc merge trong lượt này.

Đề xuất sau khi người dùng đồng ý:

1. Kiểm tra lại status và fetch origin, đối chiếu tuan/origin/tuan; nếu ref thay đổi hoặc có file mới ngoài phạm vi thì rà trước. Không pull/reset/stash-drop tự động.
2. Khi tuan vẫn cùng base, `git switch tuan` sẽ mang nguyên working tree sang nhánh đó, không cần xóa hoặc stash thay đổi. Dừng nếu Git báo nguy cơ ghi đè. Nếu tuan đã lệch, dùng commit chọn lọc tại trạng thái hiện có rồi chuyển commit sang tuan sau review thay vì switch cưỡng bức.
3. Stage đích danh tập TASK-006 đã rà, xem staged diff, loại .pio/build/.env/token và file ngoài phạm vi. Không dùng git add . một cách mù quáng.
4. Commit riêng: `feat: implement TASK-006 AUTO/MANUAL lighting control`; không ghi complete/accepted nếu hồ sơ còn PENDING. Có thể chốt nội dung nghiệm thu trước rồi commit nếu muốn một commit hoàn chỉnh.
5. Chỉ push `origin tuan` khi được đồng ý, không force, không merge main. Nếu bị403 như lần push main trước thì giữ commit local và xử lý quyền; không đổi remote hoặc credentials tự động.

TASK-005 giữ nguyên; chưa triển khai A3/TASK-007. Toàn bộ thay đổi chưa commit vẫn được giữ.
