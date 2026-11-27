# Canvas — 4ChuMeoCon · Track C

> Điền ở guide bước 1.4. CP1 17:00 Thứ Sáu 27/11: nộp bản đầu, đủ 7 dòng (dòng 4 được ghi giả thuyết + nguồn sẽ kiểm).
> CP2 19:30 Thứ Sáu 27/11: cập nhật (số bằng chứng đầu, lát cắt đã chốt) và điền dòng "Đã đổi gì so với CP1".
> Track F: chép thêm thẻ đề của nhóm (khung trong file track F) xuống dưới bảng này.

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | **Track C · Du lịch.** Xếp lịch trình một ngày cho chuyến du lịch tự túc nhiều điểm ăn chơi trong một thành phố: sắp thứ tự thuận đường, khớp giờ mở cửa. |
| 2 | Người dùng chính (một vai cụ thể — không phải "học viên nói chung") | Người **lên lịch trình chính cho nhóm bạn 3–5 người** đi du lịch tự túc (18–27 tuổi, đi 1–5 lần / năm), tự tìm điểm qua TikTok, Google Maps rồi chốt lịch cho cả nhóm. |
| 3 | Pain một câu: ai — đang làm gì — vướng đâu — hậu quả | Người lên lịch cho nhóm khi đi du lịch tự túc phải **tự sắp thứ tự nhiều điểm ăn chơi trong một ngày và tự kiểm giờ mở cửa từng nơi**, mất vài ngày lướt tìm mà vẫn xếp trái đường, tới nơi gặp quán đóng cửa → cả nhóm phải bỏ dở điểm và đứng 15–30 phút tìm chỗ thay thế. |
| 4 | Bằng chứng đầu — CP1: giả thuyết + nguồn sẽ kiểm · CP2: số đầu tiên + 1 trích dẫn | **Giả thuyết:** người lên lịch tốn nhiều thời gian nhất ở khâu sắp thứ tự và kiểm giờ mở cửa, và lịch tự xếp vẫn hay trái đường / gặp đóng cửa. **Nguồn:** khảo sát Google Form (nguồn chính, đã thu 76 phiếu) · phỏng vấn ≥3 người trong số người để lại liên hệ (kiểm lại). **Số đầu:** 49/67 (73%) người đã đi tự túc thấy mệt nhất ở khâu sắp thứ tự thuận đường; 37/67 (55%) từng có lịch trái đường / quá dày phải bỏ dở điểm. *"Đang đi thì quán đóng cửa không biết đi đâu, tòm đụa điểm lâu nữa"* — phiếu S20. Chi tiết: [evidence/summary.md](evidence/summary.md) |
| 5 | **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả) | Một người lên lịch cho nhóm · nhập danh sách điểm muốn đi, ngày đi và khung giờ trong ngày · AI quyết định thứ tự và giờ đến từng điểm sao cho thuận đường và không rơi vào giờ đóng cửa, hoặc nói rõ không xếp được và gợi ý bỏ / dời điểm nào · người lên lịch nhận lịch từng giờ kèm lý do chọn thứ tự để gửi cả nhóm. |
| 6 | AI tự làm đến đâu + 1 dòng lý do: sai thì ai chịu gì | **AI tự xếp và đề xuất, người lên lịch duyệt trước khi gửi nhóm.** AI không đặt chỗ, không gửi tin cho ai. Giờ mở cửa và thời gian di chuyển chỉ lấy từ công cụ, lịch được code kiểm (0 vi phạm) trước khi trả; thiếu dữ liệu giờ mở cửa thì báo rõ, không đoán. Lý do: sai thì cả nhóm tới nơi gặp đóng cửa, mất 15–30 phút và bỏ dở điểm — đắt vừa, nhưng người lên lịch tự xem và sửa được trước ngày đi. |
| 7 | Phân công có tên | **Cặp X (bản chạy thử):** Nguyễn Nghiêm Khánh Tiệp + Nguyễn Văn Hiếu — công cụ dữ liệu điểm / giờ mở cửa, luồng xếp lịch + code kiểm lịch. **Cặp Y (bằng chứng + đánh giá):** Nguyễn Trọng Nghĩa + Nguyễn Đức Minh — phỏng vấn 3 người, bảng impact, bộ câu thử + metric spec. Đội trưởng Nguyễn Trọng Nghĩa giữ mạch câu chuyện và nộp checkpoint. |
| — | *(CP2)* Đã đổi gì so với CP1 | |

## Nộp CP1 — bài toán 1–2 câu (không có chữ AI)

> Người lên lịch cho nhóm bạn khi đi du lịch tự túc phải tự sắp thứ tự nhiều điểm ăn chơi trong một ngày và tự kiểm giờ mở cửa từng nơi. Họ mất vài ngày lướt tìm mà lịch vẫn hay trái đường hoặc tới nơi gặp đóng cửa, khiến cả nhóm bỏ dở điểm và mất 15–30 phút đứng tìm chỗ thay thế.

**Lát cắt dự kiến (1 câu):** Một người lên lịch cho nhóm nhập danh sách điểm và khung giờ, AI quyết định thứ tự và giờ đến từng điểm để thuận đường và không rơi vào giờ đóng cửa (hoặc nói rõ không xếp được), người lên lịch nhận lịch từng giờ kèm lý do để gửi cả nhóm.
