"""Kiểm hợp đồng dữ liệu v2 giữa các phần (docs/hop-dong-du-lieu.md). Chạy trước mỗi lần push:

    python scripts/kiem_hop_dong.py

Chỉ đọc, không sửa file nào. Luôn chạy agent ở chế độ model GIẢ (không tốn token, không gọi mạng).
Phần chưa có file (ngan_sach.py, price_tier_vnd.csv, file chấm…) → báo "chưa có", không tính lỗi.
Thoát mã 1 nếu có lỗi. Chỉ dùng thư viện chuẩn.
"""
import csv
import glob
import hashlib
import importlib
import inspect
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
os.environ["MODEL_PROVIDER"] = "fake"  # ai.load_env() dùng setdefault → .env không ghi đè được
sys.path.insert(0, os.path.join(ROOT, "codebase"))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LOI, CHUA = [], []


def loi(ma, msg):
    LOI.append("[%s] %s" % (ma, msg))


def chua(ma, msg):
    CHUA.append("[%s] %s" % (ma, msg))


def norm(b):
    return b.replace(b"\r\n", b"\n").lstrip(b"\xef\xbb\xbf")


def read_csv(path):
    with open(path, "rb") as f:
        return list(csv.DictReader(io.StringIO(norm(f.read()).decode("utf-8"))))


def header(path):
    with open(path, "rb") as f:
        return norm(f.read()).decode("utf-8").splitlines()[0].split(",")


# ------------------------------------------------------------------ mốc đóng băng (chụp 28/11 00:15 từ commit 01a4084)

DATA_HASH = {
    "data/travel-behavior/chat.csv": "3fe20957e4f257a7",
    "data/travel-behavior/column_dictionary.csv": "0aa1a71468a4b225",
    "data/travel-behavior/completed_itineraries.csv": "c9370f182bf07a85",
    "data/travel-behavior/disruption_events.csv": "e29c376f699467b7",
    "data/travel-behavior/event_types.csv": "b740209b1bd4677d",
    "data/travel-behavior/events.csv": "23ad538e68b8ec6f",
    "data/travel-behavior/recommendations.csv": "62dcca9e2bfa13af",
    "data/travel-behavior/travelers.csv": "1cd31d5e963bd468",
    "data/travel-behavior/trips.csv": "d4365229983facbb",
    "data/travel-ops/edit_history.csv": "89a6b35af2a87413",
    "data/travel-ops/live_disruptions.csv": "c539d1dde9d4f3ed",
    "data/travel-ops/opening_hours.csv": "6a7168181340aa8c",
    "data/travel-ops/poi_master.csv": "83b7004391e0ac4c",
    "data/travel-ops/schedule_warnings.csv": "72ef0793d6376ecf",
    "data/travel-ops/zone_travel_matrix.csv": "bc39790991acc262",
}
BENCH_COLS = ["id", "input", "expected", "pass_criterion", "type", "source"]
BENCH_HASH = {
    "B01": "30cb32a1c753fb7a", "B02": "b2f84e0123d978b7", "B03": "d858812d977732f6", "B04": "c1ddbeb75639e1e0",
    "B05": "d8f67092badec0a1", "B06": "70da6da440ea9ac6", "B07": "feb7faf6b2c6c71a", "B08": "4b38b8bb22c2077f",
    "B09": "5c5a6d3627496114", "B10": "68bdfe303be15bfc", "B11": "a61ddf3349c4f0db", "B12": "f394e99976d44d7d",
    "B13": "96f98a6b0febf6f8", "B14": "2630babe4cf9b290", "B15": "e3142ee8874976e7", "B16": "e9625774f19a754f",
    "B17": "406b07ad7e75f0d2", "B18": "078ddafada0aa09d", "B19": "f616306f3f0b95ba", "B20": "709f9f0e577be9bf",
    "B21": "c619ef1c99d0a08f", "B22": "eb420fdfe490b82d", "B23": "02256fb0ff55f14f", "B24": "8a7648ffd4398dbc",
    "B25": "ffdd0e0b37f5709d", "B26": "8b1da21ca7758513", "B27": "75682917cf34a9e0", "B28": "0bd793a0e20202dd",
}

