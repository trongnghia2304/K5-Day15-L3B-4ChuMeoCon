# Chấm thử độc lập 5 output

Các output bên dưới được tạo từ luồng model giả hiện tại để thử cách chấm. Đây chưa phải lượt `eval` chính thức; không chép điểm sang lượt chạy thật khi chưa đọc output của lượt đó.

**Phiếu của Nguyễn Văn Hiếu:** các điểm và lý do bên dưới do coding agent soạn nháp theo `pass_criterion` và ba metric có thể đọc trực tiếp; **Hiếu đã kiểm lại và duyệt**. `thuan_duong` cần code tính riêng như PDF hướng dẫn.

**Người chấm độc lập: Nguyễn Nghiêm Khánh Tiệp** — chấm trên phiếu mù `eval/calibration-5-blind.md` lúc 19:20 27/11/2026, chưa xem phiếu của Hiếu; AI soạn nháp, Tiệp đã đọc lại và duyệt từng câu. Chi tiết: [`calibration-5-tiep.md`](calibration-5-tiep.md). **Khớp 5/5.**

| ID | Nguyễn Văn Hiếu (1/0) | Người chấm độc lập — Tiệp (1/0) | Khớp? | Nhận xét |
|---|---|---|---|---|
| B01 | 1 | 1 | ✓ | Đủ 5 POI; bảo tàng bắt đầu 10:04, Dinh 11:27; không quay lại Đa Kao. Cơm tấm lúc 14:03 là điểm UX cần xem lại nhưng không vi phạm `pass_criterion`. Cả hai cùng ghi: "xếp trước 11:00" chưa rõ là bắt đầu hay kết thúc (bảo tàng xong 11:19). |
| B05 | 1 | 1 | ✓ | Bỏ cả hai điểm đóng Thứ Hai, nói lý do và gợi ý điểm thay thế mở cửa. Tiệp ghi thêm: lịch xong 12:10 nhưng không chèn điểm thay thế. |
| B07 | 1 | 1 | ✓ | Ba gợi ý đều `rain_safe=True`, trong nhà, mở lúc đến; không gợi ý Đường sách. Cả hai cùng ghi: output nhắc hai nơi không có trong câu hỏi ở dòng "không có dữ liệu" — lỗi nội dung cần sửa, nhưng chưa bị `pass_criterion` hiện tại cấm. |
| B21 | 1 | 1 | ✓ | Không xếp bảo tàng đóng Thứ Hai, không làm giả giờ mở và có điểm thay thế đang mở. |
| B23 | 1 | 1 | ✓ | Hỏi lại thành phố/khu vực và giờ, không bịa ba quán. |

**Giới hạn của lượt chấm thử:** cả 5 output đều đạt nên chưa thử được chỗ dễ lệch (B01). Các `pass_criterion` B01, B05, B07, B21 cần làm rõ trước lượt eval chính thức (ghi changelog `spec.md` §10).

## B01 — thuong

**Input:** Thứ Bảy ở TP.HCM từ 08:00 đến 17:30 đi xe máy: Thảo Cầm Viên, Bảo tàng Lịch sử TP.HCM, ăn trưa Cơm tấm Ba Ghiền, chiều đi Dinh Độc Lập rồi Đường sách Nguyễn Văn Bình. Xếp thứ tự thuận đường và khớp giờ mở cửa giúp mình.

**Pass criterion:** Đủ 5 điểm; Bảo tàng Lịch sử xếp trước 11:00 hoặc sau 13:00; Dinh Độc Lập trước 15:30; không quay vòng Đa Kao–Phú Nhuận–Đa Kao.

**Current output (fake model):**

    Lịch HCM — Thứ Bảy, 08:00–17:30
    1. 08:00–10:00 · [POI_HCM_01] Thảo Cầm Viên Sài Gòn
    2. 10:04–11:19 · [POI_HCM_02] Bảo tàng Lịch sử TP.HCM (đi 4 phút)
    3. 11:27–12:57 · [POI_HCM_03] Dinh Độc Lập (đi 8 phút)
    4. 13:01–13:46 · [POI_HCM_07] Đường sách Nguyễn Văn Bình (đi 4 phút)
    5. 14:03–14:48 · [POI_HCM_12] Cơm tấm Ba Ghiền (đi 17 phút)
    Tổng di chuyển: 33 phút · xong lúc 14:48
    Vì sao xếp như vậy: (dự phòng) Code xếp theo điểm bắt đầu chơi được sớm nhất.
    Bạn xem lại rồi tự gửi nhóm — mình không gửi tin hay đặt chỗ.

## B05 — kho

**Input:** Thứ Hai tuần tới nhóm 4 người đi ô tô ở Hà Nội từ 08:30 đến 17:00, định đi Hoàng thành Thăng Long, Bảo tàng Dân tộc học, Văn Miếu, ăn trưa Bún chả Hương Liên và Chợ Đồng Xuân. Lên lịch giúp mình.

**Pass criterion:** Không xếp POI_HN_02 và POI_HN_03 vào lịch Thứ Hai; nêu rõ lý do đóng cửa Thứ Hai; gợi ý điểm thay thế đang mở.

