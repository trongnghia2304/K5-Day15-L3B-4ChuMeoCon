"""Luồng chính — xếp lịch trình một ngày nhiều điểm. Hình dạng: WORKFLOW CỐ ĐỊNH (spec.md §4).

    1. Code tách yêu cầu (thành phố, thứ, khung giờ, điểm…). CHỈ KHI còn thiếu mới gọi model trích JSON  [call_model, tùy chọn]
    2. Code chặn việc ngoài phạm vi (đặt bàn, nhắn tin, ép bỏ kiểm tra…) — chạy cả khi model bỏ sót
    3. Thiếu thành phố / thứ / khung giờ / điểm → HỎI LẠI một câu, không đoán (G10)
    4. Công cụ: search_pois → check_opening_hours → bảng thời gian đi. Điểm không có dữ liệu → nói rõ, không xếp
    5. Model chọn THỨ TỰ + điểm bỏ + lý do → JSON. Dữ liệu gửi dạng dòng ngắn (như luồng CP2 của Hiếu)  [call_model]
    6. Code lap_lich tính giờ; liet_ke_vi_pham liệt kê đủ lỗi. Có lỗi → trả lỗi cho model sửa  [≤ 2 vòng]
    7. Còn vi phạm → code bỏ điểm vi phạm, báo "không xếp được hết" + lý do (+ điểm thay thế nếu đóng cả ngày)
    8. Cổng kiểm cuối: kiem_lich_trinh (docs/itinerary-tool-contract.md) — chỉ lịch valid mới được hiện
    9. Trả lịch từng giờ + lý do. Người lên lịch tự duyệt rồi gửi nhóm (AI không gửi tin, không đặt chỗ)

  Nhánh GỢI Ý (bước 1 trả loai = "goi_y": đang đi thì mưa / quán đóng / quá đông / xong sớm):
    G1. Thiếu thành phố hoặc giờ hiện tại → hỏi lại
    G2. Code báo trạng thái từng điểm người dùng nhắc (check_opening_hours + get_live_disruptions)
    G3. Code lọc ứng viên ĐANG MỞ quanh vị trí (goi_y_diem: mưa → rain_safe, nắng → heat_safe, loại ăn / cafe)
    G4. Model chọn 1–3 ứng viên + lý do → JSON (chỉ trong danh sách code đã lọc)              [call_model]

Tiết kiệm token (luật 4 của Minh): câu rõ ràng chỉ gọi model 1 lần; prompt ngắn; dữ liệu dạng dòng, chỉ ghi phút đi
giữa các VÙNG; model chỉ trả JSON ngắn, câu trả lời cho người dùng do code định dạng.

Chế độ model giả (MODEL_PROVIDER trống / fake): model không trả JSON → bước 1 dùng bộ tách luật đơn giản,
bước 5 dùng thứ tự tham lam bằng code. Output ghi rõ "(dự phòng)" để không giả làm AI thật.
"""
import json
import os
import re

import ai
import tools
from ai import call_model
from ngan_sach import dong_chi_phi
from tools import (check_opening_hours, get_live_disruptions, goi_y_diem, kiem_lich_trinh, lap_lich,
                   liet_ke_vi_pham, search_pois)
from tracing import note

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_REPAIR = 2
SOFT = {"cho_qua_lau"}  # chỉ là cảnh báo, không tính là vi phạm
GENERIC = {"quan", "tiem", "ca", "phe", "cafe", "coffee", "di", "o", "an", "uong", "the", "nha", "khu", "diem"}
DAY_VN = {"Mon": "Thứ Hai", "Tue": "Thứ Ba", "Wed": "Thứ Tư", "Thu": "Thứ Năm", "Fri": "Thứ Sáu",
          "Sat": "Thứ Bảy", "Sun": "Chủ Nhật"}
OUT_OF_SCOPE = re.compile(r"\b(dat ban|dat cho|dat ve|dat phong|mua ve|thanh toan|chuyen khoan|coc|nhan tin|"
                          r"goi dien|book|giu cho|otp|so the|mat khau)\b")
INJECTION = re.compile(r"\b(bo qua|ignore|khong can kiem|dung kiem|cu ghi|tu bia|bia dai|system prompt)\b")


def _prompt(name):
    with open(os.path.join(HERE, "prompts", name), encoding="utf-8") as f:
        return f.read()


