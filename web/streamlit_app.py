"""Web demo (N4, hướng A+) — giao diện chat; mỗi lượt gửi đúng 1 câu chữ vào agent.answer(text).

Không có logic AI riêng, không tự tính giờ / tiền, không sửa nội dung output (H7: hiển thị nguyên văn).
Ngữ cảnh: chỉ khi agent vừa HỎI LẠI thì web nối tin mới với câu đã gửi trước (web/hoi_thoai.py).
Chạy máy mình:  python -m pip install -r requirements.txt  →  streamlit run web/streamlit_app.py
Biến môi trường (đặt trong .env ở máy, hoặc Variables trên Railway — KHÔNG ghi vào repo):
    MODEL_PROVIDER, MODEL_NAME, API_KEY   — như docs/connect-model.md (codebase/ai.py đọc)
    APP_PASSWORD                          — mật khẩu vào web; để trống chỉ khi chạy máy mình
    MAX_LUOT                              — số lượt hỏi tối đa mỗi phiên trình duyệt (mặc định 10)

Giao diện phong cách Editorial Travel / Modern Clean: nền giấy ấm #FAF8F5, nhấn xanh rừng #1B4D3E & đất nung #C85A32;
font Lora + Be Vietnam Pro + JetBrains Mono.
"""
import hmac
import html
import logging
import os
import re
import sys
import threading

import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))

import ai  # noqa: E402  (nạp .env vào biến môi trường)
import tracing  # noqa: E402
from agent import answer  # noqa: E402
from ghep_cau import PHUONG_TIEN, THANH_PHO, THU, doc_diem, doc_tien, ghep_cau, tach_diem_go_tay  # noqa: E402
from hien_thi import bo_ma_diem, lam_dep_cau  # noqa: E402
from hoi_thoai import cau_xong_som, ngu_canh_tiep, noi_tin  # noqa: E402

log = logging.getLogger("web")
_DAM = re.compile(r"\*\*(.+?)\*\*")  # agent đánh dấu chữ đậm kiểu Markdown trong câu hỏi lại
_DONG_LICH = re.compile(r"^\d+\.\s+\d{2}:\d{2}")
MAX_LUOT_MAC_DINH = 10
AVATAR = {"user": ":material/person:", "ai": ":material/explore:"}

CAU_MAU = (
    ("Lên lịch 1 ngày Hà Nội", "Thứ Bảy ở Hà Nội từ 08:00 đến 17:00 đi xe máy: Hồ Gươm, Nhà thờ Lớn, Chùa Một Cột."),
    ("Lên lịch TP.HCM kèm ngân sách", "Thứ Sáu ở TP.HCM từ 08:00 đến 18:00 đi xe máy: Dinh Độc Lập, Nhà thờ Đức Bà, Bếp Mẹ Ỉn. Ngân sách 300000đ/người."),
    ("Trời mưa đổi điểm trong nhà", "14:05 Thứ Bảy đang ở Thảo Cầm Viên thì mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?"),
)

SVG_PIN = (
    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>'
)
SVG_COMPASS = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>'
)

NHAN_NGAN_SACH = "Ngân sách / người"
# Chạy trong trang (st.html, unsafe_allow_javascript) → gắn vào ô ngân sách; chạy lại nhiều lần vẫn chỉ gắn 1 lần.
# Đặt giá trị qua setter gốc + phát sự kiện "input" để React (Streamlit) nhận đúng giá trị mới.
JS_NGAN_SACH = r"""
<script>
(function () {
  const w = window;
  if (w.__ganNganSach) return;
  w.__ganNganSach = true;
  const setter = Object.getOwnPropertyDescriptor(w.HTMLInputElement.prototype, "value").set;
  const dep = (v) => v.replace(/\D/g, "").replace(/^0+(?=\d)/, "").slice(0, 10)
                     .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const gan = () => {
    w.document.querySelectorAll('input[aria-label^="%s"]').forEach((o) => {
      if (o.dataset.tien) return;
      o.dataset.tien = "1";
      o.setAttribute("inputmode", "numeric");
      const sua = () => {
        const moi = dep(o.value);
        if (moi === o.value) return;
        setter.call(o, moi);
        o.dispatchEvent(new w.Event("input", { bubbles: true }));
      };
      o.addEventListener("input", sua);
      sua();
    });
  };
  gan();
  w.setInterval(gan, 500);
})();
</script>
""" % NHAN_NGAN_SACH

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Lora:wght@500;600&display=swap');

