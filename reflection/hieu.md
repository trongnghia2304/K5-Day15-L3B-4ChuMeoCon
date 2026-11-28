# Reflection — Nguyễn Văn Hiếu

1. **Vai trò và phần tôi làm.** Tôi phụ trách Data & Cost: hàm ước tính ngân sách trong `codebase/tools.py` và `codebase/ngan_sach.py`, bảng mức giá, persona mô phỏng, và hai câu thử B29–B30. Tôi chấm độc lập B01–B15 của run-1 trong `eval/grading-run1-hieu.csv` (commit `25402f5`). Tôi cũng chuẩn bị 27 địa điểm Hà Nội trên nhánh `data/mo-rong`, kèm hai nguồn và 7 dòng giờ cho mỗi điểm (commit `dbccb08`); nhánh này chờ mô phỏng xong mới merge.

2. **AI hỗ trợ và phần tôi kiểm lại.** Tôi dùng Codex hỗ trợ viết code ngân sách, tra cứu và cấu trúc dữ liệu địa điểm, đọc output để soạn phiếu chấm. Tôi kiểm lại hợp đồng H2–H6/H14, đối chiếu các giờ mở cửa có nguồn khác nhau và chọn khung thận trọng hơn; số thời lượng, mức giá và quy mô người dùng không có nguồn trực tiếp được đánh dấu *(tự ước tính)*. Tôi chạy `python scripts/kiem_hop_dong.py` và `python data/validate_travel_data.py`, đều 0 lỗi trên nhánh data.

3. **Một câu thử trượt và điều tôi học được.** B12 hỏi quán café *trong nhà* để trú mưa ở Đà Lạt, nhưng run-1 gợi ý hai quán `semi_outdoor` rồi lại viết rằng cả hai ở trong nhà. Lỗi này cho thấy giờ mở cửa đúng chưa đủ: cờ về không gian và lời giải thích cũng phải khớp dữ liệu. Lượt sau cần kiểm cả điều kiện `indoor_only` và nội dung dòng “Vì sao”, không chỉ kiểm điểm có mở cửa.