CITY_PHRASES = sorted({a for a in tools._CITY_ALIASES if len(a) >= 3} | {"tp hcm", "tp"}, key=len, reverse=True)
WEAK = {"bao", "tang", "cho", "chua", "den", "pho", "co", "nha", "hang", "bai", "bien", "ho", "dinh", "lau", "bun", "banh"}
SYSTEM_TRICH = _prompt("trich_yeu_cau.md")
SYSTEM_XEP = _prompt("xep_thu_tu.md")
SYSTEM_GOI_Y = _prompt("goi_y.md")


def _words(text):
    return tools._norm(re.sub(r"[^\w\s]", " ", text or "")).split()


def _json(text):
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b <= a:
        return None
    try:
        return json.loads(text[a:b + 1])
    except ValueError:
        return None


def _key(name):
    """Từ đặc trưng của tên điểm (bỏ phần trong ngoặc, tên thành phố, và từ chung chung như quán, tiệm, cà phê)."""
    flat = " %s " % " ".join(_words(re.sub(r"\(.*?\)", " ", name)))
    for alias in CITY_PHRASES:
        flat = flat.replace(" %s " % alias, " ")
    return (set(flat.split()) - GENERIC) or set(_words(name)) - GENERIC


# ---------------------------------------------------------------- bước 1: trích yêu cầu

DAY_WORD = {"2": "Mon", "hai": "Mon", "3": "Tue", "ba": "Tue", "4": "Wed", "tu": "Wed", "5": "Thu", "nam": "Thu",
            "6": "Fri", "sau": "Fri", "7": "Sat", "bay": "Sat"}


def _rule_parse(text):
    """Bộ tách luật — chỉ dùng khi model không trả JSON (chế độ giả, hoặc model lỗi)."""
    flat = " ".join(_words(text))
    city = next((c for a, c in sorted(tools._CITY_ALIASES.items(), key=lambda x: -len(x[0]))
                 if len(a) >= 3 and re.search(r"\b%s\b" % re.escape(a), flat)), None)
    day_text = re.sub(r"\b(sap|xep|theo) thu tu\b|\bthu tu (cac|di|giup)\b", " ", flat)  # "thứ tự" ≠ Thứ Tư
    m = re.search(r"\bthu (2|3|4|5|6|7|hai|ba|tu|nam|sau|bay)\b", day_text) or re.search(r"\bt([2-7])\b", day_text)
    thu = "Sun" if re.search(r"\b(chu nhat|cn)\b", day_text) else (DAY_WORD[m.group(1)] if m else None)
    times = []
    for m in re.finditer(r"(\d{1,2})\s*(?:h|giờ|:)\s*(\d{2})?\s*(sáng|trưa|chiều|tối|đêm)?", text.lower()):
        h, mm = int(m.group(1)), int(m.group(2) or 0)
        if m.group(3) in ("chiều", "tối", "đêm") and h < 12:
            h += 12
        if h <= 23:
            times.append("%02d:%02d" % (h, mm))
    words, toks = set(flat.split()), flat.split()
    hits = []
    for p in tools._load_csv("poi_master.csv"):
        k = _key(p["name"])
        seq = [w for w in _words(re.sub(r"\(.*?\)", " ", p["name"])) if w in k]
        pairs = {" ".join(seq[i:i + 2]) for i in range(len(seq) - 1)}
        strong = [x for x in pairs if not set(x.split()) <= WEAK and re.search(r"\b%s\b" % x, flat)]
        if (not city or p["city"] == city) and k and (
                (len(k & words) / len(k) >= 0.6 and (len(seq) == 1 or any(re.search(r"\b%s\b" % x, flat) for x in pairs)))
                or strong):  # vd "Văn Miếu" đủ nhận ra "Văn Miếu - Quốc Tử Giám"
            hits.append((min(toks.index(w) for w in k & words), p["name"]))
    diem = [n for _, n in sorted(hits)]  # theo thứ tự xuất hiện trong tin nhắn
    mode = "walk" if "di bo" in flat else ("car" if re.search(r"\b(o to|taxi|grab car)\b", flat) else "motorbike")
    goi_y = bool(re.search(r"\b(quanh day|gan day|dang o|dang dung|dang dao|co cho nao|con cho nao|co quan nao|"
                           r"goi y|doi sang|con mo|co mo|dang mo|kip mua|gio nay|luc nay|vua tu)\b", flat)) \
        and not re.search(r"\b(xep giup|xep lich|lich nay|sap lich|len lich|sap thu tu)\b", flat)
    dk = [k for k, pat in (("mua", r"\bmua\b"), ("nang", r"\b(nang|nong)\b"), ("dong_khach", r"\b(dong qua|kin ban|xep hang)\b"),
                           ("dong_cua", r"\b(dong cua|nghi ban)\b"), ("xong_som", r"\bxong som\b")) if re.search(pat, flat)]
    muon = ("an" if re.search(r"\b(an trua|an toi|quan an|dac san|pho|com|bun|banh|hai san)\b", flat)
            else "cafe" if re.search(r"\b(cafe|ca phe|chill)\b", flat)
            else "trong_nha" if re.search(r"\b(trong nha|tru mua|mai che|dieu hoa)\b", flat) else None)
    return {"loai": "goi_y" if goi_y else "xep_lich", "thanh_pho": city, "thu": thu,
            "bat_dau": None if goi_y else (times[0] if times else None),
            "ket_thuc": None if goi_y else (times[1] if len(times) > 1 else None),
            "gio_hien_tai": times[0] if goi_y and times else None,
            "vi_tri_hien_tai": diem[0] if goi_y and diem else (
                re.search(r"\b(?:o|tu) (khu [a-z ]+?)(?:,|$| xep| chay)", flat).group(1)
                if re.search(r"\b(?:o|tu) (khu [a-z ]+?)(?:,|$| xep| chay)", flat) else None),
            "dieu_kien": dk, "muon": muon, "quay_ve": bool(re.search(r"\b(quay ve|ve lai|ve trung tam)\b", flat)),
            "phuong_tien": mode, "diem": diem, "so_nguoi": None, "so_thich": "", "yeu_cau_ngoai_pham_vi": []}


