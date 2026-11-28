# Data card — dữ liệu bản chạy thử dùng

> Bản gốc cập nhật trước CP2 (27/11/2026); mở rộng Hà Nội ngày 28/11/2026. Toàn bộ dữ liệu vận hành và hành vi được đặt trong `data/` ở định dạng CSV UTF-8, đọc trực tiếp bằng thư viện chuẩn Python và kiểm chứng tự động qua `data/validate_travel_data.py` (`0 errors`).

## Dataset 1 · `data/travel-ops/` (Nguồn sự thật điểm đến, giờ mở cửa & di chuyển Việt Nam)

| | |
|---|---|
| Dùng để làm gì | Nguồn dữ liệu nền cho các công cụ trong `codebase/tools.py` — luồng chính (`codebase/agent.py`) dùng `search_pois`, `check_opening_hours`, `lap_lich`, `liet_ke_vi_pham`, `kiem_lich_trinh` (cổng kiểm cuối), `goi_y_diem`, `get_live_disruptions` (đọc `poi_master`, `opening_hours`, `zone_travel_matrix`, `live_disruptions`); `get_travel_time`, `get_schedule_warnings` có sẵn nhưng chưa dùng trong luồng — và căn cứ kiểm chứng cho bộ câu thử `eval/benchmark.csv` |
| Từ đâu | **Phần thật (`web_verified`):** tra cứu web ngày 27/11/2026 từ nguồn công khai (trang chính thức di tích/bảo tàng/TTTM như `dinhdoclap.gov.vn`, `baotanglichsutphcm.com.vn`, `hoalo.vn`, `vme.org.vn`, `vanmieu.gov.vn`, `trangtienplaza.net`, `saigoncentre.com.vn`, `aeonmall-vietnam.com`, `43factory.coffee` và cẩm nang du lịch) cho tên quán/điểm, địa chỉ, giờ mở cửa/nghỉ trưa/ngày đóng cửa và các chặng khoảng cách chính.<br>**Phần giả lập/ước tính (`estimated` / `synthetic`):** `avg_duration_min`, `rain_penalty_min`, các chặng nội cụm/chưa có nguồn đường đi cố định ghi `source_type = estimated` *(tự ước tính)*; `live_disruptions.csv` và `edit_history.csv` là `synthetic` phục vụ kiểm thử đổi lịch thời gian thực. |
| Xử lý những bước gì | Chuẩn hoá 12 mã điểm đến (`HN`, `HP`, `QN`, `SP`, `TD`, `HG`, `HUE`, `DN`, `HA`, `NT`, `DL`, `HCM` — tập trung mạnh Miền Bắc 35 POI & Miền Trung 38 POI), tách bảng giờ mở cửa theo 7 thứ `Mon`–`Sun` (áp dụng khung giờ mùa đông từ 16/10 cho miền Bắc/Trung), gắn cờ `indoor_outdoor`, `rain_safe`, `heat_safe`, và kiểm toàn vẹn khoá ngoại bằng `data/validate_travel_data.py` |
| Số dòng / số đoạn | 121 POI (`poi_master.csv`) · 847 dòng giờ mở cửa (`opening_hours.csv`) · 153 cặp vùng di chuyển (`zone_travel_matrix.csv`) · 17 sự cố live (`live_disruptions.csv`) · 18 cảnh báo quy tắc (`schedule_warnings.csv`) · 8 lịch sử cập nhật (`edit_history.csv`) · 4 dòng ánh xạ mức giá (`price_tier_vnd.csv`, 4 cột) |
| Phiên bản / ngày lấy | v1.2 · 94 điểm gốc ngày 27/11/2026; thêm 27 điểm Hà Nội ngày 28/11/2026 |
| Nhãn | kết hợp `thật` (`web_verified` cho thông tin tĩnh POI/giờ mở cửa) + `synthetic` / *(tự ước tính)* cho sự cố live và thời lượng tham quan |
| Giới hạn | Chưa nối API Google Maps / thời tiết thời gian thực; phủ 121 điểm tại 12 tỉnh/thành nhưng đợt mở rộng chỉ thêm Hà Nội; giờ mở cửa quán ăn thực tế có thể thay đổi vào dịp lễ Tết |

