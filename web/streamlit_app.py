"""Web demo (N4, hướng A+) — giao diện chat; mỗi lượt gửi đúng 1 câu chữ vào agent.answer(text).

Không có logic AI riêng, không tự tính giờ / tiền, không tách dòng output (H7: hiển thị nguyên văn).
Ngữ cảnh: chỉ khi agent vừa HỎI LẠI thì web nối tin mới với câu đã gửi trước (web/hoi_thoai.py).
Chạy máy mình:  python -m pip install -r requirements.txt  →  streamlit run web/streamlit_app.py
Biến môi trường (đặt trong .env ở máy, hoặc Variables trên Railway — KHÔNG ghi vào repo):
    MODEL_PROVIDER, MODEL_NAME, API_KEY   — như docs/connect-model.md (codebase/ai.py đọc)
    APP_PASSWORD                          — mật khẩu vào web; để trống chỉ khi chạy máy mình
    MAX_LUOT                              — số lượt hỏi tối đa mỗi phiên trình duyệt (mặc định 10)
"""
import hmac
import html
import logging
import os
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
MAX_LUOT_MAC_DINH = 10
AVATAR = {"user": ":material/person:", "ai": ":material/route:"}
GOI_Y_MO_DAU = ("Thứ Bảy ở Hà Nội từ 8h đến 17h, đi Văn Miếu, Nhà tù Hỏa Lò, Chợ Đồng Xuân",
                "14:05 Thứ Bảy đang ở Thảo Cầm Viên thì mưa lớn, quanh đây có chỗ nào trong nhà đang mở không?")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');
:root { --giay:#f4efe6; --muc:#2b2a27; --nhat:#6f6a60; --vien:#d9d1c2; --nhan:#b4532a; --nhan-toi:#8f3f1e; --the:#fbf8f2; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stBottom"] > div {
  background:var(--giay); color:var(--muc); font-family:'Be Vietnam Pro', system-ui, sans-serif; }
