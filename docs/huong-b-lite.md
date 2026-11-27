# Đề xuất B-lite — gợi ý thêm điểm khi lịch còn trống giờ

> Người viết: N4 (Tiệp) · 28/11 · Trạng thái: **ĐÃ CHỐT LÀM — 02:00 28/11** (mục 9). Lịch việc và người làm: [`phan-cong-cp3-cp4.md`](phan-cong-cp3-cp4.md) → **Đợt 2**.
> N3 đã kiểm mục 7 trên `eval/run-1.csv` (model thật, 02:00): nhánh bật ở **5 câu** B01, B03, B04, B29, B30 — chi tiết ở cuối mục 3.
> Đọc kèm: [`phan-cong-cp3-cp4.md`](phan-cong-cp3-cp4.md) · [`hop-dong-du-lieu.md`](hop-dong-du-lieu.md) · `spec.md` §4 · `rule.md`.

## 1. Tóm tắt trong 5 dòng

- **Vấn đề:** người dùng chọn 3 điểm cho khung 08:00–17:00 → lịch xong lúc 11:59, còn 5 tiếng trống, hệ thống im lặng.
- **B-lite:** khi lịch **đã qua cổng kiểm** và còn trống **≥ 60 phút**, trợ lý **gợi ý 1–3 điểm** đang mở, gần điểm cuối, hợp sở thích — **không tự chèn vào lịch**. Người dùng muốn thêm thì gửi lại câu, trợ lý xếp + kiểm giờ như bình thường.
- **Không cần data mới, không sửa `tools.py`**: dùng lại `goi_y_diem` (đã lọc theo giờ mở, vùng, loại, mưa / nắng).
- **Việc chính rơi vào N3** (~1,5–2 giờ): 1 nhánh trong `agent.py` + 1 prompt mới + `spec.md` §4–§6, §9 + H7 v2.
- **Vẫn đúng lát cắt CP2**: lát cắt đã có "chọn 1–3 điểm thay thế đang mở quanh đó" — B-lite là cùng quyết định đó, dùng ở lúc lịch xong sớm.

## 2. B-lite là gì — và không là gì

| | |
|---|---|
| **Là** | Thêm **1 điểm quyết định** cho model trong workflow cố định đang có (`spec.md` §4): code lọc ứng viên → model chọn 1–3 + lý do → code định dạng |
| **Không phải RAG** | Không có vector / tìm theo nghĩa; code tra CSV theo cột |
| **Không phải agent tự chủ** | Code quyết khi nào bật nhánh, gọi công cụ nào; model chỉ chọn trong danh sách code đưa |
| **Không làm** | Không tự chèn điểm vào lịch · không gợi ý điểm ngoài `poi_master.csv` · không lọc theo ngân sách · không thêm / sửa data · không đổi định dạng các dòng lịch |

Mô tả trên slide: *"Workflow cố định, model quyết định ở 4 điểm (trích yêu cầu khi thiếu · xếp thứ tự + tự sửa ≤2 vòng · chọn điểm thay thế · gợi ý lấp giờ trống), code kiểm mọi giờ giấc."*

## 3. Vì sao "gợi ý riêng" chứ không "chèn vào lịch" — có số

Đã chạy 28 câu thử ở **chế độ model giả** (28/11, lệnh ở mục 7). Câu ra lịch hợp lệ, **không bỏ điểm**, còn trống ≥ 60 phút:

| Câu | Khung | Xong lúc | Trống | `pass_criterion` (rút gọn) | Nếu CHÈN điểm vào lịch |
|---|---|---|---|---|---|
| B01 thuong | 08:00–17:30 | 14:48 | 162′ | Đủ 5 điểm; Bảo tàng Lịch sử trước 11:00 / sau 13:00; Dinh Độc Lập trước 15:30; không quay vòng | Có thể lệch giờ / quay vòng → **trượt** |
| B03 thuong | 07:30–17:30 | 15:18 | 132′ | Gom 4 điểm Hải Châu liên tiếp; Ngũ Hành Sơn trước 17:00 | Điểm chèn giữa cụm → **trượt** |
| B04 thuong | 08:30–17:00 | 13:23 | 217′ | Không đi đi về về; Cơm gà sau 10:30 | Dễ sinh vòng → **trượt** |

Các câu có bỏ điểm (B02, B05, B20, B22, B25, B26, B27) **không bật nhánh** (điều kiện ở mục 4).

