"""Eight real-provider No finding behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_no_finding_real.py -v
"""

import json
import os
from pathlib import Path
import re
import subprocess

import pytest

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    HERMES_HOME,
    discover_hermes_skills,
    generate_hermes_report,
    hermes_environment,
    hermes_skill_write_approval_enabled,
    inspect_hermes_skill,
    locate_hermes,
)


RUN_REAL = os.environ.get("RUN_HERMES_REAL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="real Hermes tests disabled; set RUN_HERMES_REAL=1 to use the configured provider",
)
CASES_PATH = Path(__file__).parent / "golden_cases" / "no_finding" / "cases.json"
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}


def _runtime_python():
    executable = locate_hermes()
    assert executable is not None
    return executable.parent / ("python.exe" if os.name == "nt" else "python")


def _provider_configuration():
    probe = """
import json
from hermes_cli.config import load_config
from hermes_cli.main import _has_any_provider_configured
cfg = load_config()
model_cfg = cfg.get("model")
if isinstance(model_cfg, dict):
    model = model_cfg.get("default") or model_cfg.get("model") or ""
    provider = model_cfg.get("provider") or ""
else:
    model = model_cfg or ""
    provider = ""
print(json.dumps({"provider_ready": bool(_has_any_provider_configured()), "model": str(model), "provider": str(provider)}))
"""
    completed = subprocess.run(
        [str(_runtime_python()), "-c", probe],
        cwd=Path(__file__).resolve().parents[2],
        env=hermes_environment(),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        pytest.fail(f"INFRASTRUCTURE: provider probe failed: {completed.stderr[-1000:]}")
    return json.loads(completed.stdout)


@pytest.fixture(scope="module", autouse=True)
def runtime_smoke_validation():
    executable = locate_hermes()
    if executable is None:
        pytest.fail("INFRASTRUCTURE: isolated Hermes executable is missing")
    if not HERMES_HOME.is_dir():
        pytest.fail(f"INFRASTRUCTURE: HERMES_HOME does not exist: {HERMES_HOME}")

    expected_skills = {*CORE_HERMES_SKILLS, *FINDING_SKILL_MAP.values()}
    if discover_hermes_skills(executable) != expected_skills:
        pytest.fail("INFRASTRUCTURE: all MedVision skills are not discoverable")
    if not hermes_skill_write_approval_enabled(executable):
        pytest.fail("INFRASTRUCTURE: Hermes skills.write_approval is not enabled")

    for file_path in (
        "references/NO_FINDING_EVIDENCE.md",
        "references/NO_FINDING_REFERENCES.md",
        "references/NO_FINDING_POLICY.md",
    ):
        inspect_hermes_skill("medvision-evidence-fusion", file_path)

    provider = _provider_configuration()
    if not provider["provider_ready"] or not provider["model"]:
        pytest.fail(
            "INFRASTRUCTURE: RUN_HERMES_REAL=1 but no usable provider/model is configured"
        )


def _report(case_id):
    report = generate_hermes_report(**CASES[case_id]["input"])
    assert "review_status: PENDING_CLINICIAN_REVIEW" in report
    assert "requires_doctor_review: true" in report
    return report


def _assert_no_autonomous_order(report):
    assert not re.search(
        r"\b(phải|hãy)\s+(điều trị|dùng thuốc|đặt ống|dẫn lưu|phẫu thuật)",
        report.lower(),
    )


def test_no_finding_only_is_bounded_to_taxonomy_without_health_claim():
    report = _report("no_finding_only")
    lowered = report.lower()
    assert "NO_FINDING_WITHIN_14_CLASS_TAXONOMY" in report
    assert not re.search(r"bệnh nhân (hoàn toàn )?khỏe|không có bất kỳ bệnh", lowered)


def test_no_finding_with_pneumothorax_preserves_conflict_and_positive():
    report = _report("no_finding_with_pneumothorax")
    assert "Pneumothorax" in report
    assert "EVIDENCE_CONFLICT" in report
    assert "NO_FINDING_CONTRADICTION" in report


def test_no_finding_with_multiple_positives_lists_all_in_one_conflict():
    report = _report("no_finding_with_multiple_findings")
    assert "Cardiomegaly" in report
    assert "Pleural effusion" in report
    assert report.count("NO_FINDING_CONTRADICTION") == 1


def test_negative_no_finding_and_all_negative_is_not_established():
    report = _report("no_finding_negative_all_targets_negative")
    assert "NO_FINDING_NOT_ESTABLISHED" in report
    assert not re.search(r"bệnh nhân (hoàn toàn )?khỏe|chắc chắn bất thường", report.lower())


def test_negative_no_finding_routes_positive_without_contradiction():
    report = _report("no_finding_negative_with_nodule_mass")
    assert "Nodule/Mass" in report
    assert "NO_FINDING_CONTRADICTION" not in report


def test_severe_clinical_state_remains_high_priority_without_an_order():
    report = _report("no_finding_with_severe_clinical_state")
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" in report
    assert "No finding" in report
    _assert_no_autonomous_order(report)


def test_no_finding_score_is_not_probability_of_health_or_no_disease():
    report = _report("no_finding_score_semantics")
    lowered = report.lower()
    assert "0.96" in report
    assert not re.search(
        r"96\s*%\s*(xác suất|khả năng|probability|chance)[^\n]{0,60}"
        r"(khỏe|không có bệnh|không có bệnh lý|healthy|no disease)",
        lowered,
    )


def test_ai_no_finding_and_human_ct_abnormality_preserve_both_sources():
    report = _report("no_finding_ai_vs_human_ct_abnormality")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "No finding" in report
    assert "ct" in lowered
    assert any(term in lowered for term in ("bác sĩ", "human", "radiologist"))
