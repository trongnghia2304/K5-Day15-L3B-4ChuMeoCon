"""Luồng chính của bản chạy thử — NHÓM VIẾT. Điền ở guide bước 3.2.

`python run.py`, `python run.py eval` và `python run.py simulate` đều gọi answer(text).

Hợp đồng:
    answer(text: str) -> dict có khoá "output" (str): kết quả đưa cho người dùng.
    Token, tên model, số lần gọi model / công cụ: khung tự đếm qua call_model và @tool — không cần trả.
    Bộ chạy gửi NGUYÊN ô input của câu thử vào text. Dữ liệu nền (bài học, thông báo, lịch…)
    do luồng của nhóm tự đọc qua công cụ trong tools.py.

Hình dạng: đúng như sơ đồ ở spec.md §4 (guide bước 2.2) — workflow cố định, một agent, hay nhiều agent.
Khung dưới đây là một workflow 2 bước VÍ DỤ, chỉ để luồng chạy hết từ trước CP2. Thay bằng luồng của nhóm.
Nếu viết vòng lặp agent (AI tự chọn bước tiếp): đặt giới hạn MAX_STEPS và ghi lý do dừng bằng note("dừng: …").
"""
from ai import call_model
from tools import search_pois, get_live_disruptions, get_schedule_warnings
from tracing import note  # noqa: F401

SYSTEM = (
    "Bạn là Travel AI Agent hỗ trợ khách du lịch tự túc tại Việt Nam xếp lịch trình 1 ngày "
    "thuận đường, khớp giờ mở cửa/nghỉ trưa/ngày đóng cửa thực tế và đổi điểm gấp khi gặp sự cố.\n"
    "Quy tắc bắt buộc:\n"
    "1. Chỉ dùng địa điểm, giờ mở cửa, khoảng cách và sự cố có trong phần Căn cứ; tuyệt đối không bịa quán hay giờ mở cửa.\n"
    "2. Không xếp điểm đang đóng cửa, nghỉ giữa ca, quá cutoff vé hoặc quá xa ngoài khung giờ; khi trời mưa/nắng gắt ưu tiên điểm trong nhà (rain_safe/heat_safe=True).\n"
    "3. Nếu thiếu vị trí/thành phố hoặc khung giờ, hỏi lại ngắn gọn tối đa 1-2 câu; nếu yêu cầu bất khả thi hoặc đòi đặt bàn/nhắn tin ra ngoài, từ chối thẳng, nêu rõ căn cứ và gợi ý điểm thay thế hợp lệ (chỉ tạo bản nháp chờ người duyệt).\n"
    "4. Trả lời cực kỳ ngắn gọn, súc tích theo gạch đầu dòng (khung giờ HH:MM-HH:MM · tên điểm · ghi chú ngắn), không viết mở đầu/kết luận dài dòng để tiết kiệm token."
)
MAX_STEPS = 5   # dùng khi viết vòng lặp agent


def answer(text: str) -> dict:
    # Bước 1: lấy căn cứ địa điểm, cảnh báo và sự cố từ data/travel-ops/
    pois = search_pois(query=text, limit=8)
    cities = sorted({p["city"] for p in pois})
    warnings = get_schedule_warnings(city=cities[0]) if len(cities) == 1 else []
    disruptions = get_live_disruptions(city=cities[0]) if len(cities) == 1 else []

    poi_lines = [
        "[%s] %s (%s · %s · %s · rain_safe=%s) — %s"
        % (p["poi_id"], p["name"], p["city"], p["zone"], p["indoor_outdoor"], p["rain_safe"], p["notes"])
        for p in pois
    ]
    warn_lines = ["[%s] %s: %s -> %s" % (w["warning_id"], w["poi_id"], w["detail"], w["suggested_action"]) for w in warnings]
    dis_lines = ["[%s] %s (%s): %s" % (d["disruption_id"], d["poi_id"] or d["zone"], d["disruption_type"], d["description"]) for d in disruptions]

    context = "\n".join(poi_lines + warn_lines + dis_lines) or "(Không tìm thấy địa điểm khớp trong dữ liệu)"
    # Bước 2: model quyết định dựa trên căn cứ
    reply = call_model(SYSTEM, "Căn cứ:\n%s\n\nĐầu vào của người dùng:\n%s" % (context, text))
    return {"output": reply["text"]}
