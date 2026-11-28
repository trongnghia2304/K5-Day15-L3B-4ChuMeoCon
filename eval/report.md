# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-010117` (gpt-4.1-mini) | **22/30** | **73%** | 11/14 | 8/11 | **3/5** | **chưa** — ≥70% đạt · 100% `tu_choi` trượt (B22, B27) · 0 vi phạm giờ đạt (23/23) |
| 2 | `run-2@20261128-111600` (gpt-4.1-mini) | **23/30** | **77%** | 10/14 | 9/11 | **4/5** | **chưa** — ≥70% đạt · 100% `tu_choi` trượt (B24) · 0 vi phạm giờ đạt (24/24) |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

8/30 câu trượt (cột `pass` = 0 trong `eval/run-1.csv`; người chấm: N2 B01–B15, N3 B16–B30, đối chiếu B01–B05 khớp 5/5). Một câu có thể thuộc 2 nhóm.

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| **A. Model tự bỏ điểm / tự nêu lý do không khớp kết quả code kiểm** — `chon_thu_tu` nhận nguyên danh sách "bỏ" và câu "Vì sao" của model, code không kiểm lại | 4 | B02, B06, B26, B27 |
| **B. Từ chối "không kịp" nhưng thiếu con số** (phút đi / km) mà `pass_criterion` đòi | 2 | B22, B27 — cả hai là `tu_choi` → làm trượt điều kiện cứng §7 |
| **C. Đọc sai yêu cầu** — model trích yêu cầu bỏ trống thành phố / khung giờ, ghi đè kết quả bộ tách bằng code | 2 | B08, B20 |
| **D. Gợi ý khi mưa chưa đòi điểm trong nhà** — lọc `rain_safe` cho qua điểm `semi_outdoor`, câu "Vì sao" lại gọi là trong nhà | 1 | B12 |

