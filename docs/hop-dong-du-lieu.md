# Hợp đồng dữ liệu giữa các phần — 4ChuMeoCon

> **Đọc trước khi viết code hay giao file cho người khác** (kể cả khi nhờ AI viết). File này ghi **hình dạng** của mọi thứ đi qua ranh giới giữa 2 người: tên hàm, tham số, trường trả về, cột CSV, định dạng dòng chữ. Đầu ra của người này phải khớp đúng đầu vào người kia đang chờ.
> Phân công và mốc giờ: [`phan-cong-cp3-cp4.md`](phan-cong-cp3-cp4.md) · Luật: [`../rule.md`](../rule.md).
> **Kiểm tự động trước mỗi lần push:** `python scripts/kiem_hop_dong.py` — phải in `0 lỗi`.

Phiên bản hợp đồng: **v3 — 28/11 03:33** (nhánh `feat/b-lite`, chỉ đổi lời văn H7 — xem "H7 v3"). **v2 — 28/11 ≈02:00** (v1 ≈23:50 27/11). v2 **chỉ thêm**: H1 v2 (web chat nhiều lượt), H6 v2 (nối dòng data mới), H7 v2 (dòng B-lite), H14 (staging data). Không đổi trường nào của v1.

---

## 0. Ba luật đổi hợp đồng

1. **Không đổi tên, không xoá, không đổi kiểu** trường / cột / tham số đã ghi ở đây. Chỉ được **thêm** trường mới, và trường mới phải **tuỳ chọn** (có giá trị mặc định, người dùng cũ bỏ qua được).
2. Bắt buộc phải đổi thứ đã ghi → báo **người dùng** của hợp đồng đó (cột "Ai dùng") trước, sửa file này, tăng phiên bản (v2…), ghi 1 dòng vào khối của mình ở `spec.md` §10.
3. **Người cung cấp** chịu trách nhiệm cho đầu ra khớp hợp đồng: chạy `python scripts/kiem_hop_dong.py` trước khi push.

## 1. Bản đồ ranh giới

```
N4 web ──(H1: câu chữ)──► N3 agent.answer ──(H2)──► N2 ngan_sach.dong_chi_phi ──(H3)──► N2 tools.uoc_chi_phi ──(H4)──► data/price_tier_vnd.csv
                              │                                    
                              ├──(H5: 9 công cụ có sẵn, N2 giữ)──► data/travel-ops/*.csv (H6, đóng băng)
                              └──(H7: dòng output) ──► người dùng · code chấm metric · web hiển thị
N2 benchmark B29–B30 (H8) ─► N3 run-N.csv (H9) ◄── file chấm của mọi người (H10)
N2 cost (H11) ─► N3 spec §8 · N4 slide 6          N3 eval/README, report (H12) ─► N4 slide 5
Mọi người ─► spec.md §10 (H13)
```

| Mã | Ranh giới | Người cung cấp | Ai dùng |
|---|---|---|---|
| H1 | Câu chữ web gửi vào `agent.answer` | N4 | N3, N2 (tách ngân sách) |
| H2 | `ngan_sach.dong_chi_phi` | N2 | N3 |
| H3 | `tools.uoc_chi_phi` | N2 | N2 (`ngan_sach.py`) |
| H4 | `data/travel-ops/price_tier_vnd.csv` | N2 | N2 |
| H5 | 9 công cụ có sẵn trong `tools.py` | N2 | N3 |
| H6 | Data cũ `data/travel-ops/*.csv` | đóng băng | tất cả |
| H7 | Định dạng output của `agent.answer` | N3 | người dùng, code chấm metric, N4 |
| H8 | Dòng câu thử mới trong `benchmark.csv` | N2 | N3 |
| H9 | `eval/run-N.csv` | khung (`run.py eval`), N3 chạy | mọi người chấm |
| H10 | `eval/grading-run<N>-<ten>.csv` | người chấm | N3 |
| H11 | `cost/personas.yaml`, `cost/cost-estimate.md` | N2 | N3, N4 |
| H12 | Số liệu đánh giá | N3 | N4, N1 |
| H13 | Dòng changelog | mỗi người | lab coach |
| H14 | `data/staging/*` — điểm mới chờ kiểm (Đợt 2) | N1 | N2 |

