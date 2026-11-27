# Phân công CP3 + CP4 — 4ChuMeoCon

> Chia theo **quyền sở hữu file**: mỗi file một chủ. File dùng chung thì mỗi người một khối riêng, hoặc sửa ở khung giờ khác nhau. Trước khi sửa: `git pull`. Sửa xong việc nào: commit + push ngay.
> Hình dạng dữ liệu giao giữa các người (hàm, trường, cột, dòng output): [`hop-dong-du-lieu.md`](hop-dong-du-lieu.md). Trước khi push: `python scripts/kiem_hop_dong.py` phải `0 lỗi`.
> Điền tên thật vào cột "Người": N1 = ____ · N2 = ____ · N3 = ____ · N4 = ____ (cập nhật luôn cột "Phần việc chính" trong `TEAMS.md`, đội trưởng sửa).

## Mốc

| Lúc | Việc |
|---|---|
| **23:50** 27/11 | N2 push stub `codebase/ngan_sach.py` (hàm trả `""`) |
| **00:00** 28/11 | N3 nối xong model thật (`python run.py eval --try` có token > 0), báo cả nhóm |
| **00:30** | **Đóng băng**: N2 đã push ngân sách thật + B29–B30. Sau mốc này không ai sửa `codebase/`, `data/`, `eval/benchmark.csv` |
| **00:45** | N3 chạy `python run.py eval` **một lần** → commit `eval/run-1.csv` + `traces/run-1.jsonl` |
| 02:30 | Nghỉ |
| 09:15 | N2 push file chấm B01–B15 |
| 09:30 | N4 gửi link video 30s |
| **10:00** | **Nộp CP3** (đội trưởng) |
| ≈12:00 | N3 xong run-2 + score |
| 13:30 | N2 xong `cost/cost-estimate.md` |
| 14:15 | N4 xong `demo-slides.pdf` |
| **14:30** | **Nộp CP4** |

## Bảng sở hữu file — chỉ chủ được sửa

| File | Chủ | Ghi chú |
|---|---|---|
| `evidence/*` · `spec.md` §0–§2 · `slides/outline.md` trang 1–3 | **N1** | Chỉ sửa đêm nay → không trùng giờ ai |
| `data/*` · `data/DATA_CARD.md` · `codebase/tools.py` · `codebase/ngan_sach.py` (mới) · `eval/benchmark.csv` (chỉ **thêm** B29–B30) · `cost/*` | **N2** | Làm trọn phần sau của tính năng ngân sách |
| `codebase/ai.py` · `codebase/agent.py` · `codebase/prompts/` · `eval/run-*.csv` · `traces/` · `eval/report.md` · `eval/README.md` · `spec.md` §3–§9 | **N3** | Chỉ N3 chạy eval, chỉ N3 ghi vào `run-*.csv` |
| `web/*` · `requirements.txt` · `Procfile` · `README.md` · `validation/log.md` · `slides/outline.md` trang 4–8 · `demo-slides.pdf` | **N4** | Sửa slide **ngày mai**, sau khi N1 xong |
| `eval/grading-run1-<ten>.csv` · `eval/grading-run2-<ten>.csv` | người chấm | Mỗi người một file (`id,pass,ghi_chu`), N3 gộp vào `run-N.csv` |
| `reflection/<ten>.md` | từng người | |
| `spec.md` §10 · `docs/ai-usage.md` | mỗi người **khối riêng** đã tạo sẵn | Không sửa khối người khác |
| `TEAMS.md` | đội trưởng | |

## Ngân sách "chỉ hiển thị" — gói trong N2, 2 điểm chạm

