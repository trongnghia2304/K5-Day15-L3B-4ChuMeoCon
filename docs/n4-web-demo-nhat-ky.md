# N4 · Web & Demo — đã làm gì, còn gì (Tiệp)

> Ghi để tự đọc lại và giải thích được phần có tên mình. Phân công: [`phan-cong-cp3-cp4.md`](phan-cong-cp3-cp4.md) (**Đợt 2** từ 02:00 28/11) · hợp đồng: [`hop-dong-du-lieu.md`](hop-dong-du-lieu.md) (H1 v2, H7) · B-lite: [`huong-b-lite.md`](huong-b-lite.md).
> Cập nhật: sáng 28/11, sau khi kéo `origin/main` (`7bd0b64`).

## 1. Đã xong

| Việc | File | Ghi chú |
|---|---|---|
| Web chat (A+) gọi `agent.answer(text)` | `web/streamlit_app.py`, `web/hoi_thoai.py`, `web/ghep_cau.py` | Chat là chính, form thành "điền nhanh". N3 đã duyệt H1 v2 |
| Test | `web/test_ghep_cau.py` | 15/15 (chế độ giả) |
| `requirements.txt` (streamlit) · `Procfile` · README "Chạy web" | | README cập nhật cho chat, thêm dòng ngân sách, model `gpt-4.1-mini` |
| Đề xuất B-lite | `docs/huong-b-lite.md` | Nhóm chốt làm; N3 làm trên `feat/b-lite`, merge 13:15 |
| Slide trang 4–8 — khung + kịch bản demo | `slides/outline.md` (khối N4) | Ô `__` chờ số từ N3 / N2 |
| Changelog + khai AI | `spec.md` §10 khối N4 · `docs/ai-usage.md` khối N4 | |

**Không đụng:** `codebase/`, `run.py`, `data/`, `eval/`, `cost/`, `evidence/`, `TEAMS.md`, khối của người khác.

## 2. Web hoạt động thế nào (để giải thích khi bị hỏi)

```
Ô chat ─┐                                   ┌─ lượt trước agent HỎI LẠI (trace có note "hỏi lại…")
Form ───┤→ 1 câu chữ ──► hoi_thoai.noi_tin ─┤     → gửi "<tin mới>. <câu đã gửi trước>"
Ô sửa ──┘                                   └─ lượt khác → gửi nguyên văn
                                   │
                                   ▼
                        agent.answer(text)   ← y hệt python run.py; web không có logic AI
                                   │
                                   ▼
          <pre> output NGUYÊN VĂN (H7) + "Câu đã gửi" + model / số lần gọi / token (tracing.end())
```

- **`ghep_cau.py`** — form → câu đúng mẫu H1 (`{Thứ} ở {TP} từ HH:MM đến HH:MM đi {phương tiện}: {điểm}.[ Ngân sách {số}đ/người.]`); kiểm đầu vào, báo lỗi tiếng Việt; `doc_diem()` đọc `poi_master.csv` (chỉ đọc).
- **`hoi_thoai.py`** — `la_hoi_lai(events)` đọc ghi chú trace (không đọc output, đúng H7); `noi_tin()` đặt **tin mới trước** vì bộ tách luật lấy giờ / thứ xuất hiện đầu tiên → người dùng sửa thì giá trị mới thắng; `cau_xong_som()` điền sẵn thứ, thành phố, "Đã đi: …" (agent loại các điểm đã nhắc khỏi gợi ý).
- **`streamlit_app.py`** — callback chỉ ghi "chờ gửi", gọi agent ở một chỗ (`_xu_ly_cho_gui`) rồi vẽ lại; `threading.Lock` vì `tracing.py` giữ trạng thái chung; `APP_PASSWORD` (so sánh `hmac.compare_digest`); `MAX_LUOT` lượt / phiên; chế độ giả → báo "Chưa nối model thật".

## 3. Đã kiểm

| Kiểm | Kết quả |
|---|---|
| `python web/test_ghep_cau.py` | 15/15 OK — gồm: hỏi lại → nối tin → ra lịch HN; "xong sớm" + "Đã đi" không gợi ý lại điểm đã đi |
| Streamlit `AppTest` (chat, hỏi lại + nối, nút "Còn thời gian?", sửa câu, form, hết lượt, reset, mật khẩu) | Đều đúng |
| Server thật bằng lệnh `Procfile` | health = ok |
| `python scripts/kiem_hop_dong.py` · `python run.py check` | 0 lỗi · không thấy vấn đề |
| Dòng ngân sách của N2 hiện trên web | Có ("Chi phí ước tính … → trong ngân sách") |
| Output thật run-1 của câu demo B01, B05, B07 | Khớp mô tả slide 4. **B07** có thêm dòng "Không có dữ liệu về: … Quán Gió Tam Đảo" (model trích thừa tên) → quay video dùng câu ngắn: *"14:05 chiều Thứ Bảy đang ở Thảo Cầm Viên thì mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?"* |