# ------------------------------------------------------------------ H6 · data cũ đóng băng


# H6 v2: 2 file được NỐI DÒNG — chỉ kiểm N dòng đầu (kể cả tiêu đề) y nguyên.
APPEND_OK = {
    "data/travel-ops/poi_master.csv": (95, "358cc0bfe30e867a"),
    "data/travel-ops/opening_hours.csv": (659, "7982c6ec90b9b6c8"),
}
DAYS7 = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
POI_ENUM = {
    "category": {"attraction", "beach", "cafe", "food", "mall", "market", "museum"},
    "indoor_outdoor": {"indoor", "outdoor", "semi_outdoor"},
    "price_tier": {"free", "budget", "mid", "mid_high"},
    "rain_safe": {"True", "False"}, "heat_safe": {"True", "False"},
}


def lines_of(path):
    with open(path, "rb") as f:
        return norm(f.read()).decode("utf-8").rstrip("\n").split("\n")


def zones_by_city():
    z = {}
    for r in read_csv("data/travel-ops/zone_travel_matrix.csv"):
        z.setdefault(r["city"], set()).update({r["from_zone"], r["to_zone"]})
    return z


def kiem_dong_poi(ma, rows, id_re, zones, gio_rows, tag):
    """Kiểm dòng điểm mới (H6 v2 / H14): enum, vùng có sẵn, nguồn, đủ 7 dòng giờ mở hợp lệ."""
    ids = [r["poi_id"] for r in rows]
    if len(set(ids)) != len(ids):
        loi(ma, "%s: trùng poi_id %s" % (tag, sorted({i for i in ids if ids.count(i) > 1})))
    for r in rows:
        pid = r["poi_id"]
        if not re.match(id_re, pid or ""):
            loi(ma, "%s: poi_id %r sai mẫu %s" % (tag, pid, id_re))
            continue
        city = pid.split("_")[1]
        if r["city"] != city:
            loi(ma, "%s %s: city %r không khớp mã %s" % (tag, pid, r["city"], city))
        if r["zone"] and r["zone"] not in zones.get(city, set()):
            loi(ma, "%s %s: zone %r không có trong zone_travel_matrix của %s (chỉ dùng vùng có sẵn)" % (tag, pid, r["zone"], city))
        if not r["zone"] and ma == "H6":
            loi(ma, "%s %s: thiếu zone" % (tag, pid))
        for k, ok in POI_ENUM.items():
            if r.get(k) not in ok:
                loi(ma, "%s %s: %s=%r không hợp lệ" % (tag, pid, k, r.get(k)))
        if not (r.get("avg_duration_min") or "").isdigit():
            loi(ma, "%s %s: avg_duration_min phải là số nguyên phút" % (tag, pid))
        if not (r.get("verified_source") or "").strip():
            loi(ma, "%s %s: thiếu verified_source (nguồn 1)" % (tag, pid))
        if ma == "H14" and not (r.get("nguon_2") or "").strip():
            loi(ma, "%s %s: thiếu nguon_2" % (tag, pid))
        if ma == "H6" and "nguồn 2" not in (r.get("notes") or ""):
            loi(ma, "%s %s: notes phải có 'nguồn 2: <link>'" % (tag, pid))
        g = [x for x in gio_rows if x["poi_id"] == pid]
        if sorted(x["day_of_week"] for x in g) != sorted(DAYS7):
            loi(ma, "%s %s: giờ mở cửa phải đúng 7 dòng Mon…Sun (đang có %s)" % (tag, pid, [x["day_of_week"] for x in g]))
        for x in g:
            if x["is_open"] not in ("True", "False"):
                loi(ma, "%s %s %s: is_open phải True/False" % (tag, pid, x["day_of_week"]))
            elif x["is_open"] == "True" and not (re.match(r"^\d{2}:\d{2}$", x["open_time"] or "")
                                                and re.match(r"^\d{2}:\d{2}$", x["close_time"] or "")):
                loi(ma, "%s %s %s: open_time / close_time phải dạng HH:MM" % (tag, pid, x["day_of_week"]))
    la = sorted({x["poi_id"] for x in gio_rows} - set(ids))
    if la:
        loi(ma, "%s: giờ mở cửa cho poi_id không có trong file điểm: %s" % (tag, la))


