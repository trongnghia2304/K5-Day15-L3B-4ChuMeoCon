"""Ghép form web thành câu chữ gửi vào agent.answer — hợp đồng H1 (docs/hop-dong-du-lieu.md).

Mẫu:  {Thứ} ở {Thành phố} từ {HH:MM} đến {HH:MM} đi {phương tiện}: {điểm 1}, {điểm 2}.[ Ngân sách {số}đ/người.]

File này KHÔNG import streamlit để test được bằng thư viện chuẩn (python -m unittest web.test_ghep_cau).
"""
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POI_FILE = os.path.join(ROOT, "data", "travel-ops", "poi_master.csv")

THU = ("Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật")
PHUONG_TIEN = ("xe máy", "ô tô", "đi bộ")
# Tên hiển thị (ghép vào câu) → mã thành phố trong data. Thứ tự = thứ tự trong ô chọn.
THANH_PHO = {
    "Hà Nội": "HN", "TP.HCM": "HCM", "Đà Nẵng": "DN", "Huế": "HUE", "Hội An": "HA", "Nha Trang": "NT",
    "Đà Lạt": "DL", "Sa Pa": "SP", "Hải Phòng": "HP", "Hạ Long": "QN", "Tam Đảo": "TD", "Hà Giang": "HG",
}
_GIO = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def doc_diem(path: str = POI_FILE) -> dict:
    """Đọc poi_master.csv (chỉ đọc) → {mã thành phố: [tên điểm, …]} để hiện trong ô chọn."""
    out: dict = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out.setdefault(row["city"], []).append(row["name"])
    return out


def _sach(text: str) -> str:
    """Bỏ ký tự làm vỡ mẫu câu (dấu phẩy, hai chấm, xuống dòng) trong tên điểm người dùng gõ."""
    return " ".join(re.sub(r"[,:;\n\r]", " ", text or "").split())


def ghep_cau(thu: str, thanh_pho: str, bat_dau: str, ket_thuc: str, phuong_tien: str,
             diem: list, ngan_sach: int | None = None) -> str:
    """Trả câu chữ đúng mẫu H1. Sai đầu vào → ValueError kèm lời nhắn tiếng Việt để hiện trên form."""
    if thu not in THU:
        raise ValueError("Chọn thứ trong tuần.")
    if thanh_pho not in THANH_PHO:
        raise ValueError("Chọn thành phố trong danh sách.")
    if not (_GIO.match(bat_dau or "") and _GIO.match(ket_thuc or "")):
        raise ValueError("Giờ phải dạng HH:MM, vd 08:00.")
    if ket_thuc <= bat_dau:
        raise ValueError("Giờ kết thúc phải sau giờ bắt đầu.")
    if phuong_tien not in PHUONG_TIEN:
        raise ValueError("Chọn phương tiện.")
    ten = list(dict.fromkeys(d for d in (_sach(x) for x in diem or []) if d))
    if not ten:
        raise ValueError("Chọn hoặc gõ ít nhất một điểm muốn đi.")
    cau = "%s ở %s từ %s đến %s đi %s: %s." % (thu, thanh_pho, bat_dau, ket_thuc, phuong_tien, ", ".join(ten))
    if ngan_sach:
        if int(ngan_sach) <= 0:
            raise ValueError("Ngân sách phải là số dương (VNĐ).")
        cau += " Ngân sách %dđ/người." % int(ngan_sach)
    return cau


_TIEN = re.compile(r"^(\d+(?:[.,]\d+)*)\s*(k|nghìn|ngàn|tr|triệu)?\s*(?:đ|₫|vnđ|vnd|đồng)?(?:\s*/\s*người)?$")
_HE_SO = {None: 1, "k": 1_000, "nghìn": 1_000, "ngàn": 1_000, "tr": 1_000_000, "triệu": 1_000_000}


def doc_tien(text) -> int | None:
    """'200.000đ' / '200,000' / '200k' / '1,5tr' → số đồng. Trống hoặc 0 → None. Sai → ValueError."""
    if isinstance(text, int):
        return text or None
    s = " ".join(str(text or "").lower().split())
    if not s:
        return None
    m = _TIEN.match(s)
    if not m:
        raise ValueError("Ngân sách ghi bằng số, vd 200.000đ hoặc 200k.")
    so, don_vi = m.group(1), m.group(2)
    if don_vi and re.fullmatch(r"\d+[.,]\d{1,2}", so):  # 1,5tr → 1.5 triệu
        tien = round(float(so.replace(",", ".")) * _HE_SO[don_vi])
    else:  # dấu chấm / phẩy là phân cách hàng nghìn
        tien = int(re.sub(r"[.,]", "", so)) * _HE_SO[don_vi]
    return tien or None


def tach_diem_go_tay(text: str) -> list:
    """Ô 'điểm khác' cho gõ nhiều điểm, mỗi dòng một điểm (hoặc cách nhau bằng dấu phẩy)."""
    return [x.strip() for x in re.split(r"[,\n;]", text or "") if x.strip()]
