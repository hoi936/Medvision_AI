"""Eight real-provider Pulmonary fibrosis behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_pulmonary_fibrosis_real.py -v
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
CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "pulmonary_fibrosis" / "cases.json"
)
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

    inspect_hermes_skill("medvision-pulmonary-fibrosis")
    inspect_hermes_skill(
        "medvision-pulmonary-fibrosis", "references/references.md"
    )

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
        r"\b(phải|hãy)\s+(chụp|làm)\s+(ct|hrct|sinh thiết|nội soi)|"
        r"\b(phải|hãy)\s+(điều trị|dùng thuốc)",
        report.lower(),
    )


def test_cxr_fibrosis_without_ct_stays_a_local_finding():
    report = _report("cxr_fibrosis_without_ct")
    lowered = report.lower()
    assert "pulmonary fibrosis" in lowered or "xơ phổi" in lowered
    assert "unknown" in lowered or "chưa xác định" in lowered
    assert not re.search(
        r"\b(chẩn đoán|confirmed)\b[^\n]{0,60}\b(ipf|uip|ppf)\b",
        lowered,
    )
    assert not re.search(r"honeycombing:\s*(present|có)", lowered)
    _assert_no_autonomous_order(report)


def test_ild_and_fibrosis_overlap_preserves_both_without_double_counting():
    report = _report("ild_pulmonary_fibrosis_overlap")
    lowered = report.lower()
    assert "ILD" in report
    assert "Pulmonary fibrosis" in report
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count"))
    assert "ipf đã xác nhận" not in lowered
    assert "ipf confirmed" not in lowered


def test_fibrosis_opacity_infiltration_overlap_is_not_triple_counted():
    report = _report("fibrosis_lung_opacity_infiltration_overlap")
    lowered = report.lower()
    assert "Pulmonary fibrosis" in report
    assert "Lung Opacity" in report
    assert "Infiltration" in report
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "triple count"))
    assert any(term in lowered for term in ("căn nguyên", "etiology", "unknown", "chưa xác định"))


def test_explicit_hrct_morphology_strengthens_fibrotic_evidence_without_ipf():
    report = _report("explicit_hrct_reticulation_traction_bronchiectasis")
    lowered = report.lower()
    assert "lưới hóa" in lowered or "reticulation" in lowered
    assert "giãn phế quản co kéo" in lowered or "traction bronchiectasis" in lowered
    assert "ipf đã xác nhận" not in lowered
    assert "ipf confirmed" not in lowered
    assert not re.search(r"honeycombing:\s*(present|có)", lowered)
    _assert_no_autonomous_order(report)


def test_reported_honeycombing_uip_pattern_does_not_automatically_become_ipf():
    report = _report("hrct_honeycombing_uip_compatible_pattern")
    lowered = report.lower()
    assert "honeycombing" in lowered
    assert "uip" in lowered
    assert "ipf đã xác nhận" not in lowered
    assert "ipf confirmed" not in lowered
    assert any(
        term in lowered
        for term in ("căn nguyên", "etiolog", "đa chuyên khoa", "multidisciplinary")
    )
    _assert_no_autonomous_order(report)


def test_ppf_uses_supplied_non_ipf_fibrosis_and_two_progression_domains():
    report = _report("longitudinal_ppf_two_domains_within_one_year")
    lowered = report.lower()
    assert "ppf" in lowered or "progressive pulmonary fibrosis" in lowered
    assert "không phải ipf" in lowered or "non-ipf" in lowered
    assert "khó thở" in lowered or "symptom" in lowered
    assert any(term in lowered for term in ("tiến triển hình ảnh", "radiological progression"))
    assert any(term in lowered for term in ("8 tháng", "eight months", "trong vòng một năm", "within one year"))
    assert any(term in lowered for term in ("giải thích thay thế", "alternative explanation"))
    _assert_no_autonomous_order(report)


def test_score_is_preserved_without_fibrotic_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.92" in report
    assert not re.search(
        r"92\s*%\s*(xác suất|khả năng|probability|chance)[^\n]{0,60}"
        r"(ipf|uip|ppf|fibrotic ild)|"
        r"(xác suất|probability|chance)[^\n]{0,60}92\s*%",
        lowered,
    )


def test_cxr_ai_hrct_conflict_is_explicit_and_preserves_both_sources():
    report = _report("cxr_ai_hrct_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.81" in report
    assert "hrct" in lowered
    assert "không có" in lowered
    assert "pulmonary fibrosis" in lowered or "xơ hóa phổi" in lowered
    assert any(term in lowered for term in ("cụ thể hơn", "more specific", "characterization"))
