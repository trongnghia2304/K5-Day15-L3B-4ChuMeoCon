# 4ChuMeoCon — Xếp lịch trình một ngày nhiều điểm (Track C · Du lịch)

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md).

**Lát cắt:** một người lên lịch cho nhóm · trước chuyến đi nhập danh sách điểm và khung giờ, hoặc đang đi thì gặp mưa / quán đóng / quá đông · AI quyết định **đi điểm nào, theo thứ tự nào** sao cho mọi điểm đang mở lúc đến (xếp lịch, hoặc chọn 1–3 điểm thay thế đang mở quanh đó) · người lên lịch nhận lịch từng giờ / điểm thay thế kèm lý do để gửi cả nhóm.

**Vì sao:** khảo sát 67 người đã đi du lịch tự túc — 49/67 (73%) mệt nhất ở khâu sắp thứ tự thuận đường, 38/67 (57%) từng tới nơi thì đóng cửa / hết chỗ ([evidence/summary.md](evidence/summary.md)).

| Đọc gì | File |
|---|---|
| Canvas 7 dòng | [canvas.md](canvas.md) |
| Thiết kế, sơ đồ, chuẩn "đạt" | [spec.md](spec.md) (§4 sơ đồ · §7 chuẩn "đạt") |
| Bằng chứng pain | [evidence/summary.md](evidence/summary.md) |
| Dữ liệu chạy thử | [data/DATA_CARD.md](data/DATA_CARD.md) · `data/travel-ops/` |
| Bộ câu thử, metric | [eval/benchmark.csv](eval/benchmark.csv) · [eval/metric_spec.yaml](eval/metric_spec.yaml) · [eval/README.md](eval/README.md) |
| Hợp đồng công cụ kiểm lịch | [docs/itinerary-tool-contract.md](docs/itinerary-tool-contract.md) |

---

## Chạy trong 3 phút

Cần **Python 3.10 trở lên**. **Không cần `pip install`** — chỉ dùng thư viện chuẩn.

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

Gõ `dir` (Windows) hoặc `ls` (macOS / Linux): thấy `run.py` và `README.md` là đang đứng đúng chỗ.

**Bước 2 — Chạy bản chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Chạy bản chạy thử | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model thật | `copy .env.example .env` | `cp .env.example .env` |

**Bước 3 — Gõ thử hai câu** (sau dấu `>`; Enter 2 lần với dòng trống để thoát)

```
Thứ 7 ở Hà Nội từ 8:00 đến 17:00 đi Văn Miếu, Nhà tù Hỏa Lò, Chợ Đồng Xuân
```
→ ra **lịch từng giờ** (giờ đến / rời mỗi điểm, phút đi), lý do, điểm bị bỏ nếu không kịp.

```
14:05 chiều Thứ Bảy tụi mình đang ở Thảo Cầm Viên thì trời mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?
```
→ ra **trạng thái điểm đang đứng** và **1–3 điểm thay thế đang mở**, trong nhà, kèm phút đi và giờ đóng cửa.

Thiếu thông tin (không nói thành phố, thứ hay khung giờ) thì bản chạy thử **hỏi lại**, không đoán.

> **Đang chạy ở chế độ model giả** cho tới khi nhóm nối model thật (`.env` chưa có `MODEL_PROVIDER`). Khi đó dòng "Vì sao" ghi **"(dự phòng)"**: thứ tự / điểm gợi ý do code dự phòng chọn, không phải AI. Nối model thật: [docs/connect-model.md](docs/connect-model.md).

Trong README này lệnh viết là `python …`; máy cần `python3` hay `py` thì gõ thay.

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (gõ đầu vào, nhận kết quả, kèm số lần gọi model / công cụ / token) |
| `python run.py check` | Kiểm `eval/benchmark.csv`, `eval/metric_spec.yaml`, `TEAMS.md`. Chỉ cảnh báo, không sửa file |
| `python run.py eval --try 28` | Chạy thử cả 28 câu → `eval/run-try.csv` (không tính là một lượt) |
| `python run.py eval` | Chạy cả bộ → `eval/run-N.csv` + `traces/run-N.jsonl` (chỉ đánh số khi gọi model thật) |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt |
| `python run.py simulate --try` / `simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` |