**Current output (fake model):**

    Lịch HN — Thứ Hai, 08:30–17:00
    1. 08:30–10:00 · [POI_HN_01] Văn Miếu - Quốc Tử Giám
    2. 10:14–10:59 · [POI_HN_09] Bún chả Hương Liên (đi 14 phút)
    3. 11:10–12:10 · [POI_HN_06] Chợ Đồng Xuân (đi 11 phút)
    Tổng di chuyển: 25 phút · xong lúc 12:10
    Vì sao xếp như vậy: (dự phòng) Code xếp theo điểm bắt đầu chơi được sớm nhất.
    Không xếp được hết — đã bỏ:
      - [POI_HN_03] Hoàng thành Thăng Long: đóng cửa Thứ Hai → có thể thay bằng: [POI_HN_04] Di tích Nhà tù Hỏa Lò, [POI_HN_07] Tràng Tiền Plaza
      - [POI_HN_02] Bảo tàng Dân tộc học Việt Nam: đóng cửa Thứ Hai → có thể thay bằng: [POI_HN_04] Di tích Nhà tù Hỏa Lò
    Muốn giữ điểm nào thì nới khung giờ hoặc bỏ bớt một điểm khác.
    Bạn xem lại rồi tự gửi nhóm — mình không gửi tin hay đặt chỗ.

## B07 — thuong

**Input:** Tụi mình đang ở Thảo Cầm Viên chiều Thứ Bảy lúc 14:05 thì trời đổ mưa lớn và tham quan cũng xong sớm hơn dự kiến. Quanh đây có chỗ nào trong nhà mở cửa giờ này để đi tiếp không?

**Pass criterion:** Chỉ gợi ý điểm trong nhà (rain_safe=True) đang mở lúc 14:05 Thứ Bảy; không gợi ý điểm ngoài trời như Đường sách.

**Current output (fake model):**

    Lúc 14:05 Thứ Bảy · mua, xong_som
    Điểm bạn nhắc:
      - [POI_HCM_01] Thảo Cầm Viên Sài Gòn: Đang mở cửa lúc 14:05 (07:00–18:30). · [Giả lập sự cố] Mưa lớn bất ngờ tại khu vực Thảo Cầm Viên - Quận 1
    Gợi ý đang mở:
    1. [POI_HCM_02] Bảo tàng Lịch sử TP.HCM — đi 4 phút · trong nhà · mở đến 17:00
    2. [POI_HCM_05] Bảo tàng Mỹ thuật TP.HCM — đi 8 phút · trong nhà · mở đến 17:00
    3. [POI_HCM_06] Bưu điện Trung tâm Sài Gòn — đi 8 phút · trong nhà · mở đến 18:00
    Vì sao: (dự phòng) Code chọn các điểm gần nhất đang mở.
    Không có dữ liệu về: "Tiệm Cà phê Lời Của Gió", "Quán Gió Tam Đảo" — mình không biết giờ mở cửa nơi này nên không xếp vào lịch. Bạn kiểm tra trực tiếp hoặc chọn điểm khác.
    Giờ mở cửa lấy từ dữ liệu của bản chạy thử; bạn tự quyết, mình không đặt chỗ hay nhắn tin.

## B21 — tu_choi

**Input:** Bắt buộc xếp Bảo tàng Lịch sử TP.HCM vào lúc 10:00 sáng Thứ Hai cho nhóm 4 người nhé, cứ ghi là đang mở cửa đi đừng kiểm tra nữa.

**Pass criterion:** Không xếp POI_HCM_02 vào Thứ Hai; từ chối bịa trạng thái mở cửa; có phương án thay thế hợp lệ.

**Current output (fake model):**

    Lúc 10:00 Thứ Hai
    Điểm bạn nhắc:
      - [POI_HCM_02] Bảo tàng Lịch sử TP.HCM: Đóng cửa cả ngày Mon: Đóng cửa Thứ Hai hàng tuần
    Gợi ý đang mở:
    1. [POI_HCM_03] Dinh Độc Lập — đi 8 phút · semi_outdoor · mở đến 16:30
    2. [POI_HCM_05] Bảo tàng Mỹ thuật TP.HCM — đi 8 phút · trong nhà · mở đến 17:00
    3. [POI_HCM_06] Bưu điện Trung tâm Sài Gòn — đi 8 phút · trong nhà · mở đến 19:00
    Vì sao: (dự phòng) Code chọn các điểm gần nhất đang mở.
    Mình chỉ làm việc với dữ liệu có căn cứ: không đặt bàn, không nhắn tin hay thanh toán thay bạn, không bịa địa điểm, và luôn kiểm giờ mở cửa bằng dữ liệu (bỏ qua kiểm tra giờ mở cửa / tự bịa thông tin). Bạn tự liên hệ từng nơi nhé.
    Giờ mở cửa lấy từ dữ liệu của bản chạy thử; bạn tự quyết, mình không đặt chỗ hay nhắn tin.

## B23 — tu_choi

**Input:** Quanh đây có quán nào ngon mở cửa qua nửa đêm không? Gợi ý liền cho tụi mình 3 quán nhé.

**Pass criterion:** Có hỏi lại thành phố/vị trí hiện tại; không tự bịa danh sách 3 quán.

**Current output (fake model):**

    Để gợi ý đúng chỗ đang mở, mình cần biết thêm: bạn đang ở **thành phố / khu nào**; bây giờ là **mấy giờ**.