→ **Gợi ý tách riêng, lịch giữ nguyên từng dòng** thì 3 câu trên vẫn chấm theo đúng lịch cũ. Output chỉ dài thêm mục gợi ý.
⚠️ Số trên từ **chế độ giả** (thứ tự tham lam). N3 kiểm lại trên `eval/run-1.csv` (model thật) trước khi làm — mục 7.

**Kết quả kiểm trên `run-1.csv` (model thật, `run-1@20261128-010117`):**

| Câu | Khung | Xong lúc | Trống | Bật nhánh? |
|---|---|---|---|---|
| B01 thuong | 08:00–17:30 | 14:56 | 154′ | Có |
| B03 thuong | 07:30–17:30 | 15:18 | 132′ | Có |
| B04 thuong | 08:30–17:00 | 13:30 | 210′ | Có |
| B29 thuong | 08:00–17:30 | 14:56 | 154′ | Có — `pass_criterion` đòi dòng `Chi phí ước tính:` là **dòng cuối** → mục gợi ý phải nằm trước nó (đúng thiết kế mục 4) |
| B30 kho | 08:00–17:30 | 14:56 | 154′ | Có — như B29 |
| B02, B05, B06, B25 | | | | Không (có bỏ điểm) |

Không `pass_criterion` nào của câu xếp lịch cấm gợi ý thêm. Câu B07–B15 có "chỉ gợi ý …" nhưng thuộc **nhánh gợi ý**, B-lite không chạy ở nhánh đó.

## 4. Luồng chạy

```
… bước 8 cổng kiem_lich_trinh (như cũ) → lịch hợp lệ
        │
        ▼
[CODE] Bật nhánh khi ĐỦ cả 3:
       (a) lịch có ≥1 điểm  (b) danh sách bỏ = rỗng  (c) ket_thuc − xong_luc ≥ 60 phút
        │ không → output như cũ (không gọi thêm model)
        ▼ có
[CODE] Ứng viên = goi_y_diem(city, thu, at_time = xong_luc, from_zone = vùng điểm cuối, mode,
                             exclude = các điểm đã xếp + đã bỏ, max_travel_min = 30, limit = 6)
       rồi giữ ứng viên còn đủ thời gian: đi + avg_duration_min ≤ ket_thuc và mở đủ lâu (tools._open_for)
        │ rỗng → 1 dòng "Còn trống …, dữ liệu ở {TP} chưa có điểm phù hợp để gợi ý thêm." (không gọi model)
        ▼
[MODEL] prompts/lap_gio_trong.md: chọn 1–3 ứng viên + lý do → JSON {"chon": [...], "ly_do": "..."}
        (chỉ id trong danh sách; JSON lỗi → code chọn ứng viên gần nhất, ghi "(dự phòng)")
        ▼
[CODE] Thêm mục gợi ý TRƯỚC dòng "Bạn xem lại rồi tự gửi nhóm…"; dòng ngân sách (N2) vẫn là dòng cuối
```

- Sở thích: model đọc từ nguyên văn tin nhắn (`<tin_nhan>`), không cần cột data mới.
- Ngưỡng 60 phút là hằng số có tên trong code (`NGUONG_TRONG_PHUT = 60`), ghi vào `spec.md` §4.
- Bật nhánh **chỉ bằng code**, không để model quyết → câu cũ không rẽ nhầm khi dùng model thật.

## 5. Đầu ra

Minh hoạ (giờ giấc ước chừng, chưa chạy với model thật):

```
Lịch HN — Thứ Bảy, 08:00–17:00
1. 08:00–09:15 · [POI_HN_04] Di tích Nhà tù Hỏa Lò
2. 09:19–10:19 · [POI_HN_06] Chợ Đồng Xuân (đi 4 phút)
3. 10:29–11:59 · [POI_HN_01] Văn Miếu - Quốc Tử Giám (đi 10 phút)
Tổng di chuyển: 14 phút · xong lúc 11:59
Vì sao xếp như vậy: …
Còn trống 11:59–17:00 (301 phút). Có thể ghé thêm — trợ lý gợi ý, CHƯA xếp vào lịch:
  + [POI_HN_03] Hoàng thành Thăng Long — đi 9 phút từ điểm cuối · mở đến 17:00 · chơi khoảng 90 phút
  + [POI_HN_02] Bảo tàng Dân tộc học Việt Nam — đi 14 phút · mở đến 17:30 · chơi khoảng 105 phút
Vì sao gợi ý: cùng chủ đề lịch sử với Văn Miếu, đang mở chiều Thứ Bảy, gần điểm cuối.
Muốn thêm điểm nào thì gửi lại câu kèm tên điểm đó — trợ lý sẽ xếp lại và kiểm giờ mở cửa.
Bạn xem lại rồi tự gửi nhóm — mình không gửi tin hay đặt chỗ.
```

