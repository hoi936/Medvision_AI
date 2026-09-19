"""Unit tests for the Hermes bridge; no provider or network is used."""

from pathlib import Path
from subprocess import CompletedProcess
import sys
from unittest import TestCase
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hermes_report import (
    HermesReportError,
    HermesStatus,
    build_report_prompt,
    generate_hermes_report,
    validate_generated_report,
)
from acceptance_case import build_acceptance_case


SAMPLE_RESULTS = [
    {
        "finding": "Cardiomegaly",
        "positive": True,
        "score": 0.82,
        "threshold": 0.61,
    },
    {
        "finding": "Pneumothorax",
        "positive": False,
        "score": 0.08,
        "threshold": 0.42,
    },
]


class HermesReportTests(TestCase):
    def test_prompt_preserves_safety_and_numeric_evidence(self):
        prompt = build_report_prompt(
            SAMPLE_RESULTS,
            symptoms="Khó thở",
            history="Tăng huyết áp",
            laboratory="SpO2 93%",
            demographics="Nhóm tuổi 50–59",
        )

        self.assertIn('"score": 0.82', prompt)
        self.assertIn('"threshold": 0.61', prompt)
        self.assertIn('"workflow_mode": "MISSING_LABS"', prompt)
        self.assertIn('"provided": true', prompt)
        self.assertIn('"verified": false', prompt)
        self.assertIn("không phải xác suất mắc bệnh", prompt)
        self.assertIn("## 4. Tích hợp bằng chứng", prompt)
        self.assertIn("requires_doctor_review: true", prompt)

    def test_empty_findings_are_rejected(self):
        with self.assertRaises(HermesReportError):
            build_report_prompt([], "", "", "", "")

    def test_unknown_workflow_mode_is_rejected(self):
        with self.assertRaisesRegex(HermesReportError, "không hợp lệ"):
            build_report_prompt(SAMPLE_RESULTS, "", "", "", "", "UNKNOWN")

    def test_acceptance_case_prompt_contains_canonical_reasoning_inputs(self):
        prompt = build_report_prompt(case_payload=build_acceptance_case())

        self.assertIn('"confidence_band": "NEAR_THRESHOLD_NEGATIVE"', prompt)
        self.assertIn('"Chest CT"', prompt)
        self.assertIn('"source": "VITAL_SIGN"', prompt)
        self.assertIn('"source": "LAB"', prompt)
        self.assertIn("không phải xác suất mắc bệnh", prompt)

    def test_missing_fields_are_explicitly_marked_absent(self):
        prompt = build_report_prompt(SAMPLE_RESULTS, "Khó thở", "", "", "")

        self.assertIn('"symptoms": {', prompt)
        self.assertIn('"name": "Khó thở"', prompt)
        self.assertNotIn("Chưa có triệu chứng", prompt)

    @patch("hermes_report.subprocess.run")
    @patch("hermes_report.get_hermes_status")
    def test_cli_is_called_without_shell_and_with_limited_tools(
        self, status_mock, run_mock
    ):
        status_mock.return_value = HermesStatus(True, Path("hermes"), "ready")
        valid_report = """# Bản nháp
## 2. Findings từ mô hình ảnh
## 4. Tích hợp bằng chứng
## 5. Chẩn đoán phân biệt
## 8. Safety flags
## 9. Giới hạn
review_status: PENDING_CLINICIAN_REVIEW
requires_doctor_review: true"""
        run_mock.return_value = CompletedProcess([], 0, valid_report, "")

        report = generate_hermes_report(SAMPLE_RESULTS)

        self.assertEqual(report, valid_report)
        command = run_mock.call_args.args[0]
        self.assertIn("--ignore-rules", command)
        self.assertEqual(command[command.index("-t") + 1], "clarify")
        self.assertEqual(
            command[command.index("--skills") + 1],
            "medvision-evidence-fusion,medvision-safety-check,medvision-disease-analysis",
        )
        self.assertFalse(run_mock.call_args.kwargs["shell"])

    @patch("hermes_report.subprocess.run")
    @patch("hermes_report.get_hermes_status")
    def test_provider_failure_has_setup_guidance(self, status_mock, run_mock):
        status_mock.return_value = HermesStatus(True, Path("hermes"), "ready")
        run_mock.return_value = CompletedProcess([], 1, "", "missing api key")

        with self.assertRaisesRegex(HermesReportError, "hermes setup"):
            generate_hermes_report(SAMPLE_RESULTS)

    def test_report_contract_rejects_missing_review_gate(self):
        missing = validate_generated_report("## 2. Findings từ mô hình ảnh")

        self.assertIn("requires_doctor_review: true", missing)
        self.assertIn("review_status: PENDING_CLINICIAN_REVIEW", missing)
