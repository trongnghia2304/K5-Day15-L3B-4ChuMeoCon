# Kịch bản quay demo MVP — web chat "Đi đâu trước, đi đâu sau"

> Người quay: N4. Dùng cho: **video 30 giây** (CP3, gửi N3) · **video demo dự phòng ~3 phút** (CP4, slide 4) · **demo live** (CP4).
> Mọi câu nhập dưới đây đã chạy thử với model thật `gpt-4.1-mini` ngày 28/11; kết quả ghi là thứ **đã thấy thật**. Lời của model (dòng "Vì sao…") mỗi lần có thể khác chữ một chút — lời thoại nói theo ý, không đọc nguyên văn màn hình.

## 0. Chuẩn bị (5 phút trước khi quay)

| Việc | Cách làm |
|---|---|
| Chạy web với model thật | `.venv\Scripts\python -m streamlit run web/streamlit_app.py` → mở `http://localhost:8501` |
| Kiểm model thật | Không thấy khung "Đang chạy chế độ thử" ở đầu trang. Có thấy → `.env` chưa có `MODEL_PROVIDER` |
| Trang sạch | Bấm **Bắt đầu lại** (thanh bên, mục Phiên này) · F5 |
| Màn hình | Cửa sổ trình duyệt 1280×720, zoom 100–110%, tắt thông báo Windows / Zalo, ẩn thanh dấu trang |
| Ghi màn hình | Win + Alt + R (Xbox Game Bar) hoặc OBS; bật mic nếu có lời thoại |
| Câu nhập | Mở sẵn file này bên cạnh, **copy–paste** câu nhập (gõ tay dễ sai dấu, mất thời gian) |
| Token | Mỗi lượt ~450–1.000 token; cả video dự phòng ~6.000 token |

**Không quay:** tên điểm ngoài dữ liệu (đang bị bỏ qua im lặng — mục 5) · tên có chữ "Hồ Chí Minh" khi đang ở Hà Nội (bộ tách đọc thành TP.HCM) · thành phố chỉ 5 điểm (Sa Pa, Hạ Long, Tam Đảo, Hà Giang, Hải Phòng) khi muốn khoe gợi ý lấp giờ trống.

---

## 1. Video 30 giây (CP3 — gửi link cho N3 trước 09:30)

Mục tiêu: 1 câu thường + 1 câu khó, thao tác thật, AI thật.

| Giây | Thao tác | Câu nhập (paste vào ô chat) | Trên màn hình phải thấy | Lời thoại (nếu có) |
|---|---|---|---|---|
| 0–3 | Trang đầu, khối xanh lime | — | "Đi đâu trước, đi đâu sau." | "Lên lịch đi chơi một ngày cho cả nhóm." |
| 3–15 | Paste, Enter | `Thứ Bảy ở TP.HCM từ 8h đến 17h30 đi xe máy: Thảo Cầm Viên, Bảo tàng Lịch sử TP.HCM, Cơm tấm Ba Ghiền, Dinh Độc Lập, Đường sách Nguyễn Văn Bình. Ngân sách 300000đ/người.` | Lịch 5 điểm từng giờ, phút đi · mục "Còn trống … có thể ghé thêm" · dòng cuối "Chi phí ước tính … (tự ước tính)" | "Trợ lý xếp thứ tự để tới đâu cũng còn mở cửa, còn trống giờ thì gợi ý thêm, kèm chi phí ước tính." |
| 15–28 | Paste, Enter | `Thứ Hai ở Hà Nội từ 8h30 đến 17h đi ô tô: Hoàng thành Thăng Long, Bảo tàng Dân tộc học, Văn Miếu, Bún chả Hương Liên` | "Không xếp được hết — đã bỏ: Hoàng thành Thăng Long: đóng cả ngày → có thể thay bằng: Di tích Nhà tù Hỏa Lò …" | "Thứ Hai hai điểm này đóng cửa — trợ lý không xếp, nói lý do và gợi ý chỗ thay." |
| 28–30 | Cuộn lên lịch | — | Lịch còn Văn Miếu + Bún chả | "Bạn duyệt rồi gửi cho nhóm." |