---

## 2. Kiểu dùng chung (mọi file, mọi hàm)

| Kiểu | Định dạng đúng | Sai thường gặp |
|---|---|---|
| Mã thành phố | `HN HP QN SP TD HG HUE DN HA NT DL HCM` (12 mã, chữ hoa) | `HUẾ`, `Ho Chi Minh`, `SG` (tên tự do chỉ được dùng trong câu chữ người dùng gõ) |
| Thứ | `Mon Tue Wed Thu Fri Sat Sun` | `Monday`, `T2`, `thứ 2` |
| Giờ | `"HH:MM"` 24h, có số 0 đầu: `"08:00"`, `"20:30"` | `"8:00"`, `"8h"`, `"20h30"` |
| `poi_id` | `POI_<MÃ_TP>_<2 số>` — vd `POI_HCM_02` | tên điểm, số thứ tự |
| Phương tiện | `motorbike` · `car` · `walk` | `xe máy`, `bike` |
| Đúng / sai trong CSV | chuỗi `True` / `False` | `1/0`, `yes`, `true` |
| Tiền | số nguyên VNĐ, không dấu chấm: `300000` | `300k`, `300.000`, float |
| Phút | số nguyên | `"15 phút"` |
| CSV | UTF-8, dòng 1 là tiêu đề, phân cách `,`, ô có dấu phẩy thì bọc `"` | Excel lưu lại thành ANSI / `;` → hỏng dấu tiếng Việt |

---

## 3. Hợp đồng từng ranh giới

### H1 · Câu chữ web → `agent.answer` (N4 → N3)

Hàm (không đổi): `agent.answer(text: str) -> {"output": str}`. Web **chỉ** gửi một chuỗi; không gọi công cụ, không tự tính giờ hay tiền.

Web ghép form thành **đúng mẫu** sau (cùng kiểu câu thử B01, bộ tách luật đã đọc được):

```
{Thứ} ở {Thành phố} từ {HH:MM} đến {HH:MM} đi {phương tiện}: {điểm 1}, {điểm 2}, {điểm 3}.[ Ngân sách {số}đ/người.]
```

| Ô form | Giá trị ghép vào câu |
|---|---|
| Thứ | `Thứ Hai` … `Thứ Bảy`, `Chủ Nhật` |
| Thành phố | tên hiển thị: `Hà Nội`, `TP.HCM`, `Đà Nẵng`, `Huế`, `Hội An`, `Nha Trang`, `Đà Lạt`, `Sa Pa`, `Hải Phòng`, `Hạ Long`, `Tam Đảo`, `Hà Giang` |
| Phương tiện | `xe máy` · `ô tô` · `đi bộ` |
| Điểm | tên y như người dùng gõ / chọn, cách nhau `, ` |
| Ngân sách (tuỳ chọn) | số nguyên VNĐ, không dấu chấm: `Ngân sách 300000đ/người.` — ô trống thì **bỏ cả câu** |

Ví dụ: `Thứ Bảy ở TP.HCM từ 08:00 đến 17:30 đi xe máy: Thảo Cầm Viên, Dinh Độc Lập. Ngân sách 300000đ/người.`
Ô chat tự do: gửi nguyên văn, không ghép thêm.

**H1 v2 — web chat nhiều lượt (A+, N4):** khi **lượt trước** agent hỏi lại (trace của lượt đó có ghi chú bắt đầu bằng `hỏi lại`), web gửi `"<tin mới>. <câu đã gửi trước>"`; mọi lượt khác gửi nguyên văn. N3 **giữ nguyên tiền tố `hỏi lại`** trong `note(...)` của `agent.py` (hiện có `hỏi lại: thiếu …` và `hỏi lại (gợi ý): thiếu …`). Chỉ áp dụng ở web — `run.py eval` / `simulate` gửi từng câu độc lập.

