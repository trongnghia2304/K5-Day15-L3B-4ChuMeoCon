"""Luồng CP2: tìm đúng điểm -> AI chọn thứ tự -> code kiểm -> lịch nháp."""
import json
import re
from datetime import date

from ai import call_model
from tools import (
    _norm,
    check_opening_hours,
    get_travel_time,
    kiem_lich_trinh,
    search_pois,
)
from tracing import note

SYSTEM = (
    "Bạn là Travel AI Agent hỗ trợ xếp lịch trình một ngày trong một thành phố. "
    "Chỉ dùng địa điểm, giờ mở cửa và thời gian di chuyển trong phần dữ liệu công cụ; "
    "không bịa điểm hay giờ. Ưu tiên thứ tự thuận đường, tránh ngày đóng cửa, "
    "giờ nghỉ, giờ nhận khách cuối và khung giờ người dùng. "
    "Chỉ sắp thứ tự các mã POI được cung cấp, giữ đủ từng mã đúng một lần. "
    "Trả duy nhất JSON dạng {\"poi_ids\":[\"POI_...\"]}, không thêm lời giải thích. "
    "Không tự đặt chỗ hoặc gửi tin cho ai; lịch chỉ là bản nháp chờ người dùng duyệt."
)
GENERIC_WORDS = {"bao", "tang", "ca", "phe", "nha", "hang", "tiem", "cua", "gio", "thanh", "pho", "cong", "vien"}


def _requested_pois(text: str) -> list:
    """Ghép tên điểm theo cụm từ dài nhất xuất hiện trong yêu cầu, không đoán điểm."""
    candidates = search_pois(query=text, limit=100)
    normalized = _norm(text)
    matches = []
    for poi in candidates:
        words = _norm(poi["name"]).split()
        found = None
        for size in range(len(words), 1, -1):
            for start in range(len(words) - size + 1):
                phrase = " ".join(words[start:start + size])
                match = re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", normalized)
                if match and (found is None or size > found[0]):
                    found = (size, match.start(), phrase)
            if found:
                break
        if found:
            matches.append((found[1], found[0], found[2], poi))
    # Cụm hai từ chỉ đủ rõ khi nó nhận diện đúng một điểm trong tập ứng viên.
    counts = {}
    for _, size, phrase, _ in matches:
        if size == 2:
            counts[phrase] = counts.get(phrase, 0) + 1
    matches = [m for m in matches if m[1] >= 3 or
               (counts[m[2]] == 1 and any(word not in GENERIC_WORDS for word in m[2].split()))]
    return [m[3] for m in sorted(matches, key=lambda m: m[0])]


def _visit_day(text: str):
    iso = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
    if iso:
        try:
            return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[date.fromisoformat(iso.group()).weekday()]
        except ValueError:
            return None
    normalized = _norm(text)
    for phrase, code in (("chu nhat", "Sun"), ("thu hai", "Mon"),
                         ("thu ba", "Tue"), ("thu tu", "Wed"),
                         ("thu nam", "Thu"), ("thu sau", "Fri"),
                         ("thu bay", "Sat")):
        if re.search(r"(?<!\w)" + phrase + r"(?!\w)", normalized):
            return code
    return None


def _window(text: str):
    times = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", text)
    if len(times) < 2:
        return None
    return tuple(f"{int(t.split(':')[0]):02d}:{t.split(':')[1]}" for t in times[:2])


def _mode(text: str):
    normalized = _norm(text)
    if "di bo" in normalized:
        return "walk", False
    if "o to" in normalized or "xe hoi" in normalized:
        return "car", False
    if "xe may" in normalized:
        return "motorbike", False
    return "motorbike", True


def _model_order(response: str):
    cleaned = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        value = json.loads(cleaned)
    except (ValueError, TypeError):
        return None
    if not isinstance(value, dict) or not isinstance(value.get("poi_ids"), list):
        return None
    return value["poi_ids"]


