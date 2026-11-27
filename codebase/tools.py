"""Công cụ của bài toán Travel AI Agent — đọc trực tiếp nguồn sự thật trong data/travel-ops/.

Mỗi công cụ là một hàm Python có @tool, thuần thư viện chuẩn Python.
Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không.
"""
import csv
import os
import re
import unicodedata
from datetime import date
from pathlib import Path

from tracing import tool, TOOLS  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
OPS_DIR = ROOT / "data" / "travel-ops"

_CITY_ALIASES = {
    "hn": "HN", "ha noi": "HN", "hanoi": "HN",
    "hp": "HP", "hai phong": "HP", "haiphong": "HP",
    "qn": "QN", "quang ninh": "QN", "ha long": "QN", "halong": "QN", "vinh ha long": "QN",
    "sp": "SP", "sa pa": "SP", "sapa": "SP", "lao cai": "SP",
    "td": "TD", "tam dao": "TD", "vinh phuc": "TD",
    "hg": "HG", "ha giang": "HG", "dong van": "HG",
    "hue": "HUE", "tp hue": "HUE",
    "dn": "DN", "da nang": "DN", "danang": "DN",
    "ha": "HA", "hoi an": "HA", "hoian": "HA",
    "nt": "NT", "nha trang": "NT", "nhatrang": "NT",
    "dl": "DL", "da lat": "DL", "dalat": "DL",
    "hcm": "HCM", "tp hcm": "HCM", "tphcm": "HCM", "sai gon": "HCM",
    "saigon": "HCM", "ho chi minh": "HCM", "tp ho chi minh": "HCM",
}

_DAY_ALIASES = {
    "mon": "Mon", "t2": "Mon", "thu 2": "Mon", "thu hai": "Mon", "monday": "Mon",
    "tue": "Tue", "t3": "Tue", "thu 3": "Tue", "thu ba": "Tue", "tuesday": "Tue",
    "wed": "Wed", "t4": "Wed", "thu 4": "Wed", "thu tu": "Wed", "wednesday": "Wed",
    "thu": "Thu", "t5": "Thu", "thu 5": "Thu", "thu nam": "Thu", "thursday": "Thu",
    "fri": "Fri", "t6": "Fri", "thu 6": "Fri", "thu sau": "Fri", "friday": "Fri",
    "sat": "Sat", "t7": "Sat", "thu 7": "Sat", "thu bay": "Sat", "saturday": "Sat",
    "sun": "Sun", "cn": "Sun", "chu nhat": "Sun", "sunday": "Sun",
}

_CACHE: dict[str, list[dict]] = {}


def _norm(text: str) -> str:
    text = (text or "").strip().lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.replace(".", " ").replace("-", " ").split())


def _norm_city(city: str) -> str:
    key = _norm(city)
    return _CITY_ALIASES.get(key, (city or "").strip().upper())


def _norm_day(day: str) -> str:
    key = _norm(day)
    return _DAY_ALIASES.get(key, (day or "").strip().capitalize()[:3])


def _load_csv(filename: str) -> list[dict]:
    if filename not in _CACHE:
        path = OPS_DIR / filename
        if not path.exists():
            return []
        with open(path, encoding="utf-8-sig", newline="") as f:
            _CACHE[filename] = list(csv.DictReader(f))
    return _CACHE[filename]


def _to_min(hhmm: str) -> int | None:
    s = (hhmm or "").strip()
    if ":" not in s:
        return None
    try:
        h, m = s.split(":", 1)
        return int(h) * 60 + int(m)
    except ValueError:
        return None