Gói miễn phí báo hết lượt: thêm `--wait 4` sau `eval` hoặc `simulate`. Lượt có lỗi kỹ thuật: không sửa tay, chạy lại thành lượt mới.

## Chạy web

Web là **khung chat**: mỗi lượt gửi **một câu chữ** vào đúng `agent.answer(text)` như `python run.py`. Không có logic AI riêng, không tự tính giờ / tiền. `python run.py` vẫn chạy được khi chưa cài gì.

| Việc | Lệnh |
|---|---|
| **Bản online (Railway)** | https://k5-day15-l3b-4chumeocon-production.up.railway.app/ — cần mật khẩu demo, hỏi nhóm |
| Cài (một lần, chỉ web cần) | `python -m pip install -r requirements.txt` |
| Chạy trên máy | `streamlit run web/streamlit_app.py` → mở `http://localhost:8501` |
| Kiểm ghép câu, nối tin chat, agent đọc được câu web | `python web/test_ghep_cau.py -v` (chế độ model giả, không tốn token) |

- **Ô chat:** gõ tự do — xếp lịch ("Thứ Bảy ở Hà Nội 8h–17h, đi Văn Miếu, Hỏa Lò…") hoặc đang đi gặp mưa / quán đóng / xong sớm.
- **Nhớ ngữ cảnh khi trợ lý hỏi lại** (hợp đồng H1 v2): lượt trước agent hỏi lại → web gửi `"<tin mới>. <câu đã gửi trước>"`, vd trả lời ngắn "thứ 7, 8h đến 5h chiều" vẫn ra lịch. Các lượt khác gửi nguyên văn. Web nhận biết "hỏi lại" qua ghi chú trace của agent, không đọc output.
- **Điền nhanh bằng form:** thành phố, thứ, giờ, phương tiện, chọn điểm từ dữ liệu, ngân sách → câu dạng `Thứ Bảy ở TP.HCM từ 08:00 đến 17:30 đi xe máy: Thảo Cầm Viên, Dinh Độc Lập. Ngân sách 300000đ/người.` (ngân sách để trống thì bỏ cả câu ngân sách). Ô ngân sách gõ tay, tự chèn dấu chấm khi gõ (`1.250.000 đ`, điện thoại mở bàn phím số); câu gửi agent vẫn đúng mẫu H1 (`1250000đ/người`).
- **Sửa lịch vừa rồi:** ô chứa sẵn câu đã gửi — thêm / bỏ điểm, đổi giờ rồi gửi lại. Nút **"Còn thời gian?"** điền sẵn câu hỏi gợi ý thêm điểm (người dùng điền giờ xong và nơi đang đứng).
- **Danh sách điểm có dữ liệu** theo thành phố — nơi ngoài danh sách trợ lý báo "không có dữ liệu".
- Kết quả hiện đúng câu chữ output của agent (H7), **ẩn mã điểm `[POI_…]`** (chỉ ở web — output gốc, eval, trace vẫn giữ mã), kèm câu đã gửi và số token đã dùng.
- Dùng được trên điện thoại: ô chat luôn hiện ở đáy màn hình, thanh **Điền nhanh** mở bằng nút » góc trên bên trái.

Biến môi trường (trong `.env` ở máy, hoặc *Variables* trên Railway — **không** ghi vào repo):

| Biến | Dùng làm gì |
|---|---|
| `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY` | Nối model, như [docs/connect-model.md](docs/connect-model.md). Trống = chế độ giả, web báo "chế độ model giả" |
| `APP_PASSWORD` | Mật khẩu vào web. Để trống chỉ khi chạy trên máy mình |
| `MAX_LUOT` | Số lượt hỏi tối đa mỗi phiên trình duyệt (mặc định 10) — chặn tốn token khi để link công khai |

