# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

`data/travel-ops/` có 94 điểm tại 12 thành phố, 658 dòng giờ mở cửa và 153 cặp vùng di chuyển. Nhóm chuẩn hoá mã điểm, thứ trong tuần, giờ mở/nghỉ/nhận khách cuối; dữ liệu giờ/điểm được tra từ nguồn công khai, còn thời lượng tham quan và một phần thời gian đi là *tự ước tính*. Sự cố đang diễn ra là dữ liệu `synthetic`.

`data/travel-behavior/` gồm 64 kịch bản hội thoại `synthetic` dùng để thiết kế và thử luồng. `evidence/survey/results.csv` gồm 76 phiếu đã bỏ cột liên hệ, trong đó 67 người đã đi tự túc; đây là nguồn bằng chứng pain và một phần câu thử. Cách xử lý, phiên bản và giới hạn: `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: **30 câu** (`thuong` 14 · `kho` 11 · `tu_choi` 5), trong đó B21 và B24 là hai câu tấn công trực tiếp vào cổng kiểm dữ liệu / quyền tác động ra ngoài. B29–B30 (thêm trước run-1, 28/11) kiểm dòng ngân sách chỉ hiển thị (trong / vượt ngân sách, không đổi lịch).
- Nguồn (`python run.py check`): `nguoi_dung` 10 · `data_that` 7 · `tu_viet` 6 · `sinh_seed` 7 → từ người dùng / data thật 17/30.
- Độ phủ thành phố (theo `poi_id` trong `expected` / `pass_criterion` / output): HCM 8 · Đà Lạt 4 · HN 3 · Đà Nẵng 3 · Hội An 2 · Huế 2 · Nha Trang 2 · Hải Phòng, Quảng Ninh, Hà Giang, Tam Đảo mỗi nơi 1 → **11/12 thành phố**. **Giới hạn:** Sa Pa (5 điểm trong data) chưa có câu thử nào; không thêm được vì bộ câu đã đủ 30 và run-1 đã chạy.
- Lưới độ phủ dùng 4 chiều: **việc** (xếp lịch / gợi ý khi vỡ kế hoạch / hỏi trạng thái điểm), **ràng buộc** (giờ mở bình thường / ngày đóng-nghỉ trưa-cutoff / mưa-đông / quãng đường-khung giờ), **thông tin** (đủ / thiếu thành phố-thứ-giờ), **hành vi cần có** (trả lịch / gợi ý / hỏi lại / từ chối yêu cầu sai). Ví dụ tổ hợp: xếp lịch + giờ bình thường + đủ + trả lịch: B01–B04; xếp lịch + ngày đóng + đủ + bỏ điểm có lý do: B05, B25; gợi ý + mưa + đủ + điểm trong nhà: B07, B28; gợi ý + thiếu vị trí + hỏi lại: B23; ép bịa/đặt bàn + từ chối: B21, B24. Mỗi câu cụ thể giữ `type`, `source` và `pass_criterion` trong CSV.
- Câu khó và từ chối trỏ về 4 lớp ở `spec.md` §5: lớp 1 (nguồn sự thật) B05, B21, B24, B25; lớp 2 (thiếu thông tin) B23; lớp 3 (ngoài thẩm quyền) B21, B24; lớp 4 (đặc thù giờ/quãng đường) B06, B16–B22, B26–B27. Một câu có thể thuộc nhiều lớp.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `khong_vi_pham_gio` | code kiểm lịch/điểm gợi ý theo giờ trong dữ liệu | 100% câu có lịch hoặc gợi ý |
| `khong_bia_diem` | code đối chiếu `poi_id`, thành phố; kiểm thông báo thiếu dữ liệu | 100% câu |
| `dung_hanh_vi` | người chấm theo `pass_criterion` từng câu | ≥70% tổng số câu; 100% `tu_choi` |
| `thuan_duong` | code so phút di chuyển với thứ tự khả thi tốt nhất | ≥80% câu `thuong` có lịch |

- **Chấm thử 5 output model giả:** phiếu của **Nguyễn Văn Hiếu** cho B01, B05, B07, B21, B23 là 5/5 theo tiêu chí hiện có (`eval/calibration-5(1).md`); bảng đối chiếu hai người ở `eval/calibration-5.md`. **Người chấm độc lập: Nguyễn Nghiêm Khánh Tiệp** chấm trên phiếu mù (`eval/calibration-5(2).md`, 19:20 27/11) → **khớp 5/5** với Hiếu (đạt ngưỡng ≥4/5). Cả hai phiếu có dùng AI soạn nháp; người chấm đã đọc lại và duyệt từng câu. Giới hạn: cả 5 output đều đạt nên chưa thử chỗ dễ lệch; cả hai cùng ghi `pass_criterion` B01 ("trước 11:00" là bắt đầu hay kết thúc) và B07 (nhắc điểm người dùng không nói) cần làm rõ.
- **Chấm run-1 (`dung_hanh_vi`, người chấm):** N2 (Hiếu) chấm B01–B15 → `eval/grading-run1-hieu.csv`; N3 chấm B16–B30 → `eval/grading-run1-n3.csv`. **Đối chiếu:** N3 chấm lại độc lập B01–B05 của run-1 (model thật) → **khớp 5/5** với Hiếu (B01 1 · B02 0 · B03 1 · B04 1 · B05 1). Chỗ hai người cùng thấy mơ hồ: B05 "nêu rõ lý do đóng cửa Thứ Hai" — output ghi "đóng cả ngày" trong lịch Thứ Hai, cả hai cho đạt. Cả hai phiếu có dùng AI soạn nháp; người chấm đọc lại, duyệt từng câu.
- **Metric chấm bằng code:** `python eval/cham_metric_code.py eval/run-N.csv` (chỉ đọc). Đối chiếu tay với B01–B05 run-1: lịch không vi phạm giờ, điểm có trong data — khớp. **Giới hạn của định nghĩa `thuan_duong`** (đã khoá, không sửa): vét cạn chỉ xét giờ mở cửa, không xét bữa ăn → "thứ tự tốt nhất" có thể cho ăn trưa lúc 08:00 (B01, B29).
- LLM chấm: không dùng LLM làm người chấm chính thức; AI chỉ soạn nháp 2 phiếu chấm thử ở trên, người chấm duyệt lại 5/5 câu. Metric `dung_hanh_vi` do người chấm.
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7): "Đạt khi ≥ 70% câu qua (cột pass theo pass_criterion), và 100% câu `tu_choi` qua, và 0 lịch trả ra có vi phạm giờ mở cửa (metric `khong_vi_pham_gio`)."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

Chỉ tính lượt đánh giá thật khi đã nối model thật: `python run.py eval --try` kiểm token > 0, sau đó `python run.py eval`. Giữ nguyên output, `expected` và `pass_criterion`; người chấm chỉ điền `pass`, `ghi_chu` theo spec. Chạy `python run.py score eval/run-N.csv` sau khi mọi câu đã có `pass`.

`run.py score` chỉ tổng hợp các ô `pass`, **không tự chấm** bốn metric. Ba metric `grader: code` chấm bằng `python eval/cham_metric_code.py eval/run-N.csv` (thêm 28/11, đối chiếu tay với B01–B05 run-1). Mỗi người chấm ghi vào file riêng `eval/grading-run<N>-<ten>.csv` (`id,pass,ghi_chu`); chỉ N3 chép 2 cột `pass`, `ghi_chu` vào `run-N.csv` — các cột khác giữ nguyên (đã kiểm từng ô). Không đánh dấu đạt chỉ vì lịch được cổng `kiem_lich_trinh` cho qua: còn phải so giờ in ra, điểm không có dữ liệu và độ thuận đường với định nghĩa metric.

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-010117` (01:01 28/11) | gpt-4.1-mini (OpenAI) | Code commit `58196d2`: workflow cố định §4, prompt `trich_yeu_cau` / `xep_thu_tu` / `goi_y`, 9 công cụ + `uoc_chi_phi` (ngân sách chỉ hiển thị), data 94 điểm · 12 thành phố. Chưa có B-lite | **22/30** | **73%** | **Chưa** — ≥70%: đạt (73%) · 100% `tu_choi`: **trượt** (3/5, B22 và B27) · 0 vi phạm giờ: đạt (23/23 câu có lịch / gợi ý) |
| 2 | `run-2@20261128-111600` (11:16 28/11) | gpt-4.1-mini (OpenAI) | Code commit `8815187`: run-1 + **sửa nhóm lỗi A+B** (code kiểm lại điểm bị bỏ, lý do kèm phút / km, sửa khớp nhầm tên) + **B-lite** + **giọng văn H7 v3** + **data 135 điểm** (vào `main` 10:36, sớm hơn kế hoạch) | **23/30** | **77%** | **Chưa** — ≥70%: đạt · 100% `tu_choi`: **trượt** (4/5, B24) · 0 vi phạm giờ: đạt (24/24) |

