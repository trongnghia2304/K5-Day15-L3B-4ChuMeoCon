# Phiếu chấm độc lập 5 output — Tiệp

Chấm trên phiếu mù `eval/calibration-5-blind.md` (nhánh `VanHieu`), theo `pass_criterion` và `eval/metric_spec.yaml`; bỏ qua metric `thuan_duong` theo phiếu giao việc. Chưa mở `eval/calibration-5.md` / `eval/README.md` trước khi chấm.

Người chấm: Tiệp    Thời điểm: 19:20 · 27/11/2026

> Có dùng Claude chấm nháp và đối chiếu giờ mở cửa với `data/travel-ops/opening_hours.csv` (ghi ở `docs/ai-usage.md`); Tiệp đọc lại từng câu và chịu trách nhiệm điểm cuối.

| ID | Điểm (1/0) | Lý do |
|---|---|---|
| B01 | 1 | Đủ 5 điểm; Bảo tàng Lịch sử bắt đầu 10:04 (trước 11:00, xong 11:19 trước giờ nghỉ 11:30); Dinh Độc Lập 11:27 trước 15:30; thứ tự Đa Kao → Trung tâm → Phú Nhuận không quay vòng. |
| B05 | 1 | Không xếp POI_HN_02, POI_HN_03; nêu rõ cả hai đóng cửa Thứ Hai; gợi ý Hỏa Lò và Tràng Tiền Plaza, đều mở Thứ Hai. |
| B07 | 1 | Cả 3 gợi ý (POI_HCM_02, 05, 06) trong nhà, rain_safe=True, đang mở lúc ~14:10 Thứ Bảy theo dữ liệu; không có Đường sách. |
| B21 | 1 | Không xếp POI_HCM_02 vào Thứ Hai (báo đóng cửa); từ chối "cứ ghi là đang mở"; 3 điểm thay thế đều mở lúc 10:00 Thứ Hai. |
| B23 | 1 | Hỏi lại thành phố / khu và giờ hiện tại; không đưa ra quán nào. |

**Tổng: 5/5 đạt.**

## Ghi chú khi chấm (không làm trượt pass_criterion)

- B01: "Bảo tàng Lịch sử xếp trước 11:00" mơ hồ — hiểu là *bắt đầu* trước 11:00; nếu hiểu là *kết thúc* thì câu này trượt. Output cũng xếp cơm tấm lúc 14:03 và Dinh Độc Lập buổi sáng, trái ý "ăn trưa … chiều đi Dinh Độc Lập" của người dùng — tiêu chí không kiểm điều này.
- B05: lịch xong 12:10, còn trống tới 17:00 nhưng không chèn điểm thay thế; câu "nới khung giờ để giữ điểm" sai lý do (hai điểm bị bỏ vì đóng cửa, không phải hết giờ).
- B07: output báo "Không có dữ liệu về: Tiệm Cà phê Lời Của Gió, Quán Gió Tam Đảo" dù người dùng không nhắc — có thể bộ so khớp tên bắt nhầm chữ "gió" / "mưa".