def kiem_data():
    for path, want in DATA_HASH.items():
        if path in APPEND_OK:
            continue
        if not os.path.exists(path):
            loi("H6", "%s bị xoá hoặc đổi tên (data đóng băng)" % path)
            continue
        with open(path, "rb") as f:
            got = hashlib.sha256(norm(f.read())).hexdigest()[:16]
        if got != want:
            loi("H6", "%s đã bị sửa (data đóng băng — chỉ 2 file được nối dòng; sửa có nguồn thì ghi §10 và báo N3 cập nhật mốc)"
                % path)
    them = {}
    for path, (n, want) in APPEND_OK.items():
        if not os.path.exists(path):
            loi("H6", "%s bị xoá hoặc đổi tên" % path)
            continue
        L = lines_of(path)
        if len(L) < n or hashlib.sha256("\n".join(L[:n]).encode()).hexdigest()[:16] != want:
            loi("H6", "%s: %d dòng đầu đã bị sửa / xoá — chỉ được NỐI dòng mới vào cuối (rule.md 1.7)" % (path, n - 1))
            continue
        them[path] = len(L) - n
    if any(them.values()):
        poi = read_csv("data/travel-ops/poi_master.csv")[94:]
        gio = read_csv("data/travel-ops/opening_hours.csv")[658:]
        print("  data nối thêm: %d điểm, %d dòng giờ mở" % (len(poi), len(gio)))
        kiem_dong_poi("H6", poi, r"^POI_[A-Z]+_\d{2}$", zones_by_city(), gio, "poi_master (dòng mới)")
        cu = {r["poi_id"] for r in read_csv("data/travel-ops/poi_master.csv")[:94]}
        if cu & {r["poi_id"] for r in poi}:
            loi("H6", "dòng mới trùng poi_id điểm cũ: %s" % sorted(cu & {r["poi_id"] for r in poi}))
    moi = sorted(set(p.replace(os.sep, "/") for p in glob.glob("data/travel-*/*.csv")) - set(DATA_HASH))
    if moi:
        print("  file data mới (được phép, nhớ ghi DATA_CARD): " + ", ".join(moi))


def kiem_staging():
    """H14: data/staging/ của N1 (code không đọc)."""
    p1, p2 = "data/staging/poi_moi.csv", "data/staging/gio_mo_moi.csv"
    if not os.path.exists(p1) and not os.path.exists(p2):
        chua("H14", "data/staging/poi_moi.csv, gio_mo_moi.csv")
        return
    cols_poi = header("data/travel-ops/poi_master.csv") + ["nguon_2", "ngay_xem", "nguoi_thu"]
    cols_gio = header("data/travel-ops/opening_hours.csv") + ["nguon"]
    for p, want in ((p1, cols_poi), (p2, cols_gio)):
        if not os.path.exists(p):
            loi("H14", "thiếu %s (phải đi đôi với file kia)" % p)
            return
        if header(p) != want:
            loi("H14", "%s: tiêu đề phải là %s" % (p, ",".join(want)))
            return
    poi, gio = read_csv(p1), read_csv(p2)
    print("  staging: %d điểm, %d dòng giờ mở" % (len(poi), len(gio)))
    kiem_dong_poi("H14", poi, r"^MOI_[A-Z]+_\d{2}$", zones_by_city(), gio, "staging")


def kiem_ten_khong_bi_cuop():
    """H6 v2: thêm điểm mới không được làm tim_diem(tên điểm cũ) ra điểm khác."""
    try:
        agent = importlib.import_module("agent")
    except Exception:  # noqa: BLE001 — kiem_output sẽ báo
        return
    rows = read_csv("data/travel-ops/poi_master.csv")
    if len(rows) <= 94:
        return
    for r in rows:
        p = agent.tim_diem(r["city"], r["name"])
        if not p or p["poi_id"] != r["poi_id"]:
            loi("H6", "tim_diem(%s, %r) ra %s thay vì %s — tên điểm mới cướp / trùng tên điểm cũ"
                % (r["city"], r["name"], p["poi_id"] if p else None, r["poi_id"]))


