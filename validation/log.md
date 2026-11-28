# Người dùng thử *(bonus)*

> Điền ở guide bước 4.3 — 2–3 người ngoài nhóm, ~10 phút / người, theo 5 nhịp: làm quen · bối cảnh · giao việc · quan sát · hỏi sau. Ôn lại: ngày 5, ngày 13. Chấm ở rubric Bonus.
> Không ghi tên: ghi vai. Hành vi quan sát được nặng hơn lời nói; toàn lời khen = phiên chưa đạt, giao việc khó hơn.
> Người dùng thử **không thay được** bằng chứng pain ở `evidence/`.

| Người thử (vai) | Việc giao (theo kết quả, không theo nút) | Quan sát (làm gì đầu tiên, chỗ do dự, chỗ hiểu sai) | Trích nguyên văn | Mức nghiêm trọng (cao / vừa / thấp) |
|---|---|---|---|---|
| U1 · ____ *(vai — điền)* | ____ *(việc đã giao — điền)* | ____ *(làm gì đầu tiên, chỗ do dự — điền)* | "website vẫn cần cải thiện ở phần mô tả và gợi ý địa điểm" · "người dùng vẫn cần mô tả khá cụ thể những nơi mình muốn đến" · "chủ động gợi ý các địa điểm tham quan, ăn uống, vui chơi dựa trên sở thích, ngân sách và thời gian của người dùng" | **cao** — người chưa biết đi đâu thì chưa dùng được |
| U2 · ____ *(vai — điền)* | ____ | ____ | "nội dung gợi ý còn hơi sơ sài, các địa điểm chưa phong phú và đa dạng" · "cần cải thiện thêm về sự đa dạng trong đề xuất và mức độ cá nhân hóa" | **vừa** — ít điểm trong data, gợi ý lặp |
| U3 · ____ *(vai — điền)* | ____ | ____ | "hệ thống đang làm cho người dùng khó chịu khi phải trả lời theo đúng mẫu về thứ mấy? Thời gian? Địa điểm" · "Hệ thống chỉ đang sắp xếp các địa điểm chưa phải hoàn thiện AI Agent" | **cao** — bị hỏi lại nhiều lần theo mẫu, cảm giác như điền form |

Câu hỏi sau: *"Nếu mai không được dùng nữa, bạn thấy: rất tiếc / hơi tiếc / không sao?"* → __ / __ / __

## Tổng hợp

- Chủ đề lặp nhiều nhất: **3/3 người muốn trợ lý tự gợi ý điểm** (theo sở thích, ngân sách, thời gian) thay vì người dùng phải biết trước đi đâu; 2/3 thấy gợi ý chưa đa dạng (U1, U2); 1/3 khó chịu vì bị hỏi lại theo mẫu thứ / giờ / điểm (U3). Điểm được khen: lịch chi tiết kèm giờ mở / đóng cửa (U1), tương tác thân thiện, nhanh, dễ dùng (U2, U3).
- Sửa gì trước demo (ghi `spec.md` §10): **không sửa code trước demo.** Góp ý chính (tự gợi ý điểm từ sở thích / ngân sách) là **mở rộng lát cắt** — lát cắt CP2 là "người dùng đưa danh sách điểm, AI quyết thứ tự và điểm nào đang mở", luật đề chỉ cho thu hẹp sau CP2. Trên demo: dùng form web (đã có ô thứ, giờ, điểm) để đỡ phải trả lời theo mẫu; nói rõ phần gợi ý có sẵn là B-lite (lịch xong sớm) và gợi ý khi vỡ kế hoạch.
- Giữ gì và vì sao: giữ việc **hỏi lại khi thiếu thứ / giờ** — giờ mở cửa khác nhau theo thứ, đoán sai là xếp vào giờ đóng cửa (pain chính 38/67 = 57%, nguyên tắc G10); giữ giờ mở / đóng cửa trên từng dòng (U1 khen).
- Để dành sau (slide 8 "nếu có thêm 1 tuần"): (1) chế độ "chưa biết đi đâu": nhập sở thích + ngân sách + khung giờ → code lọc điểm hợp, model chọn, vẫn kiểm giờ bằng code (U1, U3); (2) mở rộng data đều các thành phố, nhiều loại điểm hơn (U2); (3) mặc định hợp lý thay vì hỏi lại từng ý (vd "hôm nay" = thứ hiện tại, khung 8h–21h) và hỏi gộp một lần (U3).
