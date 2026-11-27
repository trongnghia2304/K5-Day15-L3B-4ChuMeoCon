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

### N3 — ____

- 

### N4 — ____

- 

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
