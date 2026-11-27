# RULE.MD — QUY TẮC BẮT BUỘC KHI DÙNG AI TRIỂN KHAI DỰ ÁN (TRAVEL AI AGENT)

> **CẢNH BÁO:** Mọi AI Coding Assistant (Antigravity, Codex, Claude Code) và thành viên nhóm BẮT BUỘC tuân thủ nghiêm ngặt các quy tắc dưới đây. Vi phạm các mục từ 1 đến 3 sẽ dẫn đến **0 điểm khối đánh giá** hoặc **trừ 10 điểm trực tiếp** theo quy chế Hackathon.

---

## 1. DANH SÁCH FILE & NỘI DUNG TUYỆT ĐỐI KHÔNG ĐƯỢC SỬA (LOCKED)

AI tuyệt đối **không được chỉnh sửa, ghi đè hoặc xóa** các thành phần sau (đã chốt từ CP2):
1. **`spec.md` — Mục `§7` (Chuẩn "Đạt" bằng số):** Giữ nguyên nguyên văn tỷ lệ `%` đạt và các điều kiện cứng. Không được hạ chuẩn cho khớp với kết quả chạy thực tế.
2. **`eval/metric_spec.yaml`:** Không sửa định nghĩa metric, công thức chấm hay ngưỡng đạt.
3. **Các dòng cũ trong `eval/benchmark.csv`:** Chỉ được **thêm mới (append)** các câu thử ở cuối file cho đủ **20–30 câu** (phủ 4 thành phố `HN`, `HCM`, `DN`, `HUE`). Tuyệt đối **không sửa cột `expected`** của các câu đã có từ CP2 và **không xóa** các câu thử bị trượt.
4. **`eval/run-1.csv` (sau khi đã chạy Lượt 1):** Không sửa tay nội dung output hay cột `pass` để làm đẹp số liệu. Mọi cải tiến ở Lượt 2 phải chạy lại toàn bộ `benchmark.csv` và xuất ra file mới `eval/run-2.csv`.
5. **Cấu trúc lõi `run.py` và format `TEAMS.md`:** Không thay đổi tên lệnh CLI (`python run.py check`, `eval`, `score`, `simulate`) và không phá vỡ định dạng bảng thành viên trong `TEAMS.md`.

---

## 2. BẢO MẬT API KEY & DỮ LIỆU CÁ NHÂN (VI PHẠM = -10 ĐIỂM)

1. **Cấm tuyệt đối lộ Secret/Key:**
   - Không viết cứng (hardcode) API key, token, mật khẩu vào bất kỳ file code (`.py`, `.json`, `.yaml`, `.md`) hay cấu hình Railway nào.
   - Luôn đọc key qua biến môi trường (`os.getenv(...)` từ `.env` ở local hoặc *Variables* trên Railway).
   - Kiểm tra `.gitignore` luôn chứa `.env` trước mọi lệnh `git add`.
2. **Ẩn danh 100% dữ liệu người dùng:**
   - Mọi file trong `evidence/survey/` và `evidence/interviews/` **phải xóa sạch** các cột/thông tin định danh cá nhân (Họ tên, Email, Số điện thoại, Zalo, mã học viên). Chỉ sử dụng mã ẩn danh (`S1, S2...` hoặc `P1, P2...`).
   - Không sử dụng mã đặt chỗ, vé máy bay, hóa đơn thật của bất kỳ ai trong `data/` hoặc `eval/`.

---

## 3. RÀNG BUỘC KỸ THUẬT & CHỐNG BỊA ĐẶT (TRACK C1 — DU LỊCH)

1. **Phạm vi cứng 4 thành phố (`HN`, `HCM`, `DN`, `HUE`):**
   - Hệ thống chỉ lập lịch trình chi tiết cho 4 mã thành phố có trong `data/places.json`: Hà Nội (`HN`), TP.HCM (`HCM`), Đà Nẵng (`DN`), Huế (`HUE`).
   - **Nguyên tắc G10 (Bắt buộc):** Nếu người dùng hỏi địa điểm ngoài 4 thành phố trên (ví dụ: Đà Lạt, Sa Pa, Phú Quốc...) hoặc thiếu thông tin vị trí/khung giờ quan trọng, Agent **phải từ chối lịch sự, nêu rõ giới hạn dữ liệu hoặc hỏi lại 1 câu ngắn** — tuyệt đối không dùng trí nhớ của LLM để bịa địa điểm.
