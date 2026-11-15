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
