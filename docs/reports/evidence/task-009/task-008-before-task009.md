# TASK-008 — Backend, SQLite và API P4/A4

- Trạng thái: Hoàn thành
- Tiến độ: 4/4 nhóm nghiệm thu bàn giao code/test/hướng dẫn
- Cập nhật: 2026-11-16T13:17:56+07:00

## Mô tả và phạm vi

Backend tại DoAn/backend/ (cùng cấp firmware), Git riêng không remote/commit/push. Python3.12/FastAPI/Pydantic2/Paho2/SQLite WAL/Pytest: collector, API, command/ACK, năng lượng/phiên/CSV. Đầu ra code/test/OpenAPI/hướng dẫn; không dashboard, Wokwi/broker thực, cloud hoặc sửa firmware.

## Tham chiếu SRS

SRS6/7/9/12, FR06/08/09/10/11; TC17–22/24/26 và ma trận năng lượng. Hợp đồng MQTTv1 và TASK-007 giữ nguyên.

## Tiêu chí hoàn thành và tiến độ

- [x] Collector strict/schema/boot/order/dedup, SQLite persistence/health/fault/offline đúng kiểm thử.
- [x] API và command/ACK/retry/timeout/concurrency đạt, không phát lại lệnh offline/restart.
- [x] Năng lượng/baseline/coverage/experiment/CSV đúng cùng dữ liệu và clock.
- [x] Test/lint/startup/OpenAPI và tài liệu Linux/Windows/bằng chứng/report/checklist/next-task hoàn tất.

## Vướng mắc và cách giải quyết

Đã tạo/cài backend ngoài workspace theo quyền được cấp; DNS sandbox đã xử lý bằng quyền mạng. Không có vướng mắc còn chặn bàn giao. Live A4 chưa chạy; fixture được gắn nhãn, không thay kết quả ESP32 thực.

## Phụ thuộc và điều kiện bắt đầu

Người dùng giao thực hiện kế hoạch TASK-008, chọn backend cùng cấp và repo riêng. Lưu hồ sơ TASK-007 trước chuyển trong evidence/task-008/task-007-before-task008.md. Không tự làm TASK-009.

## Kết quả và giới hạn

66 test backend/API/energy/transport, Ruff lint/format, pip check, OpenAPI10 endpoint và init DB idempotent PASS. [Bằng chứng](evidence/task-008/README.md). Backend có Git riêng/venv riêng, chưa commit/remote/push. Live A4/Windows chưa chạy; có1 deprecation warning TestClient. Chỉ hoàn thành code/test/hướng dẫn, không tuyên bố tích hợp ESP32 thực PASS.