### H2 · `ngan_sach.dong_chi_phi` (N2 → N3)

File `codebase/ngan_sach.py`. N3 gọi **sau cổng kiểm cuối**, đúng 1 lần mỗi lịch:

```python
def dong_chi_phi(text: str, poi_ids: list[str]) -> str
```

| Điều kiện | Bắt buộc |
|---|---|
| `text` | nguyên văn tin nhắn người dùng |
| `poi_ids` | các `poi_id` **đã xếp**, đúng thứ tự lịch (có thể rỗng) |
| Không tìm thấy ngân sách trong `text` | trả `""` (output cũ giữ nguyên) |
| Có ngân sách | trả **đúng 1 dòng** (không `\n`), bắt đầu bằng `Chi phí ước tính:` và có chữ `tự ước tính` |
| Không bao giờ | ném exception (poi_id lạ / rỗng → bỏ qua điểm đó), gọi model, đổi `poi_ids`, gọi mạng |
| Phải tách được | `Ngân sách 300000đ/người` (mẫu H1) · `ngân sách 300k` · `ngân sách 1tr` · `ngân sách 1,5 triệu` · `ngân sách 300.000đ` |

Mẫu dòng trả về (3 trạng thái, so `max` / `min` của khoảng với ngân sách):

```
Chi phí ước tính: 120.000–250.000đ/người (tự ước tính theo mức giá) · ngân sách bạn đưa: 300.000đ/người → trong ngân sách
Chi phí ước tính: 120.000–350.000đ/người (tự ước tính theo mức giá) · ngân sách bạn đưa: 300.000đ/người → có thể vượt ngân sách
Chi phí ước tính: 400.000–600.000đ/người (tự ước tính theo mức giá) · ngân sách bạn đưa: 300.000đ/người → vượt ngân sách
```

`max ≤ ngân sách` → trong · `min > ngân sách` → vượt · còn lại → có thể vượt. Dòng này **không** kèm lời khuyên bỏ điểm (ngân sách chỉ hiển thị).

### H3 · `tools.uoc_chi_phi` (N2 nội bộ)

```python
@tool
def uoc_chi_phi(poi_ids: list, so_nguoi: int = 1) -> dict
```

| Trường trả về | Kiểu | Ý nghĩa |
|---|---|---|
| `tong_min` | int | tổng VNĐ / người, cận dưới |
| `tong_max` | int | tổng VNĐ / người, cận trên |
| `so_nguoi` | int | như đầu vào |
| `tung_diem` | list[dict] | mỗi điểm: `poi_id`, `price_tier`, `min_vnd`, `max_vnd` |
| `khong_ro` | list[str] | `poi_id` không có trong data hoặc tier không có trong bảng giá |
| `nguon` | str | luôn `"(tự ước tính)"` |

Docstring ghi: tên · input · output · **không tác động ra ngoài**.

### H4 · `data/travel-ops/price_tier_vnd.csv` (N2, file mới)

Cột: `price_tier,min_vnd,max_vnd,source`. Đúng 4 dòng cho 4 giá trị có trong `poi_master.csv`: `free`, `budget`, `mid`, `mid_high`. `free` = `0,0`. `source` = `(tự ước tính)` hoặc link nguồn. Thêm 1 dòng vào `data/DATA_CARD.md`.

### H5 · 9 công cụ có sẵn (N2 giữ, N3 dùng) — **không đổi chữ ký, không bớt trường**