def _du_thong_tin(req):
    """Bộ tách luật đã đủ để chạy tiếp chưa (đủ thì không cần gọi model ở bước trích)."""
    noi = bool(req.get("thanh_pho") or req.get("diem"))
    if req.get("loai") == "goi_y":
        return noi and bool(req.get("gio_hien_tai"))
    return noi and bool(req.get("diem") and req.get("thu") and req.get("bat_dau") and req.get("ket_thuc"))


def trich_yeu_cau(text):
    """Bước 1. Code tách trước; chỉ khi còn thiếu mới gọi model (tiết kiệm 1 lượt gọi cho câu rõ ràng)."""
    req = _rule_parse(text)
    if _du_thong_tin(req):
        note("bước 1: code tách đủ thông tin → không gọi model")
    else:
        got = _json(call_model(SYSTEM_TRICH, "<tin_nhan>\n%s\n</tin_nhan>" % text)["text"])
        if isinstance(got, dict):
            req = got
        else:
            note("bước 1: model không trả JSON → dùng kết quả bộ tách luật (dự phòng)")
    req["city"] = tools._norm_city(req["thanh_pho"]) if req.get("thanh_pho") else None
    if req["city"] and not any(p["city"] == req["city"] for p in tools._load_csv("poi_master.csv")):
        req["city_unknown"], req["city"] = req["thanh_pho"], None
    if req.get("thu"):
        req["thu"] = tools._norm_day(str(req["thu"]))
    if req.get("thu") not in DAY_VN:
        req["thu"] = None
    for k in ("bat_dau", "ket_thuc", "gio_hien_tai"):
        if not (isinstance(req.get(k), str) and re.fullmatch(r"\d{2}:\d{2}", req[k])):
            req[k] = None
    req["loai"] = "goi_y" if req.get("loai") == "goi_y" else "xep_lich"
    req["dieu_kien"] = [str(x) for x in req.get("dieu_kien") or []]
    req["quay_ve"] = bool(req.get("quay_ve"))
    if req.get("phuong_tien") not in ("motorbike", "car", "walk"):
        req["phuong_tien"] = "motorbike"
    req["diem"] = [str(d) for d in req.get("diem") or []]
    req["yeu_cau_ngoai_pham_vi"] = [str(x) for x in req.get("yeu_cau_ngoai_pham_vi") or []]
    return req


def tim_diem(city, name):
    """Khớp tên người dùng gõ với POI trong dữ liệu. Không đủ khớp (≥ 60% từ đặc trưng) → None, không đoán."""
    q = _key(name) or set(_words(name))
    best, score = None, 0.0
    for p in search_pois(city=city or "", query=name, limit=5):
        s = len(q & _key(p["name"])) / len(q) if q else 0
        if s > score:
            best, score = p, s
    return best if score >= 0.6 else None


