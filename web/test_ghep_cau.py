"""Test phần web (chỉ thư viện chuẩn). Chạy: python web/test_ghep_cau.py -v

Phần tích hợp ép MODEL_PROVIDER=fake để không tốn token và không cần .env.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"  # trước khi import agent / ai

import tracing  # noqa: E402
from ghep_cau import THANH_PHO, doc_diem, ghep_cau, tach_diem_go_tay  # noqa: E402
from hoi_thoai import cau_xong_som, la_hoi_lai, ngu_canh_tiep, noi_tin  # noqa: E402


class GhepCauTest(unittest.TestCase):
    def test_dung_mau_h1_kem_ngan_sach(self):
        cau = ghep_cau("Thứ Bảy", "TP.HCM", "08:00", "17:30", "xe máy",
                       ["Thảo Cầm Viên", "Dinh Độc Lập"], 300000)
        self.assertEqual(cau, "Thứ Bảy ở TP.HCM từ 08:00 đến 17:30 đi xe máy: "
                              "Thảo Cầm Viên, Dinh Độc Lập. Ngân sách 300000đ/người.")

    def test_khong_ngan_sach_thi_bo_ca_cau(self):
        cau = ghep_cau("Chủ Nhật", "Hà Nội", "08:00", "12:00", "đi bộ", ["Văn Miếu"], None)
        self.assertNotIn("Ngân sách", cau)
        self.assertTrue(cau.endswith("Văn Miếu."))

    def test_bo_dau_phay_trong_ten_va_trung_lap(self):
        cau = ghep_cau("Thứ Hai", "Huế", "08:00", "12:00", "ô tô", ["Đại Nội, Huế", "Đại Nội  Huế", " "])
        self.assertIn(": Đại Nội Huế.", cau)

    def test_bao_loi_dau_vao_sai(self):
        ok = dict(thu="Thứ Hai", thanh_pho="Huế", bat_dau="08:00", ket_thuc="12:00",
                  phuong_tien="xe máy", diem=["Đại Nội"])
        for sai in (dict(thu="Monday"), dict(thanh_pho="Paris"), dict(bat_dau="8h"),
                    dict(ket_thuc="07:00"), dict(phuong_tien="bike"), dict(diem=[]),
                    dict(ngan_sach=-5)):
            with self.subTest(sai=sai), self.assertRaises(ValueError):
                ghep_cau(**dict(ok, **sai))

    def test_tach_diem_go_tay(self):
        self.assertEqual(tach_diem_go_tay("A, B\nC;  \n"), ["A", "B", "C"])

    def test_doc_diem_du_12_thanh_pho(self):
        diem = doc_diem()
        self.assertEqual(set(diem), set(THANH_PHO.values()))
        self.assertTrue(all(diem[c] for c in diem))


class TichHopAgentTest(unittest.TestCase):
    """Câu web ghép phải được agent đọc đúng thành phố / thứ / giờ / điểm (chế độ giả)."""

    @classmethod
    def setUpClass(cls):
        import agent
        cls.agent = agent

    def test_agent_tach_dung_cau_web(self):
        cau = ghep_cau("Thứ Bảy", "Hà Nội", "08:00", "17:00", "xe máy",
                       ["Văn Miếu - Quốc Tử Giám", "Nhà tù Hỏa Lò"], 300000)
        req = self.agent._rule_parse(cau)
        self.assertEqual((req["thanh_pho"], req["thu"], req["bat_dau"], req["ket_thuc"]),
                         ("HN", "Sat", "08:00", "17:00"))
        self.assertEqual(req["phuong_tien"], "motorbike")
        self.assertEqual(len(req["diem"]), 2)

    def test_moi_thanh_pho_deu_ra_lich(self):
        diem = doc_diem()
        for ten, ma in THANH_PHO.items():
            with self.subTest(thanh_pho=ten):
                cau = ghep_cau("Thứ Bảy", ten, "08:00", "18:00", "ô tô", diem[ma][:2])
                out = self.agent.answer(cau)["output"]
                self.assertTrue(out.startswith("Lịch "), out[:300])


class HoiThoaiTest(unittest.TestCase):
    def test_khong_ngu_canh_thi_nguyen_van(self):
        self.assertEqual(noi_tin("  xin chào ", None), "xin chào")

    def test_noi_tin_moi_dat_truoc(self):
        self.assertEqual(noi_tin("thứ 7", "Đi Hà Nội: Văn Miếu."), "thứ 7. Đi Hà Nội: Văn Miếu.")
        self.assertEqual(noi_tin("Chủ Nhật!", "A."), "Chủ Nhật! A.")

    def test_nhan_biet_hoi_lai_qua_trace(self):
        self.assertTrue(la_hoi_lai([{"kind": "note", "text": "hỏi lại: thiếu thứ"}]))
        self.assertTrue(la_hoi_lai([{"kind": "note", "text": "hỏi lại (gợi ý): thiếu giờ"}]))
        self.assertFalse(la_hoi_lai([{"kind": "note", "text": "lịch cuối: …"}, {"kind": "tool"}]))
        self.assertIsNone(ngu_canh_tiep("câu", []))

    def test_cau_xong_som_dien_san_diem_da_di(self):
        cau = ghep_cau("Thứ Bảy", "Hà Nội", "08:00", "17:00", "xe máy", ["Văn Miếu", "Chợ Đồng Xuân"], 200000)
        self.assertEqual(cau_xong_som(cau), "Lúc __:__ Thứ Bảy mình đang ở ____ (Hà Nội), xong sớm rồi, quanh đây "
                                            "còn chỗ nào đang mở không? Đã đi: Văn Miếu, Chợ Đồng Xuân.")
        self.assertEqual(cau_xong_som("gõ tự do"), "Lúc __:__ Thứ __ mình đang ở ____, xong sớm rồi, quanh đây "
                                                  "còn chỗ nào đang mở không? Đã đi: ____.")

    def test_cau_xong_som_dien_xong_thi_agent_loai_diem_da_di(self):
        import agent
        cau = ghep_cau("Thứ Bảy", "Hà Nội", "08:00", "17:00", "xe máy", ["Văn Miếu", "Nhà tù Hỏa Lò"], None)
        hoi = cau_xong_som(cau).replace("__:__", "12:00").replace("____", "Chợ Đồng Xuân", 1)
        goi_y = agent.answer(hoi)["output"].split("Gợi ý đang mở")[1]
        self.assertNotIn("POI_HN_04", goi_y)
        self.assertNotIn("POI_HN_01", goi_y)


class HoiThoaiAgentTest(unittest.TestCase):
    """Hai luồng A+ chạy thật qua agent (chế độ giả)."""

    @classmethod
    def setUpClass(cls):
        import agent
        cls.agent = agent

    def _hoi(self, text):
        tracing.begin("test")
        out = self.agent.answer(text)["output"]
        _, events = tracing.end()
        return out, events

    def test_hoi_lai_roi_noi_tin_ra_lich(self):
        tin1 = "Mai đi Hà Nội, muốn ghé Văn Miếu, Nhà tù Hỏa Lò, Chợ Đồng Xuân"
        out1, ev1 = self._hoi(tin1)
        self.assertTrue(la_hoi_lai(ev1), out1)
        out2, ev2 = self._hoi(noi_tin("thứ 7, 8h đến 5h chiều", ngu_canh_tiep(tin1, ev1)))
        self.assertTrue(out2.startswith("Lịch HN — Thứ Bảy, 08:00–17:00"), out2)
        self.assertIsNone(ngu_canh_tiep("x", ev2))

    def test_xong_som_khong_goi_y_lai_diem_da_di(self):
        tin = ("13:00 Thứ Bảy mình đang ở Chợ Đồng Xuân Hà Nội, xong sớm rồi, quanh đây còn chỗ nào "
               "đang mở không? Đã đi: Văn Miếu, Nhà tù Hỏa Lò.")
        out, _ = self._hoi(tin)
        goi_y = out.split("Gợi ý đang mở:")[1]
        self.assertNotIn("POI_HN_04", goi_y)  # Hỏa Lò
        self.assertNotIn("POI_HN_01", goi_y)  # Văn Miếu


if __name__ == "__main__":
    unittest.main()