| Hàm | Tham số (đúng tên, đúng thứ tự) | Trả về — trường N3 đang đọc |
|---|---|---|
| `search_pois` | `city='', query='', category='', indoor_only=False, rain_safe_only=False, limit=10` | list: `poi_id, name, city, district, zone, address, category, indoor_outdoor, avg_duration_min(int), rain_safe(bool), heat_safe(bool), verified_source, notes` |
| `check_opening_hours` | `poi_id, day_of_week, at_time=''` | dict: `found, poi_id, day_of_week, is_open_day, open_time, close_time, break_start, break_end, last_entry_time, open_at_time, status_reason, source_note, warnings(list)` |
| `get_travel_time` | `city, from_zone, to_zone, mode='motorbike', is_raining=False` | dict: `found, city, from_zone, to_zone, note`; khi `found`: thêm `mode, distance_km, travel_min, rain_penalty_min, total_min, walk_feasible, source_type`. `zone` là mã vùng trong data (vd `HCM_Q1_CENTER`), không phải tên quận |
| `get_live_disruptions` | `city='', zone='', poi_id=''` | list: `disruption_id, city, zone, poi_id, disruption_type, severity, start_time, end_time, description, source_type` |
| `get_schedule_warnings` | `city='', poi_id=''` | list: `warning_id, severity, rule_code, city, poi_id, time_window, detail, suggested_action` |
| `lap_lich` | `city, thu_tu, day_of_week, bat_dau, mode='motorbike', start_zone=''` | list: `poi_id, name, di_chuyen_phut(int), cho_phut(int), den, roi` |
| `liet_ke_vi_pham` | `city, lich, day_of_week, bat_dau, ket_thuc, mode='motorbike', end_zone=''` | list: `poi_id, loi, chi_tiet` |
| `kiem_lich_trinh` | `poi_ids, visit_day, start_time, end_time, mode='motorbike', is_raining=False` | dict: `valid(bool), schedule(list: poi_id, name, travel_minutes_from_previous, arrival, visit_start, departure, opening_source), issues(list)` — chi tiết `docs/itinerary-tool-contract.md` |
| `goi_y_diem` | `city, day_of_week='', at_time='', from_zone='', mode='motorbike', rain_safe=False, heat_safe=False, indoor_only=False, categories=None, exclude=None, max_travel_min=40, limit=6` | list: `poi_id, name, zone, category, indoor_outdoor, di_chuyen_phut(int), dong_cua_luc, su_co` |

Hàm nội bộ N3 cũng gọi (giữ tên): `_poi`, `_hours`, `_load_csv`, `_to_min`, `_hhmm`, `_norm`, `_norm_city`, `_norm_day`, `_open_for`, `_lap_lich`, `_kiem`, `travel_min`, `zone_min`, `_CITY_ALIASES`.

**Mã lỗi `liet_ke_vi_pham.loi`** (agent coi `cho_qua_lau` là cảnh báo, còn lại là lỗi cứng — thêm mã mới thì báo N3):
`dong_cua_ca_ngay · chua_mo_cua · qua_gio_dong · qua_gio_nhan_khach · trung_gio_nghi · chong_gio · khong_du_thoi_gian_di · ngoai_khung_gio · khong_kip_quay_ve · khong_co_du_lieu · cho_qua_lau`

**Mã lỗi `kiem_lich_trinh.issues[]`** (mỗi phần tử `{code, message}`, dừng ở lỗi đầu tiên): `invalid_input · invalid_mode · invalid_window · missing_pois · duplicate_poi · unknown_poi · mixed_cities · missing_hours · missing_route · closed_day · outside_opening_hours · after_last_entry · outside_user_window`

### H6 v2 · Data — dòng cũ đóng băng, chỉ nối dòng mới (N2)

Không sửa / xoá dòng, cột đã có trong `data/travel-ops/*.csv` và `data/travel-behavior/*.csv` (`rule.md` 1.7). **Mới ở v2:** được **nối dòng vào cuối** `poi_master.csv` và `opening_hours.csv` (nhánh `data/mo-rong`, merge sau run-2 + `simulate`). Script kiểm: 94 / 658 / 153 dòng đầu y nguyên, phần thêm đúng quy định dưới.

