# Data pack — Nhật ký hành vi & kịch bản hội thoại (`travel-behavior`, *synthetic*)

> Kiến trúc tương đương `data/preclass/`: lưu **nhật ký tương tác người dùng — Travel AI Agent** và bộ **48 tình huống đối chiếu** phủ đủ 7 thành phố Việt Nam và 4 nhóm bài toán cốt lõi.

---

## Nguồn gốc & Quy tắc nhãn

- **Nhãn dữ liệu:** toàn bộ hồ sơ người dùng, nhật ký sự kiện và câu thoại thử nghiệm trong thư mục này là **`synthetic`** (tổng hợp có cấu trúc, không gắn mã phiếu khảo sát giả).
- **Cảm hứng tình huống từ bằng chứng thật:** các mẫu sự cố (đổ mưa ở Thảo Cầm Viên và tham quan xong sớm ở `S25`/`S28`, quán đóng cửa đột xuất ở `S20`/`S38`, quán quá đông phải đổi chỗ ở `S16`, thời tiết nắng nóng ở Huế ở `S35`, mưa lạnh tấp vào cafe ở `S46`) lấy ý tưởng từ khảo sát 76 phản hồi thật ở `evidence/survey/results.csv` và `evidence/summary.md`. Dữ liệu tự sinh này **không dùng làm bằng chứng pain**.
- **Ẩn danh & Múi giờ:** mã người dùng chuẩn hóa `U0001`–`U0040`, chuyến đi `T0001`–`T0028`, lượt chat `C0001`–`C0048`, đánh giá `R0001`–`R0048`; múi giờ ISO-8601 `+07:00`.

## Quy mô & Độ phủ 4 nhóm kịch bản

| File | Số dòng | Một dòng là |
|---|---:|---|
| `travelers.csv` | 40 | Một hồ sơ người dùng ẩn danh (`khach`, nhóm tuổi, tần suất, vai trò nhóm, `data_origin = synthetic`) |
| `trips.csv` | 38 | Một phiên/ngày đi chơi tại 12 điểm đến (`HN`, `HP`, `QN`, `SP`, `TD`, `HG`, `HUE`, `DN`, `HA`, `NT`, `DL`, `HCM`) |
| `chat.csv` | 64 | Một lượt người dùng nhắn Travel AI Agent kèm kỳ vọng và `expected_poi_ids` / `forbidden_poi_ids` |
| `recommendations.csv` | 64 | Bản đánh giá phương án của Agent ứng với `chat.csv` (4 cờ ràng buộc + 3 điểm rubric `0–2`) |
| `events.csv` | 358 | Nhật ký sự kiện người dùng và thao tác tra cứu của Agent (`data` là JSON) |
| `disruption_events.csv` | 16 | Biến cố ngoại cảnh/thời gian thực phát sinh giữa chuyến đi |
| `completed_itineraries.csv` | 88 | Điểm dừng đã chốt/hoàn thành trong lịch trình |
| `column_dictionary.csv` | — | Từ điển chuẩn định nghĩa mọi cột và tập giá trị hợp lệ |
| `event_types.csv` | — | Danh mục loại sự kiện, nhóm, số dòng khớp thực tế và các khoá JSON trong `data` |

Phân bố **64 kịch bản trong `chat.csv`** (16 ca/nhóm):
- `multi_stop_scheduling`: **16** ca (`thuong`: 12, `kho`: 4)
- `dynamic_rescheduling`: **16** ca (`thuong`: 11, `kho`: 5)
- `context_aware_qa`: **16** ca (`thuong`: 11, `kho`: 5)
- `edge_adversarial`: **16** ca (`kho`: 6, `tu_choi`: 10)

## Nối các bảng

- `khach` -> `travelers.csv.khach`
- `trip_id` -> `trips.csv.trip_id`
- `chat.csv.id` = `recommendations.csv.ref` = `events.csv.ref_id`
- Mọi mã `POI_*` trong `current_poi_id`, `expected_poi_ids`, `forbidden_poi_ids`, `proposed_poi_ids`, `poi_id` -> `data/travel-ops/poi_master.csv.poi_id`
