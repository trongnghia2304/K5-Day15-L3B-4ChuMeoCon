# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-010117` (gpt-4.1-mini) | **22/30** | **73%** | 11/14 | 8/11 | **3/5** | **chưa** — ≥70% đạt · 100% `tu_choi` trượt (B22, B27) · 0 vi phạm giờ đạt (23/23) |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

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

- Nhắm vào nhóm lỗi: __ — vì sao là nhóm **đau nhất với người dùng**: __
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): __
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