| Quy định cho dòng mới | |
|---|---|
| `poi_id` | `POI_<TP>_<2 số>` nối tiếp số lớn nhất của thành phố đó (HN đang tới `_10`, HCM `_12`, DN `_10`, HUE `_12`, HA `_08`); không trùng |
| `city` | 1 trong 12 mã; đợt này ưu tiên `HCM DN HA` (nơi B-lite bật trong bộ câu thử) rồi `HN HUE` |
| `zone` | **vùng đã có** của thành phố đó trong `zone_travel_matrix.csv` — HN: `HN_BA_DINH HN_CAU_GIAY HN_DONG_DA HN_HAI_BA_TRUNG HN_HOAN_KIEM` · HCM: `HCM_PHU_NHUAN HCM_Q1_CENTER HCM_Q1_DAKAO HCM_Q3` · DN: `DN_HAI_CHAU DN_MY_KHE DN_NGU_HANH_SON DN_SON_TRA` · HUE: `HUE_CITADEL HUE_SOUTH_CENTER HUE_THIEN_MU HUE_TOMBS_SOUTH` · HA: `HA_AN_BANG HA_CAM_THANH HA_OLD_TOWN` · thành phố khác: xem `zone_travel_matrix.csv` |
| `category`, `indoor_outdoor`, `price_tier`, `rain_safe`, `heat_safe`, `status` | giá trị hợp lệ như dưới; `status = active` |
| `avg_duration_min` | số nguyên phút *(tự ước tính nếu nguồn không ghi)* |
| `verified_source` | link nguồn 1; `notes` có `nguồn 2: <link> · xem 28/11` |
| `opening_hours.csv` | **đúng 7 dòng** `Mon…Sun` cho mỗi điểm mới; giờ `HH:MM`; ngày nghỉ `is_open = False`; `source_note` ghi nguồn |
| Tên | không trùng / gần trùng tên điểm cũ cùng thành phố — script kiểm `tim_diem(tên cũ)` vẫn ra đúng điểm cũ |

Tiêu đề cột hiện tại (code đọc theo tên):

| File | Cột |
|---|---|
| `poi_master.csv` | `poi_id,name,city,district,zone,address,category,sub_category,indoor_outdoor,avg_duration_min,price_tier,crowd_level_typical,rain_safe,heat_safe,status,verified_source,notes` |
| `opening_hours.csv` | `poi_id,day_of_week,is_open,open_time,close_time,break_start,break_end,last_entry_time,source_note` |
| `zone_travel_matrix.csv` | `city,from_zone,to_zone,distance_km,travel_min_motorbike,travel_min_car,travel_min_walk,rain_penalty_min,source_type,note` |
| `live_disruptions.csv` | `disruption_id,city,zone,poi_id,disruption_type,severity,start_time,end_time,status,description,reported_by,source_type` |
| `schedule_warnings.csv` | `warning_id,severity,rule_code,city,poi_id,time_window,detail,suggested_action` |

Giá trị hợp lệ: `category` ∈ `attraction beach cafe food mall market museum` · `indoor_outdoor` ∈ `indoor outdoor semi_outdoor` · `price_tier` ∈ `free budget mid mid_high`.

### H7 · Output của `agent.answer` (N3 → người dùng, code chấm metric, web)

Code chấm `khong_vi_pham_gio` / `thuan_duong` (`eval/metric_spec.yaml`, đã khoá) đọc các dòng này → **N3 không đổi định dạng**; web **hiển thị nguyên văn, không tự tách dòng để xử lý**.

| Loại dòng | Định dạng |
|---|---|
| Tiêu đề lịch | `Lịch {TP} — {Thứ}, HH:MM–HH:MM[ · N người]` |
| Một điểm trong lịch | `{n}. HH:MM–HH:MM · [POI_ID] {Tên}[ (đi X phút, chờ mở cửa Y phút)]` |
| Tổng | `Tổng di chuyển: X phút · xong lúc HH:MM` |
| Lý do | `Vì sao xếp như vậy: …` (chế độ giả có `(dự phòng)`) |
| Điểm bị bỏ | `Không xếp được hết — đã bỏ:` rồi `  - [POI_ID] {Tên}: {lý do}` |
| Điểm không có dữ liệu | `Không có dữ liệu về: "…" — …` |
| Một gợi ý (nhánh gợi ý) | `{n}. [POI_ID] {Tên} — đi X phút · … · mở đến HH:MM` |
| Ngân sách (nếu có) | dòng **cuối cùng**, theo H2 |

