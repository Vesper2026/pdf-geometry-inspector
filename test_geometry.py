"""Core tests use real pypdf-generated PDFs; all scratch files stay in this project."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import FloatObject, NameObject, NumberObject

from examples.generate_sample import generate_samples, rectangle
from pdf_geometry import inspect_pdf, markdown

ROOT = Path(__file__).resolve().parent


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="geometry-tests-", dir=scratch)
        cls.directory = Path(cls.temp.name)
        generate_samples(cls.directory)
        cls.report = inspect_pdf(cls.directory / "geometry_cases.pdf")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def page(self, index):
        return self.report["pages"][index - 1]

    def codes(self, index):
        return {w["code"] for w in self.page(index)["warnings"]}

    def variant(self, name, configure):
        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=300)
        configure(page)
        path = self.directory / name
        writer.write(path)
        return inspect_pdf(path)["pages"][0]

    def test_real_pdf_and_metadata(self):
        self.assertEqual(len(PdfReader(self.directory / "geometry_cases.pdf").pages), 10)
        self.assertEqual(self.report["page_count"], 10)
        self.assertEqual(self.report["metadata"]["/Title"], "Synthetic PDF geometry cases")
        self.assertFalse(self.report["encrypted"])

    def test_metadata_html_is_displayed_as_text(self):
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=300)
        writer.add_metadata({"/Title": "<b>Review & verify</b>"})
        path = self.directory / "html-metadata.pdf"
        writer.write(path)
        output = markdown(inspect_pdf(path))
        self.assertIn("&lt;b&gt;Review &amp; verify&lt;/b&gt;", output)
        self.assertNotIn("<b>", output)

    def test_a4_and_crop_default(self):
        page = self.page(1)
        self.assertAlmostEqual(page["displayed_dimensions"]["width_mm"], 210, places=5)
        self.assertAlmostEqual(page["displayed_dimensions"]["height_mm"], 297, places=5)
        self.assertEqual(page["orientation"], "portrait")
        self.assertEqual(page["crop_box"]["raw"], page["media_box"]["raw"])
        self.assertEqual(page["crop_box"]["source"], "MediaBox default")

    def test_rotation_90_and_270(self):
        for index in (2, 10):
            page = self.page(index)
            self.assertAlmostEqual(page["displayed_dimensions"]["width_mm"], 297, places=5)
            self.assertAlmostEqual(page["displayed_dimensions"]["height_mm"], 210, places=5)
            self.assertEqual(page["orientation"], "landscape")
            self.assertAlmostEqual(page["visible_dimensions"]["width_mm"], 210, places=5)

    def test_cropped_letter(self):
        page = self.page(3)
        self.assertEqual(page["media_box"]["raw"], [0, 0, 612, 792])
        self.assertEqual(page["crop_box"]["raw"], [54, 36, 558, 756])
        self.assertEqual(page["visible_box_raw"], [54, 36, 558, 756])
        self.assertEqual(page["displayed_dimensions"]["width_pt"], 504)
        self.assertEqual(page["displayed_dimensions"]["height_pt"], 720)
        self.assertEqual(page["displayed_dimensions"]["width_mm"], 177.8)

    def test_user_unit(self):
        page = self.page(4)
        self.assertEqual(page["user_unit"], 2)
        self.assertEqual(page["media_box"]["raw"], [0, 0, 200, 300])
        self.assertEqual(page["displayed_dimensions"]["width_pt"], 400)
        self.assertEqual(page["displayed_dimensions"]["height_pt"], 600)
        self.assertAlmostEqual(page["displayed_dimensions"]["width_mm"], 141.111111, places=6)

    def test_crop_outside_uses_intersection(self):
        page = self.page(5)
        self.assertIn("crop_outside_media", self.codes(5))
        self.assertEqual(page["crop_box"]["raw"], [-20, -10, 700, 900])
        self.assertEqual(page["visible_box_raw"], [0, 0, 612, 792])
        self.assertEqual(page["displayed_dimensions"]["width_pt"], 612)

    def test_empty_intersection_has_no_fabricated_size(self):
        page = self.page(6)
        self.assertIn("empty_intersection", self.codes(6))
        self.assertIsNone(page["visible_box_raw"])
        self.assertIsNone(page["visible_dimensions"])
        self.assertIsNone(page["displayed_dimensions"])
        self.assertEqual(page["orientation"], "unknown")

    def test_arbitrary_rotation_has_only_unrotated_size(self):
        page = self.page(7)
        self.assertIn("non_90_rotation", self.codes(7))
        self.assertEqual(page["rotation_degrees"], 45)
        self.assertEqual(page["visible_dimensions"]["width_pt"], 612)
        self.assertIsNone(page["displayed_dimensions"])
        self.assertEqual(page["orientation"], "unknown")

    def test_nonpositive_boxes_not_reordered(self):
        self.assertIn("non_positive_cropbox", self.codes(8))
        self.assertIn("non_positive_mediabox", self.codes(9))
        self.assertEqual(self.page(9)["media_box"]["raw"], [612, 0, 0, 792])
        self.assertIsNone(self.page(8)["displayed_dimensions"])
        self.assertIsNone(self.page(9)["displayed_dimensions"])

    def test_groups_and_unknown_exclusion(self):
        group = next(g for g in self.report["size_groups"] if g["pages"] == [2, 10])
        self.assertEqual(group["orientation"], "landscape")
        self.assertEqual(self.report["ungrouped_pages"], [6, 7, 8, 9])
        self.assertEqual(sum(len(g["pages"]) for g in self.report["size_groups"]), 6)

    def test_no_metadata(self):
        report = inspect_pdf(self.directory / "no_metadata.pdf")
        self.assertIsNone(report["metadata"])
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["page_count"], 1)

    def test_encrypted_restricted(self):
        report = inspect_pdf(self.directory / "encrypted.pdf")
        self.assertTrue(report["encrypted"])
        self.assertEqual(report["status"], "restricted")
        self.assertEqual(report["access"], "password_required")
        self.assertIsNone(report["metadata"])
        self.assertIsNone(report["page_count"])
        self.assertEqual(report["pages"], [])
        self.assertEqual(report["warnings"][0]["code"], "encrypted_restricted")

    def test_unsupported_encryption_is_restricted(self):
        data = (self.directory / "encrypted.pdf").read_bytes()
        self.assertIn(b"/V 2", data)
        path = self.directory / "unsupported_encryption.pdf"
        path.write_bytes(data.replace(b"/V 2", b"/V 9", 1))
        report = inspect_pdf(path)
        self.assertEqual(report["status"], "restricted")
        self.assertTrue(report["encrypted"])
        self.assertEqual(report["access"], "encryption_unsupported")
        self.assertEqual(report["pages"], [])

    def test_public_three_page_sample(self):
        report = inspect_pdf(self.directory / "sample.pdf")
        self.assertEqual(report["page_count"], 3)
        self.assertEqual(report["pages"][0]["media_box"]["raw"], [0, 0, 595.276, 841.89])
        self.assertEqual(report["pages"][1]["orientation"], "landscape")
        crop = report["pages"][2]
        self.assertEqual(crop["crop_box"]["raw"], [18, 36, 594, 756])
        self.assertEqual(crop["displayed_dimensions"]["width_pt"], 576)
        self.assertEqual(crop["displayed_dimensions"]["width_mm"], 203.2)
        self.assertEqual(crop["displayed_dimensions"]["height_mm"], 254)

    def test_empty_password_encryption(self):
        report = inspect_pdf(self.directory / "empty_password.pdf")
        self.assertTrue(report["encrypted"])
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["access"], "readable_without_supplied_password")
        self.assertEqual(report["page_count"], 1)

    def test_input_hash_unchanged(self):
        for name in ("sample.pdf", "geometry_cases.pdf", "no_metadata.pdf", "encrypted.pdf", "empty_password.pdf"):
            with self.subTest(name=name):
                path = self.directory / name
                before = path.read_bytes()
                report = inspect_pdf(path)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(report["sha256"], hashlib.sha256(before).hexdigest())

    def test_negative_and_large_rotation(self):
        for angle, expected in ((-90, 270), (450, 90)):
            page = self.variant(f"rotate{angle}.pdf", lambda p: p.__setitem__(NameObject("/Rotate"), NumberObject(angle)))
            self.assertEqual(page["normalized_rotation_degrees"], expected)
            self.assertEqual(page["displayed_dimensions"]["width_pt"], 300)

    def test_fractional_rotation_not_truncated(self):
        page = self.variant("fractional.pdf", lambda p: p.__setitem__(NameObject("/Rotate"), FloatObject(90.5)))
        self.assertEqual(page["rotation_degrees"], 90.5)
        self.assertIsNone(page["displayed_dimensions"])

    def test_invalid_unit_unknown_physical_size(self):
        for unit in (0, -2):
            page = self.variant(f"unit{unit}.pdf", lambda p: p.__setitem__(NameObject("/UserUnit"), NumberObject(unit)))
            self.assertIsNone(page["displayed_dimensions"])
            self.assertIn("invalid_user_unit", {w["code"] for w in page["warnings"]})

    def test_offset_partial_crop_and_scaled_rotation(self):
        def configure(page):
            page[NameObject("/MediaBox")] = rectangle([10, 20, 210, 320])
            page[NameObject("/CropBox")] = rectangle([-10, 40, 150, 400])
            page[NameObject("/UserUnit")] = NumberObject(2)
            page[NameObject("/Rotate")] = NumberObject(270)
        page = self.variant("offset.pdf", configure)
        self.assertEqual(page["visible_box_raw"], [10, 40, 150, 320])
        self.assertEqual(page["visible_dimensions"]["width_pt"], 280)
        self.assertEqual(page["displayed_dimensions"]["width_pt"], 560)
        self.assertEqual(page["displayed_dimensions"]["height_pt"], 280)

    def test_inherited_boxes_and_rotation(self):
        def configure(page):
            parent = page["/Parent"]
            parent[NameObject("/MediaBox")] = rectangle([0, 0, 200, 300])
            parent[NameObject("/CropBox")] = rectangle([10, 10, 190, 290])
            parent[NameObject("/Rotate")] = NumberObject(90)
            del page["/MediaBox"]
        page = self.variant("inherited.pdf", configure)
        self.assertEqual(page["crop_box"]["raw"], [10, 10, 190, 290])
        self.assertEqual(page["displayed_dimensions"]["width_pt"], 280)
        self.assertEqual(page["displayed_dimensions"]["height_pt"], 180)

    def test_reports_are_serializable(self):
        json.dumps(self.report, allow_nan=False)
        text = markdown(self.report)
        self.assertIn("Synthetic PDF geometry cases", text)
        self.assertIn("crop_outside_media", text)
        self.assertIn("non_90_rotation", text)
        self.assertIn("mm", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
