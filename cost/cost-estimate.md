# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): dùng ít 39/67 (58,21%), 0,125 phiên/người/tháng, 1 lượt/phiên; dùng vừa 20/67 (29,85%), 0,3333 phiên/người/tháng, 2 lượt/phiên; dùng nhiều 8/67 (11,94%), 0,5 phiên/người/tháng, 3 lượt/phiên. Nguồn: `evidence/summary.md` Câu 2; quy đổi số phiên và lượt hỏi *(tự ước tính)*.
- **Số người dùng thật** 3 kịch bản: thấp **5.000** · cơ sở **10.000** · cao **20.000** người. Nguồn: `spec.md` §2; cả ba kịch bản là *(tự ước tính)*, chưa phải số người dùng đã đo.
- **Giá** 2 mức model tham chiếu: `gemini-3.1-flash-lite` **0,25 USD/1 triệu token input · 1,50 USD/1 triệu token output**; `gemini-4-hydrogen` **1,50 USD/1 triệu token input · 7,50 USD/1 triệu token output**. Nguồn: `E:/minihackathon/K5-L3-Day15-AI-Product-Hackathon/further-reading/model-prices.csv`, [bảng giá Gemini](https://ai.google.dev/gemini-api/docs/pricing), xem 25/11/2026. Đây là hai mức giá để so sánh, không phải tên model thực chạy.
- **Tỉ lệ đạt** dùng để tính: **23/30 (77%)** — `eval/run-2.csv`, run ID `run-2@20261128-111600`.
- Đo token thật trên model **`gpt-4.1-mini`** theo `traces/simulate-1.jsonl`; tính giá hai mức model tham chiếu trên. Token của model khác có thể lệch. Run-2 được chạy trên `main` có **135 POI**, khác 94 POI của run-1; so sánh hai lượt không tách riêng tác động sửa code và thêm data.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-120625` · **50 phiên** · seed **42**. Có **1/50 phiên lỗi kết nối** (`RemoteDisconnected` ở lượt hỏi thứ hai); công cụ loại phiên này khỏi trung bình, còn **49 phiên hợp lệ**.

Số liệu từ `cost/simulate-1-summary.md`, do `python run.py simulate --rate-from eval/run-2.csv` sinh ra:

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| `gemini-3.1-flash-lite` (giá tham chiếu) | $0.00044 | $0.00057 | $0.6535 | $1.31 | $2.61 | $0.00013 |
| `gemini-4-hydrogen` (giá tham chiếu) | $0.0024 | $0.0032 | $3.63 | $7.26 | $14.51 | $0.00073 |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): **~25,2 phút**, gồm xếp lịch ban đầu và xếp lại khi vỡ kế hoạch, tại quy mô cơ sở 10.000 người *(quy mô tự ước tính)*.
- Chi phí / người / tháng (cơ sở, theo giá `gemini-3.1-flash-lite`): **$0.00013**; mức giá `gemini-4-hydrogen`: **$0.00073**.
- **Kết luận:** Chi phí token ước tính thấp so với mục tiêu tiết kiệm ~25,2 phút/người/tháng, nên đáng thử nghiệm tiếp; chưa đủ để kết luận hiệu quả tài chính vì quy mô người dùng và tần suất là *(tự ước tính)*, còn hosting, lưu trữ và giờ công chưa tính.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