def answer(text: str) -> dict:
    pois = _requested_pois(text)
    if not pois:
        return {"output": "Không tìm thấy địa điểm được nêu rõ trong bộ dữ liệu. Vui lòng ghi đúng tên điểm và thành phố."}
    if len({poi["city"] for poi in pois}) != 1:
        return {"output": "Lát cắt chỉ xếp các điểm trong cùng một thành phố."}
    if len(pois) > 8:
        return {"output": "Bản chạy thử chỉ nhận tối đa 8 điểm trong một ngày; vui lòng bớt điểm."}
    day, window = _visit_day(text), _window(text)
    if day is None or window is None:
        return {"output": "Vui lòng cho biết ngày hoặc thứ đi và khung giờ bắt đầu–kết thúc (HH:MM)."}
    mode, assumed_mode = _mode(text)

    context = []
    for poi in pois:
        hours = check_opening_hours(poi["poi_id"], day)
        if not hours.get("found"):
            return {"output": f"Thiếu giờ mở cửa của {poi['name']}; chưa thể xếp lịch."}
        context.append(
            f"{poi['poi_id']} | {poi['name']} | vùng {poi['zone']} | "
            f"mở {hours['open_time'] or 'đóng cửa'}–{hours['close_time'] or 'cả ngày'} | "
            f"nghỉ {hours['break_start'] or '-'}–{hours['break_end'] or '-'} | "
            f"nhận khách cuối {hours['last_entry_time'] or '-'} | "
            f"thời lượng {poi['avg_duration_min']} phút"
        )
    for index, first in enumerate(pois):
        for second in pois[index + 1:]:
            for origin, destination in ((first, second), (second, first)):
                route = get_travel_time(origin["city"], origin["zone"], destination["zone"], mode)
                context.append(f"Đi {origin['poi_id']} -> {destination['poi_id']}: {route.get('total_min', 'thiếu')} phút")

    allowed = [poi["poi_id"] for poi in pois]
    prompt = (
        f"Ngày/thứ: {day}; khung {window[0]}–{window[1]}; phương tiện {mode}.\n"
        f"Dữ liệu công cụ:\n" + "\n".join(context) + "\n"
        f"Chỉ sắp thứ tự các mã sau: {', '.join(allowed)}.\n"
        f"Yêu cầu: {text}"
    )
    reply = call_model(SYSTEM, prompt)
    order = allowed if reply["model"] == "fake" else _model_order(reply["text"])
    if (order is None or len(order) != len(allowed)
            or any(not isinstance(pid, str) for pid in order)
            or set(order) != set(allowed)):
        note("dừng: model không trả đúng danh sách mã POI")
        return {"output": "Chưa xếp được lịch: đề xuất thứ tự không đủ hoặc có điểm ngoài dữ liệu."}

    checked = kiem_lich_trinh(order, day, window[0], window[1], mode)
    if not checked["valid"]:
        note("dừng: kiểm lịch phát hiện vi phạm")
        issue = checked["issues"][0]
        advice = "Hãy bỏ hoặc dời điểm đó sang ngày khác." if issue["code"] == "closed_day" else "Hãy đổi thứ tự, bớt điểm hoặc nới khung giờ."
        return {"output": "Chưa xếp được lịch an toàn: " + issue["message"] + ". " + advice}
    prefix = "[Luồng CP2 với model giả] " if reply["model"] == "fake" else ""
    lines = [prefix + "Lịch nháp để bạn duyệt:"]
    if assumed_mode:
        lines.append("(Tạm tính thời gian đi bằng xe máy vì bạn chưa nêu phương tiện.)")
    for stop in checked["schedule"]:
        lines.append(f"- {stop['visit_start']}–{stop['departure']}: {stop['name']} (đến {stop['arrival']}; đi từ điểm trước {stop['travel_minutes_from_previous']} phút)")
    lines.append("Giờ mở cửa và thời gian đi có thể thay đổi; hãy kiểm lại trước chuyến đi. Chưa đặt chỗ hoặc gửi lịch cho ai.")
    return {"output": "\n".join(lines)}