## 4. Còn phải làm (Đợt 2)

| Giờ | Việc | Chờ ai | Ai chờ mình |
|---|---|---|---|
| ≤30′, tuỳ | Railway (§6) | — | — |
| **08:00–09:30** | Video 30s trên bản hiện tại (model thật): B01 có ngân sách + B05 (hoặc chat hỏi lại); mở thử ẩn danh → link cho N3; điền link vào README hàng 7 + slide 4 | — | **N3** (CP3 10:00) |
| **09:30–10:30** | 3 người dùng thử trên bản hiện tại, ≥1 việc có giờ trống / thành phố ít điểm (§5) → `validation/log.md` | — | slide 8 |
| 10:00–10:20 | Họp chọn nhóm lỗi run-2 | cả nhóm | |
| **11:30–12:10** | Chấm run-2 **B16–B30** → `eval/grading-run2-tiep.csv` (`id,pass,ghi_chu`; trượt ghi metric + 1 câu lý do) | N3 push `run-2.csv` (11:15) | N3 (gộp 12:10) |
| 13:15–13:45 | (tuỳ) 1 người thử bản có B-lite + data mới; xem lại câu chữ nút "Còn thời gian?" (trùng một phần B-lite); chạy lại `python web/test_ghep_cau.py` | N3, N2 merge 13:15 | |
| **13:30–14:15** | Điền ô `__` slide 5–8 → `demo-slides.pdf` ở thư mục gốc + video dự phòng | N3 `eval/README.md`, `report.md` (≈12:30) · N2 `cost-estimate.md` (13:30) | **Đội trưởng** (CP4 14:30) |
| sau demo → 23:59 | Chấm run-3 (10 câu) · `reflection/<ten>.md` | N3 chạy run-3 | N3 |

## 5. Kịch bản người dùng thử — 5 nhịp, ~10 phút / người

1. **Làm quen** — không giới thiệu tính năng.
2. **Bối cảnh** — "lần gần nhất bạn lên lịch đi chơi tự túc cho nhóm".
3. **Giao việc theo kết quả** (không chỉ nút):
   - Việc 1: "Lên lịch Thứ Bảy ở thành phố bạn sắp đi, 3 nơi, đi cả ngày" (có giờ trống).
   - Việc 2: "Bạn đang đi thì mưa — tìm chỗ trú gần đó" (nhánh gợi ý).
   - Việc 3 (≥1 người): thành phố ít điểm (Sa Pa / Hạ Long / Tam Đảo).
4. **Quan sát** — làm gì đầu tiên (chat hay form?), chỗ do dự, chỗ hiểu sai ("(dự phòng)", "không có dữ liệu", nút "Còn thời gian?").
5. **Hỏi sau** — "Nếu mai không được dùng nữa: rất tiếc / hơi tiếc / không sao?"

Ghi **vai**, không ghi tên; trích **nguyên văn thật**, không tự bịa.

## 6. Railway (làm tay, tối đa 30 phút — quá thì demo localhost)

1. Push code lên `main` trước. 2. railway.app → New Project → Deploy from GitHub repo. 3. *Variables*: `MODEL_PROVIDER=openai`, `MODEL_NAME=gpt-4.1-mini`, `API_KEY`, `APP_PASSWORD` (mật khẩu mới), `MAX_LUOT=10` — **không** đưa key vào repo / slide / ảnh. 4. *Settings → Networking → Generate Domain* → mở ẩn danh, nhập mật khẩu, hỏi 1 câu. 5. Ghi link vào §10 khối N4 (không ghi mật khẩu).

## 7. Chạy web trên máy

```
.venv\Scripts\python -m streamlit run web/streamlit_app.py      # model thật theo .env
$env:MODEL_PROVIDER="fake"; .venv\Scripts\python -m streamlit run web/streamlit_app.py   # chế độ giả, không tốn token
```
`.venv/` nằm trong `.gitignore`, không commit.