@tool
def search_pois(
    city: str = "",
    query: str = "",
    category: str = "",
    indoor_only: bool = False,
    rain_safe_only: bool = False,
    limit: int = 10,
) -> list:
    """Tên: search_pois — Tra cứu địa điểm du lịch/ăn uống trong data/travel-ops/poi_master.csv.
    Input: city (str, vd 'HCM'/'Hà Nội'), query (str), category (str), indoor_only (bool), rain_safe_only (bool), limit (int).
    Output: danh sách dict POI gồm poi_id, name, city, zone, address, category, indoor_outdoor, avg_duration_min, rain_safe, heat_safe, notes.
    Tác động ra ngoài: Không (chỉ đọc file CSV cục bộ)."""
    rows = _load_csv("poi_master.csv")
    city_code = _norm_city(city) if city else ""
    q_norm = _norm(query)
    cat_norm = _norm(category)

    # Nếu không truyền city nhưng query nhắc tên thành phố thì tự nhận diện
    if not city_code and q_norm:
        for alias, code in _CITY_ALIASES.items():
            if len(alias) >= 3 and alias in q_norm:
                city_code = code
                break

    results = []
    for r in rows:
        if city_code and r["city"] != city_code:
            continue
        if cat_norm and _norm(r["category"]) != cat_norm and cat_norm not in _norm(r["sub_category"]):
            continue
        if indoor_only and r["indoor_outdoor"] != "indoor":
            continue
        if rain_safe_only and r["rain_safe"] != "True":
            continue

        score = 0
        if q_norm:
            haystack = _norm(" ".join([r["poi_id"], r["name"], r["district"], r["zone"], r["address"], r["category"], r["sub_category"], r["notes"]]))
            if q_norm in haystack:
                score += 10
            else:
                tokens = [t for t in q_norm.split() if len(t) >= 2]
                matched = sum(1 for t in tokens if t in haystack)
                if matched == 0 and not city_code:
                    continue
                score += matched
        else:
            score = 1

        results.append((score, {
            "poi_id": r["poi_id"],
            "name": r["name"],
            "city": r["city"],
            "district": r["district"],
            "zone": r["zone"],
            "address": r["address"],
            "category": r["category"],
            "indoor_outdoor": r["indoor_outdoor"],
            "avg_duration_min": int(r["avg_duration_min"]),
            "rain_safe": r["rain_safe"] == "True",
            "heat_safe": r["heat_safe"] == "True",
            "verified_source": r["verified_source"],
            "notes": r["notes"],
        }))

    results.sort(key=lambda item: (-item[0], item[1]["poi_id"]))
    return [item[1] for item in results[: max(1, int(limit))]]


@tool
def check_opening_hours(poi_id: str, day_of_week: str, at_time: str = "") -> dict:
    """Tên: check_opening_hours — Kiểm tra giờ mở cửa, giờ nghỉ trưa, cutoff bán vé và cảnh báo của một POI.
    Input: poi_id (str, vd 'POI_HCM_02'), day_of_week (str, vd 'Mon'/'Thứ Hai'), at_time (str tùy chọn 'HH:MM').
    Output: dict gồm is_open_day, open_time, close_time, break_start, break_end, last_entry_time, open_at_time (bool|None), status_reason, source_note, warnings.
    Tác động ra ngoài: Không (chỉ đọc file CSV cục bộ)."""
    pid = (poi_id or "").strip().upper()
    day = _norm_day(day_of_week)
    oh_rows = _load_csv("opening_hours.csv")
    rec = next((r for r in oh_rows if r["poi_id"] == pid and r["day_of_week"] == day), None)
    if not rec:
        return {"found": False, "poi_id": pid, "day_of_week": day, "status_reason": "Không tìm thấy POI hoặc thứ hợp lệ trong dữ liệu."}

    warns = [w["detail"] for w in _load_csv("schedule_warnings.csv") if w["poi_id"] == pid]
    is_open_day = rec["is_open"] == "True"
    open_at = None
    reason = rec["source_note"]

    if not is_open_day:
        open_at = False
        reason = f"Đóng cửa cả ngày {day}: {rec['source_note']}"
    elif at_time:
        t_cur = _to_min(at_time)
        t_open = _to_min(rec["open_time"])
        t_close = _to_min(rec["close_time"])
        t_bs = _to_min(rec["break_start"])
        t_be = _to_min(rec["break_end"])
        t_last = _to_min(rec["last_entry_time"])
        if t_cur is None:
            reason = f"Giờ kiểm tra không hợp lệ: {at_time}"
        elif t_open is not None and t_cur < t_open:
            open_at = False
            reason = f"Chưa mở cửa lúc {at_time} (mở từ {rec['open_time']})."
        elif t_close is not None and t_cur >= t_close:
            open_at = False
            reason = f"Đã đóng cửa lúc {at_time} (đóng lúc {rec['close_time']})."
        elif t_bs is not None and t_be is not None and t_bs <= t_cur < t_be:
            open_at = False
            reason = f"Đang nghỉ giữa ca/nghỉ trưa lúc {at_time} ({rec['break_start']}–{rec['break_end']})."
        elif t_last is not None and t_cur > t_last:
            open_at = False
            reason = f"Đã quá giờ ngưng nhận khách/bán vé ({rec['last_entry_time']}) lúc {at_time}."
        else:
            open_at = True
            reason = f"Đang mở cửa lúc {at_time} ({rec['open_time']}–{rec['close_time']})."

    return {
        "found": True,
        "poi_id": pid,
        "day_of_week": day,
        "is_open_day": is_open_day,
        "open_time": rec["open_time"],
        "close_time": rec["close_time"],
        "break_start": rec["break_start"],
        "break_end": rec["break_end"],
        "last_entry_time": rec["last_entry_time"],
        "open_at_time": open_at,
        "status_reason": reason,
        "source_note": rec["source_note"],
        "warnings": warns,
    }


