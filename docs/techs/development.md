# Quy trình phát triển và convention agent

## Cơ sở và phạm vi

- Hướng dẫn bắt buộc: [AGENTS.md](../../AGENTS.md).
- Nguồn yêu cầu: [SRS](../srs.md), đặc biệt mục 3–6 (cấu trúc, firmware, giao thức), 10–12 (gói việc, agent, kiểm thử), 16 (quản lý thay đổi).
- Hiện trạng: PlatformIO, `esp32dev`, Arduino; FirmwareApp/LightingController/SensorReader/Connectivity thực hiện P2/A2 và diagnostics, xem firmware.md về phần đã kiểm tra và giới hạn. Convention không phải bằng chứng chức năng đã nghiệm thu live.
- Mỗi yêu cầu có đầu ra riêng là một task; bước kỹ thuật là checklist con, không tự tạo task mới cho từng lệnh. Gói P0–P8/A0–A7 trong SRS là tham chiếu phạm vi, không thay thế mã task.
- Tài liệu và báo cáo viết tiếng Việt; định danh code dùng tiếng Anh. Thời điểm báo cáo dùng ISO 8601 với múi giờ `Asia/Ho_Chi_Minh` (`+07:00`).

## Nạp convention trên ba công cụ

Convention chung nằm tại [AGENTS.md](../../AGENTS.md); [CLAUDE.md](../../CLAUDE.md) chỉ có tiêu đề và import `@AGENTS.md`. Cập nhật quy tắc chung tại AGENTS.md và tài liệu này, không chép nội dung thành nhiều bản. Các liên kết tài liệu trong AGENTS.md là yêu cầu agent đọc thêm, không giả định mọi công cụ tự mở toàn bộ liên kết Markdown.

| Công cụ | Cách nạp tại dự án |
| --- | --- |
| Codex | Nạp AGENTS.md ở gốc firmware theo cơ chế hướng dẫn dự án; AGENTS.override.md nếu được tạo sẽ có ưu tiên cao hơn ở cùng cấp. |
| Claude Code | Nạp CLAUDE.md, mở rộng import @AGENTS.md vào context; dùng được cả khi phiên bản/cấu hình chưa tự đọc AGENTS.md. |
| OpenCode | Nạp AGENTS.md trực tiếp. Bản v2 không dùng CLAUDE.md làm fallback; không cần thêm opencode.json để nạp lại cùng tệp. |