[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none; }
.block-container { max-width:780px; padding-top:2.2rem; padding-bottom:6rem; }
h1, h2, h3 { font-family:'Newsreader', Georgia, serif !important; font-weight:600 !important; color:var(--muc); }
.nhan-nho { font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; color:var(--nhan); font-weight:600; margin:0 0 .35rem; }
.tieu-de { font-family:'Newsreader', Georgia, serif; font-size:2.25rem; line-height:1.15; font-weight:600; margin:0 0 .6rem; }
.dan-nhap { color:var(--nhat); font-size:1rem; line-height:1.6; margin:0 0 1.2rem; max-width:36rem; }
.ghi-chu { font-size:.8rem; color:var(--nhat); }
.bao-gia { background:#efe3cf; border-left:3px solid var(--nhan); padding:.6rem .9rem; font-size:.85rem; margin:0 0 1rem; border-radius:2px; }
[data-testid="stExpander"] details { background:var(--the); border:1px solid var(--vien); border-radius:4px; }
[data-testid="stExpander"] summary p { font-weight:500; }
[data-testid="stForm"] { border:0; padding:0; }
label p, [data-testid="stWidgetLabel"] p { font-size:.85rem !important; font-weight:500; color:var(--muc); }
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"], .stNumberInput input, .stTimeInput input {
  background:#fff !important; border-radius:3px !important; border-color:var(--vien) !important; }
[data-baseweb="tag"] { background:var(--nhan) !important; border-radius:2px !important; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { background:var(--nhan); color:#fff; border:0; border-radius:3px;
  padding:.5rem 1.2rem; font-weight:600; transition:background .15s; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background:var(--nhan-toi); color:#fff; border:0; }
.stButton > button[kind="secondary"] { background:transparent; color:var(--nhan); border:1px solid var(--vien); }
.stButton > button[kind="secondary"]:hover { background:#efe3cf; color:var(--nhan-toi); border:1px solid var(--vien); }
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible { outline:2px solid var(--muc); outline-offset:2px; }
[data-testid="stChatMessage"] { background:transparent; padding:.4rem 0; gap:.8rem; }
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { background:var(--muc); color:var(--giay); border-radius:3px; }
[data-testid="stChatMessageAvatarAssistant"] { background:var(--nhan); }
[data-testid="stChatInput"] > div { border:1px solid var(--vien); border-radius:4px; background:#fff; }
[data-testid="stChatInput"] > div:focus-within { border-color:var(--nhan); }
.tin-nguoi { background:#fff; border:1px solid var(--vien); border-radius:3px; padding:.55rem .85rem; display:inline-block; line-height:1.55; }
.cau-gui { font-size:.78rem; color:var(--nhat); margin:0 0 .45rem; border-left:2px solid var(--vien); padding-left:.6rem; }
.to-lich { background:var(--the); border:1px solid var(--vien); border-top:3px solid var(--nhan); border-radius:3px;
  padding:1rem 1.2rem; font-family:'Be Vietnam Pro', sans-serif; font-size:.93rem; line-height:1.75; white-space:pre-wrap;
  word-break:break-word; margin:0; color:var(--muc); }
.so-do { font-size:.75rem; color:var(--nhat); margin-top:.45rem; font-variant-numeric:tabular-nums; }
.ds-diem { font-size:.88rem; line-height:1.9; color:var(--muc); }
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
        st.error("Sai mật khẩu.")
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
        s["loi_form"] = "Chọn giờ bắt đầu và kết thúc."
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
            st.error("Gọi model bị lỗi (hết lượt / mất mạng). Thử lại sau ít phút.")
            return None
        tong, events = tracing.end()
    output = result.get("output", "") if isinstance(result, dict) else str(result)
    return output, tong, events


def _xu_ly_cho_gui() -> None:
    """Có tin chờ gửi → hiện tin người dùng + chờ, gọi agent, lưu lịch sử, vẽ lại trang."""
    chu, noi = st.session_state.pop("cho_gui")
    s = st.session_state
    if s["luot"] >= _max_luot():
        st.warning("Phiên này đã dùng hết %d lượt hỏi. Mở lại trang sau ít phút nhé." % _max_luot())
        return
    cau = noi_tin(chu, s["ngu_canh"]) if noi else chu
    s["luot"] += 1
    s["tin"].append({"vai": "user", "chu": chu})
    with st.chat_message("user", avatar=AVATAR["user"]):
        _md('<span class="tin-nguoi">%s</span>' % html.escape(chu))
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
    tong = t["tong"]
    _md('<div class="cau-gui">Câu đã gửi cho trợ lý: %s</div>' % html.escape(t["cau"]))
    _md('<pre class="to-lich">%s</pre>' % html.escape(t["output"]))  # H7: nguyên văn
    _md('<div class="so-do">%s · %d lần gọi model · %d lần tra dữ liệu · %d token vào, %d token ra</div>' % (
        html.escape(", ".join(tong["models"]) or "chưa gọi model"), tong["model_calls"], tong["tool_calls"],
        tong["tokens_in"], tong["tokens_out"]))


def _ve_lich_su() -> None:
    for t in st.session_state["tin"]:
        if t["vai"] == "user":
            with st.chat_message("user", avatar=AVATAR["user"]):
                _md('<span class="tin-nguoi">%s</span>' % html.escape(t["chu"]))
        else:
            with st.chat_message("assistant", avatar=AVATAR["ai"]):
                _ve_tin_ai(t)


def _ve_sua_tiep() -> None:
    """Dưới câu trả lời cuối: sửa nguyên câu đã gửi, hoặc hỏi gợi ý thêm khi còn thời gian."""
    if not any(t["vai"] == "ai" for t in st.session_state["tin"]):
        return
    if st.session_state["ngu_canh"]:
        _md('<p class="ghi-chu">Trợ lý đang hỏi thêm — trả lời ngắn ở ô chat bên dưới, '
            'mình sẽ ghép với câu trước.</p>')
    with st.expander("Sửa lịch vừa rồi, hoặc hỏi thêm điểm khi còn thời gian"):
        st.text_area("Sửa thẳng câu đã gửi (thêm / bỏ điểm, đổi giờ) rồi gửi lại", key="o_sua", height=110)
        c1, c2 = st.columns([1, 1.6])
        c1.button("Gửi lại câu này", on_click=_gui_lai_cau_sua, use_container_width=True)
        c2.button("Còn thời gian? Điền câu hỏi gợi ý thêm", on_click=_dien_cau_xong_som, type="secondary",
                  use_container_width=True)
        _md('<p class="ghi-chu">Câu gợi ý thêm có chỗ trống <b>__:__</b> và <b>____</b>: điền giờ xong và nơi đang đứng. '
            'Điểm gợi ý muốn đi thì thêm vào câu lịch rồi gửi lại để trợ lý kiểm giờ mở cửa.</p>')


def _ve_form_nhanh() -> None:
    diem_tp = _diem_theo_tp()
    with st.expander("Điền nhanh bằng form"):
        tp = st.selectbox("Thành phố", list(THANH_PHO), key="f_tp")
        with st.form("form_nhanh", border=False):
            c1, c2, c3, c4 = st.columns(4)
            c1.selectbox("Thứ", THU, index=5, key="f_thu")
            c2.time_input("Từ", value=None, step=900, key="f_tu")
            c3.time_input("Đến", value=None, step=900, key="f_den")
            c4.selectbox("Phương tiện", PHUONG_TIEN, key="f_pt")
            st.multiselect("Nơi muốn ghé (chọn từ dữ liệu)", diem_tp.get(THANH_PHO[tp], []), key="f_diem")
            st.text_area("Nơi khác chưa có trong danh sách, mỗi dòng một nơi", height=68, key="f_khac")
            st.number_input("Ngân sách mỗi người, đồng (bỏ trống nếu không cần)", min_value=0, step=50000, key="f_ns")
            st.form_submit_button("Xếp lịch cho mình", on_click=_gui_tu_form)
        if "loi_form" in st.session_state:
            st.error(st.session_state.pop("loi_form"))


def _ve_danh_sach_diem() -> None:
    diem_tp = _diem_theo_tp()
    with st.expander("Những điểm trợ lý có dữ liệu giờ mở cửa"):
        tp = st.selectbox("Xem ở thành phố", list(THANH_PHO), key="xem_tp")
        ten = diem_tp.get(THANH_PHO[tp], [])
        _md('<div class="ds-diem">%s</div>' % " · ".join(html.escape(x) for x in ten))
        _md('<p class="ghi-chu">Nơi ngoài danh sách này trợ lý sẽ báo "không có dữ liệu" và không xếp vào lịch.</p>')


def main() -> None:
    st.set_page_config(page_title="Lịch một ngày · 4ChuMeoCon", page_icon=None)
    _md(CSS)
    _md('<p class="nhan-nho">Lịch trình một ngày</p>'
        '<h1 class="tieu-de">Đi đâu trước, đi đâu sau, để chỗ nào cũng còn mở cửa.</h1>'
        '<p class="dan-nhap">Nhắn thành phố, thứ, khung giờ và những nơi muốn ghé — thiếu gì trợ lý sẽ hỏi lại. '
        'Đang đi mà gặp mưa hay quán đóng cũng nhắn được. Giờ mở cửa lấy từ dữ liệu của nhóm; '
        'trợ lý không đặt chỗ hay nhắn tin thay bạn.</p>')
    if not _qua_cong_mat_khau():
        return
    _khoi_tao()
    if ai.MODEL_PROVIDER == "fake":
        _md('<div class="bao-gia">Chưa nối model thật. Thứ tự do code dự phòng chọn, kết quả sẽ ghi "(dự phòng)".</div>')
    c1, c2 = st.columns([3, 1])
    c1.markdown('<p class="ghi-chu">Phiên này còn %d / %d lượt hỏi.</p>'
                % (_max_luot() - st.session_state["luot"], _max_luot()), unsafe_allow_html=True)
    c2.button("Cuộc trò chuyện mới", on_click=_cuoc_moi, type="secondary", use_container_width=True)
    _ve_danh_sach_diem()
    _ve_form_nhanh()

    if not st.session_state["tin"]:
        _md('<p class="ghi-chu" style="margin-top:1rem">Ví dụ để nhắn:<br>· %s<br>· %s</p>'
            % tuple(html.escape(x) for x in GOI_Y_MO_DAU))
    _ve_lich_su()
    st.chat_input("Nhắn cho trợ lý…", key="o_chat", on_submit=_gui_tu_chat)
    if "cho_gui" in st.session_state:
        _xu_ly_cho_gui()
    _ve_sua_tiep()


main()