@tool
def get_travel_time(
    city: str,
    from_zone: str,
    to_zone: str,
    mode: str = "motorbike",
    is_raining: bool = False,
) -> dict:
    """Tên: get_travel_time — Tra khoảng cách (km) và thời gian di chuyển giữa 2 cụm khu vực trong data/travel-ops/zone_travel_matrix.csv.
    Input: city (str), from_zone (str), to_zone (str), mode ('motorbike'|'car'|'walk'), is_raining (bool).
    Output: dict gồm distance_km, travel_min, rain_penalty_min, total_min, source_type, note.
    Tác động ra ngoài: Không (chỉ đọc file CSV cục bộ)."""
    city_code = _norm_city(city)
    fz = (from_zone or "").strip().upper()
    tz = (to_zone or "").strip().upper()
    col_map = {"motorbike": "travel_min_motorbike", "car": "travel_min_car", "walk": "travel_min_walk"}
    col = col_map.get((mode or "motorbike").strip().lower(), "travel_min_motorbike")

    rec = next(
        (r for r in _load_csv("zone_travel_matrix.csv") if r["city"] == city_code and r["from_zone"] == fz and r["to_zone"] == tz),
        None,
    )
    if not rec:
        return {"found": False, "city": city_code, "from_zone": fz, "to_zone": tz, "note": "Không tìm thấy cặp vùng trong ma trận."}

    base_min = int(rec[col])
    rain_pen = int(rec["rain_penalty_min"]) if is_raining else 0
    return {
        "found": True,
        "city": city_code,
        "from_zone": fz,
        "to_zone": tz,
        "mode": mode,
        "distance_km": float(rec["distance_km"]),
        "travel_min": base_min,
        "rain_penalty_min": rain_pen,
        "total_min": base_min + rain_pen if base_min < 999 else 999,
        "walk_feasible": base_min < 999 if col == "travel_min_walk" else True,
        "source_type": rec["source_type"],
        "note": rec["note"],
    }


@tool
def get_live_disruptions(city: str = "", zone: str = "", poi_id: str = "") -> list:
    """Tên: get_live_disruptions — Tra sự cố thời gian thực (mưa lớn, nắng gắt, quán đông/đóng đột xuất) từ data/travel-ops/live_disruptions.csv.
    Input: city (str), zone (str), poi_id (str).
    Output: danh sách dict sự cố đang kích hoạt (disruption_id, city, zone, poi_id, disruption_type, severity, start_time, end_time, description).
    Tác động ra ngoài: Không (chỉ đọc file CSV cục bộ)."""
    city_code = _norm_city(city) if city else ""
    z = (zone or "").strip().upper()
    pid = (poi_id or "").strip().upper()
    out = []
    for r in _load_csv("live_disruptions.csv"):
        if r["status"] != "active":
            continue
        if city_code and r["city"] != city_code:
            continue
        if z and r["zone"] != z:
            continue
        if pid and r["poi_id"] != pid:
            continue
        out.append({
            "disruption_id": r["disruption_id"],
            "city": r["city"],
            "zone": r["zone"],
            "poi_id": r["poi_id"],
            "disruption_type": r["disruption_type"],
            "severity": r["severity"],
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "description": r["description"],
            "source_type": r["source_type"],
        })
    return out