- Lịch xếp **y như cũ**. Chỉ thêm 1 dòng cuối khi tin nhắn có ngân sách → lát cắt CP2 không mở rộng, output 28 câu cũ không đổi. Model không thấy, không in số tiền; code tính.
- **N2 làm trọn:**
  - `data/travel-ops/price_tier_vnd.csv`: `price_tier,min_vnd,max_vnd,source` — ánh xạ từ cột `price_tier` có sẵn (`free / budget / mid / mid_high`), `source = "(tự ước tính)"`. Không sửa `poi_master.csv`.
  - `@tool uoc_chi_phi(poi_ids: list, so_nguoi: int = 1) -> dict` trong `tools.py` (`tong_min`, `tong_max`, `tung_diem`, `nguon`), docstring ghi "không tác động ra ngoài".
  - `codebase/ngan_sach.py` có **một hàm** `dong_chi_phi(text: str, poi_ids: list) -> str`: tự tách "ngân sách …" trong câu chữ bằng regex, gọi `uoc_chi_phi`, trả `""` nếu không có ngân sách. Dòng trả ra dạng: `Chi phí ước tính: X–Y đ/người (tự ước tính theo mức giá) · ngân sách bạn đưa: Z → trong / vượt ngân sách`.
  - B29 (`thuong`, trong ngân sách) + B30 (`kho`, vượt: cảnh báo, không bỏ điểm, không bịa giá, có chữ "tự ước tính"). Không sửa B01–B28. Không thêm metric.
  - 1 dòng vào `data/DATA_CARD.md`.
- **Điểm chạm 1 — N3:** thêm đúng 1 dòng trong `agent.py`, sau cổng `kiem_lich_trinh`, nối `ngan_sach.dong_chi_phi(text, ids)` vào output.
- **Điểm chạm 2 — N4:** web ghép ô ngân sách thành câu cố định **`Ngân sách <số>đ/người.`** rồi gọi `agent.answer(text)`. Đây là hợp đồng chữ duy nhất mà N2 phải tách được.

## Việc từng người

### N1 (vắng sáng mai) — chỉ làm đêm nay, không chờ ai
1. `spec.md` §2: điền impact = số người (nguồn công khai có link) × lần / tháng (Câu 2) × phút / lần (Câu 9 + P1–P3). Thừa số thiếu nguồn ghi *(tự ước tính)*.
2. `evidence/summary.md`: ghi độ nhạy S25/S28 ("nếu bỏ S28 thì …") cạnh số chính. **Không đổi số đã nộp CP2.**
3. `slides/outline.md` trang 1–3.
4. Khối N1 trong `spec.md` §10 và `docs/ai-usage.md`.
5. Ngày mai online, trước 23:59: `reflection/<ten-1>.md` (cần run-1 đã chấm để lấy 1 câu trượt).

### N2 (Data & Cost)
Đêm nay:
1. 23:50 push stub `ngan_sach.py`.
2. Làm trọn ngân sách (mục trên), `python run.py check` sạch, push **trước 00:30**.
3. `cost/personas.yaml`: 3 persona từ Câu 2 (1–2 lần / năm: 39 · 3–5: 20 · >5: 8 người); số người dùng thật có link nguồn; giá model từ `further-reading/model-prices.csv` của repo đề.
4. Sau khi N3 báo đã nối model: `python run.py simulate --try`.

Sáng mai:
5. Chấm B01–B15 → `eval/grading-run1-<ten-2>.csv`, push **trước 09:15**.
6. Sau run-2: `python run.py simulate` (≥50 phiên) → `cost/cost-estimate.md` (3 kịch bản, ≥2 model, chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt run-2), **trước 13:30**.
7. Nhóm lỗi chọn sửa ở lượt 2 nằm trong `tools.py` / `data/` thì N2 sửa.
8. `reflection/<ten-2>.md`.

### N3 (Agent & Eval)
Đêm nay:
1. `codebase/ai.py`: viết `call_model` theo `docs/connect-model.md` (token lấy từ `usage`). `.env` tự điền, **không commit**. `python run.py eval --try` có token > 0 → báo nhóm **00:00**.
2. Chạy thử vài câu với model thật, sửa prompt / đọc JSON nếu vỡ. **Không** viết lại vòng tự kiểm (đã có `liet_ke_vi_pham` ≤ 2 vòng + cổng `kiem_lich_trinh`), **không** chặn ngoài 4 thành phố.
3. Thêm dòng gọi `ngan_sach.dong_chi_phi`.
4. 00:45: `git pull` → `python run.py eval` **một lần** → commit ngay `eval/run-1.csv` + `traces/run-1.jsonl`.
5. Chấm B16–B30 → `eval/grading-run1-<ten-3>.csv`.
6. `spec.md` §4 (thêm dòng `uoc_chi_phi` vào bảng công cụ, thêm "không lọc / bỏ điểm theo ngân sách" vào mục Không làm) + khối N3 trong §10.