# ------------------------------------------------------------------ H8 · benchmark chỉ được thêm


def kiem_benchmark():
    path = "eval/benchmark.csv"
    if header(path) != BENCH_COLS:
        loi("H8", "tiêu đề benchmark phải đúng %s" % ",".join(BENCH_COLS))
        return
    rows = read_csv(path)
    ids = [r["id"] for r in rows]
    for bid, want in BENCH_HASH.items():
        r = next((x for x in rows if x["id"] == bid), None)
        if not r:
            loi("H8", "%s bị xoá (không được xoá câu thử)" % bid)
            continue
        got = hashlib.sha256(json.dumps([r[k] for k in BENCH_COLS], ensure_ascii=False).encode()).hexdigest()[:16]
        if got != want:
            loi("H8", "%s bị sửa (chỉ được thêm câu mới, không sửa câu cũ)" % bid)
    if ids[:len(BENCH_HASH)] != list(BENCH_HASH):
        loi("H8", "B01–B28 phải giữ nguyên thứ tự ở đầu file; câu mới thêm ở cuối")
    if len(set(ids)) != len(ids):
        loi("H8", "trùng id: %s" % sorted({i for i in ids if ids.count(i) > 1}))
    if len(rows) > 30:
        loi("H8", "%d câu — tối đa 30" % len(rows))
    for n, r in enumerate(rows[len(BENCH_HASH):], len(BENCH_HASH) + 1):
        if r["id"] != "B%02d" % n:
            loi("H8", "câu thứ %d phải có id B%02d (đang là %s)" % (n, n, r["id"]))
        if r["type"] not in ("thuong", "kho", "tu_choi"):
            loi("H8", "%s: type phải là thuong / kho / tu_choi" % r["id"])
        if not re.match(r"^(nguoi_dung|data_that|tu_viet|sinh_seed)\s*:", r["source"] or ""):
            loi("H8", "%s: source phải bắt đầu bằng nguoi_dung: / data_that: / tu_viet: / sinh_seed:" % r["id"])
        for k in ("input", "expected", "pass_criterion"):
            if not (r[k] or "").strip():
                loi("H8", "%s: cột %s trống" % (r["id"], k))
    print("  benchmark: %d câu (%d câu mới)" % (len(rows), len(rows) - len(BENCH_HASH)))


# ------------------------------------------------------------------ H5 · 9 công cụ có sẵn

SIG = {
    "search_pois": ["city", "query", "category", "indoor_only", "rain_safe_only", "limit"],
    "check_opening_hours": ["poi_id", "day_of_week", "at_time"],
    "get_travel_time": ["city", "from_zone", "to_zone", "mode", "is_raining"],
    "get_live_disruptions": ["city", "zone", "poi_id"],
    "get_schedule_warnings": ["city", "poi_id"],
    "lap_lich": ["city", "thu_tu", "day_of_week", "bat_dau", "mode", "start_zone"],
    "liet_ke_vi_pham": ["city", "lich", "day_of_week", "bat_dau", "ket_thuc", "mode", "end_zone"],
    "kiem_lich_trinh": ["poi_ids", "visit_day", "start_time", "end_time", "mode", "is_raining"],
    "goi_y_diem": ["city", "day_of_week", "at_time", "from_zone", "mode", "rain_safe", "heat_safe", "indoor_only",
                   "categories", "exclude", "max_travel_min", "limit"],
}
NOI_BO = ["_poi", "_hours", "_load_csv", "_to_min", "_hhmm", "_norm", "_norm_city", "_norm_day", "_open_for",
          "_lap_lich", "_kiem", "travel_min", "zone_min", "_CITY_ALIASES"]
LOI_CODES = {"dong_cua_ca_ngay", "chua_mo_cua", "qua_gio_dong", "qua_gio_nhan_khach", "trung_gio_nghi", "chong_gio",
             "khong_du_thoi_gian_di", "ngoai_khung_gio", "khong_kip_quay_ve", "khong_co_du_lieu", "cho_qua_lau"}


