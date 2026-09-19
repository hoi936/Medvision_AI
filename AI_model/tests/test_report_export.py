"""Tests for self-contained Markdown/PDF/Word report exports."""

from pathlib import Path
import sys
from unittest import TestCase

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from report_export import build_visual_evidence, export_report, visual_evidence_digest


class ReportExportTests(TestCase):
    def setUp(self):
        gray = np.arange(64, dtype=np.uint8).reshape(8, 8) * 4
        rgb = np.stack([gray, gray, gray], axis=-1)
        finding = {
            "finding": "Pleural effusion",
            "class_id": 8,
            "score": 0.9748,
            "threshold": 0.9136,
            "positive": True,
        }
        visual = {"heatmap": rgb, "overlay": rgb, "boxed_image": rgb}
        self.evidence = build_visual_evidence(original=gray, findings=[(finding, visual)])
        self.report = (
            "# Báo cáo\n\n## 2. Findings từ mô hình ảnh\nNội dung thử nghiệm.\n\n"
            "review_status: PENDING_CLINICIAN_REVIEW\n"
            "requires_doctor_review: true"
        )

    def test_evidence_freezes_four_png_views_and_has_stable_digest(self):
        images = self.evidence[0]["images"]

        self.assertEqual(set(images), {"original", "heatmap", "overlay", "pseudo_bbox"})
        self.assertTrue(all(data.startswith(b"\x89PNG") for data in images.values()))
        self.assertEqual(
            visual_evidence_digest(self.evidence), visual_evidence_digest(self.evidence)
        )

    def test_markdown_is_self_contained_with_embedded_images(self):
        exported = export_report(self.report, self.evidence, "Markdown (.md)")

        text = exported.data.decode("utf-8")
        self.assertEqual(exported.mime, "text/markdown")
        self.assertEqual(exported.filename, "medvision_report.md")
        self.assertEqual(text.count("data:image/png;base64,"), 4)
        self.assertIn("Pseudo bbox suy ra từ Grad-CAM", text)
        self.assertTrue(text.rstrip().endswith("requires_doctor_review: true"))

    def test_pdf_and_word_contain_embedded_images(self):
        pdf = export_report(self.report, self.evidence, "PDF (.pdf)")
        word = export_report(self.report, self.evidence, "Word (.docx)")

        self.assertTrue(pdf.data.startswith(b"%PDF"))
        self.assertGreater(len(pdf.data), 1000)
        self.assertTrue(word.data.startswith(b"PK"))
        self.assertGreater(len(word.data), 1000)