Sáng mai:
7. Chấm lại B01–B05 để đối chiếu với N2 (lệch ≥ 2/5 thì bàn lại cách hiểu `pass_criterion`, **không sửa** tiêu chí).
8. Gộp 2 file chấm vào `run-1.csv` → `python run.py score eval/run-1.csv` → `eval/README.md` mục 5 + dòng kết quả §7 → **nộp CP3 trước 10:00** (kèm link video của N4).
9. 10:00 cả nhóm đọc câu trượt → chọn 1 nhóm lỗi → sửa (file của ai người đó sửa) → `python run.py eval` → `run-2.csv` trọn 30 câu → chấm chia như run-1 → `eval/report.md` (≥3 lỗi) + `eval/README.md`.
10. Sau 13:30: `spec.md` §8–§9. `reflection/<ten-3>.md`.

### N4 (Web & Demo)
Đêm nay:
1. `web/streamlit_app.py`: form (thành phố, thứ, giờ, các điểm, phương tiện, ngân sách tuỳ chọn) → ghép thành 1 câu chữ → `agent.answer(text)`. Không sửa `codebase/app.py`, `run.py`; không import streamlit trong `codebase/` (để `python run.py` chạy được khi chưa cài streamlit).
2. `requirements.txt` (streamlit), `Procfile`, mục "Chạy web" trong `README.md`.
3. Railway, tối đa 30 phút: API key đặt trong biến môi trường Railway (**không** vào repo), có mật khẩu truy cập (`APP_PASSWORD`) + giới hạn số lượt mỗi phiên, dùng model rẻ. Quá 30 phút thì bỏ, demo localhost.

Sáng mai:
4. Video 30s (thao tác thật, AI thật: 1 câu thường + 1 câu khó) → link cho N3 **trước 09:30**, mở thử bằng cửa sổ ẩn danh.
5. 3 người ngoài nhóm, đúng vai (người đi du lịch tự túc), dùng thử 5 nhịp → `validation/log.md`.
6. Slide trang 4–8 (số từ `eval/report.md`, `cost/cost-estimate.md`) → `demo-slides.pdf` ở thư mục gốc **trước 14:15** + video demo dự phòng.
7. `reflection/<ten-4>.md`.

## Ai chờ ai

| Người chờ | Chờ ai | Thứ được giao | Hạn | Trễ thì |
|---|---|---|---|---|
| N3 | N2 | `ngan_sach.py` stub → bản thật + B29–B30 | 23:50 → 00:30 | 00:45 N3 vẫn chạy run-1; B29–B30 chưa push thì không thêm ở vòng này (run-2 phải cùng bộ với run-1) |
| N2, N4 | N3 | "đã nối model" | 00:00 | N4 làm web với chế độ giả trước |
| N2, N1 | N3 | `run-1.csv` đã commit | ≈01:00 | — |
| N3 | N2 | `grading-run1-<ten-2>.csv` | 09:15 | N3 tự chấm nốt |
| N3 | N4 | link video 30s | 09:30 | N3 quay nhanh video dòng lệnh |
| N2, N4 | N3 | `run-2.csv` + score | ≈12:00 | — |
| N3, N4 | N2 | `cost/cost-estimate.md` | 13:30 | — |
| N3 | N4 | `demo-slides.pdf` | 14:15 | — |

## Luật cả nhóm giữ
- **Không sửa:** `spec.md` §7 (chuẩn "đạt"), `eval/metric_spec.yaml`, các dòng B01–B28, `run.py`, `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, các `run-*.csv` / `simulate-*.csv` / `traces/` đã chạy (trừ cột `pass`, `ghi_chu`). Không xoá câu thử trượt.
- Dòng data cũ trong `data/travel-ops/` coi như đóng băng (13/28 câu thử nằm ngoài HN/HCM/DN/Huế); chỉ thêm file mới.
- Không commit `.env` / API key; không so khớp nguyên văn input câu thử trong code.
- Mọi thay đổi sau CP2 → 1 dòng trong khối của mình ở `spec.md` §10 (giờ · đổi gì · vì sao).
- Số không có nguồn ghi *(tự ước tính)*. Ai cũng phải giải thích được phần có tên mình.
