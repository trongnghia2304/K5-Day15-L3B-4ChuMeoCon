# RULE.MD — QUY TẮC BẮT BUỘC KHI DÙNG AI TRIỂN KHAI DỰ ÁN (TRAVEL AI AGENT)

> **CẢNH BÁO:** Mọi AI coding assistant (Antigravity, Codex, Claude Code…) và thành viên nhóm BẮT BUỘC tuân thủ các quy tắc dưới đây. Vi phạm mục 1–2 có thể làm **0 điểm khối đánh giá** hoặc **trừ 10 điểm** theo quy chế hackathon.
> Ký hiệu: **[Đề]** = luật của đề (README, 02-guide, 03-rubric của repo BTC) · **[Nhóm]** = luật nhóm tự đặt để không phá thứ đã có.
> Phân công chi tiết, mốc giờ, ai chờ ai: [`docs/phan-cong-cp3-cp4.md`](docs/phan-cong-cp3-cp4.md). Luật cho agent: [`AGENTS.md`](AGENTS.md).
> **Hợp đồng dữ liệu** (tên hàm, tham số, trường trả về, cột CSV, định dạng dòng giữa các người): [`docs/hop-dong-du-lieu.md`](docs/hop-dong-du-lieu.md) — AI của mỗi người phải đọc trước khi viết code chạm tới phần người khác. Kiểm: `python scripts/kiem_hop_dong.py` (phải `0 lỗi` trước khi push).

---

## 1. FILE & NỘI DUNG KHOÁ (đã chốt từ CP2)

1. **`spec.md` §7 — chuẩn "đạt" bằng số [Đề]:** giữ nguyên văn. Không hạ chuẩn cho khớp kết quả. Chỉ được điền dòng "Kết quả lượt 1 / lượt 2".
2. **`eval/metric_spec.yaml` [Đề]:** không sửa định nghĩa, cách chấm, ngưỡng; không thêm, bớt metric.
3. **`eval/benchmark.csv` — chỉ được THÊM [Đề]:**
   - Không sửa bất kỳ cột nào (`input`, `expected`, `pass_criterion`, `type`, `source`) của các dòng đã có (B01–B28).
   - **Không xoá** câu thử, kể cả câu trượt.
   - Câu mới chỉ thêm ở cuối file (B29, B30…), trước khi chạy run-1, tổng không quá 30 câu. Sau run-1 không thêm nữa, vì run-2 phải chạy **cùng bộ** với run-1 [Nhóm].
   - Bộ câu thử phủ cả **12 thành phố** đang có trong data; không thu hẹp về vài thành phố.
4. **Kết quả đã chạy [Đề]:** `eval/run-*.csv`, `cost/simulate-*.csv`, `traces/*` — không sửa output hay số. Chỉ người chấm điền cột `pass`, `ghi_chu`. Cải tiến thì chạy lượt mới (`run-2.csv`, `run-3.csv`).
5. **Số liệu bằng chứng [Đề]:** không sửa số khảo sát / phỏng vấn đã nộp (76 phiếu, mẫu số 67…). Chỉ được ghi thêm chú thích (vd độ nhạy khi bỏ phiếu trùng).
6. **File khung [Đề]:** không sửa `run.py`, `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`. `python run.py` vẫn là lệnh chạy bản chạy thử. Không phá định dạng bảng trong `TEAMS.md`.
7. **Data — ĐÓNG BĂNG, chỉ THÊM MỚI [Nhóm]:**
   - Không sửa, không xoá dòng hay cột đã có trong `data/travel-ops/*.csv` và `data/travel-behavior/*.csv` (94 POI · 12 thành phố). Câu thử dựa vào các `poi_id`, giờ mở cửa và thời gian đi này; sửa data là đổi đáp án ngầm của câu thử.
   - Cần dữ liệu mới thì tạo **file mới** (vd `data/travel-ops/price_tier_vnd.csv`) và ghi vào `data/DATA_CARD.md`.
   - Chỉ được sửa data cũ khi chứng minh được nó sai so với nguồn công khai: ghi nguồn + 1 dòng changelog `spec.md` §10, rồi chạy lại trọn bộ thành lượt mới.
   - Sau khi sửa `data/` phải chạy `python data/validate_travel_data.py` (0 lỗi) và `python run.py check`.