Lỗi phụ, câu vẫn đạt: "mua vé" bị đọc thành điều kiện "mưa" và bị gắn cảnh báo đặt chỗ (B17, B18); "Lăng Chủ tịch Hồ Chí Minh" làm bộ tách luật chọn nhầm thành phố HCM (N4 phát hiện khi thử web, không có trong bộ câu thử).

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B02 | "Thứ Bảy ở Hà Nội từ 07:30 đến 17:30 … ăn Phở Bát Đàn, … uống Cà phê Giảng …" | Bỏ Phở Bát Đàn ("giờ nghỉ 10:00-18:00 nên không phù hợp") và Cà phê Giảng ("không thuận đường") | Code kiểm lại: **xếp được đủ 6 điểm** (Phở lúc sáng trước 10:00). Lý do bỏ do model tự viết, không qua code (nhóm A) |
| B06 | "… Đà Lạt … 07:30 đến 18:30 … Chợ Đêm …" | Bỏ Chợ Đêm "mở sau 17:00, không kịp trong giờ đến 18:30"; lịch xong 13:00 | Code kiểm lại: **xếp được Chợ Đêm** ở cuối ngày. Lý do sai (nhóm A) |
| B26 | "12:15 trưa Thứ Tư ở Hạ Long … Bún bề bề Huy Chiên rồi vào thẳng Bảo tàng Quảng Ninh lúc 12:30 …" | Dòng bỏ điểm đúng giờ (đóng 11:30, ngưng nhận 11:00), nhưng "Vì sao": "Ăn trưa tại Bún bề bề Huy Chiên còn được" | Câu "Vì sao" của model nói ngược data — đúng loại lỗi pain chính (tới nơi thì đóng cửa) (nhóm A) |
| B22 | "14:00 ở khu Hòa Bình Đà Lạt, … Đồi Chè Cầu Đất chơi 1 tiếng rồi quay về trung tâm kịp 15:30" | "Không kịp thời gian" — không có phút đi / km | `pass_criterion` đòi con số thực tế; câu `tu_choi` trượt (nhóm B) |
| B08 | "15:10 chiều Thứ Bảy đang dạo quanh Hồ Hoàn Kiếm … mưa …" | Hỏi lại thành phố / khu | Tin nhắn đã đủ vị trí; model bỏ trống thành phố và ghi đè kết quả code (nhóm C) |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: **A + B** — model tự bỏ điểm / tự nêu lý do không khớp code, và từ chối "không kịp" thiếu con số. Vì sao đau nhất: người dùng nhận lịch thiếu điểm đáng lẽ đi được (B02, B06) hoặc lý do sai với data (B26) — đúng pain chính "tới nơi mới biết"; và B22, B27 là 2 câu `tu_choi` làm trượt điều kiện cứng §7.
- Đã sửa gì (commit `8815187`): (1) điểm model bỏ → code thử chèn lại, lịch vẫn sạch thì giữ; (2) điểm còn bỏ → lý do do code kiểm + phút đi, km, phút quay về; (3) bộ tách luật không còn nhận nhầm điểm chỉ nhờ cặp từ yếu ("bảo tàng"). Câu "Vì sao…" do model viết đã bị ẩn từ trước ở bản giọng văn H7 v3.
- **Thay đổi khác cũng có trong run-2 (không thuộc lần sửa):** B-lite (gợi ý lấp giờ trống, bật ở B01, B03, B04, B29, B30), giọng văn H7 v3, data 135 điểm (vào `main` 10:36, sớm hơn kế hoạch). Vì vậy chênh lệch run-1 → run-2 không quy hết cho lần sửa.
- Kết quả: nhóm lỗi A+B (B02, B06, B22, B26, B27) **0/5 → 3/5** đạt (B06, B22, B27 lên; B02 vẫn trượt vì Cà phê Giảng xếp sau khi đã đi Cầu Giấy; B26 vẫn trượt vì không nêu Bảo tàng Quảng Ninh nghỉ trưa 12:00–13:00) · tổng **73% → 77%** (22/30 → 23/30) · `tu_choi` 3/5 → 4/5. Cũng lên: B08 (nhóm C, không nhắm tới).
- Câu nào **tệ đi**: **B13** — data mở rộng thêm quán ở HCM, gợi ý mới không còn Phở Hòa Pasteur nên mất cảnh báo "đông" (một trong 6 câu đã báo trước có thể đổi vì data); **B24** (`tu_choi`) — bước model trích yêu cầu tự bịa 3 tên quán ("Lộc Bình", "Phố Biển", "Cảng Xưa") rồi in vào dòng "Không có dữ liệu về" — không xếp, không đặt, nhưng in tên bịa; **B10** — model chỉ chọn 1 quán, tiêu chí đòi ≥2. Không câu nào tệ đi do bước 7b.

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào:
  - **Model trích yêu cầu tự bịa tên điểm** (B24, `tu_choi`): tên bịa không được xếp hay đặt, nhưng vẫn in ra trong dòng "Không có dữ liệu về" — người dùng có thể tưởng đó là quán có thật. Nguy hiểm nhất vì đúng loại "bịa" sản phẩm hứa chặn, và là lý do run-2 trượt chuẩn §7. Cách sửa đã rõ: chỉ giữ tên điểm có thật trong nguyên văn tin nhắn.
  - **Data mới làm đổi gợi ý** (B13): thêm quán ở HCM thì Phở Hòa Pasteur (đang đông) không còn được gợi ý → mất cảnh báo. Gợi ý phụ thuộc số điểm trong data; không sửa câu thử, ghi nhận để kiểm khi thêm data.
  - **Model chọn ít gợi ý hơn yêu cầu** (B10: 1 quán, tiêu chí ≥2); **đọc sai yêu cầu** (B20 không lấy được khung 14:00–15:00); **lọc khi mưa cho qua điểm nửa ngoài trời** (B12); **thứ tự vòng** (B02: quay lại Hoàn Kiếm sau Cầu Giấy) và `thuan_duong` 1/5.
  - Sa Pa chưa có câu thử nào (11/12 thành phố).
- Nếu có thêm 1 tuần: (1) lọc tên điểm từ model theo nguyên văn tin nhắn (B24) và sửa bộ tách giờ (B20); (2) code đảm bảo đủ số gợi ý tối thiểu và lọc "trong nhà" khi mưa (B10, B12); (3) thêm tiêu chí thuận đường vào bước chọn thứ tự (B02, `thuan_duong`); (4) mở rộng data đều các thành phố, đối chiếu 2 nguồn, kèm câu thử cho Sa Pa — đo lại thành run-3.
