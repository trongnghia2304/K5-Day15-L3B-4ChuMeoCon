# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☐ *(dự kiến: review Google Maps của các điểm ăn chơi)* | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ *(dự kiến: hẹn từ 15 người để lại liên hệ trong form)* | `evidence/interviews/P1.md`… |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☑ n = 76, 67 người đã đi tự túc *(chờ nhóm xác nhận không có thành viên trong mẫu)* | [`evidence/survey/`](survey/questions.md) |

## 2. Số chính

Mẫu số T = 67 người đã đi du lịch tự túc trong 1 năm qua (bỏ 9 người "chưa đi lần nào"). Nhóm con P = 40 người tự lên lịch (lên lịch chính / phụ tìm quán / đi một mình). Cách đếm: [`survey/dem_khao_sat.py`](survey/dem_khao_sat.py).

| Chỉ số | T (N = 67) | P (N = 40) |
|---|---|---|
| Gặp ≥1 sự cố trong 3 chuyến gần nhất (Câu 6) | 57/67 (85%) | 34/40 (85%) |
| — Xong một điểm sớm, không biết đi tiếp đâu | 39/67 (58%) | 26/40 (65%) |
| — Tới nơi thì đóng cửa / hết bàn / hết vé | 38/67 (57%) | 26/40 (65%) |
| — Lịch trái đường / quá dày, phải bỏ dở điểm | 37/67 (55%) | 21/40 (52%) |
| Khâu mệt nhất: sắp thứ tự thuận đường (Câu 5) | 49/67 (73%) | 29/40 (72%) |
| Khâu mệt nhất: kiểm giờ mở cửa / ngày đóng cửa | 36/67 (54%) | 22/40 (55%) |
| Khâu mệt nhất: ước lượng thời gian chơi + di chuyển | 32/67 (48%) | 16/40 (40%) |
| Lên lịch mất "vài ngày" ở chuyến gần nhất (Câu 4) | 39/67 (58%) | 26/40 (65%) |
| Đổi kế hoạch gấp mất ≥15 phút để chốt điểm mới (Câu 9) | 37/67 (55%) | 22/40 (55%) |
| Mức ảnh hưởng 4–5 / 5 (Câu 7) | 25/67 (37%) | 16/40 (40%) |
| Đang xoay xở: lướt TikTok/Facebook/Google tìm lại (Câu 8) | 50/67 (75%) | 28/40 (70%) |
| Đang xoay xở: hỏi ChatGPT/Gemini | 39/67 (58%) | 21/40 (52%) |

Tần suất (Câu 2, N = 76): 39 người đi 1–2 lần / năm · 20 người 3–5 lần · 8 người >5 lần · 9 người chưa đi.

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Đang đi thì quán đóng cửa không biết đi đâu, tòm đụa điểm lâu nữa" — phiếu khảo sát S20
2. "đến quán thì bị đóng cửa, phải lên tiktok để kiếm quán ăn gợi ý đủ tiêu chí "ngon, bổ, rẻ"…" — phiếu S38
3. "khi đến nơi thì quán rất đông xếp hàng rất lâu nên đành phải ăn ở quán đói thủ bên cạnh" — phiếu S16
4. "khuôn viên cũng không rộng như tôi tưởng tượng nên việc tham quan kết thúc sớm hơn dự kiến" — phiếu S25
5. "gặp mưa và gió khiến cả nhóm khó khăn trong việc đến địa điểm check-in theo trong lịch trình" — phiếu S08
6. "Vì trời mưa lạnh nên cả nhóm tấp vào quán cà phê ngồi cho ngớt mưa" — phiếu S46

*(Giữ nguyên chính tả của người trả lời. S25 và S28 có nội dung Câu 10 gần giống nhau — nhóm kiểm lại có phải một người nộp hai lần không.)*

## 4. Các nguồn có khớp nhau không

Mới có một nguồn (khảo sát). Cần nguồn thứ hai để kiểm lại: phỏng vấn 3 người trong số 15 người đã để lại liên hệ, hỏi **lần gần nhất** lên lịch một ngày nhiều điểm — mất bao lâu, sai ở đâu.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **đúng / sai / phải đổi** — vì __. Điều vẫn chưa biết: khảo sát cho biết sự cố xảy ra **ở bao nhiêu người**, chưa cho biết **mỗi chuyến bao nhiêu lần** và mất bao nhiêu phút mỗi lần (ngoài Câu 9) → hỏi thêm trong phỏng vấn.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| | | |