---

## 2. BẢO MẬT API KEY & DỮ LIỆU CÁ NHÂN (vi phạm = −10 điểm) [Đề]

1. **Không lộ key:**
   - Không viết cứng API key, token, mật khẩu vào bất kỳ file nào (`.py`, `.json`, `.yaml`, `.md`, `Procfile`).
   - Key chỉ đọc từ biến môi trường: `.env` ở máy (đã có trong `.gitignore`), _Variables_ trên Railway.
   - Trước mỗi `git add`, kiểm `git status` không có `.env`.
2. **Ẩn danh dữ liệu người dùng:**
   - `evidence/survey/` và `evidence/interviews/` không có họ tên, email, số điện thoại, Zalo, mã học viên. Chỉ dùng mã `S01…`, `P1…`.
   - Không dùng mã đặt chỗ, vé, hoá đơn thật của ai trong `data/` hoặc `eval/`.
   - Chỉ gửi cho model dữ liệu đã ẩn danh.

---

## 3. RÀNG BUỘC KỸ THUẬT & CHỐNG BỊA ĐẶT (TRACK C1 — DU LỊCH)

1. **Phạm vi = dữ liệu đang có (12 thành phố: HN, HP, QN, SP, TD, HG, HUE, DN, HA, NT, DL, HCM) [Nhóm]:**
   - Không thêm luật "chỉ 4 thành phố": 13/28 câu thử nằm ở thành phố khác, chặn đi là trượt hàng loạt.
   - **G10 [Đề]:** thành phố hoặc địa điểm không có trong `data/travel-ops/poi_master.csv`, hoặc thiếu thành phố / thứ / khung giờ → nói rõ "không có dữ liệu" hoặc hỏi lại 1 câu. Agent đã làm việc này (`city_unknown`, `_khong_co`, câu hỏi lại trong `codebase/agent.py`). Không dùng trí nhớ của model để bịa địa điểm hay giờ mở cửa.
2. **Giờ, phút, tiền đều do code tính [Nhóm, theo `spec.md` §4]:**
   - Model chỉ chọn **thứ tự** và điểm bỏ (kèm lý do). Model không tự tính giờ đến, thời gian đi hay tiền.
   - Điểm lấy qua `search_pois` / `tim_diem`; thời gian đi qua `zone_travel_matrix.csv` (`travel_min`, `zone_min`, `get_travel_time`); giờ mở cửa qua `check_opening_hours`.
   - Giờ đến / rời do `lap_lich` tính. Vòng sửa dùng `liet_ke_vi_pham` (tối đa 2 vòng). Lịch chỉ được trả khi qua **cổng kiểm cuối `kiem_lich_trinh`** (0 vi phạm giờ mở cửa, nghỉ trưa, chồng giờ, thiếu thời gian đi, ngoài khung giờ).
3. **Ngân sách — CHỈ HIỂN THỊ [Nhóm]:**
   - Ngân sách không phải ràng buộc. Không lọc, bỏ hay đổi thứ tự điểm theo ngân sách; `kiem_lich_trinh` không kiểm tiền.
   - Khi tin nhắn có ngân sách, `codebase/ngan_sach.py` → `dong_chi_phi(text, poi_ids)` thêm **1 dòng cuối**: chi phí ước tính theo `price_tier` _(tự ước tính)_ + trong / vượt ngân sách. Không có ngân sách thì output y như cũ.
   - Web ghép ô ngân sách thành câu cố định `Ngân sách <số>đ/người.` rồi gọi `agent.answer(text)`.