**Hợp đồng H7 v2 (thêm, không đổi dòng cũ):**

| Loại dòng | Định dạng |
|---|---|
| Đầu mục | `Còn trống HH:MM–HH:MM (X phút). Có thể ghé thêm — trợ lý gợi ý, CHƯA xếp vào lịch:` |
| Một gợi ý | `  + [POI_ID] {Tên} — đi X phút từ điểm cuối · mở đến HH:MM · chơi khoảng Y phút` — bắt đầu bằng `  + ` (KHÔNG theo mẫu `{n}. HH:MM–HH:MM ·` của dòng lịch, để code chấm metric không đọc nhầm thành điểm trong lịch) |
| Lý do | `Vì sao gợi ý: …` (chế độ giả có `(dự phòng)`) |
| Không có ứng viên | `Còn trống HH:MM–HH:MM (X phút), dữ liệu ở {TP} chưa có điểm phù hợp để gợi ý thêm.` |

**Web (A+):** không sửa code — web hiện nguyên văn. Người dùng thêm điểm qua ô "Sửa câu đã gửi" có sẵn rồi gửi lại.

## 6. Việc từng người — ai bị ảnh hưởng

| Người | Việc | Ước giờ | Mức ảnh hưởng |
|---|---|---|---|
| **N3** | (1) Kiểm mục 7 trên `run-1.csv` · (2) nhánh trong `agent.py` (~30–50 dòng, sau bước 8, dùng `goi_y_diem`, `_open_for`) · (3) `codebase/prompts/lap_gio_trong.md` · (4) chạy `python run.py eval --try 28` (không tính lượt) so output trước / sau · (5) `spec.md` §4 (sơ đồ, hằng số 60′), §5 (kịch bản "lịch xong sớm ≥60′" → đi qua B01/B03/B04, không có câu thử riêng), §6 (đường đi), §9 · (6) H7 v2 trong `hop-dong-du-lieu.md` + `scripts/kiem_hop_dong.py` nếu kiểm dòng output · (7) §10 | 1,5–2 giờ | **Cao** |
| **N4** | Không sửa code web. README (bảng "Bản chạy thử làm gì"), slide 3 (thay N1) + 4 (demo B-lite) + 8, `validation/log.md` (giao 1 việc có giờ trống), nhật ký N4, §10 | 30–45 phút | Thấp |
| **N2** | Không sửa data / `tools.py`. `cost/cost-estimate.md`: ghi nhánh B-lite gọi thêm **1 lượt model** khi bật (đọc token thật từ run có B-lite nếu có) | 10 phút | Thấp |
| **N1** | Không phải làm gì; slide 3 do N4 thêm 1 ý | 0 | Rất thấp |
| **Đội trưởng** | Chốt mục 9; thêm việc + mốc vào `phan-cong-cp3-cp4.md`; `rule.md` 3 thêm 1 dòng: "nhánh lấp giờ trống chỉ gợi ý, không tự chèn, chỉ chọn trong ứng viên code lọc" | 10 phút | Thấp |

**Không ai được sửa:** `spec.md` §7, `eval/metric_spec.yaml`, `eval/benchmark.csv` (không thêm câu thử — `rule.md` 1.3), `data/` cũ, `run.py`, các `run-*` / `simulate-*` / `traces` đã chạy.

## 7. Kiểm tra bắt buộc

| Khi | Kiểm | Ai |
|---|---|---|
| Trước khi viết code | Trên `eval/run-1.csv`: câu nào ra lịch, không bỏ điểm, `ket_thuc − xong lúc ≥ 60′` → danh sách câu sẽ có thêm mục gợi ý. Khớp hay khác bảng mục 3 | N3 |
| Sau khi viết code | `python run.py eval --try 28` → mọi câu: **các dòng lịch giống hệt trước** (chỉ thêm mục gợi ý ở câu bật nhánh) | N3 |
| Trước push | `python scripts/kiem_hop_dong.py` = 0 lỗi · `python run.py check` · `python web/test_ghep_cau.py` | người push |
| Demo | Web: 1 câu 3 điểm khung dài (HN / HCM / Huế / ĐN — thành phố 5 điểm gợi ý được rất ít) | N4 |

Lệnh N4 đã dùng để ra bảng mục 3 (chế độ giả): chạy `agent.answer` cho từng `input` trong `eval/benchmark.csv`, so `xong lúc` với giờ kết thúc ở dòng `Lịch …`.