:root {
  --canvas: #FAF8F5;
  --card: #FFFFFF;
  --surface-warm: #F3EFE9;
  --surface-user: #EFE9DF;
  --ink: #1C1917;
  --ink-muted: #57534E;
  --ink-soft: #78716C;
  --primary: #1B4D3E;
  --primary-hover: #143D30;
  --primary-tint: #ECF4F0;
  --accent: #C85A32;
  --accent-tint: #FDF2EC;
  --border: #E7E2DA;
  --border-strong: #D6CFC3;
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 18px;
  --r-pill: 999px;
  --shadow-card: 0 2px 12px rgba(28, 25, 23, 0.045);
  --shadow-input: 0 4px 18px rgba(28, 25, 23, 0.06);
}

html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stBottom"] > div {
  background: var(--canvas) !important;
  color: var(--ink);
}
.stApp :is(p, li, label, span, div, button, input, textarea):not([data-testid="stIconMaterial"]):not([class*="material"]) {
  font-family: 'Be Vietnam Pro', system-ui, -apple-system, sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], [data-testid="stDecoration"] {
  display: none;
}
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button { color: var(--ink); }

.block-container {
  max-width: 50rem;
  padding-top: 1.75rem;
  padding-bottom: 7.5rem;
}
.stApp p, .stApp li {
  font-weight: 400;
  line-height: 1.6;
  color: var(--ink);
}

/* Header Editorial Travel */
.khoi-header {
  border-bottom: 1px solid var(--border);
  padding: 4px 0 24px;
  margin: 0 0 28px;
}
.khoi-header.gon {
  padding: 0 0 16px;
  margin: 0 0 20px;
}
.header-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin: 0 0 12px;
}
.header-eyebrow {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.74rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 500;
}
.city-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--primary-tint);
  color: var(--primary);
  border: 1px solid rgba(27, 77, 62, 0.16);
  border-radius: var(--r-pill);
  padding: 3px 11px;
  font-size: 0.76rem;
  font-weight: 500;
  line-height: 1.3;
}
.khoi-header h1 {
  font-family: 'Lora', Georgia, serif !important;
  font-weight: 600 !important;
  font-size: clamp(2rem, 4.6vw, 2.85rem) !important;
  line-height: 1.15 !important;
  letter-spacing: -0.02em;
  color: var(--ink) !important;
  margin: 0 !important;
  padding: 0 !important;
  text-wrap: balance;
}
.khoi-header.gon h1 {
  font-size: 1.55rem !important;
}
.header-sub {
  font-size: 0.98rem;
  line-height: 1.55;
  color: var(--ink-muted);
  margin: 10px 0 0;
  max-width: 40rem;
}
.khoi-header.gon .header-sub {
  display: none;
}

.loi-nhac {
  font-size: 0.92rem;
  font-weight: 500 !important;
  color: var(--ink-muted);
  margin: 0 0 12px;
}
.che-do-thu {
  background: var(--accent-tint);
  border: 1px solid rgba(200, 90, 50, 0.22);
  border-radius: var(--r-md);
  padding: 11px 15px;
  font-size: 0.88rem;
  color: #7C2D12;
  margin: 0 0 22px;
}
.phu {
  font-size: 0.83rem;
  color: var(--ink-soft);
  margin: 10px 0 0;
  line-height: 1.5;
}

/* Bong bóng chat & nhãn vai trò */
[data-testid^="stChatMessageAvatar"] { display: none !important; }
[data-testid="stChatMessage"] { background: transparent; padding: 8px 0; gap: 0; }

.hang-nguoi {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}
.nhan-vai {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin: 0 4px 4px;
}
.nhan-vai.ai {
  color: var(--primary);
}
.tin-nguoi {
  background: var(--surface-user);
  border: 1px solid var(--border);
  border-radius: var(--r-lg) var(--r-lg) 4px var(--r-lg);
  padding: 13px 18px;
  max-width: 36rem;
  font-size: 0.96rem;
  font-weight: 400;
  line-height: 1.55;
  color: var(--ink);
}

