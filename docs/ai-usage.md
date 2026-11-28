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

- **Đợt 2 (28/11):** Dùng Antigravity tra cứu 2 nguồn công khai cho 13 điểm TP.HCM vào `data/staging/` theo hợp đồng H14 (N2 duyệt lọc 7 điểm vào `data/mo-rong`), và chuẩn bị `Dockerfile`, `.dockerignore`, `railway.json` để deploy web Streamlit lên Railway (theo bàn giao từ N4); tự chạy kiểm `kiem_hop_dong.py`, `validate_travel_data.py`, `run.py check` và `web/test_ghep_cau.py`.

### N2 — Nguyễn Văn Hiếu

- Dùng Codex hỗ trợ viết hàm đọc mức giá POI, tách ngân sách trong câu và chuẩn bị cấu hình persona chi phí.
- Tự đối chiếu H2–H3 trong `docs/hop-dong-du-lieu.md`, số khảo sát Câu 2 và chạy kiểm hợp đồng; mức dùng/tháng và quy mô người dùng được ghi rõ là tự ước tính.
- Dùng Codex tìm và cấu trúc 27 địa điểm Hà Nội từ trang cửa hàng, trung tâm thương mại và nguồn đối chiếu công khai; ghi hai link mỗi điểm, đánh dấu giờ nguồn lệch, kiểm đủ 189 dòng giờ và `python scripts/kiem_hop_dong.py` 0 lỗi.
- Dùng Codex hỗ trợ đọc output `run-1` và soạn phiếu B01–B15; tự đối chiếu từng `pass_criterion` và giờ trong data, chốt 11/15 đạt trong `eval/grading-run1-hieu.csv`.
- Dùng Codex điền nháp báo cáo chi phí từ `cost/personas.yaml` và `spec.md` §2; giữ trống tỉ lệ đạt, bảng mô phỏng và kết luận cho đến khi có `run-2` đã chấm.
- Dùng Codex đối chiếu 13 điểm HCM staging của N1 với trang cụ thể; tự giữ 6 điểm có giờ/cờ không gian chưa khớp ngoài dữ liệu chạy, chỉ nối 7 điểm đủ nguồn và ghi URL, lý do trong `data/kiem-nguon-hcm.md`. Chạy lại validator và kiểm hợp đồng trước khi push.
- Dùng Codex chuyển riêng 27 điểm HN đã kiểm từ nhánh data sang `main` theo yêu cầu deploy; tự kiểm chỉ nối dòng POI/giờ, giữ HCM ở nhánh chờ và ghi lại rằng run-2 sẽ có nền dữ liệu khác run-1.
- Dùng Codex đọc run-2 và soạn phiếu B01–B15; tự đối chiếu từng `pass_criterion`, đặc biệt B02 đi vòng về Hoàn Kiếm, B10 thiếu quán thứ hai, B12 quán nửa trong nửa ngoài và B13 thiếu cảnh báo đông.
- Dùng Codex đọc file tổng hợp mô phỏng do code sinh, chép nguyên số chi phí và tỉ lệ đạt run-2 vào báo cáo; tự kiểm 50 phiên, 1 lỗi kết nối và model thật `gpt-4.1-mini`, giữ nguyên CSV/trace của lượt chạy.
- Dùng Codex kiểm link công khai của bảng giá đề và giá `gpt-4.1-mini` trên tài liệu OpenAI; tính lại dòng giá model thật từ CSV bằng đúng hàm tổng hợp của khung, giữ nguyên dữ liệu lượt mô phỏng.

### N3 — ____

- Dùng Claude Code (Opus) viết `codebase/agent.py` phần ngân sách và nhánh B-lite (`feat/b-lite`), prompt `lap_gio_trong.md`, `scripts/kiem_hop_dong.py`, `eval/cham_metric_code.py`, `docs/hop-dong-du-lieu.md`, `rule.md`, `docs/phan-cong-cp3-cp4.md`; soạn nháp phiếu chấm B16–B30 của run-1 và chấm lại B01–B05.
- Đã tự kiểm: đọc lại và duyệt từng phiếu chấm (sửa B25); B-lite so 30 câu trước / sau ở chế độ giả — chỉ thêm mục gợi ý, không đổi dòng lịch nào; script kiểm thử trên bản sao với lỗi cố tình; gộp điểm vào `run-1.csv` có so từng ô; `python scripts/kiem_hop_dong.py` 0 lỗi, `python run.py check` sạch.

### N4 — Nguyễn Nghiêm Khánh Tiệp

- Dùng Claude Code viết nháp `web/streamlit_app.py` (form → khung chat A+), `web/ghep_cau.py`, `web/hoi_thoai.py` (nối tin khi agent hỏi lại), test `web/test_ghep_cau.py`, `Procfile`, mục "Chạy web" trong `README.md`, và đề xuất `docs/huong-b-lite.md` (AI chạy 28 câu ở chế độ giả để đếm câu bị ảnh hưởng; N3 kiểm lại trên run-1 model thật).
- Đã tự kiểm: 15 test (ghép câu, agent đọc đúng câu web ở cả 12 thành phố, hỏi lại → nối tin → ra lịch, câu "xong sớm" không gợi ý lại điểm đã đi — chế độ giả); chạy thử web không trình duyệt (chat, form, sửa câu, hết lượt, sai / đúng mật khẩu) và chạy server thật bằng lệnh của `Procfile`; `python scripts/kiem_hop_dong.py` 0 lỗi, `python run.py check` sạch.
- **28/11:** Dùng Claude Code soạn nháp phiếu chấm run-2 B16–B30 (`eval/grading-run2-tiep.csv`) — AI đọc `output` từng câu đối chiếu `pass_criterion`, giữ cùng cách hiểu tiêu chí với phiếu run-1 của N3, tra trace B24; người chấm đọc lại và duyệt từng câu trước khi nộp. Sửa web cho điện thoại (ô chat không bị thanh địa chỉ che, nút gửi cùng hàng), ẩn mã `[POI_…]` khi hiển thị, ô ngân sách tự chèn dấu chấm; tự kiểm bằng 23 test web, `kiem_hop_dong` 0 lỗi và xem trên khung điện thoại 390px.

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
