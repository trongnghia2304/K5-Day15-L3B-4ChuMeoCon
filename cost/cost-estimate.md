# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): dùng ít 39/67 (58,21%), 0,125 phiên/người/tháng, 1 lượt/phiên; dùng vừa 20/67 (29,85%), 0,3333 phiên/người/tháng, 2 lượt/phiên; dùng nhiều 8/67 (11,94%), 0,5 phiên/người/tháng, 3 lượt/phiên. Nguồn: `evidence/summary.md` Câu 2; quy đổi số phiên và lượt hỏi *(tự ước tính)*.
- **Số người dùng thật** 3 kịch bản: thấp **5.000** · cơ sở **10.000** · cao **20.000** người. Nguồn: `spec.md` §2; cả ba kịch bản là *(tự ước tính)*, chưa phải số người dùng đã đo.
- **Giá** 2 mức model tham chiếu: `gemini-3.1-flash-lite` **0,25 USD/1 triệu token input · 1,50 USD/1 triệu token output**; `gemini-4-hydrogen` **1,50 USD/1 triệu token input · 7,50 USD/1 triệu token output**. Nguồn: `E:/minihackathon/K5-L3-Day15-AI-Product-Hackathon/further-reading/model-prices.csv`, [bảng giá Gemini](https://ai.google.dev/gemini-api/docs/pricing), xem 25/11/2026. Đây là hai mức giá để so sánh, không phải tên model thực chạy.
- **Tỉ lệ đạt** dùng để tính: __/__ (__%) — lượt `run-__` (lượt 2)
- Đo token trên model `gpt-4.1-mini` (theo cấu hình `.env` lúc thử mô phỏng 28/11), tính giá hai mức tham chiếu trên. Kiểm lại model trong trace của lượt mô phỏng chính trước khi chốt.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-__.csv` · run ID __ · __ phiên · seed __

*(dán bảng từ `cost/simulate-N-summary.md`)*

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): **~25,2 phút**, gồm xếp lịch ban đầu và xếp lại khi vỡ kế hoạch, tại quy mô cơ sở 10.000 người *(quy mô tự ước tính)*.
- Chi phí / người / tháng (cơ sở, model __): __
- **Kết luận một dòng — đáng làm không:** __

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