Sau khi quay: xem lại 1 lần, cắt đầu đuôi → mục 6.

---

## 2. Video demo dự phòng (~3 phút, CP4) — đi qua mọi tính năng

Mỗi cảnh: **thao tác → câu nhập → thứ phải thấy → tính năng chứng minh**. Quay liền một mạch, giữa các cảnh không cần bấm Bắt đầu lại (trừ khi ghi).

### Cảnh 1 · Mở đầu (0:00–0:15)
- **Thao tác:** trang sạch, chuột lướt qua khối lime, 2 câu mẫu, thanh bên.
- **Thấy:** "Đi đâu trước, đi đâu sau." · 2 câu mẫu bấm được · thanh bên "Điền nhanh", "Điểm có dữ liệu", "Phiên này: Chưa tốn token nào".
- **Lời thoại:** "Người lên lịch cho nhóm nhắn thành phố, ngày đi, khung giờ và những nơi muốn ghé. Giờ mở cửa lấy từ dữ liệu của nhóm, không lấy từ trí nhớ của AI."

### Cảnh 2 · Xếp lịch thường + ngân sách + gợi ý lấp giờ trống (0:15–0:50)
- **Câu nhập:** `Thứ Bảy ở TP.HCM từ 8h đến 17h30 đi xe máy: Thảo Cầm Viên, Bảo tàng Lịch sử TP.HCM, Cơm tấm Ba Ghiền, Dinh Độc Lập, Đường sách Nguyễn Văn Bình. Ngân sách 300000đ/người.`
- **Thấy:** 5 dòng lịch `HH:MM–HH:MM · [POI_…] Tên (đi X phút)` · "Tổng di chuyển … xong lúc …" · "Vì sao xếp như vậy" · **"Còn trống … CHƯA xếp vào lịch"** + 1–3 điểm `+ [POI_…]` · dòng cuối **"Chi phí ước tính … (tự ước tính theo mức giá) … → trong / vượt ngân sách"**.
- **Chứng minh:** model chọn thứ tự, code tính giờ và kiểm giờ mở cửa · B-lite chỉ gợi ý, không tự chèn · ngân sách chỉ hiển thị.
- **Lời thoại:** "AI chỉ chọn thứ tự. Giờ đến, phút đi, giờ mở cửa đều do code tính và kiểm. Lịch xong sớm thì trợ lý gợi ý thêm vài chỗ đang mở gần đó — nhưng không tự thêm vào lịch."

### Cảnh 3 · Thêm điểm gợi ý bằng "Sửa lịch vừa rồi" (0:50–1:10)
- **Thao tác:** mở **Sửa lịch vừa rồi** → trong ô câu, thêm tên 1 điểm vừa được gợi ý ở cảnh 2 vào danh sách điểm (trước dấu chấm, cách bằng dấu phẩy) → **Gửi lại câu này**.
- **Thấy:** lịch mới có thêm điểm đó, giờ được tính lại; "Tổng di chuyển" đổi.
- **Chứng minh:** người dùng quyết thêm gì; trợ lý xếp lại + kiểm giờ.
- **Lời thoại:** "Muốn thêm chỗ nào thì sửa thẳng câu và gửi lại."
- ⚠️ Chỉ thêm điểm **có trong danh sách gợi ý vừa hiện** (chắc chắn có dữ liệu và đang mở). Tên gợi ý mỗi lần có thể khác.

