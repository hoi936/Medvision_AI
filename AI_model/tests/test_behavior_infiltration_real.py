"""Eight real-provider Infiltration behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_infiltration_real.py -v
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
CASES_PATH = Path(__file__).parent / "golden_cases" / "infiltration" / "cases.json"
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

    inspect_hermes_skill("medvision-infiltration")
    inspect_hermes_skill("medvision-infiltration", "references/references.md")

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
        r"\b(phải|hãy)\s+(chụp ct|dùng kháng sinh|dùng thuốc|điều trị|sinh thiết)",
        report.lower(),
    )


def test_isolated_infiltration_preserves_legacy_label_without_disease_conversion():
    report = _report("isolated_infiltration_missing_context")
    lowered = report.lower()
    assert "infiltration" in lowered
    assert any(term in lowered for term in ("không đặc hiệu", "lỗi thời", "legacy", "obsolete"))
    assert "chẩn đoán viêm phổi" not in lowered
    assert "chẩn đoán nhiễm trùng" not in lowered
    assert "chẩn đoán ild" not in lowered


def test_infiltration_and_lung_opacity_remain_distinct_but_deduplicated():
    report = _report("infiltration_with_lung_opacity")
    lowered = report.lower()
    assert "Infiltration" in report
    assert "Lung Opacity" in report
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count"))
    assert "chẩn đoán viêm phổi" not in lowered


def test_consolidation_refines_morphology_without_confirming_pneumonia():
    report = _report("infiltration_with_consolidation")
    lowered = report.lower()
    assert "infiltration" in lowered
    assert "consolidation" in lowered or "đông đặc" in lowered
    assert any(term in lowered for term in ("cụ thể hơn", "more specific", "mô tả hình thái"))
    assert "viêm phổi đã xác nhận" not in lowered
    assert "pneumonia confirmed" not in lowered


def test_triple_overlap_preserves_three_outputs_without_triple_counting():
    report = _report("triple_overlap_with_consolidation")
    lowered = report.lower()
    assert "Infiltration" in report
    assert "Lung Opacity" in report
    assert "consolidation" in lowered or "đông đặc" in lowered
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "triple count"))
    assert "ba finding xác nhận viêm phổi" not in lowered


def test_fever_and_cough_support_hypothesis_without_pathogen_or_antibiotic_order():
    report = _report("infiltration_with_fever_and_cough")
    lowered = report.lower()
    assert "sốt" in lowered and "ho" in lowered
    assert any(term in lowered for term in ("giả thuyết", "nghi ngờ", "cân nhắc", "hypothesis"))
    assert "viêm phổi đã xác nhận" not in lowered
    assert "tác nhân" not in lowered or any(
        term in lowered for term in ("chưa xác định", "không được cung cấp", "không suy diễn")
    )
    _assert_no_autonomous_order(report)


def test_immunocompromised_acute_context_makes_ct_characterization_relevant_only():
    report = _report("immunocompromised_acute_diffuse_context")
    lowered = report.lower()
    assert "suy giảm miễn dịch" in lowered or "immunocompromised" in lowered
    assert "lan tỏa" in lowered or "diffuse" in lowered
    assert "CT_CHARACTERIZATION_RELEVANT" in report
    assert "nhiễm trùng đã xác nhận" not in lowered
    _assert_no_autonomous_order(report)


def test_score_is_preserved_without_underlying_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.84" in report
    assert "84%" not in report
    assert not re.search(
        r"84\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}84\s*%",
        lowered,
    )


def test_ai_later_imaging_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_or_later_imaging_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.79" in report
    assert "ct" in lowered and "không có" in lowered
    assert "infiltration" in lowered