**Đợt mở rộng 28/11 (HN đã vào `main` để deploy):** Thêm 27 địa điểm Hà Nội (`POI_HN_11`–`POI_HN_37`) và 189 dòng giờ, chỉ nối cuối hai CSV, giữ nguyên 94 điểm/658 dòng gốc. Mỗi điểm có hai URL trong `poi_master.csv` (`verified_source`, `notes`); giờ từng thứ ghi URL ở `opening_hours.csv.source_note`. File staging HN gốc còn trong lịch sử nhánh `data/mo-rong`; staging trên `main` do N1 dùng cho HCM. Nguồn gồm trang chính thức Vincom, Highlands Coffee, Pizza 4P's, Bảo tàng Lịch sử Quốc gia và trang đối chiếu Foody, MoMo, cẩm nang du lịch; giờ nguồn lệch được ghi trong `notes`, dùng khung giờ thận trọng hơn. `avg_duration_min`, `price_tier`, mức đông và cờ phù hợp mưa/nắng là *(tự ước tính)* để chạy thử; chưa xác minh trực tiếp tại cửa hàng. Không dùng OSM cho đợt này.

**Bảng giá phụ `data/travel-ops/price_tier_vnd.csv` (4 dòng · 4 cột):** Ánh xạ 4 mức `free`, `budget`, `mid`, `mid_high` sang khoảng VNĐ/người (`min_vnd`, `max_vnd`); cột `source` ghi *(tự ước tính)*. Bảng phục vụ hiển thị chi phí tham khảo; không chỉnh sửa `poi_master.csv`.

## Dataset 2 · `data/travel-behavior/` (Nhật ký hành vi & 64 kịch bản hội thoại Travel AI Agent)

| | |
|---|---|
| Dùng để làm gì | Thử nghiệm luồng hội thoại của Agent, kiểm thử 4 nhóm kịch bản (`multi_stop_scheduling`, `dynamic_rescheduling`, `context_aware_qa`, `edge_adversarial`) và trích chọn một phần câu thử có nguồn `sinh_seed` sang `eval/benchmark.csv` |
| Từ đâu | Nhóm tự thiết kế và sinh có cấu trúc bằng script Python dựa trên ràng buộc thật ở `data/travel-ops/` và lấy cảm hứng tình huống từ khảo sát thật `evidence/survey/results.csv` (không gắn mã phiếu khảo sát giả vào hồ sơ người dùng) |
| Xử lý những bước gì | Chuẩn hoá mã ẩn danh (`U0001`–`U0040`, `T0001`–`T0038`, `C0001`–`C0064`), viết từ điển cột (`column_dictionary.csv`) và danh mục sự kiện (`event_types.csv`), kiểm trùng lặp/JSON/khoá ngoại/độ phủ bằng `data/validate_travel_data.py` |
| Số dòng / số đoạn | 40 hồ sơ người dùng · 38 chuyến đi · 64 kịch bản hội thoại (`16` ca/nhóm) · 64 đánh giá rubric · 358 sự kiện · 16 sự cố giữa chuyến · 88 điểm dừng hoàn thành |
| Phiên bản / ngày lấy | v1.1 · cập nhật ngày 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Dữ liệu tự sinh phản ánh đúng cấu trúc bài toán và bẫy giờ/khoảng cách, **không phải bằng chứng pain** và chưa bao gồm ngôn ngữ chat nhiều lỗi chính tả/viết tắt phức tạp của người dùng thật |

**Data `synthetic` (nhóm tự sinh):** Sinh bằng script Python xác định dựa trên bảng `data/travel-ops/` (0 lỗi qua `data/validate_travel_data.py`, đối chiếu toàn bộ 64 kịch bản với giờ mở cửa và ma trận vùng). Data tự dựng **không phải bằng chứng pain**.

## Dataset 3 · `evidence/survey/results.csv` (Khảo sát người dùng du lịch tự túc)

| | |
|---|---|
| Dùng để làm gì | Đào bằng chứng pain (`evidence/summary.md`) và làm nguồn `nguoi_dung` cho các câu thử thực tế trong `eval/benchmark.csv` |
| Từ đâu | Khảo sát Google Form do nhóm thu thập ngày 27/11/2026 từ người đi du lịch tự túc |
| Xử lý những bước gì | Ẩn danh (xoá toàn bộ cột liên hệ Email/Zalo trước khi commit), lọc mẫu số `T = 67` người đã đi tự túc trong 1 năm qua (bỏ 9 người chưa đi) và nhóm con `P = 40` người tự lên lịch bằng script `evidence/survey/dem_khao_sat.py` |
| Số dòng / số đoạn | 76 phiếu (`S01`–`S76`), trong đó 67 phiếu hợp lệ cho phân tích pain |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `thật` |
| Giới hạn | Chủ yếu tập trung ở độ tuổi trẻ 18–27; phiếu `S25` và `S28` có nội dung Câu 10 gần giống nhau (nhóm đã ghi chú kiểm lại ở `evidence/summary.md`) |
