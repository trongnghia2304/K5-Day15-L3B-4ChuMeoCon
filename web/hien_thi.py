"""Chỉ phục vụ phần hiển thị web: không đổi output của agent (eval vẫn chấm trên output gốc có mã điểm)."""
import re

_MA_DIEM = re.compile(r"\[POI_[A-Za-z0-9_]+\]\s?")


_TIEN_TRONG_CAU = re.compile(r"(?<![\d.])(\d{4,})đ")


def dinh_dang_tien(so) -> str:
    """200000 → '200.000đ' (cùng cách viết với dòng chi phí của agent). Chữ người dùng tự gõ thì để nguyên."""
    return f"{so:,}đ".replace(",", ".") if isinstance(so, int) else str(so)


def lam_dep_cau(chu: str) -> str:
    """Câu hiện trong bong bóng người dùng: 'Ngân sách 300000đ/người' → 'Ngân sách 300.000đ/người'."""
    return _TIEN_TRONG_CAU.sub(lambda m: dinh_dang_tien(int(m.group(1))), chu)


def bo_ma_diem(dong: str) -> str:
    """'1. 08:00–09:30 · [POI_HN_01] Văn Miếu' → '1. 08:00–09:30 · Văn Miếu'. Người dùng không cần thấy mã nội bộ."""
    return _MA_DIEM.sub("", dong)