def params(f):
    return list(inspect.signature(getattr(f, "__wrapped__", f)).parameters)


def can_co(ma, ten, obj, keys):
    thieu = [k for k in keys if k not in obj]
    if thieu:
        loi(ma, "%s thiếu trường %s" % (ten, thieu))


def kiem_tools(tools):
    for name, want in SIG.items():
        f = getattr(tools, name, None)
        if not f:
            loi("H5", "tools.%s bị xoá hoặc đổi tên" % name)
        elif params(f) != want:
            loi("H5", "tools.%s đổi tham số: %s (hợp đồng: %s)" % (name, params(f), want))
    for name in NOI_BO:
        if not hasattr(tools, name):
            loi("H5", "tools.%s (agent đang dùng) bị xoá hoặc đổi tên" % name)
    ids = ["POI_HCM_01", "POI_HCM_02", "POI_HCM_03"]
    try:
        p = tools.search_pois("HCM", "Dinh")
        can_co("H5", "search_pois[0]", p[0] if p else {}, ["poi_id", "name", "city", "district", "zone", "address",
               "category", "indoor_outdoor", "avg_duration_min", "rain_safe", "heat_safe", "verified_source", "notes"])
        can_co("H5", "check_opening_hours", tools.check_opening_hours("POI_HCM_02", "Mon", "10:00"),
               ["found", "poi_id", "day_of_week", "is_open_day", "open_time", "close_time", "break_start", "break_end",
                "last_entry_time", "open_at_time", "status_reason", "source_note", "warnings"])
        can_co("H5", "get_travel_time", tools.get_travel_time("HCM", "HCM_Q1_CENTER", "HCM_Q3"),
               ["found", "city", "from_zone", "to_zone", "note", "mode", "distance_km", "travel_min", "total_min"])
        lich = tools.lap_lich("HCM", ids, "Sat", "08:00")
        can_co("H5", "lap_lich[0]", lich[0] if lich else {}, ["poi_id", "name", "di_chuyen_phut", "cho_phut", "den", "roi"])
        vp = tools.liet_ke_vi_pham("HCM", lich, "Mon", "08:00", "12:00")
        can_co("H5", "liet_ke_vi_pham[0]", vp[0] if vp else {}, ["poi_id", "loi", "chi_tiet"])
        la = {x["loi"] for x in vp} - LOI_CODES
        if la:
            loi("H5", "liet_ke_vi_pham có mã lỗi mới %s — báo N3 trước (agent coi mã lạ là lỗi cứng)" % la)
        k = tools.kiem_lich_trinh(ids, "Sat", "08:00", "17:30", "motorbike")
        can_co("H5", "kiem_lich_trinh", k, ["valid", "schedule", "issues"])
        can_co("H5", "kiem_lich_trinh.schedule[0]", k["schedule"][0] if k.get("schedule") else {},
               ["poi_id", "name", "travel_minutes_from_previous", "arrival", "visit_start", "departure", "opening_source"])
        k2 = tools.kiem_lich_trinh(["POI_HCM_02"], "Mon", "08:00", "12:00")
        can_co("H5", "kiem_lich_trinh.issues[0]", k2["issues"][0] if k2.get("issues") else {}, ["code", "message"])
        g = tools.goi_y_diem("HCM", "Sat", "14:00", "")
        can_co("H5", "goi_y_diem[0]", g[0] if g else {}, ["poi_id", "name", "zone", "category", "indoor_outdoor",
                                                         "di_chuyen_phut", "dong_cua_luc", "su_co"])
        d = tools.get_live_disruptions(city="HCM")
        can_co("H5", "get_live_disruptions[0]", d[0] if d else {}, ["disruption_id", "city", "zone", "poi_id",
               "disruption_type", "severity", "start_time", "end_time", "description", "source_type"])
    except Exception as e:  # noqa: BLE001
        loi("H5", "gọi thử công cụ bị lỗi: %r" % e)