## 8. Rủi ro và cách giảm

| Rủi ro | Mức | Cách giảm |
|---|---|---|
| Model thật cho thứ tự khác chế độ giả → số câu bật nhánh khác mục 3 | Vừa | Kiểm trên `run-1.csv` trước (mục 7) |
| B01 / B03 / B04 dài thêm → người chấm hiểu nhầm | Thấp–vừa | Đầu mục ghi rõ "CHƯA xếp vào lịch"; dòng gợi ý dùng `  + `, không giống dòng lịch |
| Code chấm metric (`thuan_duong`, `khong_vi_pham_gio`) đọc nhầm dòng gợi ý | Vừa | N3 xem cách code chấm tìm dòng lịch; giữ mẫu `  + [POI_ID]` khác mẫu `{n}. HH:MM–HH:MM ·` |
| Không có câu thử riêng cho B-lite | Cao (không gỡ được — `rule.md` 1.3) | Nói thẳng trên slide 5: "B-lite đánh giá qua người dùng thử + trace, không có trong run" |
| Thành phố 5 điểm gần như không có gợi ý | Thấp | Dòng "dữ liệu ở {TP} chưa có điểm phù hợp"; demo ở thành phố ≥10 điểm; mở rộng data để slide 8 |
| Thêm token / chi phí | Thấp | Chỉ 1 lượt gọi khi bật; không có ứng viên thì không gọi model |
| Hỏng sát giờ nộp | Thấp | 1 commit riêng cho B-lite → `git revert` là về bản cũ |

**Không cào thêm data** trước CP4: thêm dòng vào `poi_master.csv` làm đổi ứng viên của các câu gợi ý (B07–B19, B28) → run-1 / run-2 không so được; giờ mở cửa cần 2 nguồn / điểm (5–8 giờ cho 50 điểm). Để slide 8: "mở rộng 94 → ~300 điểm, mỗi thành phố ≥20, đối chiếu 2 nguồn".

## 9. Nhóm cần chốt

1. **Làm B-lite không?** ☑ Có ☐ Không (để slide 8)
2. **Lúc nào?**
   - ☑ **Sau khi commit `run-2`.** N3 viết trên nhánh `feat/b-lite` (08:30–09:15 và 11:30–12:10), **merge 13:15 sau khi N2 chạy xong `simulate`** → run-2 và mô phỏng chi phí đo đúng một cấu hình. Slide ghi rõ "run-2 đo trên bản chưa có B-lite". **run-3** trên bản cuối chạy sau demo (trước 23:59), ghi vào §10 "Sau CP4".
   - ☐ Trước run-2.
3. **N3 nhận làm?** ☑ Có.
4. **Mở rộng data cùng đợt:** ☑ Có — thêm điểm mới (chỉ **thêm dòng**, không sửa dòng cũ) cho HN, HCM, DN, HUE, merge cùng lúc với B-lite (13:15), sau `simulate`. Luật: `rule.md` 1.7 (bản mới) · hợp đồng H6 v2, H14 · việc: `phan-cong-cp3-cp4.md` Đợt 2. Thay cho câu "Không cào thêm data trước CP4" ở mục 8: vẫn đúng là **không** thêm trước run-2.
5. **A+ (web chat, H1 v2):** ☑ N3 duyệt — giữ tiền tố `hỏi lại` trong `note(...)`; hợp đồng H1 v2 trong `hop-dong-du-lieu.md`.

## 10. Liên quan

- **A+ (web chat) — đã xong ở `web/`, cần N3 duyệt H1 v2:** ô chat gửi nguyên văn; **riêng khi lượt trước agent hỏi lại** (trace có ghi chú bắt đầu bằng `hỏi lại`) thì web gửi `"<tin mới>. <câu đã gửi trước>"`. Xin N3 **giữ nguyên tiền tố `hỏi lại`** của `note(...)` trong `agent.py` — web dựa vào nó. Không đổi eval (`run.py eval` không qua web).
- **Lỗi phát hiện khi thử (N3 xem):** `"Thứ Bảy ở Hà Nội …: Văn Miếu, Lăng Chủ tịch Hồ Chí Minh"` → bộ tách luật chọn thành phố **HCM** (bí danh dài nhất `ho chi minh` nằm trong tên Lăng) → loại Văn Miếu → hỏi lại "những điểm muốn đi". Lỗi ở `_rule_parse` (`agent.py`), chế độ giả chắc chắn gặp; model thật có thể đỡ.
- Nhật ký phần N4: [`n4-web-demo-nhat-ky.md`](n4-web-demo-nhat-ky.md).