**Railway:** New Project → Deploy from GitHub repo → tab *Variables* thêm 5 biến trên (dùng model rẻ) → *Settings → Networking → Generate Domain*. Railway tự cài `requirements.txt` và chạy lệnh trong `Procfile`.

## Bản chạy thử làm gì

Hình dạng: **workflow cố định** có một bước phân luồng (chi tiết và sơ đồ ở [spec.md](spec.md) §4).

| Bước | Ai làm | File |
|---|---|---|
| Tách thành phố, thứ, khung giờ, điểm, mưa / nắng… từ câu chat | Code; **chỉ khi còn thiếu** mới gọi model trích | `codebase/agent.py`, `codebase/prompts/trich_yeu_cau.md` |
| Khớp tên điểm với dữ liệu; tên không có trong dữ liệu → nói "không có dữ liệu" | Code | `search_pois` trong `codebase/tools.py` |
| **Xếp lịch:** chọn thứ tự đi + điểm bỏ | **Model** (quyết định trung tâm) | `codebase/prompts/xep_thu_tu.md` |
| Tính giờ đến / rời, liệt kê vi phạm; có vi phạm → model sửa (≤ 2 vòng) → còn thì code bỏ điểm | Code | `lap_lich`, `liet_ke_vi_pham` |
| Cổng kiểm cuối: chỉ lịch `valid` mới hiện | Code | `kiem_lich_trinh` |
| **Gợi ý thay thế:** code lọc điểm đang mở, hợp mưa / nắng / loại; model chọn 1–3 | Code lọc, **model chọn** | `goi_y_diem`, `codebase/prompts/goi_y.md` |
| Tin nhắn có ngân sách → 1 dòng cuối "Chi phí ước tính … (tự ước tính) → trong / vượt ngân sách"; không lọc / bỏ điểm theo tiền | Code | `codebase/ngan_sach.py`, `uoc_chi_phi` |
| Định dạng câu trả lời; chặn đặt bàn / nhắn tin / "bỏ qua kiểm tra" | Code | `codebase/agent.py` |

AI **không** đặt bàn, mua vé, thanh toán hay nhắn tin; mọi giờ và phút do code tính từ dữ liệu.

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm (chọn thứ tự / chọn điểm thay thế) | **Giả ở CP2** → thật từ CP3 | Model: `gpt-4.1-mini` (OpenAI) từ run-1. Chế độ giả dùng thứ tự / lựa chọn dự phòng bằng code, output ghi "(dự phòng)" |
| Tên điểm, địa chỉ, giờ mở cửa | Theo nguồn công khai, xem nhãn trong `data/travel-ops/` | Dòng `estimated` là tự ước tính — xem [data/DATA_CARD.md](data/DATA_CARD.md) |
| Thời gian chơi mỗi điểm, một số chặng di chuyển | Tự ước tính | `avg_duration_min`, `source_type = estimated` |
| Sự cố đang xảy ra (mưa, quán đông, đóng đột xuất) | **Giả lập** | `data/travel-ops/live_disruptions.csv`, nhãn `[Giả lập sự cố]` trong output |
| Vị trí người dùng | Người dùng tự nói | Không dùng GPS |

## Dùng AI vào việc gì

Nhóm dùng Claude Code để viết nháp code luồng chính, công cụ lập lịch / kiểm lịch / gợi ý, prompt, script đếm khảo sát và nháp `spec.md`; các thành viên đọc, chạy lại bằng `python run.py` / `eval --try` và sửa phần mình phụ trách. *(Nhóm bổ sung công cụ khác và người kiểm từng phần.)* Chi tiết: [docs/ai-usage.md](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | `demo-slides.pdf` ở thư mục gốc · link video: https://drive.google.com/file/d/1mumo5YJhOwXtHauAe20BVFD_fyfpwCZE/view · bản online: https://k5-day15-l3b-4chumeocon-production.up.railway.app/ |
| + | *Bonus:* người dùng thử | `validation/log.md` |
