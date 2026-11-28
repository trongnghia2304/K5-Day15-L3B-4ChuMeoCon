# Tóm tắt mô phỏng simulate-1@20261128-120625

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 31 | 1 | 789 | 102 | 1.6 | 13.9 |
| dung_vua | 16 | 2 | 1244 | 173 | 2.5 | 27.3 |
| dung_nhieu | 2 | 3 | 1791 | 243 | 3.5 | 30.5 |

Tỉ lệ đạt dùng để tính: 23/30 (77%) — lượt run-2@20261128-111600

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (5.000 người) | Chi phí / tháng — cơ sở (10.000 người) | Chi phí / tháng — cao (20.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.00044 | $0.00057 | $0.00041 | $0.6535 | $1.31 | $2.61 | $0.00013 |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.0024 | $0.0032 | $0.0023 | $3.63 | $7.26 | $14.51 | $0.00073 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-4.1-mini. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 1/50.
