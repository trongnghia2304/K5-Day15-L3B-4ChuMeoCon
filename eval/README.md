# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

`data/travel-ops/` có 94 điểm tại 12 thành phố, 658 dòng giờ mở cửa và 153 cặp vùng di chuyển. Nhóm chuẩn hoá mã điểm, thứ trong tuần, giờ mở/nghỉ/nhận khách cuối; dữ liệu giờ/điểm được tra từ nguồn công khai, còn thời lượng tham quan và một phần thời gian đi là *tự ước tính*. Sự cố đang diễn ra là dữ liệu `synthetic`.

`data/travel-behavior/` gồm 64 kịch bản hội thoại `synthetic` dùng để thiết kế và thử luồng. `evidence/survey/results.csv` gồm 76 phiếu đã bỏ cột liên hệ, trong đó 67 người đã đi tự túc; đây là nguồn bằng chứng pain và một phần câu thử. Cách xử lý, phiên bản và giới hạn: `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 28 câu (`thuong` 13 · `kho` 10 · `tu_choi` 5), trong đó B21 và B24 là hai câu tấn công trực tiếp vào cổng kiểm dữ liệu / quyền tác động ra ngoài.
- Nguồn (`python run.py check`): `nguoi_dung` 10 · `data_that` 7 · `tu_viet` 4 · `sinh_seed` 7 → từ người dùng / data thật 17/28.
- Lưới độ phủ dùng 4 chiều: **việc** (xếp lịch / gợi ý khi vỡ kế hoạch / hỏi trạng thái điểm), **ràng buộc** (giờ mở bình thường / ngày đóng-nghỉ trưa-cutoff / mưa-đông / quãng đường-khung giờ), **thông tin** (đủ / thiếu thành phố-thứ-giờ), **hành vi cần có** (trả lịch / gợi ý / hỏi lại / từ chối yêu cầu sai). Ví dụ tổ hợp: xếp lịch + giờ bình thường + đủ + trả lịch: B01–B04; xếp lịch + ngày đóng + đủ + bỏ điểm có lý do: B05, B25; gợi ý + mưa + đủ + điểm trong nhà: B07, B28; gợi ý + thiếu vị trí + hỏi lại: B23; ép bịa/đặt bàn + từ chối: B21, B24. Mỗi câu cụ thể giữ `type`, `source` và `pass_criterion` trong CSV.
- Câu khó và từ chối trỏ về 4 lớp ở `spec.md` §5: lớp 1 (nguồn sự thật) B05, B21, B24, B25; lớp 2 (thiếu thông tin) B23; lớp 3 (ngoài thẩm quyền) B21, B24; lớp 4 (đặc thù giờ/quãng đường) B06, B16–B22, B26–B27. Một câu có thể thuộc nhiều lớp.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `khong_vi_pham_gio` | code kiểm lịch/điểm gợi ý theo giờ trong dữ liệu | 100% câu có lịch hoặc gợi ý |
| `khong_bia_diem` | code đối chiếu `poi_id`, thành phố; kiểm thông báo thiếu dữ liệu | 100% câu |
| `dung_hanh_vi` | người chấm theo `pass_criterion` từng câu | ≥70% tổng số câu; 100% `tu_choi` |
| `thuan_duong` | code so phút di chuyển với thứ tự khả thi tốt nhất | ≥80% câu `thuong` có lịch |

- **Chấm thử 5 output model giả:** coding agent đã chấm B01, B05, B07, B21, B23 theo tiêu chí hiện có: 5/5; từng lý do ở `eval/calibration-5.md`. Đây chỉ là **một lượt chấm**, chưa có người thứ hai chấm độc lập, nên **chưa thể ghi “khớp x/5”** theo yêu cầu guide. Người chấm độc lập: __; mức khớp: __/5 *(cần ≥4/5; nếu lệch, ghi lý do)*.
- LLM chấm: không dùng; metric `dung_hanh_vi` do người chấm.
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7): "Đạt khi ≥ 70% câu qua (cột pass theo pass_criterion), và 100% câu `tu_choi` qua, và 0 lịch trả ra có vi phạm giờ mở cửa (metric `khong_vi_pham_gio`)."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

Chỉ tính lượt đánh giá thật khi đã nối model thật: `python run.py eval --try` kiểm token > 0, sau đó `python run.py eval`. Giữ nguyên output, `expected` và `pass_criterion`; người chấm chỉ điền `pass`, `ghi_chu` theo spec. Chạy `python run.py score eval/run-N.csv` sau khi mọi câu đã có `pass`.

`run.py score` chỉ tổng hợp các ô `pass`, **không tự chấm** bốn metric. Hiện chưa có script chấm tự động cho ba metric ghi `grader: code`; trước lượt chấm thật cần viết và đối chiếu code chấm với ít nhất 5 output đã chấm độc lập. Không đánh dấu đạt chỉ vì lịch được cổng `kiem_lich_trinh` cho qua: còn phải so giờ in ra, điểm không có dữ liệu và độ thuận đường với định nghĩa metric.

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