/* Thẻ phụ ẩn mặc định cho "Trợ lý đọc thành" */
.cau-gui-chi-tiet {
  margin: 0 0 10px;
}
.cau-gui-chi-tiet summary {
  cursor: pointer;
  list-style: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--ink-soft);
  padding: 3px 10px;
  border-radius: var(--r-pill);
  background: var(--surface-warm);
  border: 1px solid var(--border);
  transition: border-color 180ms ease, color 180ms ease;
}
.cau-gui-chi-tiet summary::-webkit-details-marker { display: none; }
.cau-gui-chi-tiet summary:hover {
  color: var(--ink);
  border-color: var(--border-strong);
}
.cau-gui-noi-dung {
  margin-top: 6px;
  padding: 9px 13px;
  border-radius: var(--r-sm);
  background: var(--surface-warm);
  border: 1px solid var(--border);
  font-size: 0.84rem;
  color: var(--ink-muted);
  line-height: 1.5;
}

/* Thẻ lịch trình chuyên nghiệp (giữ nguyên văn 100% H7) */
.to-lich {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 22px 24px;
  box-shadow: var(--shadow-card);
  font-size: 0.95rem;
  line-height: 1.65;
  word-break: break-word;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
}
.to-lich b { font-weight: 600; color: var(--ink); }
.lich-tieu-de {
  font-family: 'Lora', Georgia, serif !important;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--primary);
  padding-bottom: 10px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.lich-diem {
  padding: 8px 12px;
  margin: 6px 0;
  background: var(--canvas);
  border-left: 3px solid var(--primary);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  font-weight: 500;
}
.lich-tong {
  margin: 12px 0 8px;
  padding: 8px 12px;
  background: var(--surface-warm);
  border-radius: var(--r-sm);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--ink);
}
.lich-goi-y-head {
  margin: 14px 0 6px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-strong);
  font-weight: 600;
  color: var(--accent);
}
.lich-goi-y-item {
  padding: 6px 12px;
  margin: 4px 0;
  background: var(--accent-tint);
  border-radius: var(--r-sm);
  font-size: 0.91rem;
  color: var(--ink);
}
.lich-chi-phi {
  margin-top: 14px;
  padding: 10px 14px;
  background: var(--primary-tint);
  border: 1px solid rgba(27, 77, 62, 0.18);
  border-radius: var(--r-sm);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--primary);
}
.lich-dong {
  margin: 4px 0;
  color: var(--ink-muted);
}

/* Nút: hài hòa với bảng màu xanh rừng */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
  background: var(--primary);
  color: #FFFFFF;
  border: 1px solid var(--primary);
  border-radius: var(--r-pill);
  font-weight: 500;
  padding: 10px 20px;
  min-height: 44px;
  cursor: pointer;
  transition: background-color 180ms ease, border-color 180ms ease, transform 120ms ease, box-shadow 180ms ease;
}
.stButton > button p, [data-testid="stFormSubmitButton"] > button p {
  font-weight: 500;
  color: inherit;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  color: #FFFFFF;
}
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active {
  transform: scale(0.985);
}
.stButton > button[kind="secondary"] {
  background: var(--card);
  color: var(--ink);
  border: 1px solid var(--border-strong);
}
.stButton > button[kind="secondary"]:hover {
  background: var(--surface-warm);
  color: var(--ink);
  border-color: var(--primary);
}
.stApp button:focus-visible {
  outline: 2px solid var(--primary) !important;
  outline-offset: 2px;
}

/* Quick Prompts — thẻ gợi ý nhanh 1 chạm */
.st-key-mau .stButton > button {
  background: var(--card);
  color: var(--ink);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  justify-content: flex-start;
  text-align: left;
  padding: 14px 18px;
  min-height: 48px;
  box-shadow: var(--shadow-card);
  margin-bottom: 4px;
}
.st-key-mau .stButton > button:hover {
  border-color: var(--primary);
  background: var(--primary-tint);
  color: var(--ink);
  transform: translateY(-1px);
}
.st-key-mau .stButton > button p {
  text-align: left;
  font-weight: 400;
  font-size: 0.92rem;
  line-height: 1.45;
}
.st-key-mau .stButton > button > div {
  justify-content: flex-start;
  width: 100%;
}

/* Inputs & Chat Input — viền mảnh hiện đại, focus mượt */
[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-baseweb="input"] input,
[data-baseweb="textarea"],
[data-baseweb="textarea"] textarea,
.stNumberInput input,
.stNumberInput button {
  background: var(--card) !important;
  border-radius: var(--r-sm) !important;
  border-color: var(--border-strong) !important;
  color: var(--ink) !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(27, 77, 62, 0.14) !important;
}

