# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | ☑ |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn + hướng bị loại | `spec.md` §2 | ☑ |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ · AI tự làm đến đâu, vì sao | `spec.md` §4 | ☑ |
| 4 | Demo live | 1 trường hợp thường + 1 trường hợp khó (lấy từ bộ câu thử); mạng hỏng → video dự phòng | `eval/benchmark.csv` | ☐ |
| 5 | **Đánh giá thế nào** | Dataset · bộ câu thử · metric · lượt 1 → lượt 2 so với chuẩn "đạt" (kèm run ID) · lỗi chính | `eval/README.md`, `eval/report.md` | ☐ |
| 6 | **Chi phí khi dùng thật** | Chi phí / task thành công · 3 kịch bản · so với impact | `cost/cost-estimate.md` | ☐ |
| 7 | Kết luận | Go / iterate / stop — dẫn số ở trang 1, 5, 6 | — | ☐ |
| 8 | Nếu có thêm 1 tuần | 2–3 việc, trỏ về lỗi còn lại / phản hồi người dùng | `eval/report.md` mục 4 · `validation/log.md` | ☐ |

---

## Nội dung chi tiết Trang 1–3 *(N1 phụ trách — chốt số từ `evidence/summary.md` và `spec.md` §2, §4)*

### Trang 1 — Người dùng & Pain
- **Người dùng chính:** Người tự lên lịch trình cho nhóm bạn đi du lịch tự túc (18–27 tuổi, đi 1–5 lần/năm; nhóm tự lên lịch/phụ tìm quán chiếm `40/67 = 60%` người đã đi, Câu 3).
- **Việc họ cố làm xong:** Sắp thứ tự và giờ đến cho nhiều điểm ăn chơi trong 1 ngày tại 1 thành phố sao cho thuận đường và đến nơi lúc đang mở cửa — hoặc đổi điểm kịp thời khi vỡ kế hoạch.
- **Số liệu bằng chứng thật** (`evidence/survey/results.csv`, n = 76, mẫu số `T = 67` người đã đi tự túc; độ nhạy bỏ S28 chỉ lệch ±1–2%, không đổi kết luận):
  - **49/67 (73%)** mệt nhất ở khâu sắp thứ tự thuận đường · **36/67 (54%)** mệt ở khâu kiểm giờ mở cửa / ngày nghỉ (Câu 5).
  - **57/67 (85%)** gặp ≥1 sự cố trong 3 chuyến gần nhất: **38/67 (57%)** gặp đóng cửa/hết chỗ · **39/67 (58%)** xong sớm không biết đi đâu · **37/67 (55%)** lịch trái đường/quá dày phải bỏ điểm (Câu 6).
  - **39/67 (58%)** mất "vài ngày" lên lịch (Câu 4); **37/67 (55%)** mất ≥15 phút chốt điểm mới khi vỡ kế hoạch (Câu 9).
  - **Phỏng vấn kiểm lại (`P1–P3`):** 3/3 người đều phải đổi lịch giữa chuyến và mất từ **30–45 phút (`P1`)**, **45–60 phút (`P3`)** đến **vài tiếng (`P2`)**; 2/3 nói khâu mệt nhất là sắp thứ tự / cân đối khoảng cách *(lệch: 0/3 gặp trực tiếp lỗi giờ mở cửa, sự cố thật là thông tin sai, xe hỏng, mưa lớn)*.
- **Trích dẫn nguyên văn:**
  - *"Đang đi thì quán đóng cửa không biết đi đâu, tòm đụa điểm lâu nữa"* — phiếu `S20`.
  - *"gặp mưa và gió khiến cả nhóm khó khăn trong việc đến địa điểm check-in theo trong lịch trình"* — phiếu `S08`.
  - *"Khâu mệt nhất là xác minh thông tin và sắp xếp thứ tự các địa điểm..."* — phỏng vấn `P1`.

### Trang 2 — Vì sao chọn bài này (Impact & Hướng bị loại)
- **Quy mô thị trường tham chiếu:** Việt Nam có ~**20–22 triệu** thanh niên 16–30 tuổi (`gso.gov.vn`) và ~**137 triệu** lượt khách nội địa năm 2025 (`vietnamtourism.gov.vn`). Quy mô cơ sở thử nghiệm: **10.000 người tự lên lịch / tháng** *(tự ước tính ≈ 0,05% thanh niên VN)*.
- **Bảng Impact rút gọn** (từ `spec.md §2`):

