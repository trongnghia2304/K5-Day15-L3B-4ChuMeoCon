# Kiểm nguồn staging HCM — 28/11/2026

N1 giao 13 điểm trong `data/staging/`. N2 đối chiếu địa chỉ, giờ mở và đặc tính tránh mưa trên trang cụ thể. Hai cột URL trong staging ban đầu phần lớn chỉ là trang chủ, nên URL dùng trong dữ liệu chính được thay bằng trang của đúng địa điểm. Dữ liệu chính trên nhánh `data/mo-rong` chỉ thêm dòng, chưa merge vào `main` trước lượt mô phỏng chi phí.

## 7 điểm đủ nguồn — đã nối trên nhánh

| Staging → ID thật | Kiểm nguồn | Điều chỉnh |
|---|---|---|
| `MOI_HCM_01` → `POI_HCM_13` Bếp Mẹ Ỉn | [Trang quán](https://bep.mein.vn/contact/) và [VnGuide](https://vnguide.vn/restaurant/bep-me-in): 136/9 Lê Thánh Tôn, 10:30–22:30 mỗi ngày | Không đổi giờ |
| `MOI_HCM_02` → `POI_HCM_14` Quán Bụi Original | [Trang quán](https://quan-bui.com/vi/original/) và [VnGuide](https://vnguide.vn/restaurant/quan-bui-original): 19 Ngô Văn Năm, 07:00–23:00 mỗi ngày | Không đổi giờ |
| `MOI_HCM_04` → `POI_HCM_15` Bánh Xèo 46A | [MIA](https://mia.vn/cam-nang-du-lich/banh-xeo-46a-dinh-cong-trang-18183) và [Wherebest](https://wherebest.com/en/restaurant-banh-xeo-46a-ho-chi-minh-city): 46A Đinh Công Tráng, 10:00–14:00 và 16:00–21:00 | Đổi `indoor_outdoor` thành `semi_outdoor`, `rain_safe`/`heat_safe` thành `False` vì nguồn mô tả chỗ ngồi mở |
| `MOI_HCM_06` → `POI_HCM_16` Tonkin Specialty Coffee | [Trang quán](https://tonkin.coffee/tonkin-garden-egg-coffee/) và [MIA](https://mia.vn/cam-nang-du-lich/tonkin-specialty-coffee-19828): 91 Lý Tự Trọng, 08:00–21:00 mỗi ngày | Không đổi giờ |
| `MOI_HCM_08` → `POI_HCM_17` S'mores Phan Tôn | [Dicaphekhong](https://app.dicaphekhong.com/cafe/smores-saigon-caffe-phan-ton-1a-phan-ton-quan-1) và [MoMo](https://www.momo.vn/page/1046630): 1A Phan Tôn, 08:00–22:00 | Đổi `indoor_outdoor` thành `semi_outdoor`, `rain_safe`/`heat_safe` thành `False` vì có khoảng thông tầng/ngoài trời |
| `MOI_HCM_11` → `POI_HCM_18` Vincom Center Đồng Khởi | [Vincom](https://vincom.com.vn/vincom-center-dong-khoi/gioi-thieu) và [Traveloka](https://www.traveloka.com/vi-vn/explore/destination/mall-vincom-center-dong-khoi/1003119): 72 Lê Thánh Tôn, T2–T6 10:00–22:00, T7–CN 09:30–22:00 | Không đổi giờ |
| `MOI_HCM_13` → `POI_HCM_19` Diamond Plaza | [Trang trung tâm](https://diamondplaza.com.vn/location) và [cẩm nang Sofitel](https://sofitel-saigon-plaza.com/wp-content/uploads/sites/211/2024/04/Saigon-Guidebook-1.pdf): 34 Lê Duẩn, 09:30–22:00 | Không đổi giờ; giờ theo trang chính thức hiện tại |

## 6 điểm giữ ở staging — chưa nối

| ID | Lý do |
|---|---|
| `MOI_HCM_03` Cục Gạch Quán | [HCMC.com](https://hcmc.com/vi/directory/b/cuc-gach-quan/) ghi đóng 23:30; [nguồn đối chiếu](https://www.vinaspot.com/en/v/cuc-gach-quan) ghi 23:00. Staging còn đánh dấu `indoor` dù quán có sân vườn. Cần chốt giờ và cờ không gian. |
| `MOI_HCM_05` Hum Signature | [Trang Hum hiện tại](https://hum-dining.vn/hum-signature/) ghi địa chỉ 34 Võ Văn Tần, 18:00–22:00 và nghỉ thứ Tư; staging ghi 32 Võ Văn Tần, 10:00–22:00 cả tuần. Không dùng dữ liệu cũ. |
| `MOI_HCM_07` Little HaNoi Egg Coffee | [Trang địa điểm](https://littlehanoi.com.vn/locations) xác nhận 119/5 Yersin, nhưng [nguồn giờ](https://restaurantguru.com/Little-HaNoi-Egg-Coffee-Yersin-Ho-Chi-Minh-City) ghi 07:00–21:30 và [nguồn khác](https://vnguide.vn/restaurant/little-hanoi-egg-coffee) ghi 07:00–21:00; staging ghi 08:00–22:00. |
| `MOI_HCM_09` Cà Phê Đỗ Phủ | [Dân Trí](https://dantri.com.vn/du-lich/bi-an-quan-com-tam-o-tphcm-co-can-ham-ngay-trong-tu-ao-20250501061814441.htm) ghi 07:00–22:30, [Foody](https://www.foody.vn/ho-chi-minh/ca-phe-do-phu-com-tam-dai-han-ca-phe-com-tam-tra-dang-dung) ghi 08:00–22:00; cần chốt khung bảo thủ trước khi thêm. |
| `MOI_HCM_10` Dabao Concept Cố Đô | [Vietnam Craft Coffee](https://www.vietnamcraftcoffee.com/vi/cafes/dabao-concept-coffee) ghi 07:00–21:00 nhưng cũng mô tả chỗ ngồi ngoài trời; staging đánh dấu hoàn toàn `indoor`, `rain_safe=True`. Cần chốt cờ không gian. |
| `MOI_HCM_12` Saigon Skydeck | Nguồn về giờ nhận cuối không khớp: [trang Skydeck](https://saigonobservationdeck.com/how-to-get-there/) ghi 90 phút trước 21:30 (20:00), [nguồn đối chiếu](https://www.vietnamtourism.com/en/bitexco-tower-and-the-saigon-skydeck-history-views-tickets) ghi 20:45 như staging. Cần xác nhận trước khi nối. |

Các điểm bị giữ lại không bị xoá khỏi staging; N1 có thể bổ sung nguồn. Cờ mưa/nắng, mức đông, thời lượng và `price_tier` của các điểm được thêm là ước tính để chạy thử, không phải thông tin được nguồn xác nhận đầy đủ.