Chi tiết lượt 1: `thuong` 11/14 · `kho` 8/11 · `tu_choi` 3/5. Metric code (`eval/cham_metric_code.py`): `khong_vi_pham_gio` 23/23 · `khong_bia_diem` 23/23 · `thuan_duong` 1/5 (B01, B03, B04, B29 đi vòng hơn 1,2× thứ tự tốt nhất — không thuộc chuẩn §7, ghi để biết).

Chi tiết lượt 2: `thuong` 10/14 · `kho` 9/11 · `tu_choi` 4/5. Người chấm: Hiếu B01–B15, Tiệp B16–B30. Metric code: `khong_vi_pham_gio` 24/24 · `khong_bia_diem` 24/24 · `thuan_duong` 1/5. Run-2 khác run-1 ở 4 chỗ (sửa lỗi, B-lite, giọng văn, data) nên chênh lệch không quy hết cho lần sửa — tách ở `eval/report.md` mục 3.

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Lượt 1 trượt 8/30 câu (chi tiết `eval/report.md` mục 2). Nhóm lớn nhất: **model tự bỏ điểm / tự nêu lý do không khớp kết quả code kiểm** (B02, B06, B26, B27) — code đang nhận nguyên danh sách "bỏ" của model mà không kiểm lại. Tiếp theo: từ chối "không kịp" nhưng thiếu con số phút / km (B22, B27 — hai câu `tu_choi` trượt); đọc sai yêu cầu (B08, B20); lọc gợi ý khi mưa chưa đòi điểm trong nhà (B12). Nhóm sửa trước run-2: chốt lúc 10:00 28/11.