# ---------------------------------------------------------------- bước 5: chọn thứ tự

def _greedy(req, ids):
    """Thứ tự dự phòng bằng code: luôn đi tới điểm bắt đầu chơi được sớm nhất."""
    city, thu, start = req["city"], req["thu"], req["bat_dau"]
    bo = [{"poi_id": i, "ly_do": "đóng cửa %s" % DAY_VN[thu]} for i in ids if tools._hours(i, thu)["is_open"] != "True"]
    left, order = [i for i in ids if all(b["poi_id"] != i for b in bo)], []
    while left:
        nxt = min(left, key=lambda i: tools._to_min(tools._lap_lich(city, order + [i], thu, start, req["phuong_tien"])[-1]["den"]))
        order.append(nxt)
        left.remove(nxt)
    return {"thu_tu": order, "bo": bo, "ly_do": "(dự phòng) Code xếp theo điểm bắt đầu chơi được sớm nhất."}


IO = {"indoor": "trong", "outdoor": "ngoai", "semi_outdoor": "nua_ngoai"}


def _dong_diem(pid, thu):
    """Một dòng ngắn cho mỗi điểm: mã|tên|vùng|giờ mở|nghỉ|nhận cuối|phút chơi|trong/ngoài trời."""
    p, h = tools._poi(pid), check_opening_hours(pid, thu)
    gio = "%s-%s" % (h["open_time"], h["close_time"]) if h.get("is_open_day") else "DONG_CA_NGAY"
    return "%s|%s|%s|%s|nghi %s|nhan cuoi %s|%sp|%s" % (
        pid, p["name"], p["zone"], gio, "%s-%s" % (h["break_start"], h["break_end"]) if h.get("break_start") else "-",
        h.get("last_entry_time") or "-", p["avg_duration_min"], IO.get(p["indoor_outdoor"], p["indoor_outdoor"]))


def _dong_vung(city, ids, mode):
    """Phút đi giữa các vùng có mặt (mỗi cặp một lần) — thay cho bảng mọi cặp điểm."""
    zones = sorted({tools._poi(i)["zone"] for i in ids})
    pairs = ["%s-%s %d" % (a, b, tools.zone_min(city, a, b, mode)) for n, a in enumerate(zones) for b in zones[n + 1:]]
    same = tools.zone_min(city, zones[0], zones[0], mode) if zones else 0
    return "Đi giữa vùng (phút; cùng vùng %d): %s" % (same, "; ".join(pairs) or "-")


def chon_thu_tu(req, ids, vi_pham=None, thu_tu_truoc=None):
    lines = ["%s · %s-%s · %s" % (req["thu"], req["bat_dau"], req["ket_thuc"], req["phuong_tien"])]
    lines += [_dong_diem(i, req["thu"]) for i in ids]
    lines.append(_dong_vung(req["city"], ids, req["phuong_tien"]))
    if vi_pham:
        lines.append("LỖI LẦN TRƯỚC (thứ tự %s): %s" % (",".join(thu_tu_truoc or []),
                     "; ".join("%s %s" % (x["poi_id"], x["chi_tiet"]) for x in vi_pham)))
    lines.append("Yêu cầu: <tin_nhan>%s</tin_nhan>" % req.get("_text", ""))
    plan = _json(call_model(SYSTEM_XEP, "<du_lieu>\n%s\n</du_lieu>" % "\n".join(lines))["text"])
    if not isinstance(plan, dict) or not isinstance(plan.get("thu_tu"), list):
        note("bước 5: model không trả JSON → thứ tự dự phòng bằng code")
        return _greedy(req, ids)
    order = list(dict.fromkeys(i for i in plan["thu_tu"] if i in ids))
    bo = [b for b in plan.get("bo") or [] if isinstance(b, dict) and b.get("poi_id") in ids and b["poi_id"] not in order]
    bo += [{"poi_id": i, "ly_do": "không được xếp vào lịch"} for i in ids
           if i not in order and all(b["poi_id"] != i for b in bo)]
    return {"thu_tu": order, "bo": bo, "ly_do": str(plan.get("ly_do", ""))}


# ---------------------------------------------------------------- luồng chính

CATS = {"an": ["food", "market"], "cafe": ["cafe"], "tham_quan": None, "trong_nha": None}