| Hướng | Tần suất / tháng | Thời gian / lần | Impact / tháng (10.000 người) | Quyết định |
|---|---:|---:|---:|---|
| **A. Xếp lịch ban đầu** (thuận đường + đúng giờ mở) | 0,23 *(từ Câu 2)* | 90 phút *(tự ước tính từ Câu 4 & P1–P3)* | **207.000 phút** (3.450 giờ) | **Chọn** |
| **B. Xếp lại khi vỡ kế hoạch** (mưa / đóng cửa / đông) | 0,15 *(từ Câu 2 & P1–P3)* | 30 phút *(từ Câu 9 & P1–P3)* | **45.000 phút** (750 giờ) | **Chọn** |
| C. Gợi ý nhanh chung ("quanh 2km có gì") | 0,15 | ~10 phút *(tự ước tính)* | 15.000 phút (250 giờ) | **Loại** |

- **Tổng Impact hướng chọn (A + B):** **252.000 phút / tháng** (**4.200 giờ / tháng**, ≈ **25,2 phút / người / tháng**).
- **Vì sao loại C:** Impact ròng thấp hơn **16 lần** so với A+B và trùng tính năng sẵn có của Google Maps (`67%` đã tự mở Maps, Câu 8); chỉ giữ phần lọc "đang mở + hợp thời tiết" gộp vào nhánh B.

### Trang 3 — Giải pháp (Lát cắt 1 câu · Kiến trúc · Giới hạn tự động)
- **Lát cắt 1 câu:** Người lên lịch cho nhóm nhập danh sách điểm & khung giờ (hoặc sự cố đang gặp) → AI quyết định **đi điểm nào, theo thứ tự nào** sao cho mọi điểm đều đang mở khi đến → trả lịch từng giờ hoặc 1–3 điểm thay thế kèm lý do để người dùng duyệt gửi nhóm.
- **Kiến trúc workflow cố định 2 nhánh** (khớp `spec.md §4`, dùng dữ liệu `data/travel-ops/` gồm **94 POI · 12 TP**):
  1. **Tách yêu cầu & Chặn ngoài phạm vi:** Code tách thành phố/thứ/giờ/điểm (chỉ gọi model trích JSON khi thiếu; `25/28` câu thử ở chế độ giả chỉ gọi model 1 lần), khớp mã qua `search_pois`.
  2. **Nhánh xếp lịch:** Tra `opening_hours.csv` + `zone_travel_matrix.csv` → Model chỉ chọn **thứ tự & lý do** → Code tính giờ (`lap_lich`), kiểm đủ lỗi (`liet_ke_vi_pham`, vòng sửa ≤ 2), và bắt buộc qua cổng cuối **`kiem_lich_trinh`** (còn vi phạm thì code bỏ điểm kèm lý do + gợi ý thay thế).
  3. **Nhánh gợi ý đổi điểm:** Tra `check_opening_hours` + `get_live_disruptions` → `goi_y_diem` (code) lọc ứng viên đang mở, `rain_safe`/`heat_safe` → Model chọn 1–3 điểm kèm lý do.
  4. **Ngân sách "chỉ hiển thị":** Khi người dùng có ghi ngân sách, `ngan_sach.dong_chi_phi` (`uoc_chi_phi` đọc `price_tier_vnd.csv` *(tự ước tính)*) chỉ gắn thêm 1 dòng tham khảo ở cuối, không sửa hay bỏ điểm trong lịch.
- **Mức tự động — "AI tự làm khi chắc, chuyển người khi không":** Code tính toàn bộ giờ/phút và kiểm đóng cửa nên lệnh *"bỏ qua kiểm tra"* bị vô hiệu hóa; thiếu thành phố/giờ thì hỏi lại 1 câu (**G10**); **không tự đặt bàn, mua vé, thanh toán hay nhắn tin cho nhóm** — người lên lịch luôn là người duyệt cuối.

---

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần):

| Trang | Người nói |
|---|---|
| | |