### Cảnh 4 · Chat nhiều lượt — trợ lý hỏi lại (1:10–1:35)
- **Câu nhập 1:** `Mai đi Hà Nội, muốn ghé Văn Miếu, Nhà tù Hỏa Lò, Chợ Đồng Xuân`
- **Thấy:** "Để xếp lịch không trúng giờ đóng cửa, mình cần biết thêm: đi **thứ mấy** …; **khung giờ** …"
- **Câu nhập 2:** `thứ 7, 8h đến 5h chiều`
- **Thấy:** dòng nhỏ "Trợ lý đọc thành: thứ 7, 8h đến 5h chiều. Mai đi Hà Nội, …" · lịch Hà Nội Thứ Bảy 08:00–17:00, 3 điểm, xong khoảng 11:59 · mục "Còn trống …".
- **Chứng minh:** thiếu thông tin thì hỏi lại, không đoán (G10) · web ghép câu trả lời ngắn với câu trước.
- **Lời thoại:** "Thiếu ngày hay giờ, trợ lý hỏi lại chứ không đoán. Trả lời ngắn là đủ."

### Cảnh 5 · Câu khó — điểm đóng cửa đúng hôm đi (1:35–1:55)
- **Câu nhập:** `Thứ Hai ở Hà Nội từ 8h30 đến 17h đi ô tô: Hoàng thành Thăng Long, Bảo tàng Dân tộc học, Văn Miếu, Bún chả Hương Liên`
- **Thấy:** lịch còn Văn Miếu, Bún chả Hương Liên · "Không xếp được hết — đã bỏ: … Hoàng thành Thăng Long: đóng cả ngày → có thể thay bằng: … Nhà tù Hỏa Lò, … Chợ Đồng Xuân" · tương tự Bảo tàng Dân tộc học.
- **Chứng minh:** không xếp điểm đóng cửa (metric `khong_vi_pham_gio`), nói lý do, gợi ý thay thế.
- **Lời thoại:** "Thứ Hai hai bảo tàng này nghỉ. Trợ lý bỏ ra, nói vì sao, và gợi ý chỗ thay đang mở."

### Cảnh 6 · Đang đi thì mưa (1:55–2:15)
- **Câu nhập:** `14:05 chiều Thứ Bảy đang ở Thảo Cầm Viên thì mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?`
- **Thấy:** "Điểm bạn nhắc: Thảo Cầm Viên … [Giả lập sự cố] Mưa lớn …" · "Gợi ý đang mở: Bảo tàng Lịch sử TP.HCM — đi 4 phút · trong nhà · mở đến 17:00" (có thể 1–3 gợi ý).
- **Chứng minh:** nhánh gợi ý khi vỡ kế hoạch; chỉ chọn nơi **đang mở** + trong nhà.
- **Lời thoại:** "Đang đi mà mưa, nhắn một câu là có chỗ trong nhà gần nhất còn mở." Nói rõ: sự cố mưa là **dữ liệu giả lập** để demo.

### Cảnh 7 · Yêu cầu ngoài phạm vi (2:15–2:35)
- **Câu nhập:** `Thứ Bảy ở Đà Nẵng từ 8h đến 12h: Chợ Hàn, Bảo tàng Chăm. Đặt bàn giúp mình luôn nhé`
- **Thấy:** vẫn ra lịch (Bảo tàng Điêu khắc Chăm → Chợ Hàn) · "Mình chỉ làm việc với dữ liệu có căn cứ: không đặt bàn, không nhắn tin hay thanh toán thay bạn …" · mục "Còn trống …" (vd Mì Quảng Bà Mua).
- **Chứng minh:** không có tác động ra ngoài; từ chối phần ngoài phạm vi nhưng vẫn làm phần được.
- **Lời thoại:** "Trợ lý không đặt bàn hay nhắn tin thay bạn — chỉ xếp lịch để bạn tự quyết."

### Cảnh 8 · Điền nhanh bằng form (2:35–2:55)
- **Thao tác:** thanh bên → Thành phố **Huế** → Thứ **Chủ Nhật** → Từ **08:00**, Đến **12:00** → Nơi muốn ghé: chọn 2–3 điểm trong danh sách → **Xếp lịch**.
- **Thấy:** tin nhắn dạng `Chủ Nhật ở Huế từ 08:00 đến 12:00 đi xe máy: …` + lịch.
- **Chứng minh:** không cần gõ; chỉ chọn được điểm **có dữ liệu** (danh sách "Điểm có dữ liệu" bên dưới).
- **Lời thoại:** "Không muốn gõ thì chọn từ danh sách — toàn là nơi có dữ liệu giờ mở cửa."

