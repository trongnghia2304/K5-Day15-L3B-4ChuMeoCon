# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | | | | |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | | | Kiểm tay __ dòng, khớp __ | |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | | | | |

## Khai theo từng người

> Mỗi người chỉ sửa khối của mình (2–3 dòng: dùng AI vào việc gì · đã tự kiểm / sửa gì). Phân công: `docs/phan-cong-cp3-cp4.md`.

### N1 — Nguyễn Trọng Nghĩa

- **Công cụ AI đã dùng:** Antigravity (hỗ trợ kiểm tra read-only cấu trúc `data/`, tạo `data/travel-ops/price_tier_vnd.csv` + cập nhật `data/DATA_CARD.md`, viết script tính độ nhạy S25/S28 trên `evidence/survey/results.csv`, tra cứu nguồn công khai `gso.gov.vn` / `vietnamtourism.gov.vn` để điền bảng Impact ở `spec.md §2`, và soạn nội dung Trang 1–3 trong `slides/outline.md`).
- **Người tự kiểm & đối chiếu:** Đã đối chiếu trực tiếp kết quả tính độ nhạy S25/S28 với `evidence/survey/results.csv` và giữ nguyên 100% số liệu gốc đã nộp CP2; kiểm tra lại toàn bộ phép tính Impact và gắn nhãn *(tự ước tính)* cho mọi thừa số không có nguồn trực tiếp; chạy `python data/validate_travel_data.py` (`0 errors`), `python run.py check` (`Không thấy vấn đề`) và kiểm `git diff` xác nhận không sửa các mục đã khoá (§3–§9, B01–B28, khối N2–N4).

### N2 — Nguyễn Văn Hiếu

- Dùng Codex hỗ trợ viết hàm đọc mức giá POI, tách ngân sách trong câu và chuẩn bị cấu hình persona chi phí.
- Tự đối chiếu H2–H3 trong `docs/hop-dong-du-lieu.md`, số khảo sát Câu 2 và chạy kiểm hợp đồng; mức dùng/tháng và quy mô người dùng được ghi rõ là tự ước tính.
- Dùng Codex tìm và cấu trúc 27 địa điểm Hà Nội từ trang cửa hàng, trung tâm thương mại và nguồn đối chiếu công khai; ghi hai link mỗi điểm, đánh dấu giờ nguồn lệch, kiểm đủ 189 dòng giờ và `python scripts/kiem_hop_dong.py` 0 lỗi.
- Dùng Codex hỗ trợ đọc output `run-1` và soạn phiếu B01–B15; tự đối chiếu từng `pass_criterion` và giờ trong data, chốt 11/15 đạt trong `eval/grading-run1-hieu.csv`.

### N3 — ____

- 

### N4 — Nguyễn Nghiêm Khánh Tiệp

- Dùng Claude Code viết nháp `web/streamlit_app.py` (form → khung chat A+), `web/ghep_cau.py`, `web/hoi_thoai.py` (nối tin khi agent hỏi lại), test `web/test_ghep_cau.py`, `Procfile`, mục "Chạy web" trong `README.md`, và đề xuất `docs/huong-b-lite.md` (AI chạy 28 câu ở chế độ giả để đếm câu bị ảnh hưởng; N3 kiểm lại trên run-1 model thật).
- Đã tự kiểm: 15 test (ghép câu, agent đọc đúng câu web ở cả 12 thành phố, hỏi lại → nối tin → ra lịch, câu "xong sớm" không gợi ý lại điểm đã đi — chế độ giả); chạy thử web không trình duyệt (chat, form, sửa câu, hết lượt, sai / đúng mật khẩu) và chạy server thật bằng lệnh của `Procfile`; `python scripts/kiem_hop_dong.py` 0 lỗi, `python run.py check` sạch.

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
