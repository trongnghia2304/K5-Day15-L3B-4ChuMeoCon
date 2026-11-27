"""Ngữ cảnh hội thoại của web chat (hướng A+) — chỉ là ghép chữ, không có logic AI.

Luật (đề xuất hợp đồng H1 v2):
  - Tin đầu / tin sau khi đã ra lịch → gửi nguyên văn.
  - Lượt trước agent HỎI LẠI (trace có ghi chú bắt đầu bằng "hỏi lại") → nối: "<tin mới>. <câu đã gửi lần trước>".
    Tin mới đặt TRƯỚC vì bộ tách luật lấy giờ / thứ xuất hiện đầu tiên → người dùng sửa thì giá trị mới thắng.
  - Web không đọc output để quyết định (H7) — chỉ đọc ghi chú trace do agent tự ghi.
"""
import re

TIEN_TO_HOI_LAI = "hỏi lại"
MAU_XONG_SOM = ("Lúc __:__ {thu} mình đang ở ____ {tp}, xong sớm rồi, quanh đây còn chỗ nào đang mở không? "
                "Đã đi: {da_di}.")
_CAU_FORM = re.compile(r"^(Thứ \w+|Chủ Nhật) ở (.+?) từ .+? đi (?:xe máy|ô tô|đi bộ): (.+?)\.(?: Ngân sách|$)")


def la_hoi_lai(events: list) -> bool:
    """True nếu agent vừa hỏi lại (agent.py ghi note "hỏi lại: thiếu …" / "hỏi lại (gợi ý): thiếu …")."""
    return any(e.get("kind") == "note" and str(e.get("text", "")).startswith(TIEN_TO_HOI_LAI) for e in events or [])


def noi_tin(tin_moi: str, ngu_canh: str | None) -> str:
    """Câu gửi cho agent. Không có ngữ cảnh đang chờ → nguyên văn tin mới."""
    moi = (tin_moi or "").strip()
    if not ngu_canh:
        return moi
    return "%s %s" % (moi if re.search(r"[.!?]$", moi) else moi + ".", ngu_canh.strip())


def ngu_canh_tiep(cau_da_gui: str, events: list) -> str | None:
    """Ngữ cảnh giữ cho lượt sau: chỉ giữ khi agent hỏi lại; đã ra lịch / gợi ý thì bắt đầu lại."""
    return cau_da_gui if la_hoi_lai(events) else None


def cau_xong_som(cau_da_gui: str) -> str:
    """Câu mẫu cho nút "Còn thời gian?". Người dùng tự điền giờ và nơi đang đứng (web không đọc output).

    Câu do form ghép (mẫu H1) thì điền sẵn thứ, thành phố, các điểm đã đi (agent loại điểm đã nhắc khỏi gợi ý);
    câu gõ tự do thì để chỗ trống cho người dùng điền.
    """
    m = _CAU_FORM.search(cau_da_gui or "")
    if m:
        return MAU_XONG_SOM.format(thu=m.group(1), tp="(%s)" % m.group(2), da_di=m.group(3))
    return MAU_XONG_SOM.format(thu="Thứ __", tp="", da_di="____").replace(" ,", ",")