# ------------------------------------------------------------------ H4 · H3 · H2 · ngân sách

TIERS = {"free", "budget", "mid", "mid_high"}


def kiem_ngan_sach(tools):
    path = "data/travel-ops/price_tier_vnd.csv"
    if not os.path.exists(path):
        chua("H4", path)
    elif header(path) != ["price_tier", "min_vnd", "max_vnd", "source"]:
        loi("H4", "%s: tiêu đề phải là price_tier,min_vnd,max_vnd,source" % path)
    else:
        rows = read_csv(path)
        if {r["price_tier"] for r in rows} != TIERS or len(rows) != 4:
            loi("H4", "%s: phải đúng 4 dòng %s" % (path, sorted(TIERS)))
        for r in rows:
            if not (r["min_vnd"].isdigit() and r["max_vnd"].isdigit()) or int(r["min_vnd"]) > int(r["max_vnd"]):
                loi("H4", "%s: dòng %s — min_vnd, max_vnd phải là số nguyên VNĐ và min ≤ max" % (path, r["price_tier"]))
            elif r["price_tier"] == "free" and r["max_vnd"] != "0":
                loi("H4", "%s: free phải là 0,0" % path)
            if not r["source"].strip():
                loi("H4", "%s: dòng %s thiếu source" % (path, r["price_tier"]))

    f = getattr(tools, "uoc_chi_phi", None)
    if not f:
        chua("H3", "tools.uoc_chi_phi")
    else:
        if params(f) != ["poi_ids", "so_nguoi"]:
            loi("H3", "uoc_chi_phi tham số phải là (poi_ids, so_nguoi=1), đang là %s" % params(f))
        try:
            r = f(["POI_HCM_01", "POI_KHONG_CO_99"], 2)
            can_co("H3", "uoc_chi_phi", r, ["tong_min", "tong_max", "so_nguoi", "tung_diem", "khong_ro", "nguon"])
            if not (isinstance(r.get("tong_min"), int) and isinstance(r.get("tong_max"), int)):
                loi("H3", "uoc_chi_phi: tong_min, tong_max phải là int")
            if "POI_KHONG_CO_99" not in (r.get("khong_ro") or []):
                loi("H3", "uoc_chi_phi: poi_id lạ phải nằm trong khong_ro")
            if r.get("tung_diem"):
                can_co("H3", "uoc_chi_phi.tung_diem[0]", r["tung_diem"][0], ["poi_id", "price_tier", "min_vnd", "max_vnd"])
        except Exception as e:  # noqa: BLE001
            loi("H3", "uoc_chi_phi lỗi với poi_id lạ: %r" % e)

    try:
        ns = importlib.import_module("ngan_sach")
    except ModuleNotFoundError:
        chua("H2", "codebase/ngan_sach.py")
        return None
    except Exception as e:  # noqa: BLE001 — lỗi cú pháp / lỗi khi nạp làm hỏng luôn agent
        loi("H2", "codebase/ngan_sach.py nạp bị lỗi (agent cũng sẽ hỏng): %r" % e)
        return None
    fn = getattr(ns, "dong_chi_phi", None)
    if not fn:
        loi("H2", "ngan_sach.py thiếu hàm dong_chi_phi")
        return None
    if params(fn) != ["text", "poi_ids"]:
        loi("H2", "dong_chi_phi tham số phải là (text, poi_ids), đang là %s" % params(fn))
    ids = ["POI_HCM_01", "POI_HCM_03"]
    try:
        if fn("Thứ Bảy ở TP.HCM từ 08:00 đến 17:30: Thảo Cầm Viên.", ids) != "":
            loi("H2", "không có ngân sách thì dong_chi_phi phải trả \"\"")
        for cau in ("Ngân sách 300000đ/người.", "ngân sách 300k", "ngân sách 1tr", "ngân sách 1,5 triệu",
                    "ngân sách 300.000đ"):
            out = fn("Thứ Bảy ở TP.HCM từ 08:00 đến 17:30: Thảo Cầm Viên. " + cau, ids)
            if not isinstance(out, str) or not out.startswith("Chi phí ước tính:") or "\n" in out \
                    or "tự ước tính" not in out:
                loi("H2", "\"%s\" → phải ra 1 dòng bắt đầu 'Chi phí ước tính:' có 'tự ước tính', đang ra %r"
                    % (cau, out))
            elif not re.search(r"→ (trong ngân sách|có thể vượt ngân sách|vượt ngân sách)$", out):
                loi("H2", "\"%s\" → dòng phải kết thúc bằng '→ trong / có thể vượt / vượt ngân sách': %r" % (cau, out))
        fn("Ngân sách 300000đ/người.", [])
        fn("Ngân sách 300000đ/người.", ["POI_KHONG_CO_99"])
    except Exception as e:  # noqa: BLE001
        loi("H2", "dong_chi_phi ném lỗi (không được): %r" % e)
    return fn


