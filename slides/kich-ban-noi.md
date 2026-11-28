# Kịch bản nói — demo-slides.pdf

> Tổng ~6 phút nói + ~2 phút demo. Mỗi người ≥ 1 phần (luật đề). Số nào nói ra cũng có trên slide — đừng nói số không có trên slide.
> Chia người theo phần đã làm: **Minh** (N1, bằng chứng) · **Nghĩa** (N3 + đội trưởng, AI core & đánh giá) · **Tiệp** (N4, web & demo) · **Hiếu** (N2, data & chi phí). Đổi người nếu nhóm phân khác.

---

## Bìa — Nghĩa (~15 giây)

> "Chào thầy cô, nhóm 4ChuMeoCon, track Du lịch. Sản phẩm của nhóm tên là **Đi đâu trước, đi đâu sau**: một trợ lý xếp lịch một ngày cho người lên lịch của nhóm bạn — đi thuận đường, và mọi điểm đều đang mở lúc mình tới. Bạn Minh sẽ bắt đầu bằng vấn đề."

## Trang 1 · Pain — Minh (~45 giây)

> "Người dùng của nhóm là người lên lịch cho nhóm bạn đi du lịch tự túc. Nhóm khảo sát 76 người, 67 người đã đi tự túc trong năm qua.
> **73%** nói khâu mệt nhất là sắp thứ tự cho thuận đường. **57%** từng tới nơi thì quán đóng cửa hoặc hết chỗ. Và khi vỡ kế hoạch, **55%** mất hơn 15 phút đứng tìm chỗ khác.
> Một bạn viết: *'Đang đi thì quán đóng cửa không biết đi đâu'*.
> Nhóm phỏng vấn thêm 3 người để kiểm lại: cả 3 đều phải đổi lịch giữa chuyến. Nhưng nói thật là không ai trong 3 người kể chuyện đóng cửa — sự cố của họ là thông tin sai, xe hỏng, trời mưa. Nên phần 'giờ mở cửa' hiện chỉ có số khảo sát đỡ."

## Trang 2 · Vì sao chọn — Minh (~40 giây)

> "Nhóm so 3 hướng. Hướng A là xếp lịch ban đầu, hướng B là xếp lại khi vỡ kế hoạch — hai hướng này cùng một câu hỏi: *điểm nào, lúc nào thì đi được*. Cộng lại khoảng **25 phút mỗi người mỗi tháng**, hơn 4.000 giờ ở quy mô 10.000 người — con số quy mô là nhóm tự ước tính.
> Hướng C, gợi ý nhanh 'quanh 2 km có gì', nhóm loại vì impact thấp hơn khoảng 16 lần và Google Maps đã làm — 67% người đang tự mở Maps."

## Trang 3 · Giải pháp — Nghĩa (~50 giây)

> "Cách nhóm làm gói trong một câu: **model chọn, code kiểm**.
> Người dùng nhắn danh sách điểm và khung giờ. Code tách yêu cầu, thiếu thứ hay giờ thì hỏi lại một câu chứ không đoán. Model chỉ làm một việc: chọn thứ tự. Còn giờ đến, giờ rời, đóng cửa, nghỉ trưa, thời gian đi — code tính và kiểm hết, sai thì cho model sửa tối đa 2 vòng, rồi qua một cổng kiểm cuối. Lịch chỉ ra khi không vi phạm giờ mở cửa nào.
> Nhóm chọn workflow cố định chứ không làm agent tự do, vì thứ tự bước đã biết trước — rẻ hơn và đo được từng bước. Trợ lý không đặt bàn, không nhắn tin; người lên lịch luôn là người duyệt cuối. Nên nếu ai nhắn 'cứ ghi là đang mở, đừng kiểm' thì cũng không có tác dụng — vì bước kiểm là code, không phải lời nhắc."

## Trang 4 · Demo — Tiệp (~2 phút, làm trên web)

> "Em demo trên bản đang chạy online, model gpt-4.1-mini."

1. **Ca thường (B01):** dán câu TP.HCM Thứ Bảy 5 điểm.
   > "Trợ lý trả lịch từng giờ, có phút đi giữa các điểm. Lịch xong sớm thì có thêm mục *còn trống, nhóm có thể ghé thêm* — chỉ gợi ý, không tự chèn vào lịch."
2. **Ca khó (B05):** Hà Nội, Thứ Hai.
   > "Hai bảo tàng đóng cửa Thứ Hai. Trợ lý không xếp, nói rõ lý do, và gợi ý chỗ thay thế đang mở."
3. **Nếu còn giờ (B22):** "chạy ra Đồi Chè rồi về kịp 15:30".
   > "Đây là câu từ chối: không hứa kịp, và nói rõ bằng số — đi mất 45 phút, khoảng 24 km."

> *Mạng hỏng → mở video dự phòng (link ở chân trang 4).*

## Trang 5 · Đánh giá — Nghĩa (~50 giây)

