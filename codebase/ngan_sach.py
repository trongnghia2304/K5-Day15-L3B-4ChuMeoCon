"""Dòng chi phí chỉ hiển thị; không thay đổi lịch đã qua cổng kiểm."""

import re

from tools import uoc_chi_phi


_BUDGET = re.compile(r"ngân\s+sách\s+(\d[\d.,]*)\s*(triệu|tr|k|nghìn|ngàn|đ|vnd)?", re.IGNORECASE)


def dong_chi_phi(text: str, poi_ids: list[str]) -> str:
    match = _BUDGET.search(text or "")
    if not match:
        return ""
    amount, unit = match.groups()
    unit = (unit or "").lower()
    try:
        if unit in ("triệu", "tr", "k", "nghìn", "ngàn"):
            budget = round(float(amount.replace(",", ".")) * (1_000_000 if unit in ("triệu", "tr") else 1_000))
        else:
            budget = int(amount.replace(".", "").replace(",", ""))
    except ValueError:
        return ""
    estimate = uoc_chi_phi(poi_ids or [])
    low, high = estimate["tong_min"], estimate["tong_max"]
    if estimate["khong_ro"] or not estimate["tung_diem"]:
        cost = "chưa đủ dữ liệu giá"
        status = "có thể vượt ngân sách"
    else:
        cost = f"{low:,}–{high:,}đ/người".replace(",", ".")
        status = "trong ngân sách" if high <= budget else "vượt ngân sách" if low > budget else "có thể vượt ngân sách"
    limit = f"{budget:,}".replace(",", ".")
    return f"Chi phí ước tính: {cost} (tự ước tính theo mức giá) · ngân sách bạn đưa: {limit}đ/người → {status}"
