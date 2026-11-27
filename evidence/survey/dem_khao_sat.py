"""Đếm kết quả khảo sát — chạy lại được: python evidence/survey/dem_khao_sat.py

Cách đếm (ghi trước khi đọc số):
- Nguồn: evidence/survey/results.csv (bản đã xoá cột liên hệ Email/Zalo).
- Mẫu số chính T = người trả lời Câu 2 khác "Chưa đi lần nào" (đã đi du lịch tự túc trong 1 năm qua).
  Người chưa đi được form bỏ qua các câu sau nên không tính.
- Nhóm con P = trong T, người tự lên lịch: "Người lên lịch trình chính", "Người phụ tìm quán ăn...",
  hoặc "Thường đi du lịch một mình". Đây là người dùng chính của lát cắt.
- Câu chọn nhiều: một người được đếm 1 lần cho mỗi lựa chọn có chứa cụm từ khoá bên dưới.
- Câu 11, 12 là câu giả định ("nếu có AI…", "có sẵn sàng dùng không") — KHÔNG dùng làm bằng chứng pain.
"""
import csv
import collections
from pathlib import Path

ROWS = list(csv.DictReader(open(Path(__file__).with_name("results.csv"), encoding="utf-8")))
COLS = list(ROWS[0].keys())
Q = {n: next(c for c in COLS if c.startswith(f"Câu {n}.")) for n in range(1, 13)}

T = [r for r in ROWS if r[Q[2]].strip() != "Chưa đi lần nào"]
PLANNER = ("Người lên lịch", "Người phụ", "Thường đi du lịch một mình")
P = [r for r in T if r[Q[3]].startswith(PLANNER)]

OPTS = {
    5: {"Sắp xếp thứ tự thuận đường": "Sắp xếp thứ tự",
        "Kiểm tra giờ mở cửa / ngày đóng cửa": "Kiểm tra giờ mở cửa",
        "Ước lượng thời gian chơi + di chuyển": "Ước lượng thời gian",
        "Cân đối sở thích trong nhóm": "Cân đối sở thích",
        "Lọc thông tin thật – giả": "Lọc thông tin"},
    6: {"Xong sớm, không biết đi tiếp đâu": "Đi xong 1 điểm sớm",
        "Tới nơi thì đóng cửa / hết bàn / hết vé": "Tới nơi thì quán",
        "Lịch trái đường / quá dày, bỏ dở điểm": "trái đường hoặc quá dày",
        "Chưa từng gặp sự cố": "Chưa từng gặp"},
    8: {"Lướt TikTok/Facebook/Google tìm lại": "TikTok",
        "Google Maps tìm đại quanh 1–2km": "Google Maps tìm đại",
        "Hỏi ChatGPT/Gemini": "ChatGPT",
        "Hỏi người địa phương / lễ tân / tài xế": "người địa phương",
        "Bỏ lịch trình còn lại": "Bỏ lịch trình"},
}


def pct(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)"


def report(name, S):
    n = len(S)
    print(f"\n## {name} — N = {n}")
    for q, opts in OPTS.items():
        print(f"Câu {q}:")
        for label, key in opts.items():
            print(f"  {pct(sum(key in r[Q[q]] for r in S), n)}  {label}")
    hit = sum(bool(r[Q[6]].strip()) and "Chưa từng" not in r[Q[6]] for r in S)
    print(f"Câu 6 gặp ≥1 sự cố: {pct(hit, n)}")
    print(f"Câu 7 mức ảnh hưởng 4–5/5: {pct(sum(r[Q[7]] in ('4', '5') for r in S), n)}")
    print("Câu 9 thời gian chốt điểm mới:", dict(collections.Counter(r[Q[9]] for r in S)))
    slow = sum(r[Q[9]].startswith(("Từ 15", "Trên 30")) for r in S)
    print(f"Câu 9 mất ≥15 phút: {pct(slow, n)}")
    print("Câu 4 thời gian lên lịch:", dict(collections.Counter(r[Q[4]] for r in S)))


print(f"Tổng phiếu: {len(ROWS)}")
print("Câu 2:", dict(collections.Counter(r[Q[2]] for r in ROWS)))
print("Câu 3:", dict(collections.Counter(r[Q[3]] for r in ROWS)))
report("Đã đi du lịch tự túc (T)", T)
report("Người tự lên lịch (P)", P)