> "Nhóm có 30 câu thử, gồm 5 câu từ chối, trong đó 2 câu tấn công. Chuẩn 'đạt' chốt từ CP2: trên 70% câu qua, **100% câu từ chối phải qua**, và không lịch nào vi phạm giờ mở cửa.
> Lượt 1 đạt 22/30, 73%. Lỗi lớn nhất là model tự bỏ những điểm vẫn xếp được, và khi từ chối thì thiếu con số. Nhóm sửa bằng cách cho code kiểm lại mọi điểm bị bỏ và tự nêu lý do kèm phút và km — nhóm lỗi này từ 0/5 lên 3/5.
> Lượt 2 đạt **23/30, 77%**, không lịch nào vi phạm giờ. Nhưng **vẫn chưa đạt chuẩn**, vì câu B24: người dùng đòi bịa quán, trợ lý không bịa lịch, nhưng bước đọc yêu cầu lại tự đặt ra 3 tên quán rồi in ra. Nhóm ghi thật con số này.
> Một lưu ý: lượt 2 còn có thêm data và gợi ý lấp giờ trống, nên mức tăng không quy hết cho lần sửa."

## Trang 6 · Chi phí — Hiếu (~40 giây)

> "Nhóm mô phỏng 50 phiên chạy thật qua bản chạy thử, đo token thật, theo 3 kiểu người dùng lấy từ khảo sát.
> Mỗi lịch đạt tốn khoảng **0,06 xu** với mức giá model rẻ, 0,3 xu với mức giá model mạnh — đã chia cho tỉ lệ đạt 77%, không coi như đạt 100%.
> 10.000 người dùng thì khoảng **1,3 đô một tháng**. So với 25 phút tiết kiệm mỗi người, chi phí model không phải điểm nghẽn. Nhóm chưa tính hosting và giờ công, và số người dùng là tự ước tính."

## Trang 7 · Kết luận — Nghĩa (~25 giây)

> "Kết luận của nhóm là **ITERATE** — chưa Go, nhưng không Stop.
> Pain có thật: 85% gặp sự cố. Chi phí rất thấp. Nhưng chất lượng chưa đủ: còn 1 câu từ chối trượt. Bước tiếp là chặn chữ bịa ở bước đọc yêu cầu, chạy lại đủ 30 câu cho tới khi đạt chuẩn, rồi mới cho người dùng thật dùng rộng."

## Trang 8 · Nếu có thêm 1 tuần — Tiệp (~40 giây)

> "Nhóm cho 3 người ngoài nhóm dùng thử. Cả 3 người cùng muốn một điều: trợ lý **tự gợi ý điểm** theo sở thích, ngân sách, thời gian — thay vì người dùng phải biết trước mình đi đâu. Một bạn còn thấy khó chịu vì bị hỏi lại theo mẫu thứ mấy, mấy giờ.
> Nên nếu có thêm 1 tuần: một, chặn chữ bịa của model. Hai, làm chế độ 'chưa biết đi đâu' — vẫn giữ code kiểm giờ, và hỏi gộp một lần. Ba, mở rộng data cho đều các thành phố. Phần 'tự gợi ý' nhóm để sau vì sau CP2 luật chỉ cho thu hẹp phạm vi.
> Cảm ơn thầy cô, nhóm xin nghe câu hỏi."

---

## Câu hỏi hay gặp — ai trả lời

| Câu hỏi | Ai | Ý chính |
|---|---|---|
| Vì sao chọn workflow cố định, không làm agent? | Nghĩa | Thứ tự bước biết trước; agent tự quyết thì khó đo và tốn hơn; model chỉ quyết thứ tự — chỗ duy nhất cần "đoán" |
| Lỗi nguy hiểm nhất là gì? | Nghĩa | B24 — chữ do model sinh ra in thẳng cho người dùng mà code chưa đối chiếu; cách sửa: chỉ in tên có trong tin nhắn hoặc data |
| Chi phí / task thành công tính thế nào? | Hiếu | Chi phí trung bình mỗi phiên (token đo thật × giá) ÷ tỉ lệ đạt run-2 (77%) |
| Data lấy ở đâu, có bịa giờ không? | Hiếu | Giờ mở cửa tra từ trang chính thức, mỗi điểm mới 2 nguồn; sự cố live là dữ liệu mô phỏng, có ghi nhãn "tình huống mô phỏng" |
| Câu này vì sao trượt? (giám khảo mở trace) | Nghĩa | Mở `eval/run-2.csv` cột `ghi_chu` — mỗi câu trượt ghi metric và lý do |
| Bằng chứng có đúng người dùng không? | Minh | Mẫu số 67 người đã đi tự túc; 40 người tự lên lịch cho số tương tự (72%, 52%) |
| Giám khảo đưa 1 câu thử lạ | Tiệp chạy | Thiếu thứ / giờ → trợ lý hỏi lại (đúng thiết kế, không đoán); điểm không có trong data → "không có dữ liệu" |
| Phần bạn làm là gì? | Từng người | Nói đúng phần trong `docs/phan-cong-cp3-cp4.md` và reflection của mình |