4. **Chạy độc lập, tái lập được [Nhóm]:** lõi `codebase/` chỉ đọc `data/` trong repo, không gọi API bản đồ / thời tiết / đặt vé khi chạy. Ngoại lệ duy nhất là lời gọi model trong `codebase/ai.py`.
5. **Không có tác động ra ngoài [Đề]:** không đặt bàn, mua vé, thanh toán, nhắn tin thay người dùng. Mọi công cụ đều chỉ đọc.
6. **Không giấu câu thử vào code [Đề]:** không so khớp nguyên văn input của bộ câu thử trong code hay prompt.

---

## 4. PHÂN QUYỀN FILE (chống xung đột git) [Nhóm]

Mỗi người (và AI của người đó) chỉ tạo / sửa file trong phần của mình. Chi tiết: [`docs/phan-cong-cp3-cp4.md`](docs/phan-cong-cp3-cp4.md).

| Người                                 | Được sửa                                                                                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **N1** — evidence, impact, slide 1–3  | `evidence/*` · `spec.md` §0–§2 · `slides/outline.md` trang 1–3                                                                                          |
| **N2** — data, tools, ngân sách, cost | `data/*` (chỉ thêm, xem 1.7) · `data/DATA_CARD.md` · `codebase/tools.py` · `codebase/ngan_sach.py` · `eval/benchmark.csv` (chỉ thêm B29–B30) · `cost/*` |
| **N3** — AI core, eval                | `codebase/ai.py` · `codebase/agent.py` · `codebase/prompts/` · `eval/run-*.csv` · `traces/` · `eval/report.md` · `eval/README.md` · `spec.md` §3–§9     |
| **N4** — web, demo, người dùng thử    | `web/*` · `requirements.txt` · `Procfile` · `README.md` · `validation/log.md` · `slides/outline.md` trang 4–8 · `demo-slides.pdf`                       |
| Mỗi người                             | `eval/grading-run<N>-<ten>.csv` của mình · `reflection/<ten>.md` · khối của mình trong `spec.md` §10 và `docs/ai-usage.md`                              |
| Đội trưởng                            | `TEAMS.md`                                                                                                                                              |

- **Chỉ N3 chạy `python run.py eval`** (khung tự đánh số `run-N`; hai máy chạy = hai bản `run-1` khác nhau).
- Người chấm ghi vào file chấm riêng; chỉ N3 chép cột `pass`, `ghi_chu` vào `run-N.csv`.
- Web Streamlit đặt ở `web/streamlit_app.py`. **Không sửa `codebase/app.py`** (`run.py` gọi file này). Không import streamlit trong `codebase/`.
- Trước khi sửa: `git pull`. Xong mỗi việc: commit + push ngay.

---

## 5. KỶ LUẬT CODE & KIỂM TRA TRƯỚC KHI COMMIT

1. **Tiết kiệm token:** chỉ đọc file liên quan tới việc đang làm (dùng `head` với CSV lớn), sửa theo diff nhỏ, không viết lại cả file nếu không cần.
2. **Không commit file nháp cá nhân:** `PROGRESS.md`, `task_plan.md`, `findings.md`, `progress.md`, thư mục `.agent/skills/`… (chặn qua `.git/info/exclude`).
3. **Changelog [Đề]:** mọi thay đổi sau CP2 (19:30 27/11) → 1 dòng trong **khối của mình** ở `spec.md` §10: giờ · đổi gì · vì sao.
4. **Tự kiểm trước khi báo xong:**
   - **Mọi lần push** → `python scripts/kiem_hop_dong.py` ra `0 lỗi` (hợp đồng H1–H13).
   - Sửa `data/` hoặc `eval/benchmark.csv` → `python run.py check` không lỗi.
   - Sửa `codebase/` → `python run.py` chạy được; trước run-1, so output 28 câu với bản trước để biết mình đổi gì.
   - `web/streamlit_app.py` chỉ là giao diện gọi `agent.answer`, không có logic AI riêng.
5. **Giải thích được phần có tên mình [Đề]:** dùng AI thoải mái, nhưng ai không giải thích được phần mình làm thì phần đó 0 điểm. Ghi 2–3 dòng vào khối của mình trong `docs/ai-usage.md`.