# ------------------------------------------------------------------ H7 · định dạng output agent

R_LICH = re.compile(r"^\d+\. \d{2}:\d{2}–\d{2}:\d{2} · \[POI_[A-Z]+_\d{2}\] .+")
R_GOIY = re.compile(r"^\d+\. \[POI_[A-Z]+_\d{2}\] .+ — đi \d+ phút · .+ · mở đến \d{2}:\d{2}")


def kiem_output(co_ngan_sach):
    rows = {r["id"]: r["input"] for r in read_csv("eval/benchmark.csv")}
    try:
        agent = importlib.import_module("agent")
        o1 = agent.answer(rows["B01"])["output"]
        lines = o1.splitlines()
        if not re.match(r"^Lịch .+ — .+, \d{2}:\d{2}–\d{2}:\d{2}", lines[0]):
            loi("H7", "B01: dòng đầu phải là 'Lịch {TP} — {Thứ}, HH:MM–HH:MM', đang là %r" % lines[0])
        lich = [x for x in lines if re.match(r"^\d+\. ", x)]
        if not lich or not all(R_LICH.match(x) for x in lich):
            loi("H7", "B01: dòng lịch phải dạng 'n. HH:MM–HH:MM · [POI_ID] Tên' — %r" % lich[:2])
        if not any(x.startswith("Tổng di chuyển: ") for x in lines):
            loi("H7", "B01: thiếu dòng 'Tổng di chuyển: X phút · xong lúc HH:MM'")
        if any(x.startswith("Vì sao") for x in lines):
            loi("H7", "B01: còn dòng 'Vì sao…' — H7 v3: lý do của model chỉ ghi vào trace, không hiện")
        if "Chi phí ước tính:" in o1:
            loi("H7", "B01 không có ngân sách mà output có dòng chi phí")
        o7 = agent.answer(rows["B07"])["output"].splitlines()
        goi = [x for x in o7 if re.match(r"^\d+\. ", x)]
        if goi and not all(R_GOIY.match(x) for x in goi):
            loi("H7", "B07: dòng gợi ý phải dạng 'n. [POI_ID] Tên — đi X phút · … · mở đến HH:MM' — %r" % goi[:1])
        # H7 v2 · B-lite (chỉ kiểm khi output có mục "Còn trống")
        if any(x.startswith("Còn trống ") for x in lines):
            i = next(n for n, x in enumerate(lines) if x.startswith("Còn trống "))
            dau = lines[i]
            if not re.match(r"^Còn trống \d{2}:\d{2}–\d{2}:\d{2} \(\d+ phút\)(\. Nếu muốn, nhóm có thể ghé thêm \(mình chỉ gợi ý, "
                            r"chưa xếp vào lịch\):|, dữ liệu ở .+ chưa có chỗ nào hợp để gợi ý thêm\.)$", dau):
                loi("H7", "B01: dòng đầu mục B-lite sai mẫu H7 v3: %r" % dau)
            cong = [x for x in lines if x.startswith("  + ")]
            for x in cong:
                if not re.match(r"^  \+ \[POI_[A-Z]+_\d{2}\] .+ — đi \d+ phút từ điểm cuối · mở đến \d{2}:\d{2} · chơi khoảng \d+ phút$", x):
                    loi("H7", "B01: dòng gợi ý B-lite sai mẫu H7 v3: %r" % x)
            if "chưa xếp vào lịch" in dau and not cong:
                loi("H7", "B01: có đầu mục B-lite mà không có dòng '  + [POI_ID] …'")
            cuoi = next((n for n, x in enumerate(lines) if x.startswith("Bạn xem lại rồi tự gửi nhóm")), len(lines))
            if not i < cuoi:
                loi("H7", "B01: mục B-lite phải nằm trước dòng 'Bạn xem lại rồi tự gửi nhóm…'")
            if any(R_LICH.match(x) for x in lines[i:]):
                loi("H7", "B01: có dòng dạng lịch 'n. HH:MM–HH:MM · [POI]' sau mục B-lite — code chấm metric sẽ đọc nhầm")
        if co_ngan_sach:
            ob = agent.answer(rows["B01"] + " Ngân sách 300000đ/người.")["output"].splitlines()
            if not ob[-1].startswith("Chi phí ước tính:"):
                loi("H7", "có ngân sách thì dòng cuối phải là dòng 'Chi phí ước tính:' (agent nối sau cổng kiểm)")
            if [x for x in ob if R_LICH.match(x)] != lich:
                loi("H7", "thêm ngân sách mà lịch bị đổi — ngân sách chỉ được hiển thị")
    except Exception as e:  # noqa: BLE001
        loi("H7", "chạy agent ở chế độ giả bị lỗi: %r" % e)