Dấu gạch giữa hai giờ là `–` (en dash), không phải `-`.

**H7 v2 — B-lite (thêm, không đổi dòng nào ở trên)** · nằm **sau** dòng lý do / điểm bị bỏ / không có dữ liệu, **trước** `Bạn xem lại rồi tự gửi nhóm…`; dòng ngân sách vẫn cuối cùng:

| Loại dòng | Định dạng |
|---|---|
| Đầu mục | `Còn trống HH:MM–HH:MM (X phút). Có thể ghé thêm — trợ lý gợi ý, CHƯA xếp vào lịch:` |
| Một gợi ý lấp giờ | `  + [POI_ID] {Tên} — đi X phút từ điểm cuối · mở đến HH:MM · chơi khoảng Y phút` (bắt đầu bằng 2 dấu cách + `+`, **không** theo mẫu dòng lịch `{n}. HH:MM–HH:MM ·` để code chấm metric không đọc nhầm) |
| Lý do | `Vì sao gợi ý: …` (chế độ giả có `(dự phòng)`) |
| Mời thêm | `Muốn thêm điểm nào thì gửi lại câu kèm tên điểm đó — trợ lý sẽ xếp lại và kiểm giờ mở cửa.` |
| Không có ứng viên | `Còn trống HH:MM–HH:MM (X phút), dữ liệu ở {TP} chưa có điểm phù hợp để gợi ý thêm.` |

**H7 v3 — lời văn (28/11, góp ý "nhẹ nhàng, thực tế, không cứng nhắc")** · các mẫu dòng code chấm đọc **không đổi**: `Lịch {…} — {Thứ}, HH:MM–HH:MM` · `{n}. HH:MM–HH:MM · [POI_ID] …` · `Tổng di chuyển: …` · `Lúc HH:MM[ Thứ …]…` · `{n}. [POI_ID] … — đi X phút · … · mở đến HH:MM` · `  + [POI_ID] … — đi X phút từ điểm cuối · …` · `Không có dữ liệu về: …` · `Bạn xem lại rồi tự gửi nhóm…` · dòng ngân sách cuối cùng.

| Chỗ đổi | v2 | v3 |
|---|---|---|
| Tên thành phố ở tiêu đề lịch | `Lịch HN — …` | `Lịch Hà Nội — …` (tên đầy đủ) |
| Lý do do model viết | `Vì sao xếp như vậy: …` · `Vì sao: …` · `Vì sao gợi ý: …` | **Không hiện**, chỉ ghi vào trace (`note`). Khi code chọn dự phòng (chưa dùng AI) có dòng `(Chưa dùng AI ở bước này: …)` |
| Điểm bị bỏ | `Không xếp được hết — đã bỏ:` + `  - [POI_ID] Tên: lý do` | `Có điểm mình chưa xếp được:` + `  - Tên: lý do` (lý do do code kiểm, **vẫn giữ**) |
| Điểm thay thế | `có thể thay bằng: [POI_ID] Tên` | `có thể thay bằng Tên` |
| Tiêu đề nhánh gợi ý | `Lúc 14:05 Thứ Bảy · mua, xong_som` | `Lúc 14:05 Thứ Bảy — trời mưa, xong sớm.` |
| Điểm người dùng nhắc | `Điểm bạn nhắc:` + `  - [POI_ID] Tên: <status_reason>` | `Về mấy chỗ bạn nhắc:` + `  - Tên: đang mở (đến HH:MM)` / `đóng cửa cả ngày Thứ …` / `đang nghỉ giữa ca (…), mở lại lúc …` / `đã ngưng nhận khách / bán vé từ …` (đủ mốc giờ như cũ) |
| Sự cố giả lập | `· [Giả lập sự cố] …` | `Lưu ý (tình huống mô phỏng: …)` — **không được bỏ nhãn mô phỏng** (rubric R3: phần còn giả phải ghi rõ) |
| Trong / ngoài trời | `semi_outdoor` | `trong nhà` · `ngoài trời` · `nửa trong nửa ngoài` |
| Đầu mục B-lite | `… Có thể ghé thêm — trợ lý gợi ý, CHƯA xếp vào lịch:` | `… Nếu muốn, nhóm có thể ghé thêm (mình chỉ gợi ý, chưa xếp vào lịch):` · không ứng viên: `…, dữ liệu ở {Tên TP} chưa có chỗ nào hợp để gợi ý thêm.` |
| Từ chối việc ngoài phạm vi | `… (bỏ qua kiểm tra giờ mở cửa / tự bịa thông tin) …` | câu thường, không ngoặc kỹ thuật; loại yêu cầu ghi vào trace |
| Web (N4) | hiển thị nguyên văn | **được ẩn mã `[POI_ID]` khi hiển thị**; không được xoá / sửa nội dung khác |

