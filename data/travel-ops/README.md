# Data pack — Vận hành điểm đến & nguồn sự thật lịch trình (`travel-ops`)

> Kiến trúc tương đương `data/training-ops/`: chứa **nguồn sự thật vận hành (Operational Ground-Truth)** để Travel AI Agent và các công cụ trong `codebase/tools.py` tra cứu khi xếp lịch đa điểm và đổi lịch theo thời gian thực.

---

## Nguồn gốc & Phân tách Thật / Giả lập

- **Dữ liệu địa điểm thực tế đã tra cứu web (27–28/11/2026):** Tên địa điểm, địa chỉ cụ thể, giờ mở cửa/đóng cửa, ca bán, giờ nghỉ trưa, ngày đóng cửa trong tuần (`Mon`..`Sun`), và các chặng khoảng cách chính trong `poi_master.csv`, `opening_hours.csv`, `zone_travel_matrix.csv` (dòng `source_type = web_verified`) đều được đối chiếu từ nguồn công khai (trang chính thức di tích/bảo tàng/TTTM và cẩm nang du lịch). Mỗi POI đều ghi nguồn ở cột `verified_source`; 27 điểm Hà Nội và 7 điểm HCM thêm ngày 28/11 có nguồn thứ hai trong `notes` và `data/kiem-nguon-hcm.md`.
- **Dữ liệu giả lập / tự ước tính (`synthetic` / `estimated`):**
  - `avg_duration_min`, `rain_penalty_min`, và một số chặng di chuyển nội/liên cụm ghi `source_type = estimated` là *(tự ước tính)* phục vụ tính lịch trình thử nghiệm.
  - `live_disruptions.csv` và `edit_history.csv` là `synthetic` (mô phỏng các tình huống mưa lớn, hết hàng sớm, quá tải, nắng gắt để test chức năng đổi lịch thời gian thực).
- **Thuần Python stdlib:** toàn bộ bảng đều ở định dạng CSV UTF-8, đọc trực tiếp bằng module `csv` chuẩn của Python 3.10+.

## Quy mô dữ liệu

| Thành phần | Quy mô | Chi tiết |
|---|---:|---|
| Thành phố phủ sóng | 12 | Miền Bắc: `HN`, `HP`, `QN`, `SP`, `TD`, `HG` · Miền Trung: `HUE`, `DN`, `HA`, `NT` · Tây Nguyên & Nam: `DL`, `HCM` |
| Địa điểm (`poi_master.csv`) | 135 POI | Miền Bắc 65 (`HN` 40, `HP` 5, `QN` 5, `SP` 5, `TD` 5, `HG` 5) · Miền Trung 38 (`HUE` 12, `DN` 10, `HA` 8, `NT` 8) · Tây Nguyên & Nam 32 (`DL` 9, `HCM` 23) |
| Lịch mở cửa (`opening_hours.csv`) | 945 dòng | Đủ 7 thứ `Mon`..`Sun` cho từng POI (135 × 7); các điểm HN/HCM mới ghi nguồn 2 trong `notes` và `data/kiem-nguon-hcm.md` |
| Ma trận di chuyển (`zone_travel_matrix.csv`) | 153 cặp vùng | Có cột `source_type` phân biệt `web_verified` và `estimated` |
| Sự cố live (`live_disruptions.csv`) | 17 dòng | `synthetic` — mô phỏng sự cố mưa, sương mù, nắng gắt, quá tải, đóng cửa đột xuất |
| Cảnh báo quy tắc (`schedule_warnings.csv`) | 18 dòng | Quy tắc chặn ảo giác (đóng cửa Thứ Hai, bán 2 ca, chỉ bán sáng, cutoff vé/thuyền, khoảng cách xa) |
| Lịch sử cập nhật (`edit_history.csv`) | 8 dòng | Nhật ký rà soát & đối chiếu dữ liệu |

## Các file

| File | Một dòng là | Các cột chính |
|---|---|---|
| `poi_master.csv` | Một địa điểm tham quan / ăn uống / cafe / TTTM | `poi_id`, `name`, `city`, `district`, `zone`, `address`, `category`, `sub_category`, `indoor_outdoor`, `avg_duration_min`, `price_tier`, `crowd_level_typical`, `rain_safe`, `heat_safe`, `status`, `verified_source`, `notes` |
| `opening_hours.csv` | Giờ mở cửa của 1 POI vào 1 thứ | `poi_id`, `day_of_week`, `is_open`, `open_time`, `close_time`, `break_start`, `break_end`, `last_entry_time`, `source_note` |
| `zone_travel_matrix.csv` | Chi phí di chuyển giữa 2 vùng cùng thành phố | `city`, `from_zone`, `to_zone`, `distance_km`, `travel_min_motorbike`, `travel_min_car`, `travel_min_walk`, `rain_penalty_min`, `source_type`, `note` |
| `live_disruptions.csv` | Một sự cố thời gian thực giả lập | `disruption_id`, `city`, `zone`, `poi_id`, `disruption_type`, `severity`, `start_time`, `end_time`, `status`, `description`, `reported_by`, `source_type` |
| `schedule_warnings.csv` | Một cảnh báo rà soát lịch trình | `warning_id`, `severity`, `rule_code`, `city`, `poi_id`, `time_window`, `detail`, `suggested_action` |
| `edit_history.csv` | Một lần cập nhật dữ liệu vận hành | `edited_at`, `editor`, `table_name`, `record_id`, `field_changed`, `old_value`, `new_value`, `reason` |

## Nối các bảng

- `opening_hours.csv.poi_id` -> `poi_master.csv.poi_id`
- `zone_travel_matrix.(city, from_zone/to_zone)` -> `poi_master.(city, zone)`
- `live_disruptions.poi_id` -> `poi_master.poi_id`
- `schedule_warnings.poi_id` -> `poi_master.poi_id`
