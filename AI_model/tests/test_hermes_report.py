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
)


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

        self.assertIn("model_score=0.8200", prompt)
        self.assertIn("decision_threshold=0.6100", prompt)
        self.assertIn("KHÔNG phải xác suất lâm sàng", prompt)
        self.assertIn("không phải chẩn đoán", prompt.lower())
        self.assertIn("dữ liệu không đáng tin cậy", prompt)
        self.assertIn("<workflow_code>MISSING_LABS</workflow_code>", prompt)
        self.assertIn("## Ma trận bằng chứng", prompt)
        self.assertIn("requires_doctor_review: true", prompt)

    def test_empty_findings_are_rejected(self):
        with self.assertRaises(HermesReportError):
            build_report_prompt([], "", "", "", "")

    def test_unknown_workflow_mode_is_rejected(self):
        with self.assertRaisesRegex(HermesReportError, "không hợp lệ"):
            build_report_prompt(SAMPLE_RESULTS, "", "", "", "", "UNKNOWN")

    @patch("hermes_report.subprocess.run")
    @patch("hermes_report.get_hermes_status")
    def test_cli_is_called_without_shell_and_with_limited_tools(
        self, status_mock, run_mock
    ):
        status_mock.return_value = HermesStatus(True, Path("hermes"), "ready")
        run_mock.return_value = CompletedProcess([], 0, "# Báo cáo nháp", "")

        report = generate_hermes_report(SAMPLE_RESULTS)

        self.assertEqual(report, "# Báo cáo nháp")
        command = run_mock.call_args.args[0]
        self.assertIn("--ignore-rules", command)
        self.assertEqual(command[command.index("-t") + 1], "clarify")
        self.assertEqual(
            command[command.index("--skills") + 1], "medvision-disease-analysis"
        )
        self.assertFalse(run_mock.call_args.kwargs["shell"])

    @patch("hermes_report.subprocess.run")
    @patch("hermes_report.get_hermes_status")
    def test_provider_failure_has_setup_guidance(self, status_mock, run_mock):
        status_mock.return_value = HermesStatus(True, Path("hermes"), "ready")
        run_mock.return_value = CompletedProcess([], 1, "", "missing api key")

        with self.assertRaisesRegex(HermesReportError, "hermes setup"):
            generate_hermes_report(SAMPLE_RESULTS)