[data-testid="stChatInput"] > div {
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--r-lg) !important;
  background: var(--card) !important;
  box-shadow: var(--shadow-input);
  padding: 2px 6px 2px 12px;
  transition: border-color 180ms ease, box-shadow 180ms ease;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(27, 77, 62, 0.14), var(--shadow-input) !important;
}
/* Nút gửi cùng hàng với chữ (Streamlit mặc định để nút ở hàng riêng bên dưới → khoảng trống to, trông như mất chữ) */
[data-testid="stChatInput"] > div > div {
  flex-direction: row !important;
  align-items: flex-end;
  gap: 8px;
}
[data-testid="stChatInput"] > div > div > div:first-child { flex: 1 1 auto; min-width: 0; }
[data-testid="stChatInput"] > div > div > div:last-child { flex: 0 0 auto; width: auto; padding-bottom: 4px; }
[data-testid="stChatInput"] textarea {
  color: var(--ink) !important;
  padding: 8px 2px !important;
  max-height: 9rem;
  overflow-y: auto !important;
  word-break: break-word;
}
.st-key-f_ns [data-testid="stTextInputRootElement"] { display: flex; align-items: center; }
.st-key-f_ns [data-testid="stTextInputRootElement"]::after {
  content: "đ";
  padding: 0 14px 0 4px;
  color: var(--ink-soft);
  font-weight: 500;
}
.st-key-f_ns input { font-variant-numeric: tabular-nums; }
.st-key-f_ns [data-testid="InputInstructions"] { display: none; }
.stElementContainer:has(> .stHtml:empty) { display: none; }
[data-testid="stChatInputSubmitButton"] {
  background: var(--primary) !important;
  color: #FFFFFF !important;
  border-radius: var(--r-pill) !important;
  transition: background-color 180ms ease;
}
[data-testid="stChatInputSubmitButton"]:hover {
  background: var(--primary-hover) !important;
}
[data-testid="stChatInputSubmitButton"]:disabled {
  background: var(--surface-warm) !important;
  color: var(--ink-soft) !important;
}