@tool
def get_schedule_warnings(city: str = "", poi_id: str = "") -> list:
    """Tên: get_schedule_warnings — Tra các quy tắc cảnh báo lịch trình (đóng cửa theo thứ, nghỉ trưa, khoảng cách xa) từ data/travel-ops/schedule_warnings.csv.
    Input: city (str), poi_id (str).
    Output: danh sách dict cảnh báo (warning_id, severity, rule_code, city, poi_id, time_window, detail, suggested_action).
    Tác động ra ngoài: Không (chỉ đọc file CSV cục bộ)."""
    city_code = _norm_city(city) if city else ""
    pid = (poi_id or "").strip().upper()
    out = []
    for r in _load_csv("schedule_warnings.csv"):
        if city_code and r["city"] != city_code:
            continue
        if pid and r["poi_id"] != pid:
            continue
        out.append(dict(r))
    return out


_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def _strict_min(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise ValueError("Giờ phải có dạng HH:MM (24 giờ)")
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def _clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _day_code(value: str) -> str:
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return _DAYS[date.fromisoformat(value).weekday()]
    day = _norm_day(value)
    if day not in _DAYS:
        raise ValueError("Ngày phải là YYYY-MM-DD hoặc thứ hợp lệ")
    return day


@tool
def kiem_lich_trinh(
    poi_ids: list,
    visit_day: str,
    start_time: str,
    end_time: str,
    mode: str = "motorbike",
    is_raining: bool = False,
) -> dict:
    """Tên: kiem_lich_trinh — Tính giờ và kiểm thứ tự POI do AI đề xuất.
    Input: danh sách poi_id có thứ tự, ngày YYYY-MM-DD hoặc thứ, khung HH:MM,
    phương tiện motorbike/car/walk, cờ mưa. Output: valid, schedule, issues.
    Tác động ra ngoài: Không; chỉ tạo lịch nháp để người dùng duyệt.
    """
    def fail(code, message, schedule=None):
        return {"valid": False, "schedule": schedule or [],
                "issues": [{"code": code, "message": message}]}

    try:
        day = _day_code(visit_day)
        start, end = _strict_min(start_time), _strict_min(end_time)
    except (TypeError, ValueError) as exc:
        return fail("invalid_input", str(exc))
    if end <= start:
        return fail("invalid_window", "Giờ kết thúc phải sau giờ bắt đầu trong cùng ngày")
    if mode not in ("motorbike", "car", "walk"):
        return fail("invalid_mode", "Phương tiện phải là motorbike, car hoặc walk")
    if not isinstance(poi_ids, list) or not poi_ids or any(not isinstance(pid, str) for pid in poi_ids):
        return fail("missing_pois", "Cần danh sách mã POI không rỗng")
    ids = [pid.strip().upper() for pid in poi_ids]
    if len(set(ids)) != len(ids):
        return fail("duplicate_poi", "Danh sách có địa điểm bị lặp")

    pois = {p["poi_id"]: p for p in _load_csv("poi_master.csv")}
    hours = {(r["poi_id"], r["day_of_week"]): r for r in _load_csv("opening_hours.csv")}
    schedule, current, previous = [], start, None
    city = None
    for pid in ids:
        poi = pois.get(pid)
        if poi is None or poi["status"] != "active":
            return fail("unknown_poi", f"Không có dữ liệu điểm đang hoạt động: {pid}", schedule)
        if city is not None and poi["city"] != city:
            return fail("mixed_cities", "Lát cắt chỉ xếp các điểm trong cùng một thành phố", schedule)
        city = poi["city"]
        opening = hours.get((pid, day))
        if opening is None:
            return fail("missing_hours", f"Thiếu giờ mở cửa của {poi['name']} vào {day}", schedule)
        if opening["is_open"] != "True":
            return fail("closed_day", f"{poi['name']} đóng cửa vào {day}", schedule)

        travel = 0
        if previous is not None:
            route = get_travel_time(city, previous["zone"], poi["zone"], mode, is_raining)
            if not route.get("found") or route.get("total_min", 999) >= 999:
                return fail("missing_route", f"Không có thời gian đi phù hợp từ {previous['name']} đến {poi['name']}", schedule)
            travel = route["total_min"]
        arrival = current + travel
        open_at, close_at = _strict_min(opening["open_time"]), _strict_min(opening["close_time"])
        duration = int(poi["avg_duration_min"])
        visit_start = max(arrival, open_at)
        break_start = _to_min(opening["break_start"])
        break_end = _to_min(opening["break_end"])
        if break_start is not None and break_end is not None:
            if visit_start < break_end and visit_start + duration > break_start:
                visit_start = break_end
        departure = visit_start + duration
        last_entry = _to_min(opening["last_entry_time"])
        if last_entry is not None and visit_start > last_entry:
            return fail("after_last_entry", f"{poi['name']} ngưng nhận khách lúc {opening['last_entry_time']}", schedule)
        if departure > close_at:
            return fail("outside_opening_hours", f"{poi['name']} không đủ thời gian trước giờ đóng {opening['close_time']}", schedule)
        if departure > end:
            return fail("outside_user_window", f"{poi['name']} kết thúc sau {end_time}", schedule)
        schedule.append({"poi_id": pid, "name": poi["name"],
                         "travel_minutes_from_previous": travel,
                         "arrival": _clock(arrival), "visit_start": _clock(visit_start),
                         "departure": _clock(departure),
                         "opening_source": opening["source_note"]})
        current, previous = departure, poi
    return {"valid": True, "schedule": schedule, "issues": []}


# ---------------------------------------------------------------- lập lịch, liệt kê vi phạm, gợi ý thay thế
# (bổ sung cho kiem_lich_trinh ở trên: lap_lich + liet_ke_vi_pham dùng trong vòng sửa, goi_y_diem cho nhánh gợi ý)
# Giờ, phút luôn do code tính từ opening_hours.csv và zone_travel_matrix.csv — model chỉ chọn thứ tự.

def _poi(pid: str) -> dict | None:
    return next((r for r in _load_csv("poi_master.csv") if r["poi_id"] == pid), None)


def _hours(pid: str, day: str) -> dict | None:
    return next((r for r in _load_csv("opening_hours.csv") if r["poi_id"] == pid and r["day_of_week"] == day), None)


def _hhmm(minutes: int) -> str:
    return "%02d:%02d" % (minutes // 60 % 24, minutes % 60)


def travel_min(city: str, a: str, b: str, mode: str = "motorbike") -> int:
    """Phút đi giữa 2 POI theo vùng (hàm thường, không ghi trace). Không có cặp vùng → 999."""
    pa, pb = _poi(a), _poi(b)
    if not pa or not pb:
        return 999
    col = {"car": "travel_min_car", "walk": "travel_min_walk"}.get(mode, "travel_min_motorbike")
    rec = next((r for r in _load_csv("zone_travel_matrix.csv")
                if r["city"] == _norm_city(city) and r["from_zone"] == pa["zone"] and r["to_zone"] == pb["zone"]), None)
    return int(rec[col]) if rec else 999


def zone_min(city: str, z1: str, z2: str, mode: str = "motorbike") -> int:
    """Phút đi giữa 2 vùng (hàm thường, không ghi trace). Không có cặp vùng → 999."""
    col = {"car": "travel_min_car", "walk": "travel_min_walk"}.get(mode, "travel_min_motorbike")
    rec = next((r for r in _load_csv("zone_travel_matrix.csv")
                if r["city"] == _norm_city(city) and r["from_zone"] == z1 and r["to_zone"] == z2), None)
    return int(rec[col]) if rec else 999


def _window(rec: dict):
    o, c = _to_min(rec["open_time"]), _to_min(rec["close_time"])
    if o is not None and c is not None and c <= o:
        c += 24 * 60  # mở qua nửa đêm
    return o, c, _to_min(rec["break_start"]), _to_min(rec["break_end"]), _to_min(rec["last_entry_time"])


def _lap_lich(city: str, thu_tu: list, day_of_week: str, bat_dau: str, mode: str = "motorbike",
              start_zone: str = "") -> list:
    day = _norm_day(day_of_week)
    t, prev, out = _to_min(bat_dau) or 0, None, []
    for pid in thu_tu:
        p, rec = _poi(pid), _hours(pid, day)
        if not p or not rec:
            continue
        dur = int(p["avg_duration_min"])
        move = travel_min(city, prev, pid, mode) if prev else (zone_min(city, start_zone, p["zone"], mode) if start_zone else 0)
        arrive = t + move
        o, c, bs, be, _ = _window(rec)
        start = max(arrive, o if o is not None else arrive)
        if bs is not None and be is not None and bs - dur < start < be:
            start = be  # không kịp xong trước giờ nghỉ → chờ mở lại
        out.append({"poi_id": pid, "name": p["name"], "di_chuyen_phut": move, "cho_phut": start - arrive,
                    "den": _hhmm(start), "roi": _hhmm(start + dur)})
        t, prev = start + dur, pid
    return out


@tool
def lap_lich(city: str, thu_tu: list, day_of_week: str, bat_dau: str, mode: str = "motorbike", start_zone: str = "") -> list:
    """Tên: lap_lich — Tính giờ đến / giờ rời từng điểm theo thứ tự đã chọn (code tính, không phải model).
    Input: city, thu_tu (list poi_id), day_of_week, bat_dau ('HH:MM'), mode ('motorbike'|'car'|'walk'),
    start_zone (vùng đang đứng, tùy chọn — cộng thời gian đi tới điểm đầu).
    Output: list {poi_id, name, di_chuyen_phut, cho_phut, den, roi}. Đến sớm / trúng giờ nghỉ trưa thì cộng thời gian chờ.
    Tác động ra ngoài: Không."""
    return _lap_lich(city, thu_tu, day_of_week, bat_dau, mode, start_zone)


def _kiem(city, lich, day_of_week, bat_dau, ket_thuc, mode="motorbike", end_zone=""):
    day = _norm_day(day_of_week)
    issues, prev = [], None
    for s in lich:
        pid = s.get("poi_id")
        rec = _hours(pid, day)
        if not _poi(pid) or not rec:
            issues.append({"poi_id": pid, "loi": "khong_co_du_lieu", "chi_tiet": "không có điểm / giờ mở cửa trong dữ liệu"})
            continue
        den, roi = _to_min(s["den"]), _to_min(s["roi"])
        if roi < den:
            roi += 24 * 60
        o, c, bs, be, last = _window(rec)
        if rec["is_open"] != "True":
            issues.append({"poi_id": pid, "loi": "dong_cua_ca_ngay", "chi_tiet": "đóng cửa %s: %s" % (day, rec["source_note"])})
        else:
            if o is not None and den < o:
                issues.append({"poi_id": pid, "loi": "chua_mo_cua", "chi_tiet": "đến %s, mở %s" % (s["den"], rec["open_time"])})
            if c is not None and roi > c:
                issues.append({"poi_id": pid, "loi": "qua_gio_dong", "chi_tiet": "rời %s, đóng %s" % (s["roi"], rec["close_time"])})
            if last is not None and den > last:
                issues.append({"poi_id": pid, "loi": "qua_gio_nhan_khach", "chi_tiet": "đến %s, ngưng nhận %s" % (s["den"], rec["last_entry_time"])})
            if bs is not None and be is not None and den < be and roi > bs:
                issues.append({"poi_id": pid, "loi": "trung_gio_nghi", "chi_tiet": "nghỉ %s–%s" % (rec["break_start"], rec["break_end"])})
        if den < _to_min(bat_dau) or roi > _to_min(ket_thuc):
            issues.append({"poi_id": pid, "loi": "ngoai_khung_gio",
                           "chi_tiet": "%s–%s ngoài khung %s–%s" % (s["den"], s["roi"], bat_dau, ket_thuc)})
        if prev:
            gap, need = den - _to_min(prev["roi"]), travel_min(city, prev["poi_id"], pid, mode)
            if gap < 0:
                issues.append({"poi_id": pid, "loi": "chong_gio", "chi_tiet": "đến trước khi rời điểm trước"})
            elif gap < need:
                issues.append({"poi_id": pid, "loi": "khong_du_thoi_gian_di", "chi_tiet": "có %d phút, cần %d phút" % (gap, need)})
            elif gap - need > 60:
                issues.append({"poi_id": pid, "loi": "cho_qua_lau", "chi_tiet": "chờ %d phút" % (gap - need)})
        prev = s
    if end_zone and lich and _poi(lich[-1].get("poi_id")):
        last = lich[-1]
        back = zone_min(city, _poi(last["poi_id"])["zone"], end_zone, mode)
        if _to_min(last["roi"]) + back > _to_min(ket_thuc):
            issues.append({"poi_id": last["poi_id"], "loi": "khong_kip_quay_ve",
                           "chi_tiet": "rời %s + %d phút quay về = %s, quá %s"
                           % (last["roi"], back, _hhmm(_to_min(last["roi"]) + back), ket_thuc)})
    return issues


@tool
def liet_ke_vi_pham(city: str, lich: list, day_of_week: str, bat_dau: str, ket_thuc: str, mode: str = "motorbike",
                    end_zone: str = "") -> list:
    """Tên: liet_ke_vi_pham — Liệt kê ĐỦ mọi vi phạm của một lịch (để model sửa trong vòng lặp).
    Khác kiem_lich_trinh (dừng ở lỗi đầu tiên, dùng làm cổng kiểm cuối): công cụ này không dừng sớm,
    và tính thêm vùng xuất phát / quay về.
    Input: city, lich (list {poi_id, den, roi}), day_of_week, bat_dau, ket_thuc ('HH:MM'), mode.
    Output: list vi phạm {poi_id, loi, chi_tiet}; [] là lịch sạch. Loại lỗi: khong_co_du_lieu · dong_cua_ca_ngay ·
    chua_mo_cua · qua_gio_dong · qua_gio_nhan_khach · trung_gio_nghi · ngoai_khung_gio · chong_gio ·
    khong_du_thoi_gian_di · khong_kip_quay_ve (khi có end_zone) · cho_qua_lau (chỉ là cảnh báo).
    Tác động ra ngoài: Không."""
    return _kiem(city, lich, day_of_week, bat_dau, ket_thuc, mode, end_zone)


def _open_for(pid: str, day: str, at: int, need_min: int) -> tuple:
    """(mở được không, giờ đóng) cho một POI lúc `at` phút, cần ở lại ít nhất need_min phút.
    day rỗng → chỉ tính là mở nếu mở như vậy ở CẢ 7 thứ (chưa biết thứ thì không đoán)."""
    days = [day] if day else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    close = None
    for d in days:
        rec = _hours(pid, d)
        if not rec or rec["is_open"] != "True":
            return False, None
        o, c, bs, be, last = _window(rec)
        if o is None or c is None or at < o or at + need_min > c or (last is not None and at > last):
            return False, None
        if bs is not None and be is not None and at < be and at + need_min > bs:
            return False, None
        close = rec["close_time"]
    return True, close


@tool
def goi_y_diem(city: str, day_of_week: str = "", at_time: str = "", from_zone: str = "", mode: str = "motorbike",
               rain_safe: bool = False, heat_safe: bool = False, indoor_only: bool = False, categories: list = None,
               exclude: list = None, max_travel_min: int = 40, limit: int = 6) -> list:
    """Tên: goi_y_diem — Lọc điểm thay thế ĐANG MỞ quanh một vùng (code lọc, model chỉ chọn trong danh sách này).
    Input: city, day_of_week (rỗng = chưa biết thứ → chỉ lấy nơi mở mọi ngày giờ đó), at_time 'HH:MM' (rỗng = chỉ cần
    mở cửa hôm đó), from_zone, mode, rain_safe / heat_safe / indoor_only (bool), categories (list, vd ['food','cafe']),
    exclude (list poi_id), max_travel_min, limit.
    Output: list {poi_id, name, zone, category, indoor_outdoor, di_chuyen_phut, dong_cua_luc, su_co} xếp theo phút đi.
    Bỏ điểm đang có sự cố live mức high. Tác động ra ngoài: Không."""
    city_code, day = _norm_city(city), (_norm_day(day_of_week) if day_of_week else "")
    at = _to_min(at_time) if at_time else None
    live = {r["poi_id"]: r for r in _load_csv("live_disruptions.csv") if r["status"] == "active" and r["poi_id"]}
    out = []
    for p in _load_csv("poi_master.csv"):
        pid = p["poi_id"]
        if p["city"] != city_code or pid in (exclude or []) or p["status"] != "active":
            continue
        if categories and p["category"] not in categories:
            continue
        if (rain_safe and p["rain_safe"] != "True") or (heat_safe and p["heat_safe"] != "True"):
            continue
        if indoor_only and p["indoor_outdoor"] != "indoor":
            continue
        move = zone_min(city_code, from_zone, p["zone"], mode) if from_zone else 0
        if move > max_travel_min:
            continue
        if at is not None:
            ok, close = _open_for(pid, day, at + move, min(45, int(p["avg_duration_min"])))
        else:
            rec = _hours(pid, day) if day else None
            ok, close = bool(rec and rec["is_open"] == "True"), (rec["close_time"] if rec else None)
        if not ok:
            continue
        d = live.get(pid)
        if d and d["severity"] == "high":
            continue
        out.append({"poi_id": pid, "name": p["name"], "zone": p["zone"], "category": p["category"],
                    "indoor_outdoor": p["indoor_outdoor"], "di_chuyen_phut": move, "dong_cua_luc": close,
                    "su_co": d["description"] if d else ""})
    out.sort(key=lambda x: (x["di_chuyen_phut"], bool(x["su_co"]), x["poi_id"]))
    return out[:max(1, int(limit))]


@tool
def uoc_chi_phi(poi_ids: list, so_nguoi: int = 1) -> dict:
    """Tên: uoc_chi_phi — ước tính khoảng chi phí của các điểm trong lịch.
    Input: poi_ids theo thứ tự lịch, so_nguoi để ghi nhận số người.
    Output: tong_min, tong_max VNĐ/người; so_nguoi, tung_diem, khong_ro, nguon.
    Tác động ra ngoài: Không; chỉ đọc bảng giá và danh mục điểm."""
    points = {r["poi_id"]: r for r in _load_csv("poi_master.csv")}
    prices = {r["price_tier"]: r for r in _load_csv("price_tier_vnd.csv")}
    result = {"tong_min": 0, "tong_max": 0, "so_nguoi": so_nguoi,
              "tung_diem": [], "khong_ro": [], "nguon": "(tự ước tính)"}
    for pid in poi_ids or []:
        point = points.get(pid)
        tier = point["price_tier"] if point else ""
        price = prices.get(tier)
        if not price:
            result["khong_ro"].append(pid)
            continue
        try:
            low, high = int(price["min_vnd"]), int(price["max_vnd"])
        except (KeyError, ValueError, TypeError):
            result["khong_ro"].append(pid)
            continue
        result["tung_diem"].append({"poi_id": pid, "price_tier": tier,
                                   "min_vnd": low, "max_vnd": high})
        result["tong_min"] += low
        result["tong_max"] += high
    return result