Nguồn chính thức: [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Claude Code imports](https://code.claude.com/docs/en/memory#share-one-file-with-other-coding-tools), [OpenCode instructions](https://opencode.ai/docs/instructions).

### Khởi động và xác nhận

Mở terminal ở gốc `firmware/`, sau đó chạy `codex`, `claude` hoặc `opencode` tương ứng. Sau khi sửa convention, mở phiên mới để tránh phụ thuộc context cũ. Không chạy `/init` để ghi đè hướng dẫn đã thiết lập.

- Trong Claude Code, dùng `/context all` để kiểm tra Memory files; xác nhận CLAUDE.md và nội dung import từ AGENTS.md. Một số phiên có thể yêu cầu xác nhận import lần đầu theo chính sách của Claude Code.
- Trong từng công cụ, có thể gửi yêu cầu chỉ đọc: “Liệt kê các tệp hướng dẫn dự án đã nạp và tóm tắt quy định về SRS, techs, báo cáo, task, checklist và Arduino. Không sửa tệp.” Đối chiếu câu trả lời với AGENTS.md; yêu cầu này chỉ là kiểm tra nhận hướng dẫn, không triển khai P0.
- Nếu thiếu convention, kiểm tra workspace có đúng firmware không; kiểm tra cấu hình global/managed, hướng dẫn override và việc tắt nạp project instructions. Với OpenCode, kiểm tra `OPENCODE_DISABLE_PROJECT_CONFIG` không bật. Không tự thay cấu hình global để vượt chính sách managed.

### Mức xác minh hiện tại

Đã kiểm tra cấu trúc tệp và đường dẫn import tại dự án, đối chiếu tài liệu chính thức. OpenCode cục bộ báo v2.0.26 khi dùng thư mục XDG tạm trong /tmp vì thư mục log mặc định không ghi được trong phiên này. Claude CLI không có trong PATH; chưa chạy phiên model mới của ba công cụ để kiểm tra context thực tế. Các tệp thiết lập cơ chế nhận convention, không phải cơ chế cưỡng chế mọi hành vi của model. Khi cần xác nhận trên phiên sử dụng thực tế, làm bước chỉ đọc ở trên.

## Vòng đời task

1. Đọc SRS, task hiện tại/tiếp theo, báo cáo gần nhất và tài liệu kỹ thuật liên quan. Ghi yêu cầu SRS áp dụng hoặc lý do task hỗ trợ dự án mà không triển khai FR cụ thể.
2. Nếu cùng yêu cầu đang làm, giữ mã task. Nếu là yêu cầu mới, lấy số lớn nhất đã dùng trong các tệp báo cáo cộng một; không tái dùng mã đã hủy. Không xóa lịch sử khi thay task hiện tại.
3. Trước thay đổi, cập nhật `task.md`: mô tả, phạm vi, tiêu chí nghiệm thu, checklist và trạng thái `Đang thực hiện`.
4. Triển khai, cập nhật tài liệu kỹ thuật và tiến độ theo kết quả thật. Nếu bị chặn, ghi nguyên nhân, bằng chứng, cách xử lý, người/phụ thuộc cần hỗ trợ; tiếp tục phần không phụ thuộc nếu có.
5. Kiểm tra theo tầng bị ảnh hưởng. Chỉ chuyển `Hoàn thành` khi đủ tiêu chí; sau đó ghi báo cáo và checklist lịch sử, cập nhật đề xuất tiếp theo.
6. Không tự chạy task được đề xuất. Khi được giao task mới, chuyển mô tả từ `next-task.md` sang `task.md`, đối chiếu lại yêu cầu và hiện trạng trước khi bắt đầu.

Trạng thái hợp lệ: `Chưa bắt đầu`, `Đang thực hiện`, `Bị chặn`, `Hoàn thành`, `Đã hủy`. Tiến độ ghi `n/N` mục nghiệm thu đã đạt kèm checkbox; không ước lượng phần trăm tùy ý. Task đang bị chặn không được ghi thành hoàn thành chỉ vì hết lượt làm việc. Task hoàn thành vẫn được giữ trong `task.md` đến yêu cầu tiếp theo.

Yêu cầu kiểm tra dự án cũng có task và báo cáo. Trao đổi thuần hội thoại không tạo task mới. Ở chế độ chỉ lập kế hoạch, không sửa tệp; trình bày nội dung dự kiến trong câu trả lời.

## Tổ chức tài liệu kỹ thuật

Tạo `docs/techs/<danh-muc>.md` khi có nội dung, tên tiếng Anh dạng `kebab-case`. Tìm và cập nhật tài liệu cùng chủ đề trước khi tạo mới.

| Danh mục | Nội dung |
| --- | --- |
| `architecture` | [Kiến trúc A0 và điểm bàn giao](architecture.md) |
| `setup` | [Môi trường P0, firmware thử nghiệm, Docker MQTT, Wokwi và nghiệm thu](setup.md) |
| `development` | Quy trình agent, convention, mẫu báo cáo và công cụ định dạng |
| `firmware` | [Controller P2 và MQTT A3](firmware.md); xem giới hạn host/live |
| `hardware` | [Pin map, đấu nối và giới hạn giả lập](hardware.md) |
| `mqtt` | [Hợp đồng MQTT v1](mqtt.md): topic, schema, ACK, deadline, chống trùng và reconnect |
| `simulation` | [Chạy Wokwi và hướng dẫn A3](simulation.md) |
| `testing` | [Host checks và ma trận live P1–A3](testing.md) |

Chưa tạo sẵn các trang trống. Task chạm nhiều danh mục phải cập nhật các trang chịu ảnh hưởng; nếu kiểm tra không dẫn đến thay đổi kỹ thuật, ghi kết quả ở báo cáo và lý do không cần sửa techs. Không biến thiết kế dự kiến thành mô tả triển khai thực tế.

Mẫu trang kỹ thuật:

```markdown
# <Chủ đề>

## Tham chiếu SRS
<Mục/FR/TC liên quan; phân biệt yêu cầu với quyết định triển khai.>

## Triển khai và cấu hình
<Trách nhiệm module, luồng xử lý, tham số có đơn vị, cách sử dụng.>

## Kiểm tra
<Lệnh/bước tái lập, môi trường, kỳ vọng, kết quả và liên kết bằng chứng.>

## Giới hạn và vấn đề còn lại
<Phần chưa triển khai/chưa xác minh, cách giải quyết hoặc “Không có”.>
```

## Arduino và C++

Định dạng dựa trên [Arduino ESP32 Coding Guidelines](https://docs.espressif.com/projects/arduino-esp32/en/latest/guides/coding_guidelines.html). Quy ước đặt tên dưới đây là lựa chọn nhất quán của dự án, không yêu cầu đổi API thư viện hoặc hợp đồng SRS.

- Giữ `src/main.cpp`, include `<Arduino.h>` khi dùng Arduino API; giữ `setup()` để khởi tạo và `loop()` để điều phối. Trong `.cpp`, khai báo hàm trước khi gọi, không dựa vào cơ chế tự sinh prototype của sketch `.ino`.
- Hàm/biến dùng `camelCase` (`readSensors`, `lastSampleMs`); kiểu và module mới dùng `PascalCase` (`LightController.h/.cpp`); giữ tên entry point có sẵn. Hằng dùng `UPPER_SNAKE_CASE`, ưu tiên `constexpr` thay macro cho giá trị có kiểu.
- Ghi đơn vị trong tên như `SAMPLE_INTERVAL_MS`, `distanceCm`; gom pin, ngưỡng và chu kỳ vào cấu hình có tên. Dùng kiểu số phù hợp kích thước/range và kiểm tra đầu vào; không đổi tên trường JSON, node ID hay giá trị giao thức chỉ để hợp naming code.
- Tách đọc cảm biến, logic điều khiển, PWM và MQTT theo trách nhiệm. Logic thuần có thể kiểm thử bằng đầu vào/clock giả lập, không phụ thuộc `Arduino.h` nếu không cần.
- Dùng lịch thời gian không chặn cho điều khiển/reconnect; timeout hữu hạn. Với bộ đếm 32 bit, so khoảng thời gian bằng phép trừ unsigned để chịu tràn, kiểm thử biên; không so deadline bằng phép cộng thiếu xử lý tràn. Giữ uptime 64 bit theo hợp đồng SRS.
- Không dùng `delay()` dài hoặc vòng chờ mạng vô hạn. Chờ microsecond/timeout cảm biến chỉ trong giới hạn SRS. AUTO phải tiếp tục khi mất mạng.
- Kiểm tra giá trị trả về của PWM/publish và API có thể lỗi. Đối chiếu API với Arduino ESP32 thực tế; với Core 3.x, dùng LEDC API 3.x theo SRS, không chép API 2.x hoặc tự nâng phiên bản để chữa lỗi biên dịch.
- Formatter: 2 dấu cách, không tab; dòng tối đa 160 ký tự; ngoặc mở cùng dòng; có ngoặc cả nhánh một câu lệnh; con trỏ sát tên biến; giữ thứ tự include theo nhóm có chủ đích. Tệp UTF-8, LF, có newline cuối tệp.
- Không định dạng lại code ngoài phạm vi task. `.editorconfig` giữ khoảng trắng cuối dòng Markdown vì có thể là dấu xuống dòng có chủ đích. Không ghi đè README hướng dẫn sẵn có.

### Công cụ định dạng

Chạy tại gốc `firmware/`, thay đường dẫn ví dụ bằng các tệp thực sự thay đổi:

```bash
clang-format --version
clang-format --dry-run --Werror src/LightController.cpp include/LightController.h
```

Khi được phép sửa mã, dùng `clang-format -i` với đúng các tệp trong phạm vi task. Các đường dẫn ví dụ trên chưa tồn tại; không coi đây là lệnh build hiện tại. Công cụ phải hỗ trợ các khóa trong [cấu hình](../../.clang-format); bản 23.1.4 hiện có đã đọc được cấu hình. Nếu gặp khóa không hỗ trợ, ghi phiên bản/lỗi và đề xuất công cụ tương thích, không âm thầm bỏ quy tắc.

Không thêm hook hoặc CI trong task thiết lập này. Source P0 hiện tại đã được kiểm tra formatter; không suy ra đã format hoặc nghiệm thu các module nghiệp vụ chưa tồn tại. Thay đổi thuần tài liệu/cấu hình formatter không yêu cầu build firmware; thay đổi code phải build environment bị ảnh hưởng và chạy ca logic tương ứng. Khi có ba environment thì kiểm tra đủ các environment bị ảnh hưởng, không báo ba node đạt khi mới có `esp32dev`.

## Mẫu task hiện tại và task tiếp theo

Hai tệp dùng chung cấu trúc sau; `next-task.md` luôn có thêm phụ thuộc/điều kiện bắt đầu. Nếu chưa có đề xuất, giữ các trường và ghi “Chưa xác định”, `0/0`, `Chưa bắt đầu`; không tự tạo công việc để điền.

```markdown
# TASK-NNN — <Tên task>

- Trạng thái: <Trạng thái hợp lệ>
- Tiến độ: <n/N mục>
- Cập nhật: <YYYY-MM-DDTHH:mm:ss+07:00>

## Mô tả và phạm vi
<Yêu cầu, đầu ra, giới hạn.>

## Tham chiếu SRS
<Mục/FR/TC hoặc lý do là task hỗ trợ.>

## Tiêu chí hoàn thành và tiến độ
- [ ] <Đầu ra và cách kiểm chứng>

## Vướng mắc và cách giải quyết
<Nguyên nhân, bằng chứng, hành động cần làm hoặc “Không có”.>

## Phụ thuộc và điều kiện bắt đầu
<Yêu cầu giao việc, đầu vào, môi trường cần có.>
```

## Báo cáo và bảo toàn lịch sử

Mỗi lần kết thúc một lượt thực hiện task, kể cả chưa hoàn thành, thêm một khối báo cáo lên đầu [report.md](../reports/report.md). Đọc nội dung cũ trước khi ghi; kết quả phải là `khối_mới + dấu_phân_cách + toàn_bộ_nội_dung_cũ`. Không sửa, cắt, đảo thứ tự hoặc ghi đè các báo cáo trước. Xác nhận phần đuôi vẫn khớp nội dung cũ; nếu ghi lỗi, khôi phục nội dung đã đọc trước khi báo hoàn thành. Không cần tiêu đề cố định nằm trên mục mới nhất.

```markdown
## <YYYY-MM-DDTHH:mm:ss+07:00> — TASK-NNN — <Tên task>

- Trạng thái: <Trạng thái task>
- Tiến độ: <n/N mục>

### Đã thực hiện
<Thay đổi thực tế và đường dẫn liên quan.>

### Kiểm tra và kết quả
<PASS/FAIL/chưa chạy; lệnh/bước, kết quả và bằng chứng.>

### Vướng mắc
<Mô tả và ảnh hưởng, hoặc “Không có”.>

### Cách giải quyết
<Việc cần làm, phụ thuộc, bước xác nhận sau xử lý; không có thì ghi “Không có”.>

### Tài liệu và bước tiếp theo
<Techs đã cập nhật, mục SRS liên quan, đề xuất nhưng chưa tự triển khai.>
```

[checklists.md](../reports/checklists.md) là lịch sử task hoàn thành: thêm mục mới trước các mục task cũ, gồm mã/tên, ngày hoàn thành, checklist đã làm và liên kết báo cáo/bằng chứng. Không đưa task đang làm hoặc task tương lai vào danh sách hoàn thành. Giữ các mục cũ, tránh thêm trùng mã; nếu mở lại một task, giữ bằng chứng cũ và ghi rõ lượt bổ sung.

## Xác minh convention

Kiểm tra liên kết nội bộ, tính đồng bộ mã task/trạng thái, bảo toàn lịch sử báo cáo, cấu hình formatter đọc được và định dạng mẫu qua stdin hai lần cho cùng kết quả. Đối chiếu SRS/source/cấu hình build trước–sau để xác nhận task tài liệu không sửa chức năng. Kết quả chạy thực tế được ghi tại [báo cáo](../reports/report.md).