def _zone_of(city, text):
    """Vùng của chỗ người dùng đang đứng: khớp tên POI hoặc tên quận / khu trong dữ liệu. Không khớp → ''."""
    if not text or not city:
        return ""
    p = tim_diem(city, text)
    if p:
        return p["zone"]
    q = _key(text) or set(_words(text))
    for r in tools._load_csv("poi_master.csv"):
        if r["city"] == city and q and len(q & set(_words(r["district"] + " " + r["address"]))) / len(q) >= 0.6:
            return r["zone"]
    return ""


def _thay_the(req, pid, exclude, n=2):
    """Gợi ý điểm cùng loại, mở cửa đúng thứ đó, gần điểm bị bỏ (code lọc — không gọi model)."""
    p = tools._poi(pid)
    c = goi_y_diem(req["city"], req["thu"], "", p["zone"], req["phuong_tien"], categories=[p["category"]],
                   exclude=exclude, limit=n) or goi_y_diem(req["city"], req["thu"], "", p["zone"], req["phuong_tien"],
                                                            exclude=exclude, limit=n)
    return ", ".join("[%s] %s" % (x["poi_id"], x["name"]) for x in c)


def answer(text: str) -> dict:
    # Bước 1–2
    req = trich_yeu_cau(text)
    req["_text"] = text
    flat = " ".join(_words(text))
    ngoai = list(req["yeu_cau_ngoai_pham_vi"])
    if OUT_OF_SCOPE.search(flat) and not any("dat" in " ".join(_words(x)) for x in ngoai):
        ngoai.append("đặt chỗ / nhắn tin / thanh toán")
    if INJECTION.search(flat):
        note("phát hiện câu điều khiển trong tin nhắn — coi là dữ liệu, vẫn kiểm lịch bằng code")
        ngoai.append("bỏ qua kiểm tra giờ mở cửa / tự bịa thông tin")
    canh_bao = []
    if ngoai:
        canh_bao.append("Mình chỉ làm việc với dữ liệu có căn cứ: không đặt bàn, không nhắn tin hay thanh toán thay bạn, "
                        "không bịa địa điểm, và luôn kiểm giờ mở cửa bằng dữ liệu (%s). Bạn tự liên hệ từng nơi nhé."
                        % "; ".join(dict.fromkeys(ngoai)))

    # Bước 4 (làm trước bước 3 để câu hỏi lại nhắc được điểm đã nhận)
    ids, khong_co = [], []
    for name in req["diem"]:
        p = tim_diem(req["city"], name)
        if p and not req["city"]:
            req["city"] = p["city"]
        if p and p["city"] == req["city"] and p["poi_id"] not in ids:
            ids.append(p["poi_id"])
        elif not p:
            khong_co.append(name)
    req["zone"] = _zone_of(req["city"], req.get("vi_tri_hien_tai"))

    if req["loai"] == "goi_y":
        return {"output": goi_y_thay_the(req, ids, khong_co, canh_bao)}

    # Chưa biết thứ nhưng giờ mở cửa của mọi điểm giống nhau cả tuần → kết quả không phụ thuộc thứ, xếp luôn
    if not req["thu"] and ids and all(len({(r["is_open"], r["open_time"], r["close_time"], r["break_start"],
                                             r["break_end"], r["last_entry_time"]) for d in DAY_VN
                                            for r in [tools._hours(i, d)]}) == 1 for i in ids):
        req["thu"], req["thu_bat_ky"] = "Mon", True
        note("chưa biết thứ nhưng giờ mở cửa các điểm giống nhau mọi ngày → xếp không cần thứ")

    # Bước 3: thiếu thông tin → hỏi lại, không đoán (G10)
    thieu = []
    if not req["city"]:
        thieu.append("**thành phố** nào" + (" (mình chưa có dữ liệu %s)" % req["city_unknown"] if req.get("city_unknown") else ""))
    if not req["thu"]:
        thieu.append("đi **thứ mấy** (giờ mở cửa và ngày nghỉ của từng nơi khác nhau theo thứ)")
    if not req["bat_dau"] or not req["ket_thuc"]:
        thieu.append("**khung giờ** trong ngày (vd 8h đến 21h)")
    if not ids:
        thieu.append("**những điểm muốn đi**")
    if thieu:
        lines = ["Để xếp lịch không trúng giờ đóng cửa, mình cần biết thêm: " + "; ".join(thieu) + "."]
        if ids:
            lines.append("Điểm đã nhận: " + ", ".join(tools._poi(i)["name"] for i in ids) + ".")
        if ids and not req["thu"] and req["bat_dau"]:  # chưa biết thứ: điểm nào không mở giờ đó ở BẤT KỲ ngày nào
            for i in ids:
                need = min(45, int(tools._poi(i)["avg_duration_min"]))
                if not any(tools._open_for(i, d, tools._to_min(req["bat_dau"]), need)[0] for d in DAY_VN):
                    h = tools._hours(i, "Sat")
                    lines.append("Lưu ý: [%s] %s không mở lúc %s vào bất kỳ ngày nào (giờ mở %s–%s%s)."
                                 % (i, tools._poi(i)["name"], req["bat_dau"], h["open_time"], h["close_time"],
                                    ", nghỉ %s–%s" % (h["break_start"], h["break_end"]) if h["break_start"] else ""))
        if ids and req["thu"]:  # biết thứ rồi thì báo ngay điểm đóng cửa cả ngày, kèm điểm thay thế
            for i in ids:
                if tools._hours(i, req["thu"])["is_open"] != "True":
                    alt = _thay_the(req, i, ids)
                    lines.append("Lưu ý: [%s] %s đóng cửa %s, mình sẽ không xếp vào lịch.%s"
                                 % (i, tools._poi(i)["name"], DAY_VN[req["thu"]], " Có thể thay bằng: " + alt if alt else ""))
        note("hỏi lại: thiếu " + ", ".join(thieu))
        return {"output": "\n".join(lines + _khong_co(khong_co) + canh_bao)}
    if tools._to_min(req["ket_thuc"]) <= tools._to_min(req["bat_dau"]):
        return {"output": "Khung giờ %s–%s chưa hợp lệ (giờ kết thúc phải sau giờ bắt đầu). Bạn ghi lại giúp mình?"
                % (req["bat_dau"], req["ket_thuc"])}

    # Bước 5–6: model chọn thứ tự, code tính giờ + kiểm, model sửa tối đa MAX_REPAIR vòng
    city, thu, mode = req["city"], req["thu"], req["phuong_tien"]
    start_zone, end_zone = req["zone"], (req["zone"] if req["quay_ve"] else "")
    plan, hard = chon_thu_tu(req, ids), []
    for vong in range(MAX_REPAIR + 1):
        lich = lap_lich(city, plan["thu_tu"], thu, req["bat_dau"], mode, start_zone)
        issues = liet_ke_vi_pham(city, lich, thu, req["bat_dau"], req["ket_thuc"], mode, end_zone)
        hard = [x for x in issues if x["loi"] not in SOFT]
        note("vòng %d: %d vi phạm" % (vong, len(hard)))
        if not hard or vong == MAX_REPAIR or ai.MODEL_PROVIDER == "fake":
            break
        plan = chon_thu_tu(req, ids, vi_pham=hard, thu_tu_truoc=plan["thu_tu"])

    # Bước 7: còn vi phạm → code bỏ điểm vi phạm cho đến khi lịch sạch
    bo = list(plan["bo"])
    while hard:
        bad = hard[0]["poi_id"]
        bo.append({"poi_id": bad, "ly_do": "; ".join(x["chi_tiet"] for x in hard if x["poi_id"] == bad)})
        plan["thu_tu"] = [i for i in plan["thu_tu"] if i != bad]
        lich = tools._lap_lich(city, plan["thu_tu"], thu, req["bat_dau"], mode, start_zone)
        issues = tools._kiem(city, lich, thu, req["bat_dau"], req["ket_thuc"], mode, end_zone)
        hard = [x for x in issues if x["loi"] not in SOFT]

    # Bước 8: cổng kiểm cuối — kiem_lich_trinh (dừng ở lỗi đầu tiên). Chỉ lịch valid mới được hiện.
    # Chưa tính vùng xuất phát nên chỉ chạy khi không có start_zone (khi có, liet_ke_vi_pham đã tính đủ).
    while plan["thu_tu"] and not start_zone:
        gate = kiem_lich_trinh(plan["thu_tu"], thu, req["bat_dau"], req["ket_thuc"], mode)
        if gate["valid"]:
            break
        bad = plan["thu_tu"][min(len(gate["schedule"]), len(plan["thu_tu"]) - 1)]
        note("cổng kiểm cuối chặn %s: %s" % (bad, gate["issues"][0]["message"]))
        bo.append({"poi_id": bad, "ly_do": gate["issues"][0]["message"]})
        plan["thu_tu"] = [i for i in plan["thu_tu"] if i != bad]
        lich = tools._lap_lich(city, plan["thu_tu"], thu, req["bat_dau"], mode, start_zone)
        issues = tools._kiem(city, lich, thu, req["bat_dau"], req["ket_thuc"], mode, end_zone)
    for b in bo:  # điểm đóng cửa cả ngày → gợi ý điểm cùng loại đang mở hôm đó
        if tools._hours(b["poi_id"], thu)["is_open"] != "True":
            alt = _thay_the(req, b["poi_id"], ids)
            if alt:
                b["ly_do"] += " → có thể thay bằng: " + alt
    note("lịch cuối: %s · bỏ: %s" % (plan["thu_tu"], [b["poi_id"] for b in bo]))
    output = _format(req, lich, issues, bo, plan["ly_do"], khong_co, canh_bao)
    cost_line = dong_chi_phi(text, plan["thu_tu"])
    return {"output": output + ("\n" + cost_line if cost_line else "")}