Giữ nguyên chữ `Gợi ý đang mở` (test web cắt theo chữ này). Test web cần đổi 1 dòng (N4): `startswith("Lịch HN — Thứ Bảy, 08:00–17:00")` → `startswith("Lịch Hà Nội — Thứ Bảy, 08:00–17:00")`.

Chỉ bật khi: lịch có ≥ 1 điểm · không có điểm bị bỏ · `ket_thuc − xong lúc ≥ 60` (`NGUONG_TRONG_PHUT = 60` trong `agent.py`). Không bật ở nhánh gợi ý và câu hỏi lại.

### H8 · Dòng câu thử mới trong `eval/benchmark.csv` (N2 → N3)

| Cột | Quy định |
|---|---|
| `id` | `B29`, `B30` — nối tiếp, không trùng |
| `input` | câu chữ như người dùng gõ (nên theo mẫu H1) |
| `expected` | hành vi đúng, cụ thể (điểm nào, giờ nào, dòng chi phí nào) |
| `pass_criterion` | **kiểm được** bằng cách đọc output (vd "có dòng `Chi phí ước tính:` chứa `vượt ngân sách`; lịch giữ đủ 3 điểm; không có số tiền ngoài dòng đó") |
| `type` | `thuong` · `kho` · `tu_choi` |
| `source` | bắt đầu bằng `nguoi_dung:` · `data_that:` · `tu_viet:` · `sinh_seed:` rồi ghi chi tiết |

Chỉ thêm ở cuối, trước 00:30. Không đụng B01–B28 (script kiểm từng dòng).

### H9 · `eval/run-N.csv` (khung tạo — chỉ N3 chạy)

Cột (do `eval/run_eval.py` sinh, không sửa): `run_id,id,type,input,expected,pass_criterion,output,pass,ghi_chu,model,model_calls,tool_calls,tokens_in,tokens_out,latency_s,error`. Chỉ N3 điền `pass`, `ghi_chu` sau khi gộp H10.

### H10 · File chấm `eval/grading-run<N>-<ten>.csv` (người chấm → N3)

| Cột | Quy định |
|---|---|
| `id` | mã câu thử có trong `run-N.csv` |
| `pass` | `1` hoặc `0` (không để trống khi đã nhận chấm câu đó) |
| `ghi_chu` | trượt thì ghi **metric trượt** (`khong_vi_pham_gio` / `khong_bia_diem` / `dung_hanh_vi` / `thuan_duong`) + 1 câu lý do; đạt thì có thể để trống |

Tiêu đề đúng `id,pass,ghi_chu`. `<ten>` viết không dấu, liền (vd `grading-run1-hieu.csv`). Câu chấm chồng (B01–B05) N3 so 2 file; lệch thì bàn, không tự sửa của người kia.

### H11 · Chi phí (N2 → N3 §8, N4 slide 6)