# ------------------------------------------------------------------ H10 · file chấm


def kiem_file_cham():
    files = sorted(glob.glob("eval/grading-run*-*.csv"))
    if not files:
        chua("H10", "eval/grading-run<N>-<ten>.csv")
    ids = {r["id"] for r in read_csv("eval/benchmark.csv")}
    for path in files:
        p = path.replace(os.sep, "/")
        if not re.match(r"^eval/grading-run\d+-[a-z0-9]+\.csv$", p):
            loi("H10", "%s: tên phải là eval/grading-run<N>-<ten không dấu>.csv" % p)
        if header(path) != ["id", "pass", "ghi_chu"]:
            loi("H10", "%s: tiêu đề phải là id,pass,ghi_chu" % p)
            continue
        for r in read_csv(path):
            if r["id"] not in ids:
                loi("H10", "%s: id %s không có trong benchmark" % (p, r["id"]))
            if r["pass"] not in ("0", "1"):
                loi("H10", "%s: %s — pass phải là 1 hoặc 0" % (p, r["id"]))
            if r["pass"] == "0" and not re.search(r"khong_vi_pham_gio|khong_bia_diem|dung_hanh_vi|thuan_duong",
                                                   r["ghi_chu"] or ""):
                loi("H10", "%s: %s trượt — ghi_chu phải nêu metric trượt" % (p, r["id"]))


# ------------------------------------------------------------------ an toàn: không commit .env


def kiem_env():
    try:
        out = subprocess.run(["git", "ls-files", ".env"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except OSError:
        return
    if out:
        loi("KEY", ".env đang được git theo dõi — gỡ ngay: git rm --cached .env (luật đề: −10 điểm)")


def main():
    print("Kiểm hợp đồng dữ liệu — docs/hop-dong-du-lieu.md")
    kiem_env()
    kiem_data()
    kiem_staging()
    kiem_benchmark()
    try:
        tools = importlib.import_module("tools")
    except Exception as e:  # noqa: BLE001
        loi("H5", "codebase/tools.py nạp bị lỗi: %r" % e)
        tools = None
    if tools is None:
        for x in LOI:
            print("  LỖI " + x)
        print("%d lỗi" % len(LOI))
        return 1
    kiem_tools(tools)
    fn = kiem_ngan_sach(tools)
    kiem_output(fn is not None)
    kiem_ten_khong_bi_cuop()
    kiem_file_cham()
    for x in CHUA:
        print("  chưa có (không tính lỗi): " + x)
    for x in LOI:
        print("  LỖI " + x)
    print("%d lỗi" % len(LOI))
    return 1 if LOI else 0


if __name__ == "__main__":
    sys.exit(main())