# ---------------------------------------------------------------- nhánh gợi ý điểm thay thế (đang đi thì vỡ kế hoạch)

def _trang_thai(pid, thu, at):
    """Một điểm người dùng nhắc có mở lúc `at` không — code đọc opening_hours.csv, kèm sự cố live."""
    p = tools._poi(pid)
    if thu:
        h = check_opening_hours(pid, thu, tools._hhmm(at))
        txt = h.get("status_reason", "")
    else:
        ok_all = tools._open_for(pid, "", at, 0)[0]
        ok_any = any(tools._open_for(pid, d, at, 0)[0] for d in DAY_VN)
        txt = ("đang mở giờ này (mọi ngày trong tuần)" if ok_all else
               "giờ này tùy thứ — bạn cho mình biết hôm nay thứ mấy" if ok_any else "không mở vào giờ này ở bất kỳ ngày nào")
    need = min(45, int(p["avg_duration_min"]))
    if thu and h.get("open_at_time") and not tools._open_for(pid, thu, at, need)[0]:
        txt += " Nhưng không đủ %d phút để tham quan trước giờ nghỉ / đóng cửa%s." % (
            need, " (nghỉ %s–%s)" % (h["break_start"], h["break_end"]) if h.get("break_start") else "")
    live = [d["description"] for d in get_live_disruptions(poi_id=pid)]
    return "[%s] %s: %s%s" % (pid, p["name"], txt, (" · " + "; ".join(live)) if live else "")


