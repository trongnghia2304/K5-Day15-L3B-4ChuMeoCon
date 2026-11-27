# Hợp đồng xếp lịch CP2

> **Cập nhật sau khi gộp (27/11, ~18:25):** `codebase/agent.py` hiện chạy luồng mở rộng ở `spec.md` §4
> (phân luồng xếp lịch / gợi ý thay thế, vòng sửa ≤ 2). `kiem_lich_trinh` dưới đây giữ nguyên và là
> **cổng kiểm cuối** của nhánh xếp lịch: chỉ thứ tự được `valid: true` mới hiện như lịch nháp. Vòng sửa
> dùng thêm `liet_ke_vi_pham` (liệt kê đủ lỗi, không dừng ở lỗi đầu, tính vùng xuất phát / quay về) và
> `lap_lich`; nhánh gợi ý dùng `goi_y_diem` + `get_live_disruptions`. Khi có vùng xuất phát, cổng này
> chưa tính chặng đầu nên bỏ qua, `liet_ke_vi_pham` kiểm thay. Phần "Luồng" và "Giới hạn" bên dưới là
> bản gốc của luồng CP2 trước khi gộp. Bước xếp thứ tự dùng lại cách gửi dữ liệu dạng dòng của luồng này để giữ
> số token thấp; câu rõ ràng chỉ gọi model 1 lần như bản gốc.

Nguồn dữ liệu duy nhất: `data/travel-ops/` (`poi_master.csv`, `opening_hours.csv`,
`zone_travel_matrix.csv`). Nguồn và giới hạn từng bảng ở `data/DATA_CARD.md`.
Dữ liệu sự cố trong `live_disruptions.csv` là giả lập và chưa được dùng trong
lát cắt xếp lịch trước chuyến đi.

## Luồng

`answer(text)` tìm POI được nêu rõ, lấy giờ mở cửa và thời gian di chuyển,
gọi `call_model` để chọn **thứ tự mã POI**, rồi gọi
`kiem_lich_trinh(poi_ids, visit_day, start_time, end_time, mode)`.
Model phải trả JSON `{"poi_ids": ["POI_..."]}` với đúng các mã đầu vào, mỗi mã
một lần. Model giả của CP2 dùng thứ tự người dùng nêu và ghi nhãn giả rõ ràng.

`kiem_lich_trinh` là công cụ chỉ đọc, trả `valid`, `schedule`, `issues`.
Chỉ `valid: true` mới được hiện như lịch nháp. Khi `valid: false`, `schedule`
có thể chứa đoạn đã kiểm trước lỗi; không được đưa đoạn đó như lịch hoàn chỉnh.
Code kiểm cùng thành phố, ngày đóng cửa, giờ nghỉ, giờ nhận khách cuối,
thời lượng tham quan, thời gian di chuyển và khung giờ người dùng.

Các mã lỗi: `invalid_input`, `invalid_window`, `invalid_mode`,
`missing_pois`, `duplicate_poi`, `unknown_poi`, `mixed_cities`,
`missing_hours`, `closed_day`, `missing_route`, `after_last_entry`,
`outside_opening_hours`, `outside_user_window`.

## Giới hạn

- Chỉ xếp một ngày trong một thành phố, tối đa 8 điểm được gọi đúng tên.
- Cần thứ/ngày và hai mốc giờ `HH:MM`. Nếu không nêu phương tiện thì tạm
  tính xe máy và ghi rõ giả định trong lịch nháp.
- Chưa tính thời gian từ vị trí xuất phát tới điểm đầu tiên, tắc đường,
  thời tiết thực tế, giá vé hoặc đặt chỗ.
- Việc nhận diện tên điểm từ câu tự nhiên còn giới hạn; câu có tên mơ hồ cần
  hỏi lại thay vì đoán.
- Model giả chỉ phục vụ khung CP2; không được tính là AI thật hoặc lượt eval.
