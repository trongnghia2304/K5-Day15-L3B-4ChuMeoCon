"""Web demo (N4, hướng A+) — giao diện chat; mỗi lượt gửi đúng 1 câu chữ vào agent.answer(text).

Không có logic AI riêng, không tự tính giờ / tiền, không tách dòng output (H7: hiển thị nguyên văn).
Ngữ cảnh: chỉ khi agent vừa HỎI LẠI thì web nối tin mới với câu đã gửi trước (web/hoi_thoai.py).
Chạy máy mình:  python -m pip install -r requirements.txt  →  streamlit run web/streamlit_app.py
Biến môi trường (đặt trong .env ở máy, hoặc Variables trên Railway — KHÔNG ghi vào repo):
    MODEL_PROVIDER, MODEL_NAME, API_KEY   — như docs/connect-model.md (codebase/ai.py đọc)
    APP_PASSWORD                          — mật khẩu vào web; để trống chỉ khi chạy máy mình
    MAX_LUOT                              — số lượt hỏi tối đa mỗi phiên trình duyệt (mặc định 10)

Giao diện theo DESIGN.md: khung đen trắng, nút pill, một khối màu lime ở đầu trang; Inter + JetBrains Mono.
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
from ghep_cau import PHUONG_TIEN, THANH_PHO, THU, doc_diem, ghep_cau, tach_diem_go_tay  # noqa: E402
from hoi_thoai import cau_xong_som, ngu_canh_tiep, noi_tin  # noqa: E402

log = logging.getLogger("web")
_DAM = re.compile(r"\*\*(.+?)\*\*")  # agent đánh dấu chữ đậm kiểu Markdown trong câu hỏi lại
MAX_LUOT_MAC_DINH = 10
AVATAR = {"user": ":material/person:", "ai": ":material/signpost:"}
CAU_MAU = (
    "Thứ Bảy ở Hà Nội từ 8h đến 17h, đi Văn Miếu, Nhà tù Hỏa Lò, Chợ Đồng Xuân",
    "14:05 Thứ Bảy đang ở Thảo Cầm Viên thì mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400&display=swap');
/* Token theo DESIGN.md */
:root {
  --ink:#000000; --canvas:#ffffff; --hairline:#e6e6e6; --hairline-soft:#f1f1f1; --surface-soft:#f7f7f5;
  --block-lime:#dceeb1; --r-sm:6px; --r-md:8px; --r-lg:24px; --r-pill:50px;
}
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stBottom"] > div {
  background:var(--canvas); color:var(--ink); }
.stApp :is(p, li, label, span, div, button, input, textarea):not([data-testid="stIconMaterial"]):not([class*="material"]) {
  font-family:'Inter', system-ui, helvetica, sans-serif; font-feature-settings:"kern"; }
[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display:none; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button { color:var(--ink); }
.block-container { max-width:48rem; padding-top:1.5rem; padding-bottom:7rem; }
.stApp p, .stApp li { font-weight:330; line-height:1.45; letter-spacing:-0.14px; }

/* color-block-section (lime) — khối màu duy nhất trên màn hình */
.khoi { background:var(--block-lime); border-radius:var(--r-lg); padding:48px; margin:0 0 32px; }
.khoi .eyebrow { font-family:'JetBrains Mono', menlo, monospace !important; font-size:.8rem; letter-spacing:.54px;
  text-transform:uppercase; font-weight:400; margin:0 0 20px; }
.khoi h1 { font-family:'Inter', sans-serif !important; font-weight:340 !important; font-size:clamp(2.6rem, 7vw, 4rem) !important;
  line-height:1.04 !important; letter-spacing:-0.96px; margin:0 !important; padding:0 !important; color:var(--ink) !important; }
.stApp .khoi h1 * { font-family:'Inter', sans-serif !important; }
.khoi h1, .stApp .khoi .subhead { text-wrap:balance; }
.khoi.gon { padding:24px 32px; margin-bottom:24px; }
.khoi.gon .eyebrow { margin-bottom:8px; }
.khoi.gon h1 { font-size:1.9rem !important; letter-spacing:-0.4px; }
.khoi.gon .subhead { display:none; }
.stApp .khoi .subhead { font-size:1.3rem; font-weight:340; line-height:1.35; letter-spacing:-0.26px; margin:20px 0 0; max-width:32rem; }

.loi-nhac { font-size:1rem; font-weight:480 !important; margin:0 0 8px; }
.che-do-thu { background:var(--surface-soft); border:1px solid var(--hairline); border-radius:var(--r-md); padding:12px 16px;
  font-size:.92rem; margin:0 0 24px; }
.phu { font-size:.85rem; margin:8px 0 0; }

/* Hội thoại — không ảnh đại diện, tin người dùng căn phải */
[data-testid^="stChatMessageAvatar"] { display:none !important; }
[data-testid="stChatMessage"] { background:transparent; padding:6px 0; gap:0; }
.hang-nguoi { display:flex; justify-content:flex-end; }
.tin-nguoi { background:var(--surface-soft); border-radius:var(--r-lg) var(--r-lg) var(--r-sm) var(--r-lg); padding:12px 18px;
  max-width:34rem; font-size:1rem; font-weight:400; line-height:1.45; }
.cau-gui { font-size:.85rem; margin:0 0 8px; }
.cau-gui b { font-weight:540; }
.to-lich { background:var(--canvas); border:1px solid var(--hairline); border-radius:var(--r-lg); padding:24px;
  font-size:1rem; font-weight:350; line-height:1.75; word-break:break-word; font-variant-numeric:tabular-nums; }
.to-lich b { font-weight:600; }

/* Nút: pill. Chính = đen, phụ = trắng viền mảnh */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
  background:var(--ink); color:var(--canvas); border:1px solid var(--ink); border-radius:var(--r-pill);
  font-weight:480; padding:10px 20px; min-height:44px; }
.stButton > button p, [data-testid="stFormSubmitButton"] > button p { font-weight:480; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background:#222; border-color:#222; color:var(--canvas); }
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active { transform:scale(.98); }
.stButton > button[kind="secondary"] { background:var(--canvas); color:var(--ink); border:1px solid var(--hairline); }
.stButton > button[kind="secondary"]:hover { background:var(--surface-soft); color:var(--ink); border-color:var(--ink); }
.stApp button:focus-visible { outline:2px solid var(--ink) !important; outline-offset:2px; }

/* template-card: câu mẫu */
.st-key-mau .stButton > button { background:var(--surface-soft); color:var(--ink); border:1px solid transparent;
  border-radius:var(--r-md); justify-content:flex-start; text-align:left; padding:16px; min-height:0; }
.st-key-mau .stButton > button:hover { border-color:var(--ink); background:var(--surface-soft); color:var(--ink); }
.st-key-mau .stButton > button p { text-align:left; font-weight:400; }
.st-key-mau .stButton > button > div { justify-content:flex-start; width:100%; }

/* text-input */
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="input"] input, [data-baseweb="textarea"],
[data-baseweb="textarea"] textarea, .stNumberInput input, .stNumberInput button {
  background:var(--canvas) !important; border-radius:var(--r-md) !important; border-color:var(--hairline) !important; }
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
  border-color:var(--ink) !important; box-shadow:0 0 0 1px var(--ink) !important; }
[data-testid="stChatInput"] > div { border:1px solid var(--hairline); border-radius:var(--r-pill); background:var(--canvas); padding-left:8px; }
[data-testid="stChatInput"] > div:focus-within { border-color:var(--ink); box-shadow:0 0 0 1px var(--ink); }
[data-testid="stChatInputSubmitButton"] { background:var(--ink) !important; color:var(--canvas) !important; border-radius:9999px !important; }
[data-testid="stChatInputSubmitButton"]:disabled { background:var(--surface-soft) !important; color:#999 !important; }
[data-baseweb="tag"] { background:var(--ink) !important; border-radius:var(--r-pill) !important; }
[data-baseweb="tag"] span { color:var(--canvas) !important; }
label p, [data-testid="stWidgetLabel"] p { font-size:.9rem !important; font-weight:480 !important; color:var(--ink); }
[data-testid="stExpander"] details { background:var(--canvas); border:1px solid var(--hairline); border-radius:var(--r-md); }
[data-testid="stExpander"] summary p { font-weight:480 !important; }
[data-testid="stForm"] { border:0; padding:0; }

/* Thanh bên */
[data-testid="stSidebar"] { background:var(--canvas); border-right:1px solid var(--hairline); }
[data-testid="stSidebar"][data-collapsed="false"] { min-width:20rem !important; max-width:22rem !important; width:21rem !important; }
[data-testid="stSidebarHeader"] { height:2.2rem; padding:.5rem 1rem 0; }
[data-testid="stSidebar"] h2 { font-family:'Inter', sans-serif !important; font-weight:540 !important; font-size:1.45rem !important;
  letter-spacing:-0.26px; color:var(--ink); margin:8px 0 4px !important; padding:0 !important; }
.ds-diem { margin:0; padding:0; list-style:none; }
.stApp .ds-diem li { margin:0; padding:8px 0; font-size:.92rem; border-bottom:1px solid var(--hairline-soft); }
.stApp [data-testid="stSidebar"] hr { border-color:var(--hairline); }

@media (max-width: 768px) {
  .block-container { padding-top:3.4rem; }
  .khoi { border-radius:0; margin-left:-1rem; margin-right:-1rem; padding:32px 24px; }
  .stButton > button, [data-testid="stFormSubmitButton"] > button { width:100%; }
}
@media (prefers-reduced-motion: reduce) { * { transition:none !important; animation:none !important; } }
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
    nhap = st.text_input("Mật khẩu demo", type="password")
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
                       list(s.get("f_diem") or []) + tach_diem_go_tay(s.get("f_khac", "")), int(s.get("f_ns") or 0) or None)
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
    if t["cau"] != _tin_nguoi_truoc(t):
        _md('<div class="cau-gui">Trợ lý đọc thành: <b>%s</b></div>' % html.escape(t["cau"]))
    _md('<div class="to-lich">%s</div>' % _nguyen_van(t["output"]))  # H7: nguyên văn


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
    return '<div class="hang-nguoi"><div class="tin-nguoi">%s</div></div>' % html.escape(chu)


def _nguyen_van(output: str) -> str:
    """Output agent → 1 dòng HTML giữ nguyên chữ: escape, giữ thụt đầu dòng, xuống dòng bằng <br>.

    Markdown của Streamlit làm hỏng khối HTML nhiều dòng (gộp dòng, đọc "1." thành danh sách), nên không để ký tự
    xuống dòng nào lọt vào chuỗi markdown. Chỉ đổi cách hiển thị, không tách hay sửa nội dung (H7).
    """
    dong = []
    for line in output.split("\n"):
        than = line.lstrip(" ")
        dong.append("&nbsp;" * (len(line) - len(than)) + _DAM.sub(r"<b>\1</b>", html.escape(than)))
    return "<br>".join(dong)


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
    _md('<p class="loi-nhac">Chưa biết nhắn gì? Bấm thử một câu:</p>')
    with st.container(key="mau"):
        for i, cau in enumerate(CAU_MAU):
            st.button(cau, key="mau_%d" % i, on_click=_dat_gui, args=(cau, True), type="secondary",
                      use_container_width=True)
    _md('<p class="phu">Muốn chọn điểm từ danh sách thay vì gõ? Mở mục Điền nhanh ở cột bên trái.</p>')


def _ve_sua_tiep() -> None:
    """Dưới câu trả lời cuối: sửa nguyên câu đã gửi, hoặc hỏi thêm chỗ đi khi còn thời gian."""
    if not any(t["vai"] == "ai" for t in st.session_state["tin"]):
        return
    if st.session_state["ngu_canh"]:
        _md('<p class="loi-nhac">Trợ lý đang hỏi thêm. Trả lời ngắn ở ô chat, trợ lý sẽ ghép với câu trước.</p>')
    with st.expander("Sửa lịch vừa rồi"):
        st.text_area("Thêm hoặc bỏ điểm, đổi giờ ngay trong câu rồi gửi lại", key="o_sua", height=110)
        c1, c2 = st.columns([1, 1.5])
        c1.button("Gửi lại câu này", on_click=_gui_lai_cau_sua, use_container_width=True)
        c2.button("Còn thời gian? Hỏi chỗ đi thêm", on_click=_dien_cau_xong_som, type="secondary",
                  use_container_width=True)
        _md('<p class="phu">Câu hỏi chỗ đi thêm có chỗ trống <b>__:__</b> và <b>____</b>. Điền giờ xong và nơi đang đứng, '
            'rồi gửi lại.</p>')


def _ve_thanh_ben() -> None:
    diem_tp = _diem_theo_tp()
    with st.sidebar:
        st.markdown("## Điền nhanh")
        tp = st.selectbox("Thành phố", list(THANH_PHO), key="f_tp")
        with st.form("form_nhanh", border=False):
            c1, c2 = st.columns(2)
            c1.selectbox("Thứ", THU, index=5, key="f_thu")
            c2.selectbox("Đi bằng", PHUONG_TIEN, key="f_pt")
            c3, c4 = st.columns(2)
            c3.time_input("Từ", value=None, step=900, key="f_tu")
            c4.time_input("Đến", value=None, step=900, key="f_den")
            st.multiselect("Nơi muốn ghé", diem_tp.get(THANH_PHO[tp], []), key="f_diem",
                           placeholder="Chọn từ danh sách")
            st.text_area("Nơi khác, mỗi dòng một nơi", height=68, key="f_khac")
            st.number_input("Ngân sách mỗi người (đồng, để 0 nếu không cần)", min_value=0, step=50000, key="f_ns")
            st.form_submit_button("Xếp lịch", on_click=_gui_tu_form, use_container_width=True)
        if "loi_form" in st.session_state:
            st.error(st.session_state.pop("loi_form"))

        st.markdown("## Điểm có dữ liệu")
        ten = diem_tp.get(THANH_PHO[tp], [])
        _md('<ul class="ds-diem">%s</ul>' % "".join("<li>%s</li>" % html.escape(x) for x in ten))
        _md('<p class="phu">Nơi ngoài danh sách này trợ lý sẽ báo không có dữ liệu và không xếp vào lịch.</p>')

        st.divider()
        con = _max_luot() - st.session_state["luot"]
        st.markdown("## Phiên này")
        _md('<p class="phu">%s<br>Còn %d lượt hỏi.</p>' % (_tong_token_phien(), con))
        st.button("Bắt đầu lại", on_click=_cuoc_moi, type="secondary", use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Đi đâu trước, đi đâu sau", page_icon=None, initial_sidebar_state="auto")
    _md(CSS)
    dang_chat = bool(st.session_state.get("tin")) or "cho_gui" in st.session_state
    _md('<div class="khoi%s"><p class="eyebrow">Lịch trình một ngày</p><h1>Đi đâu trước, đi đâu sau.</h1>'
        '<p class="subhead">Nhắn thành phố, ngày đi, khung giờ và những nơi muốn ghé. Trợ lý xếp thứ tự để tới đâu '
        'cũng còn mở cửa, rồi bạn gửi lịch cho cả nhóm.</p></div>' % (" gon" if dang_chat else ""))
    if not _qua_cong_mat_khau():
        return
    _khoi_tao()
    _ve_thanh_ben()
    if ai.MODEL_PROVIDER == "fake":
        _md('<div class="che-do-thu">Đang chạy chế độ thử, chưa dùng model: thứ tự do máy xếp theo luật đơn giản, '
            'kết quả ghi "(dự phòng)".</div>')
    if not st.session_state["tin"] and "cho_gui" not in st.session_state:
        _ve_man_trong()
    _ve_lich_su()
    st.chat_input("Vd: Thứ Bảy ở Huế từ 8h đến 17h, đi Đại Nội, chùa Thiên Mụ", key="o_chat", on_submit=_gui_tu_chat)
    if "cho_gui" in st.session_state:
        _xu_ly_cho_gui()
    _ve_sua_tiep()


main()