def goi_y_thay_the(req, ids, khong_co, canh_bao):
    gio = req.get("gio_hien_tai") or req.get("bat_dau")
    thieu = []
    if not req["city"]:
        thieu.append("bạn đang ở **thành phố / khu nào**")
    if not gio:
        thieu.append("bây giờ là **mấy giờ**")
    if thieu:
        note("hỏi lại (gợi ý): thiếu " + ", ".join(thieu))
        return "\n".join(["Để gợi ý đúng chỗ đang mở, mình cần biết thêm: " + "; ".join(thieu) + "."]
                         + _khong_co(khong_co) + canh_bao)
    at, thu, mode = tools._to_min(gio), req["thu"], req["phuong_tien"]
    zone = req["zone"] or (tools._poi(ids[0])["zone"] if ids else "")
    dk, muon = set(req["dieu_kien"]), req.get("muon")
    filt = dict(rain_safe="mua" in dk, heat_safe="nang" in dk,
                indoor_only=muon == "trong_nha", max_travel_min=15 if mode == "walk" else 30, limit=6)
    cand = goi_y_diem(req["city"], thu or "", gio, zone, mode, categories=CATS.get(muon), exclude=ids, **filt)
    if not cand and CATS.get(muon):
        cand = goi_y_diem(req["city"], thu or "", gio, zone, mode, exclude=ids, **filt)
        note("không có ứng viên đúng loại '%s' → nới bỏ điều kiện loại" % muon)

    chon, ly_do = [c["poi_id"] for c in cand[:3]], "(dự phòng) Code chọn các điểm gần nhất đang mở."
    if cand:
        lines = ["%s %s · %s · muốn: %s" % (gio, thu or "?", ",".join(sorted(dk)) or "-", muon or "-")]
        lines += ["%s|%s|%s|%s|đi %dp|đến %s%s" % (c["poi_id"], c["name"], c["category"],
                                                   IO.get(c["indoor_outdoor"], c["indoor_outdoor"]), c["di_chuyen_phut"],
                                                   c["dong_cua_luc"], "|sự cố: " + c["su_co"] if c["su_co"] else "")
                  for c in cand]
        lines.append("Yêu cầu: <tin_nhan>%s</tin_nhan>" % req.get("_text", ""))
        pick = _json(call_model(SYSTEM_GOI_Y, "<du_lieu>\n%s\n</du_lieu>" % "\n".join(lines))["text"])
        if isinstance(pick, dict) and isinstance(pick.get("chon"), list):
            ok = [i for i in pick["chon"] if i in {c["poi_id"] for c in cand}][:3]
            if ok:
                chon, ly_do = ok, str(pick.get("ly_do", ""))
        else:
            note("bước gợi ý: model không trả JSON → chọn bằng code (dự phòng)")

    by_id = {c["poi_id"]: c for c in cand}
    head = "Lúc %s%s%s" % (gio, " " + DAY_VN[thu] if thu else "", " · " + ", ".join(sorted(dk)) if dk else "")
    out = [head]
    if ids:
        out.append("Điểm bạn nhắc:")
        out += ["  - " + _trang_thai(i, thu, at) for i in ids]
    if chon:
        out.append("Gợi ý đang mở%s:" % ("" if thu else " (chưa biết thứ nên chỉ lấy nơi mở mọi ngày giờ này)"))
        for n, i in enumerate(chon, 1):
            c = by_id[i]
            out.append("%d. [%s] %s — đi %d phút · %s · mở đến %s%s" % (
                n, i, c["name"], c["di_chuyen_phut"], "trong nhà" if c["indoor_outdoor"] == "indoor" else c["indoor_outdoor"],
                c["dong_cua_luc"], " · lưu ý: " + c["su_co"] if c["su_co"] else ""))
        out.append("Vì sao: " + ly_do)
    else:
        out.append("Mình không tìm thấy điểm nào trong dữ liệu đang mở và đi tới kịp từ đây lúc %s. "
                   "Bạn nới điều kiện (đi xa hơn, không cần trong nhà) để mình tìm lại nhé." % gio)
    out += _khong_co(khong_co) + canh_bao
    out.append("Giờ mở cửa lấy từ dữ liệu của bản chạy thử; bạn tự quyết, mình không đặt chỗ hay nhắn tin.")
    return "\n".join(out)


