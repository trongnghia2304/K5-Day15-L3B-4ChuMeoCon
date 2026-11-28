# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☐ *(dự kiến: review Google Maps của các điểm ăn chơi)* | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☑ 3 người (P1 trực tiếp, P2 nhắn tin, P3 trực tiếp) | [`P1`](interviews/P1.md) · [`P2`](interviews/P2.md) · [`P3`](interviews/P3.md) |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☑ n = 76, 67 người đã đi tự túc | [`evidence/survey/`](survey/questions.md) |

## 2. Số chính

Mẫu số T = 67 người đã đi du lịch tự túc trong 1 năm qua (bỏ 9 người "chưa đi lần nào"). Nhóm con P = 40 người tự lên lịch (lên lịch chính / phụ tìm quán / đi một mình). Cách đếm: [`survey/dem_khao_sat.py`](survey/dem_khao_sat.py).

| Chỉ số | T (N = 67) | P (N = 40) | Độ nhạy nếu bỏ S28 (T' = 66 · P' = 39) |
|---|---|---|---|
| Gặp ≥1 sự cố trong 3 chuyến gần nhất (Câu 6) | 57/67 (85%) | 34/40 (85%) | 56/66 (85%) · P': 33/39 (85%) |
| — Xong một điểm sớm, không biết đi tiếp đâu | 39/67 (58%) | 26/40 (65%) | 38/66 (58%) · P': 25/39 (64%) |
| — Tới nơi thì đóng cửa / hết bàn / hết vé | 38/67 (57%) | 26/40 (65%) | 37/66 (56%) · P': 25/39 (64%) |
| — Lịch trái đường / quá dày, phải bỏ dở điểm | 37/67 (55%) | 21/40 (52%) | 37/66 (56%) · P': 21/39 (54%) |
| Khâu mệt nhất: sắp thứ tự thuận đường (Câu 5) | 49/67 (73%) | 29/40 (72%) | 48/66 (73%) · P': 28/39 (72%) |
| Khâu mệt nhất: kiểm giờ mở cửa / ngày đóng cửa | 36/67 (54%) | 22/40 (55%) | 35/66 (53%) · P': 21/39 (54%) |
| Khâu mệt nhất: ước lượng thời gian chơi + di chuyển | 32/67 (48%) | 16/40 (40%) | 32/66 (48%) · P': 16/39 (41%) |
| Lên lịch mất "vài ngày" ở chuyến gần nhất (Câu 4) | 39/67 (58%) | 26/40 (65%) | 38/66 (58%) · P': 25/39 (64%) |
| Đổi kế hoạch gấp mất ≥15 phút để chốt điểm mới (Câu 9) | 37/67 (55%) | 22/40 (55%) | 36/66 (55%) · P': 21/39 (54%) |
| Mức ảnh hưởng 4–5 / 5 (Câu 7) | 25/67 (37%) | 16/40 (40%) | 25/66 (38%) · P': 16/39 (41%) |
| Đang xoay xở: lướt TikTok/Facebook/Google tìm lại (Câu 8) | 50/67 (75%) | 28/40 (70%) | 49/66 (74%) · P': 27/39 (69%) |
| Đang xoay xở: hỏi ChatGPT/Gemini | 39/67 (58%) | 21/40 (52%) | 39/66 (59%) · P': 21/39 (54%) |

Tần suất (Câu 2, N = 76): 39 người đi 1–2 lần / năm · 20 người 3–5 lần · 8 người >5 lần · 9 người chưa đi.

> **Ghi chú độ nhạy S25/S28:** Hai phiếu S25 và S28 có câu chuyện Câu 10 gần giống nhau (cùng kể đi Thảo Cầm Viên gặp mưa, xong sớm; khác Câu 7: `1` vs `2` và Câu 9: `5–15p` vs `15–30p`). Giữ nguyên toàn bộ số chính đã chốt CP2 (`N = 76`, `T = 67`, `P = 40`). Nếu gộp/bỏ S28 (`T' = 66`, `P' = 39`), mọi tỷ lệ chỉ lệch tối đa **±1–2 điểm %** và **không làm thay đổi kết luận giả thuyết** (sắp thứ tự vẫn `73% ≥ 65%`, trái đường `56% ≥ 40%`, gặp ≥1 sự cố giữ nguyên `85%`).

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Đang đi thì quán đóng cửa không biết đi đâu, tòm đụa điểm lâu nữa" — phiếu khảo sát S20
2. "đến quán thì bị đóng cửa, phải lên tiktok để kiếm quán ăn gợi ý đủ tiêu chí "ngon, bổ, rẻ"…" — phiếu S38
3. "khi đến nơi thì quán rất đông xếp hàng rất lâu nên đành phải ăn ở quán đói thủ bên cạnh" — phiếu S16
4. "khuôn viên cũng không rộng như tôi tưởng tượng nên việc tham quan kết thúc sớm hơn dự kiến" — phiếu S25
5. "gặp mưa và gió khiến cả nhóm khó khăn trong việc đến địa điểm check-in theo trong lịch trình" — phiếu S08
6. "Vì trời mưa lạnh nên cả nhóm tấp vào quán cà phê ngồi cho ngớt mưa" — phiếu S46