- `cost/personas.yaml`: đúng khung `cost/simulate.py` đọc — `sessions` (≥50) · `seed` · `users{low, base, high, source}` · `personas[]{name, share, uses_per_month, turns_per_session, source}` (tổng `share` = 1) · `prices[]{model, input, output, source}` (USD / 1 triệu token, ≥2 model) · `usd_to_vnd{rate, source}`.
- `cost/cost-estimate.md` phải có đủ các số sau, **ghi đúng nhãn** để N3, N4 chép:

| Nhãn | Ví dụ |
|---|---|
| `Lượt mô phỏng:` | `cost/simulate-1.csv (50 phiên, seed 42)` |
| `Tỉ lệ đạt dùng để chia:` | `run-2: 21/30 (70%)` |
| `Chi phí / phiên (cơ sở):` | theo từng model |
| `Chi phí / task thành công (cơ sở):` | theo từng model, kèm tên model |
| Bảng 3 kịch bản | cột `Kịch bản · Số người dùng · Chi phí / tháng (model rẻ) · Chi phí / tháng (model mạnh)` |
| `Kết luận:` | 1 câu: đáng làm không, so với impact `spec.md` §2 |

### H12 · Số liệu đánh giá (N3 → N4, N1)

N3 ghi ở `eval/README.md` mục 5 (bảng có sẵn) và dòng kết quả `spec.md` §7: `run ID · model · đạt / tổng · % · đạt chuẩn?`. `eval/report.md` có mục `Lỗi chính` liệt kê ≥3 lỗi dạng `B.. · input · output · vì sao sai · đã sửa / chưa`. Slide chép số từ đây, không tự tính lại.

### H13 · Dòng changelog `spec.md` §10

Chỉ thêm vào **khối của mình**: `| HH:MM DD/MM | Đổi gì (file, hàm) | Vì sao (câu thử / lỗi / bằng chứng) |`.

### H14 · `data/staging/` — điểm mới chờ kiểm (N1 → N2, Đợt 2)

Code **không đọc** thư mục này. N1 thu thập, N2 kiểm nguồn thứ 2 rồi chép sang `data/travel-ops/` theo H6 v2 (gán `poi_id` thật).

| File | Cột |
|---|---|
| `data/staging/poi_moi.csv` | **đúng cột `poi_master.csv`** + `nguon_2,ngay_xem,nguoi_thu` |
| `data/staging/gio_mo_moi.csv` | **đúng cột `opening_hours.csv`** + `nguon` |

- `poi_id` tạm: `MOI_<TP>_<2 số>` (vd `MOI_HN_01`); `gio_mo_moi.csv` dùng đúng mã tạm này, **7 dòng `Mon…Sun` / điểm**.
- `zone`, `category`, `indoor_outdoor`, `price_tier`, `rain_safe`, `heat_safe` theo H6 v2. Chưa chắc vùng → để trống, N2 gán.
- `verified_source` = nguồn 1, `nguon_2` = nguồn 2 (đều là link đã mở xem); `ngay_xem` = `28/11`; `nguoi_thu` = `N1`.
- Giờ mở cửa **chép từ nguồn**, không để AI điền; nguồn không ghi giờ → bỏ điểm đó. Không ghi tên người review, số điện thoại cá nhân.
- Ưu tiên (để B-lite và câu mưa có ứng viên): `cafe`, `food`, điểm `indoor`, nơi mở tới tối; ở vùng gần các điểm đang có.

---

## 4. Kiểm trước khi push

```
python scripts/kiem_hop_dong.py
```

Script kiểm: dòng data cũ không đổi, dòng nối thêm đúng H6 v2 (vùng có sẵn, 7 dòng giờ mở, có nguồn, không cướp tên điểm cũ) · `data/staging/` đúng H14 · dòng B-lite đúng H7 v2 (nếu có) · B01–B28 không đổi, B29+ đúng cột (H8) · 9 công cụ đúng chữ ký và đủ trường (H5) · `price_tier_vnd.csv` (H4) · `uoc_chi_phi` (H3) · `dong_chi_phi` (H2) · output agent đúng định dạng dòng (H7) · file chấm (H10). Phần nào chưa có file thì báo "chưa có", không tính lỗi.
