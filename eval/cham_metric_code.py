"""Chấm 3 metric `grader: code` của eval/metric_spec.yaml trên một eval/run-N.csv. CHỈ ĐỌC, không sửa file nào.

    python eval/cham_metric_code.py eval/run-1.csv

- khong_vi_pham_gio: lấy các dòng lịch "n. HH:MM–HH:MM · [POI_ID] …" + dòng "Lịch {TP} — {Thứ}, HH:MM–HH:MM",
  tính lại thời gian đi giữa các điểm rồi chạy tools._kiem (bỏ cảnh báo cho_qua_lau). Với output gợi ý
  ("n. [POI_ID] … — đi X phút"): mọi điểm phải mở lúc (giờ hiện tại + X phút), đúng thứ. Câu hỏi lại / từ chối
  (không có lịch, không có gợi ý) không tính vào mẫu số.
- khong_bia_diem: mọi poi_id trong output có trong data/travel-ops/poi_master.csv; điểm trong lịch cùng thành phố.
- thuan_duong (câu `thuong` có lịch): tổng phút đi ≤ 1,2 × thứ tự tốt nhất (vét cạn trên cùng tập điểm, chỉ tính
  các thứ tự 0 vi phạm theo tools._lap_lich + tools._kiem).
Dòng B-lite "  + [POI_ID] …" (H7 v2) KHÔNG phải dòng lịch → không tính.
Chạy ở chế độ model giả (không gọi model). Chỉ dùng thư viện chuẩn.
"""
import csv
import itertools
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(ROOT, "codebase"))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import tools  # noqa: E402

R_LICH = re.compile(r"^\d+\. (\d{2}:\d{2})–(\d{2}:\d{2}) · \[(POI_[A-Z]+_\d{2})\]")
R_GOIY = re.compile(r"^\d+\. \[(POI_[A-Z]+_\d{2})\] .+ — đi (\d+) phút")
R_HEAD = re.compile(r"^Lịch (.+?) — (.+?), (\d{2}:\d{2})–(\d{2}:\d{2})")
R_LUC = re.compile(r"^Lúc (\d{2}:\d{2})(?: (Thứ \w+|Chủ Nhật))?")
DAYS = {"Thứ Hai": "Mon", "Thứ Ba": "Tue", "Thứ Tư": "Wed", "Thứ Năm": "Thu", "Thứ Sáu": "Fri", "Thứ Bảy": "Sat",
        "Chủ Nhật": "Sun"}


def mode_of(text):
    t = tools._norm(text)
    return "walk" if "di bo" in t else ("car" if re.search(r"\b(o to|taxi|grab car)\b", t) else "motorbike")


def cham(r, pois):
    o, res = r["output"].splitlines(), {}
    ids = [m.group(3) for x in o for m in [R_LICH.match(x)] if m] + [m.group(1) for x in o for m in [R_GOIY.match(x)] if m]
    res["khong_bia_diem"] = all(i in pois for i in ids) if ids else None
    head = next((R_HEAD.match(x) for x in o if R_HEAD.match(x)), None)
    lich = [R_LICH.match(x) for x in o if R_LICH.match(x)]
    if head and lich:
        day_txt = head.group(2).split(" ·")[0]
        thu = DAYS.get(day_txt, "")  # "giờ mở cửa giống nhau mọi ngày" → kiểm cả 7 thứ qua Mon (giờ như nhau)
        thu = thu or "Mon"
        city, mode = pois[lich[0].group(3)]["city"], mode_of(r["input"])
        if any(pois[m.group(3)]["city"] != city for m in lich):
            res["khong_bia_diem"] = False
        sched = [{"poi_id": m.group(3), "name": "", "den": m.group(1), "roi": m.group(2), "di_chuyen_phut": 0,
                  "cho_phut": 0} for m in lich]
        for a, b in zip(sched, sched[1:]):
            b["di_chuyen_phut"] = tools.travel_min(city, a["poi_id"], b["poi_id"], mode)
        vp = [x for x in tools._kiem(city, sched, thu, head.group(3), head.group(4), mode, "") if x["loi"] != "cho_qua_lau"]
        res["khong_vi_pham_gio"], res["vi_pham"] = not vp, ["%s:%s" % (x["loi"], x["poi_id"]) for x in vp]
        if r["type"] == "thuong":
            order = [m.group(3) for m in lich]

            def tong(seq):
                return sum(tools.travel_min(city, a, b, mode) for a, b in zip(seq, seq[1:]))
            best, best_seq = None, None
            for perm in itertools.permutations(order):
                lp = tools._lap_lich(city, list(perm), thu, head.group(3), mode)
                if not [x for x in tools._kiem(city, lp, thu, head.group(3), head.group(4), mode, "") if x["loi"] != "cho_qua_lau"]:
                    if best is None or tong(perm) < best:
                        best, best_seq = tong(perm), perm
            res["thuan_duong"] = best is None or tong(order) <= 1.2 * best
            res["phut_di"] = "%d / tốt nhất %s%s" % (tong(order), best, (" " + "→".join(best_seq)) if best_seq else "")
    elif ids and o and R_LUC.match(o[0]):
        m = R_LUC.match(o[0])
        at, thu = tools._to_min(m.group(1)), DAYS.get(m.group(2) or "", "")
        sai = [g.group(1) for x in o for g in [R_GOIY.match(x)] if g
               and not tools._open_for(g.group(1), thu, at + int(g.group(2)), 0)[0]]
        res["khong_vi_pham_gio"], res["vi_pham"] = not sai, sai
    return res


def main():
    if len(sys.argv) != 2:
        sys.exit("Dùng: python eval/cham_metric_code.py eval/run-N.csv")
    pois = {p["poi_id"]: p for p in tools._load_csv("poi_master.csv")}
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig", newline="")))
    kq = {r["id"]: cham(r, pois) for r in rows}
    print("Chấm metric code — %s (%s)" % (sys.argv[1], rows[0]["run_id"] if rows else "?"))
    for name, nguong in (("khong_vi_pham_gio", "100%"), ("khong_bia_diem", "100%"), ("thuan_duong", "≥ 80%")):
        co = {k: v[name] for k, v in kq.items() if v.get(name) is not None}
        dat = [k for k, v in co.items() if v]
        print("  %-18s %d/%d (%s) · ngưỡng %s · trượt: %s" % (name, len(dat), len(co),
              "%d%%" % round(100 * len(dat) / len(co)) if co else "-", nguong,
              ", ".join(k for k, v in co.items() if not v) or "không"))
    for k, v in kq.items():
        if v.get("vi_pham") or "phut_di" in v:
            print("  %s %s" % (k, " · ".join(s for s in (("vi phạm: " + ", ".join(v["vi_pham"])) if v.get("vi_pham") else "",
                                                       ("phút đi: " + v["phut_di"]) if "phut_di" in v else "") if s)))


if __name__ == "__main__":
    main()