*(Giữ nguyên chính tả của người trả lời. S25 và S28 có nội dung Câu 10 gần giống nhau — nhóm kiểm lại có phải một người nộp hai lần không.)*

## 4. Các nguồn có khớp nhau không

Hai nguồn: khảo sát (n = 76) và phỏng vấn 3 người (P1 đi Sài Gòn 2 người · P2 đi Đà Nẵng 6 người · P3 đi Ninh Bình 12 người), hỏi **lần gần nhất** lên lịch một ngày nhiều điểm. **Một phần khớp.**

**Khớp:**
- Cả 3 đều phải đổi kế hoạch giữa chuyến và mất 30 phút đến vài tiếng: P1 30–45 phút, P2 vài tiếng, P3 45–60 phút (khảo sát Câu 9: 55% mất ≥15 phút).
- P1 và P2 nói khâu mệt nhất là sắp thứ tự / cân đối khoảng cách giữa các điểm (khảo sát Câu 5: 73%).
- Cả 3 xoay xở bằng TikTok + Google Maps; P2 và P3 còn dùng ChatGPT (khảo sát Câu 8: 75% lướt tìm lại, 58% hỏi ChatGPT).
- Tần suất 1–3 lần trong 3 chuyến gần nhất (P1 2–3, P2 1, P3 1–2).

**Lệch / ngược giả thuyết:**
- Không ai trong 3 người gặp quán đóng cửa hoặc sai giờ mở cửa. Sự cố thật: thông tin điểm sai (P1: video TikTok ghi nhầm địa điểm), xe hỏng (P2), mưa lớn (P3). Khảo sát nói 57% gặp đóng cửa / hết bàn / hết vé, nhưng phỏng vấn không xác nhận riêng lỗi giờ mở cửa.
- P2: nút thắt là chốt ý kiến cả nhóm (mỗi người một sở thích), mất vài tiếng — đúng "cách giải thích khác" số 1 trong hypothesis.md.
- P3: khâu mệt nhất là tìm villa cho 12 người, ngoài phạm vi lát cắt.
- P1 tin người quen hơn công cụ; P2, P3 đã tự xoay xở được (điểm dự phòng, lịch linh hoạt).
- Cỡ nhóm 2, 6, 12 người, không riêng 3–5 như canvas.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **đúng** — cả hai ngưỡng đã đặt trước đều đạt: sắp thứ tự thuận đường là khâu mệt nhất ở 49/67 (73%) ≥ 65%; lịch trái đường / quá dày phải bỏ dở điểm ở 37/67 (55%) ≥ 40%, và gặp đóng cửa / hết bàn / hết vé ở 38/67 (57%). Nhóm tự lên lịch (N = 40) cho số tương tự (72%, 52%). Hai chỗ chưa khớp hẳn giả thuyết: Câu 7 chỉ 25/67 (37%) chấm mức ảnh hưởng 4–5/5 (người dùng không coi là pain nặng), và "đóng cửa" gộp chung với hết bàn / hết vé nên chưa tách riêng được lỗi giờ mở cửa. Phỏng vấn 3 người kiểm lại (mục 4): khớp ở khâu sắp thứ tự / xác minh và việc đổi kế hoạch tốn 30 phút đến vài tiếng, nhưng **không xác nhận lỗi giờ mở cửa**. Sự cố thật là thông tin điểm sai, xe hỏng, thời tiết, và chốt ý kiến cả nhóm. Vì vậy giả thuyết đúng ở khâu sắp thứ tự và đổi lịch, còn phần "kiểm giờ mở cửa" chỉ có số khảo sát hỗ trợ, chưa có chuyện kể nào. Số lần mỗi chuyến: 1–3 lần trong 3 chuyến gần nhất; phút mỗi lần: 30–45 (P1), vài tiếng (P2), 45–60 (P3). Mẫu phỏng vấn nhỏ (3 người).

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| P1 · người lên lịch chuyến 2 người (Sài Gòn) · trực tiếp | 27/11 18:00 | ☑ |
| P2 · người lên lịch chuyến 6 người (Đà Nẵng) · nhắn tin | 27/11 18:05 | ☑ |
| P3 · người lên lịch chuyến 12 người (Ninh Bình) · trực tiếp | 27/11 18:35 | ☑ |