### Cảnh 9 · Kết (2:55–3:05)
- **Thao tác:** chỉ chuột vào thanh bên **Phiên này**.
- **Thấy:** "Đã dùng **… token** (… vào, … ra) với gpt-4.1-mini. Còn … lượt hỏi."
- **Lời thoại:** "Mỗi lượt vài trăm token với model rẻ. Người lên lịch duyệt lại rồi tự gửi cho nhóm — trợ lý không gửi tin hay đặt chỗ."

---

## 3. Demo live trên sân khấu (CP4)

- Dùng **Cảnh 2 → Cảnh 5 → Cảnh 6** (≈1 phút 30). Bấm Bắt đầu lại trước khi lên.
- 1 giờ trước: chạy thử 1 câu (README "Trước khi lên") · `.env` có trên máy demo · mạng ổn.
- **Giám khảo đưa câu lạ:** chỉ nhận câu có thành phố + thứ + khung giờ + điểm trong danh sách "Điểm có dữ liệu". Câu thiếu → trợ lý hỏi lại (đúng thiết kế, nói luôn điều đó).
- **Hỏng mạng / model lỗi** ("Không gọi được model …") → mở video dự phòng ngay, không thử lại quá 1 lần.

## 4. Bảng tính năng ↔ cảnh (để trả lời giám khảo)

| Tính năng | Cảnh | Bằng chứng trong repo |
|---|---|---|
| Xếp thứ tự, code kiểm giờ mở cửa | 2, 5 | `spec.md` §4 · `eval/run-1.csv` (22/30) |
| Gợi ý lấp giờ trống (B-lite), không tự chèn | 2, 7 | `docs/huong-b-lite.md` |
| Ngân sách chỉ hiển thị | 2 | `codebase/ngan_sach.py` |
| Hỏi lại khi thiếu (G10) + web nối tin (H1 v2) | 4 | `web/hoi_thoai.py` |
| Bỏ điểm đóng cửa + gợi ý thay thế | 5 | câu thử B05 |
| Gợi ý khi vỡ kế hoạch (mưa) | 6 | câu thử B07 |
| Từ chối đặt bàn / nhắn tin | 7 | câu thử B24 |
| Form chỉ chọn điểm có dữ liệu | 8 | `web/ghep_cau.py` |
| Tổng token phiên | 9 | `web/streamlit_app.py` |

## 5. Lỗi đã biết — không quay, báo N3

| Lỗi | Tái hiện | Hiện tượng |
|---|---|---|
| Tên điểm ngoài dữ liệu bị bỏ qua im lặng | `Thứ Bảy ở Hà Nội từ 8h đến 12h: Văn Miếu, Hồ Gươm phố đi bộ, Nhà tù Hỏa Lò` | Lịch chỉ có 2 điểm, **không** có dòng "Không có dữ liệu về: Hồ Gươm phố đi bộ". Nguyên nhân: câu đủ thông tin nên code không gọi model trích; bộ tách luật chỉ nhận tên có trong dữ liệu (`agent.py` `_rule_parse`) |
| Tên có "Hồ Chí Minh" đổi thành phố | `Thứ Bảy ở Hà Nội …: Văn Miếu, Lăng Chủ tịch Hồ Chí Minh` | Hiểu thành TP.HCM, hỏi lại "những điểm muốn đi" |

## 6. Sau khi quay

1. Cắt đầu / đuôi; video 30s ≤ 35 giây.
2. Tải lên (YouTube **không công khai** hoặc Google Drive "ai có link đều xem được").
3. **Mở link bằng cửa sổ ẩn danh** — xem được mới gửi.
4. Gửi link cho N3 (CP3) · điền vào `README.md` hàng 7 "link video" và `slides/outline.md` trang 4.
5. Không để lộ `.env`, API key, mật khẩu demo trong khung hình.