def _khong_co(names):
    if not names:
        return []
    return ["Không có dữ liệu về: %s — mình không biết giờ mở cửa nơi này nên không xếp vào lịch. "
            "Bạn kiểm tra trực tiếp hoặc chọn điểm khác." % ", ".join('"%s"' % n for n in names)]


def _format(req, lich, issues, bo, ly_do, khong_co, canh_bao):
    day = "giờ mở cửa giống nhau mọi ngày" if req.get("thu_bat_ky") else DAY_VN[req["thu"]]
    out = ["Lịch %s — %s, %s–%s%s" % (req.get("thanh_pho") or req["city"], day, req["bat_dau"],
                                      req["ket_thuc"], " · %s người" % req["so_nguoi"] if req.get("so_nguoi") else "")]
    if not lich:
        out.append("Không xếp được điểm nào vào khung giờ này.")
    for n, s in enumerate(lich, 1):
        extra = (["đi %d phút" % s["di_chuyen_phut"]] if s["di_chuyen_phut"] else []) + \
                (["chờ mở cửa %d phút" % s["cho_phut"]] if s["cho_phut"] else [])
        out.append("%d. %s–%s · [%s] %s%s" % (n, s["den"], s["roi"], s["poi_id"], s["name"],
                                             " (%s)" % ", ".join(extra) if extra else ""))
    if lich:
        out.append("Tổng di chuyển: %d phút · xong lúc %s" % (sum(s["di_chuyen_phut"] for s in lich), lich[-1]["roi"]))
    if ly_do:
        out.append("Vì sao xếp như vậy: " + ly_do)
    if bo:
        out.append("Không xếp được hết — đã bỏ:")
        out += ["  - [%s] %s: %s" % (b["poi_id"], tools._poi(b["poi_id"])["name"], b.get("ly_do", "")) for b in bo]
        out.append("Muốn giữ điểm nào thì nới khung giờ hoặc bỏ bớt một điểm khác.")
    out += ["Lưu ý: [%s] %s" % (x["poi_id"], x["chi_tiet"]) for x in issues if x["loi"] in SOFT]
    out += _khong_co(khong_co) + canh_bao
    out.append("Bạn xem lại rồi tự gửi nhóm — mình không gửi tin hay đặt chỗ.")
    return "\n".join(out)
