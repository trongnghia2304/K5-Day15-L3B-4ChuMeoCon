"""Kiểm hợp đồng dữ liệu giữa các phần (docs/hop-dong-du-lieu.md). Chạy trước mỗi lần push:

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


def kiem_data():
    for path, want in DATA_HASH.items():
        if not os.path.exists(path):
            loi("H6", "%s bị xoá hoặc đổi tên (data đóng băng)" % path)
            continue
        with open(path, "rb") as f:
            got = hashlib.sha256(norm(f.read())).hexdigest()[:16]
        if got != want:
            loi("H6", "%s đã bị sửa (data đóng băng — chỉ thêm file mới; sửa có nguồn thì ghi §10 và báo N3 cập nhật mốc)"
                % path)
    moi = sorted(set(p.replace(os.sep, "/") for p in glob.glob("data/travel-*/*.csv")) - set(DATA_HASH))
    if moi:
        print("  data mới (được phép, nhớ ghi DATA_CARD): " + ", ".join(moi))


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
        if "Chi phí ước tính:" in o1:
            loi("H7", "B01 không có ngân sách mà output có dòng chi phí")
        o7 = agent.answer(rows["B07"])["output"].splitlines()
        goi = [x for x in o7 if re.match(r"^\d+\. ", x)]
        if goi and not all(R_GOIY.match(x) for x in goi):
            loi("H7", "B07: dòng gợi ý phải dạng 'n. [POI_ID] Tên — đi X phút · … · mở đến HH:MM' — %r" % goi[:1])
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
    kiem_file_cham()
    for x in CHUA:
        print("  chưa có (không tính lỗi): " + x)
    for x in LOI:
        print("  LỖI " + x)
    print("%d lỗi" % len(LOI))
    return 1 if LOI else 0


if __name__ == "__main__":
    sys.exit(main())