2. **Dữ liệu & Tính toán 100% qua Công cụ (Zero Hallucination):**
   - AI không được tự nhẩm thời gian di chuyển, tiền bạc hay tự nhớ giờ mở cửa quán.
   - Mọi địa điểm phải lấy từ `data/places.json` qua `tra_diem_choi`; mọi quãng đường/thời gian chạy xe phải tra từ `data/travel_matrix.json` qua `uoc_thoi_gian_di`.
   - Trước khi trả về lịch trình cuối cùng cho người dùng, Agent **bắt buộc** gọi hàm kiểm tra chéo `kiem_lich_trinh` để đảm bảo **0 vi phạm** giờ mở cửa, giờ nghỉ trưa, chồng lấn thời gian di chuyển hoặc vượt ngân sách.
   - Khi người dùng không nêu sở thích cụ thể, hệ thống tự động lọc theo nhãn `is_must_visit: true` để xếp lịch trình cân bằng tiêu chuẩn.
3. **Chạy độc lập (Offline-ready cho Eval & Simulate):**
   - Lõi `codebase/` phải chạy độc lập 100% trên dữ liệu nội bộ (`data/places.json`, `data/travel_matrix.json`), không gọi API bản đồ/thời tiết/đặt vé bên thứ ba lúc thực thi để đảm bảo lệnh `python run.py eval` và `python run.py simulate` chạy ổn định, tái lập được.

---

## 4. PHÂN QUYỀN THƯ MỤC CHO 4 THÀNH VIÊN (CHỐNG XUNG ĐỘT GIT)

Mỗi AI Agent chỉ được phép tạo/sửa file trong phạm vi thư mục được giao cho thành viên đó, **cấm sửa chéo file của người khác**:
- **Người 1 (Evidence, Benchmark & Slide khung):** `evidence/`, `spec.md` (`§1–§3`), `eval/benchmark.csv`, `eval/metric_spec.yaml`, khung `demo-slides.pdf`.
- **Người 2 (Data 4 thành phố, OSRM, Tools & Cost):** `data/places.json`, `data/travel_matrix.json`, `data/DATA_CARD.md`, `codebase/tools.py`, `cost/`.
- **Người 3 (AI Core, Guardrails & Eval Report):** `codebase/ai.py`, `codebase/agent.py`, `spec.md` (`§4–§5`), `eval/run-1.csv`, `eval/run-2.csv`, `eval/report.md`, `eval/README.md`.
- **Người 4 (Web UI Streamlit, Railway & User Validation):** `app.py`, `Procfile`, `requirements.txt`, `README.md`, `validation/log.md`.

---

## 5. KỶ LUẬT CODE & KIỂM TRA TRƯỚC KHI COMMIT

1. **Tiết kiệm Token:** Chỉ đọc đúng file liên quan tới task hiện tại (dùng `head` khi kiểm tra CSV/JSON lớn), sửa code theo diff nhỏ, không viết lại toàn bộ file nếu không cần thiết.
2. **Không commit file nháp cá nhân:** Tuyệt đối không đưa `PROGRESS.md`, `task_plan.md`, `findings.md`, `progress.md` hay thư mục `.agent/skills/` lên Git chung (chặn qua `.git/info/exclude`).
3. **Bắt buộc tự kiểm (Verification):**
   - Sau khi sửa `data/` hoặc `eval/benchmark.csv`, phải chạy `python run.py check` xác nhận không có lỗi trước khi báo hoàn thành.
   - Đảm bảo `app.py` (Streamlit) chỉ đóng vai trò giao diện gọi thẳng vào `codebase/agent.py`, không viết tách biệt 2 logic AI khác nhau.