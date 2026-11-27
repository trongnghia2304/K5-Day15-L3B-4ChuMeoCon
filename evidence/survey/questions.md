# Khảo sát — bộ câu hỏi và cách thu

- **Công cụ:** Google Form
- **Kênh gửi:** bạn bè, người quen của thành viên nhóm *(nhóm ghi rõ kênh cụ thể: nhóm Zalo / Facebook / Discord nào)*
- **Phiếu đầu → phiếu cuối:** 27/11/2026 11:41 → 27/11/2026 16:30
- **Số phiếu:** 76 · đã đi du lịch tự túc trong 1 năm qua: 67
- **Kết quả:** [results.csv](results.csv) — đã xoá cột liên hệ (Email / Zalo), thêm mã phiếu `S01…S76`. Bản gốc không commit.
- **Cách đếm:** [dem_khao_sat.py](dem_khao_sat.py) (chạy lại: `python evidence/survey/dem_khao_sat.py`)
- **Người trong nhóm có trả lời không:** ____ *(nhóm xác nhận; nếu có thì ghi mã phiếu để loại)*

## Câu hỏi

| # | Câu hỏi | Kiểu | Dùng làm bằng chứng? |
|---|---|---|---|
| 1 | Độ tuổi của bạn? | Chọn một | Mô tả mẫu |
| 2 | Trong 1 năm qua, bạn đi du lịch tự túc bao nhiêu lần? | Chọn một | Lọc mẫu số + tần suất cho chi phí |
| 3 | Khi đi cùng bạn bè / người thân, bạn thường giữ vai trò gì? | Chọn một | Lọc người dùng chính |
| 4 | Ở chuyến tự túc gần nhất, bạn mất bao lâu để lên xong lịch trình? | Chọn một | Có (hành vi đã xảy ra) |
| 5 | Khi xếp nhiều điểm trong 1 ngày, khâu nào mệt / tốn thời gian nhất? (tối đa 3) | Chọn nhiều | Có |
| 6 | Trong 3 chuyến gần nhất, bạn đã gặp sự cố nào? | Chọn nhiều | Có (hành vi đã xảy ra) |
| 7 | Mức ảnh hưởng của các sự cố đó (1–5)? | Thang 1–5 | Có |
| 8 | Gặp tình huống ngoài ý muốn thì bạn thường xử lý thế nào? | Chọn nhiều | Có (cách đang xoay xở) |
| 9 | Đổi kế hoạch gấp tại điểm đến thì mất bao lâu để chốt điểm mới? | Chọn một | Có (thời gian mất → impact) |
| 10 | Kể 1 lần gần nhất bị "vỡ kế hoạch" và cách xoay xở | Đoạn văn | Có (trích dẫn nguyên văn) |
| 11 | Nếu có "Hướng dẫn viên AI", tính năng nào đúng vấn đề nhất? (tối đa 2) | Chọn nhiều | **Không** — câu giả định |
| 12 | Có sẵn sàng dùng thử miễn phí không? | Chọn một | **Không** — câu giả định |
| — | Để lại Email / Zalo nếu muốn trò chuyện thêm | Ngắn | Đã xoá khỏi bản commit |

## Giới hạn

- Mẫu là bạn bè, người quen của nhóm (không ngẫu nhiên), 58/76 người 18–27 tuổi.
- Câu 6 hỏi "3 chuyến gần nhất", không giới hạn 1 tháng.
- Câu 5, 6, 8 là chọn nhiều nên các % không cộng thành 100%.
- Câu 11, 12 hỏi về giải pháp tương lai — chỉ để tham khảo, không tính là bằng chứng pain.