[data-baseweb="tag"] {
  background: var(--primary) !important;
  border-radius: var(--r-pill) !important;
}
[data-baseweb="tag"] span { color: #FFFFFF !important; }

label p, [data-testid="stWidgetLabel"] p {
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  color: var(--ink-muted);
}
[data-testid="stExpander"] details {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
}
[data-testid="stExpander"] summary p {
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  color: var(--ink);
}
[data-testid="stForm"] { border: 0; padding: 0; }

/* Sidebar phân nhóm trực quan */
[data-testid="stSidebar"] {
  background: var(--surface-warm) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"][data-collapsed="false"] {
  min-width: 20.5rem !important;
  max-width: 22.5rem !important;
  width: 21.5rem !important;
}
[data-testid="stSidebarHeader"] { height: 2.2rem; padding: 0.5rem 1rem 0; }
.sb-title {
  font-family: 'Lora', Georgia, serif !important;
  font-size: 1.32rem;
  font-weight: 600;
  color: var(--ink);
  margin: 4px 0 2px;
}
.sb-sub {
  font-size: 0.8rem;
  color: var(--ink-soft);
  margin: 0 0 14px;
}
.sb-group {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
  border-top: 1px solid var(--border-strong);
  padding-top: 12px;
  margin: 14px 0 8px;
}
.sb-group.first {
  border-top: 0;
  padding-top: 0;
  margin-top: 4px;
}
.ds-diem {
  margin: 0;
  padding: 0;
  list-style: none;
  max-height: 220px;
  overflow-y: auto;
}
.stApp .ds-diem li {
  margin: 0;
  padding: 6px 2px;
  font-size: 0.85rem;
  color: var(--ink-muted);
  border-bottom: 1px solid var(--border);
}
.stApp .ds-diem li:last-child { border-bottom: 0; }
.stApp [data-testid="stSidebar"] hr { border-color: var(--border-strong); margin: 14px 0; }

/* Khung app theo chiều cao nhìn thấy thật: trên điện thoại 100vh tính cả phần bị thanh địa chỉ che → ô chat bị đẩy khuất */
@supports (height: 100dvh) {
  [data-testid="stApp"], [data-testid="stAppViewContainer"] { height: 100dvh !important; bottom: auto !important; }
}
@media (max-width: 768px) {
  [data-testid="stHeader"] { background: var(--canvas) !important; border-bottom: 1px solid var(--border); height: 3rem; }
  .block-container { padding-top: 3.75rem; padding-left: 1rem; padding-right: 1rem; padding-bottom: 1.5rem; }
  .khoi-header { padding: 0 0 14px; margin: 0 0 16px; }
  .khoi-header h1 { font-size: 1.7rem !important; }
  .khoi-header.gon h1 { font-size: 1.3rem !important; }
  .header-sub { font-size: 0.9rem; margin-top: 6px; }
  .che-do-thu { margin-bottom: 14px; font-size: 0.84rem; }
  .st-key-mau .stButton > button { padding: 10px 14px; min-height: 44px; }
  .st-key-mau .stButton > button p { font-size: 0.86rem; }
  [data-testid="stBottomBlockContainer"] {
    padding: 8px 12px calc(10px + env(safe-area-inset-bottom)) !important;
  }
  [data-testid="stChatInput"] textarea { font-size: 16px !important; }  /* < 16px thì iOS tự phóng to khi gõ */
  .to-lich { padding: 16px 18px; }
  .stButton > button, [data-testid="stFormSubmitButton"] > button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
</style>
"""


# ---------------------------------------------------------------- tiện ích


@st.cache_resource
def _khoa() -> threading.Lock:
    """tracing.py giữ trạng thái chung cho cả tiến trình → mỗi lúc chỉ chạy 1 lượt để đếm token đúng."""
    return threading.Lock()


@st.cache_data
def _diem_theo_tp() -> dict:
    return doc_diem()


def _max_luot() -> int:
    try:
        return max(1, int(os.environ.get("MAX_LUOT") or MAX_LUOT_MAC_DINH))
    except ValueError:
        return MAX_LUOT_MAC_DINH


def _md(text: str) -> None:
    st.markdown(text, unsafe_allow_html=True)


def _qua_cong_mat_khau() -> bool:
    """APP_PASSWORD có đặt → bắt nhập đúng mới cho dùng. So sánh hằng thời gian."""
    mat_khau = os.environ.get("APP_PASSWORD", "")
    if not mat_khau or st.session_state.get("da_vao"):
        return True
    _md(
        '<div class="khoi-header">'
        '<div class="header-meta"><span class="header-eyebrow">Trợ lý lịch trình 1 ngày</span></div>'
        '<h1>Đi đâu trước, đi đâu sau.</h1>'
        '<p class="header-sub">Xếp thứ tự theo giờ mở cửa thực tế, gợi ý đổi điểm trong nhà khi trời mưa và ước tính ngân sách cho nhóm.</p>'
        '</div>'
    )
    nhap = st.text_input("Mật khẩu demo", type="password", placeholder="Nhập mật khẩu do nhóm cung cấp")
    if nhap and hmac.compare_digest(nhap.encode("utf-8"), mat_khau.encode("utf-8")):
        st.session_state["da_vao"] = True
        st.rerun()
    if nhap:
        st.error("Sai mật khẩu. Hỏi người trong nhóm để lấy mật khẩu demo.")
    return False


# ---------------------------------------------------------------- trạng thái hội thoại (callback chỉ ghi "chờ gửi")


def _khoi_tao() -> None:
    st.session_state.setdefault("tin", [])          # [{"vai": "user", "chu"} | {"vai": "ai", "output", "cau", "tong"}]
    st.session_state.setdefault("ngu_canh", None)   # câu đã gửi khi agent đang hỏi lại
    st.session_state.setdefault("luot", 0)
    if "o_sua_moi" in st.session_state:             # đặt giá trị ô sửa TRƯỚC khi widget được vẽ
        st.session_state["o_sua"] = st.session_state.pop("o_sua_moi")


def _dat_gui(chu: str, noi: bool) -> None:
    chu = (chu or "").strip()
    if chu:
        st.session_state["cho_gui"] = (chu, noi)


def _gui_tu_chat() -> None:
    _dat_gui(st.session_state.get("o_chat", ""), noi=True)


def _gui_tu_form() -> None:
    s = st.session_state
    if s.get("f_tu") is None or s.get("f_den") is None:
        s["loi_form"] = "Chọn giờ bắt đầu và giờ kết thúc."
        return
    try:
        cau = ghep_cau(s["f_thu"], s["f_tp"], s["f_tu"].strftime("%H:%M"), s["f_den"].strftime("%H:%M"), s["f_pt"],
                       list(s.get("f_diem") or []) + tach_diem_go_tay(s.get("f_khac", "")), doc_tien(s.get("f_ns")))
    except ValueError as e:
        s["loi_form"] = str(e)
        return
    _dat_gui(cau, noi=False)  # form đã đủ thông tin → không nối ngữ cảnh cũ


def _gui_lai_cau_sua() -> None:
    _dat_gui(st.session_state.get("o_sua", ""), noi=False)  # người dùng tự sửa nguyên câu


def _dien_cau_xong_som() -> None:
    cuoi = next((t for t in reversed(st.session_state["tin"]) if t["vai"] == "ai"), None)
    st.session_state["o_sua"] = cau_xong_som(cuoi["cau"] if cuoi else "")


def _cuoc_moi() -> None:
    for k in ("tin", "ngu_canh", "o_sua", "cho_gui"):
        st.session_state.pop(k, None)


def _goi_agent(text: str) -> tuple[str, dict, list] | None:
    """Gọi agent.answer đúng 1 lần. Trả (output, tóm tắt trace, sự kiện trace) hoặc None nếu lỗi."""
    with _khoa():
        tracing.begin("web")
        try:
            result = answer(text)
        except NotImplementedError as e:
            tracing.end()
            st.error("Chưa nối model: %s" % e)
            return None
        except Exception:  # lỗi gọi model (hết lượt, sai key, mất mạng)
            tracing.end()
            log.exception("agent.answer lỗi với câu: %s", text)
            st.error("Không gọi được model (hết lượt hoặc mất mạng). Đợi vài phút rồi gửi lại.")
            return None
        tong, events = tracing.end()
    output = result.get("output", "") if isinstance(result, dict) else str(result)
    return output, tong, events


def _xu_ly_cho_gui() -> None:
    """Có tin chờ gửi → hiện tin người dùng + chờ, gọi agent, lưu lịch sử, vẽ lại trang."""
    chu, noi = st.session_state.pop("cho_gui")
    s = st.session_state
    if s["luot"] >= _max_luot():
        st.warning("Phiên này đã hết %d lượt hỏi. Tải lại trang sau vài phút để hỏi tiếp." % _max_luot())
        return
    cau = noi_tin(chu, s["ngu_canh"]) if noi else chu
    s["luot"] += 1
    s["tin"].append({"vai": "user", "chu": chu})
    with st.chat_message("user", avatar=AVATAR["user"]):
        _md(_bong_bong_nguoi(chu))
    with st.chat_message("assistant", avatar=AVATAR["ai"]), st.spinner("Đang đối chiếu giờ mở cửa…"):
        kq = _goi_agent(cau)
    if kq is None:
        return
    output, tong, events = kq
    s["tin"].append({"vai": "ai", "output": output, "cau": cau, "tong": tong})
    s["ngu_canh"] = ngu_canh_tiep(cau, events)
    s["o_sua_moi"] = cau
    st.rerun()


# ---------------------------------------------------------------- vẽ giao diện


def _ve_tin_ai(t: dict) -> None:
    chi_tiet = ""
    if t["cau"] != _tin_nguoi_truoc(t):
        chi_tiet = (
            '<details class="cau-gui-chi-tiet">'
            '<summary>Trợ lý đọc thành…</summary>'
            '<div class="cau-gui-noi-dung">%s</div>'
            '</details>'
        ) % html.escape(t["cau"])
    _md(
        '<div class="nhan-vai ai">%s<span>Trợ lý lịch trình</span></div>'
        '%s'
        '<div class="to-lich">%s</div>' % (SVG_COMPASS, chi_tiet, _nguyen_van(t["output"]))
    )  # H7: giữ nguyên câu chữ, chỉ ẩn mã điểm


def _tong_token_phien() -> str:
    """Một câu tóm tắt token đã dùng trong cả phiên (cộng từ trace của từng lượt)."""
    lich_su = [t["tong"] for t in st.session_state["tin"] if t["vai"] == "ai"]
    vao = sum(x["tokens_in"] for x in lich_su)
    ra = sum(x["tokens_out"] for x in lich_su)
    model = sorted({m for x in lich_su for m in x["models"]} - {"fake"})
    if not model:
        return "Chưa tốn token nào."
    return "Đã dùng <b>%s token</b> (%s vào, %s ra) với %s." % (
        _so(vao + ra), _so(vao), _so(ra), html.escape(", ".join(model)))


def _so(n: int) -> str:
    """1234567 → 1.234.567 (cách viết số của Việt Nam)."""
    return f"{n:,}".replace(",", ".")


def _bong_bong_nguoi(chu: str) -> str:
    return (
        '<div class="hang-nguoi">'
        '<div class="nhan-vai">Bạn</div>'
        '<div class="tin-nguoi">%s</div>'
        '</div>'
    ) % html.escape(lam_dep_cau(chu))


def _lop_dong(line: str) -> str:
    """Gán lớp CSS trình bày theo loại dòng output — không sửa nội dung chữ (H7)."""
    s = line.strip()
    if s.startswith("Lịch "):
        return "lich-tieu-de"
    if _DONG_LICH.match(s):
        return "lich-diem"
    if s.startswith("Tổng di chuyển:"):
        return "lich-tong"
    if s.startswith("Còn trống "):
        return "lich-goi-y-head"
    if line.startswith("  + ") or s.startswith("+ [POI_"):
        return "lich-goi-y-item"
    if s.startswith("Chi phí ước tính:"):
        return "lich-chi-phi"
    return "lich-dong"


def _nguyen_van(output: str) -> str:
    """Output agent → HTML: escape, giữ thụt đầu dòng, bọc lớp trình bày, ẩn mã điểm [POI_…] (chỉ ở web)."""
    khoi = []
    for line in output.split("\n"):
        if not line.strip():
            khoi.append('<div class="lich-dong">&nbsp;</div>')
            continue
        lop = _lop_dong(line)
        than = line.lstrip(" ")
        thut = 0 if lop == "lich-goi-y-item" else len(line) - len(than)  # thẻ gợi ý đã có khung riêng
        noi_dung = "&nbsp;" * thut + _DAM.sub(r"<b>\1</b>", html.escape(bo_ma_diem(than)))
        khoi.append('<div class="%s">%s</div>' % (lop, noi_dung))
    return "".join(khoi)


def _tin_nguoi_truoc(t: dict) -> str:
    tin = st.session_state["tin"]
    i = tin.index(t)
    return tin[i - 1]["chu"] if i and tin[i - 1]["vai"] == "user" else ""


def _ve_lich_su() -> None:
    for t in st.session_state["tin"]:
        if t["vai"] == "user":
            with st.chat_message("user", avatar=AVATAR["user"]):
                _md(_bong_bong_nguoi(t["chu"]))
        else:
            with st.chat_message("assistant", avatar=AVATAR["ai"]):
                _ve_tin_ai(t)


def _ve_man_trong() -> None:
    _md('<p class="loi-nhac">Gợi ý nhanh — bấm 1 chạm để thử ngay:</p>')
    with st.container(key="mau"):
        for i, (nhan, cau) in enumerate(CAU_MAU):
            st.button(
                "%s  —  %s" % (nhan, lam_dep_cau(cau)),
                key="mau_%d" % i,
                on_click=_dat_gui,
                args=(cau, True),
                type="secondary",
                use_container_width=True,
            )
    _md('<p class="phu">Hoặc chọn điểm từ danh sách ở <b>Điền nhanh</b> (thanh bên; trên điện thoại bấm » góc trên bên trái).</p>')


def _ve_sua_tiep() -> None:
    """Dưới câu trả lời cuối: sửa nguyên câu đã gửi, hoặc hỏi thêm chỗ đi khi còn thời gian."""
    if not any(t["vai"] == "ai" for t in st.session_state["tin"]):
        return
    if st.session_state["ngu_canh"]:
        _md('<p class="loi-nhac">Trợ lý đang hỏi thêm — trả lời ngắn ở ô chat bên dưới, trợ lý sẽ tự ghép với câu trước.</p>')
    with st.expander("Sửa lịch vừa rồi"):
        st.text_area("Thêm hoặc bỏ điểm, đổi giờ ngay trong câu rồi gửi lại", key="o_sua", height=104)
        c1, c2 = st.columns([1, 1.5])
        c1.button("Gửi lại câu này", on_click=_gui_lai_cau_sua, use_container_width=True)
        c2.button("Còn thời gian? Hỏi chỗ đi thêm", on_click=_dien_cau_xong_som, type="secondary",
                  use_container_width=True)
        _md('<p class="phu">Câu hỏi chỗ đi thêm có chỗ trống <b>__:__</b> và <b>____</b>. Điền giờ xong và nơi đang đứng, '
            'rồi gửi lại.</p>')


def _ve_thanh_ben() -> None:
    diem_tp = _diem_theo_tp()
    with st.sidebar:
        _md('<div class="sb-title">Điền nhanh</div>'
            '<p class="sb-sub">Chọn nhanh các thông số, trợ lý sẽ ghép câu và kiểm giờ mở cửa.</p>')

        _md('<div class="sb-group first">1 · Chuyến đi</div>')
        tp = st.selectbox("Thành phố", list(THANH_PHO), key="f_tp")

        with st.form("form_nhanh", border=False):
            c1, c2 = st.columns(2)
            c1.selectbox("Thứ", THU, index=5, key="f_thu")
            c2.selectbox("Phương tiện", PHUONG_TIEN, key="f_pt")

            _md('<div class="sb-group">2 · Thời gian &amp; Ngân sách</div>')
            c3, c4 = st.columns(2)
            c3.time_input("Từ", value=None, step=900, key="f_tu")
            c4.time_input("Đến", value=None, step=900, key="f_den")
            st.text_input(NHAN_NGAN_SACH + " (VNĐ)", key="f_ns", placeholder="Vd: 300.000",
                          help="Gõ số tiền, dấu chấm tự thêm (300.000). Để trống nếu không cần.")

            _md('<div class="sb-group">3 · Điểm muốn ghé</div>')
            st.multiselect("Chọn từ danh sách", diem_tp.get(THANH_PHO[tp], []), key="f_diem",
                           placeholder="Chọn một hoặc nhiều điểm…")
            st.text_area("Nơi khác (tuỳ chọn)", height=64, key="f_khac",
                         placeholder="Mỗi dòng một địa điểm")
            st.form_submit_button("Xếp lịch", on_click=_gui_tu_form, use_container_width=True)

        if "loi_form" in st.session_state:
            st.error(st.session_state.pop("loi_form"))

        ten = diem_tp.get(THANH_PHO[tp], [])
        with st.expander("Điểm có dữ liệu tại %s (%d)" % (tp, len(ten)), expanded=False):
            _md('<ul class="ds-diem">%s</ul>' % "".join("<li>%s</li>" % html.escape(x) for x in ten))
            _md('<p class="phu">Nơi ngoài danh sách này trợ lý sẽ báo không có dữ liệu và không tự bịa.</p>')

        st.divider()
        con = _max_luot() - st.session_state["luot"]
        _md('<p class="phu" style="margin-top:0;margin-bottom:10px;">%s<br>Còn <b>%d</b> lượt hỏi trong phiên.</p>'
            % (_tong_token_phien(), con))
        st.button("Làm mới cuộc trò chuyện", on_click=_cuoc_moi, type="secondary", use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Đi đâu trước, đi đâu sau", page_icon=None, initial_sidebar_state="auto")
    _md(CSS)
    if not _qua_cong_mat_khau():
        return
    _khoi_tao()
    _ve_thanh_ben()
    st.html(JS_NGAN_SACH, unsafe_allow_javascript=True)  # dấu chấm hàng nghìn khi gõ ô ngân sách

    tp_chon = st.session_state.get("f_tp", next(iter(THANH_PHO)))
    so_diem = len(_diem_theo_tp().get(THANH_PHO[tp_chon], []))
    dang_chat = bool(st.session_state.get("tin")) or "cho_gui" in st.session_state
    _md(
        '<div class="khoi-header%s">'
        '<div class="header-meta">'
        '<span class="header-eyebrow">Trợ lý lịch trình 1 ngày</span>'
        '<span class="city-badge">%s<span>%s · %d điểm</span></span>'
        '</div>'
        '<h1>Đi đâu trước, đi đâu sau.</h1>'
        '<p class="header-sub">Xếp thứ tự theo giờ mở cửa thực tế, gợi ý đổi điểm trong nhà khi trời mưa và ước tính ngân sách cho nhóm.</p>'
        '</div>' % (" gon" if dang_chat else "", SVG_PIN, html.escape(tp_chon), so_diem)
    )

    if ai.MODEL_PROVIDER == "fake":
        _md('<div class="che-do-thu">Đang chạy chế độ thử (chưa nối model thật): thứ tự do máy xếp dự phòng, '
            'kết quả ghi "(dự phòng)".</div>')
    if not st.session_state["tin"] and "cho_gui" not in st.session_state:
        _ve_man_trong()
    _ve_lich_su()
    st.chat_input("Thứ mấy, ở đâu, mấy giờ, đi đâu?", key="o_chat",
                  on_submit=_gui_tu_chat)
    if "cho_gui" in st.session_state:
        _xu_ly_cho_gui()
    _ve_sua_tiep()


main()
